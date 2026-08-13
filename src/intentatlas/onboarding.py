from __future__ import annotations

import json
import locale
import os
import re
import shutil
import subprocess  # nosec B404
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import IO, Any

from .acquisition import CacheEntry, ManagedRepositoryCache, is_github_url, normalize_github_url
from .change_report import ChangeReport, collect_change_report_context, render_change_report
from .change_set import ChangeSet, collect_change_set
from .config import ProjectConfig
from .diagnostic import RepositoryDiagnostic, diagnose_repository
from .graph import AtlasGraph
from .viewer import serve_graph

MAX_GIT_OUTPUT_BYTES = 1_000_000
MAX_TERMINAL_VALUE = 4_096
_BIDI_CONTROLS = frozenset(
    {
        "\u061c",
        "\u200e",
        "\u200f",
        "\u202a",
        "\u202b",
        "\u202c",
        "\u202d",
        "\u202e",
        "\u2066",
        "\u2067",
        "\u2068",
        "\u2069",
    }
)
_REVISION = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/@{}^~+\-]{0,199}$")


MESSAGES: dict[str, dict[str, str]] = {
    "en": {
        "title": "IntentAtlas guided change analysis",
        "path_prompt": "Local project directory or public GitHub repository URL: ",
        "remote_source": "Public source: {value}",
        "remote_consent": (
            "Enter  Approve bounded HTTPS acquisition into the managed local cache and analyze | "
            "Q  Exit: "
        ),
        "remote_trust": (
            "This may contact github.com and write only the managed OS cache. It uses a shallow "
            "history bound of {history}, rejects credentials/private repositories, disables "
            "hooks, filters, submodules, LFS smudging, plugins, and project code, and excludes "
            "atlas/Private. Limits: {files} files, {bytes} checkout bytes, {seconds} seconds."
        ),
        "acquiring": "Stage: acquiring approved public repository",
        "cache": (
            "Managed cache: {state}; ID {id}; exact revision {revision}; history "
            "{commits}/{depth} commits"
        ),
        "root": "Repository root: {value}",
        "scope": "Recommended scope: {value}",
        "trust": (
            "Local and no external request; no writes, tests, hooks, project code, plugins, "
            "indexers, compilers, or package managers; atlas/Private excluded."
        ),
        "trust_network_path": (
            "No external request is made by IntentAtlas; operating-system access to this path may "
            "be network-backed. No writes, tests, hooks, project code, plugins, indexers, "
            "compilers, or package managers; atlas/Private excluded."
        ),
        "cancel": "Ctrl+C cancels safely without persistent output.",
        "readiness": (
            "Readiness limits: unsupported languages {unsupported}; oversized supported files "
            "{oversized}; discovery truncated {truncated}; workspace ambiguity {ambiguity}."
        ),
        "ambiguity_scope": (
            "Workspace ambiguity is a readiness heuristic, not proof that symbol resolution "
            "abstained; exact edges still require unique workspace, module, and symbol identity."
        ),
        "confirm": "Enter  Analyze the recommended scope | S  Select scope | Q  Exit: ",
        "scope_menu": (
            "W worktree | S staged | H exact HEAD | C explicit commit | R explicit range | Q exit: "
        ),
        "commit_prompt": "Commit revision: ",
        "base_prompt": "Base revision: ",
        "head_prompt": "Head revision: ",
        "checking": "Stage: checking repository",
        "selecting": "Stage: selecting scope",
        "building": "Stage: building local evidence",
        "ranking": "Stage: ranking requirements and tests",
        "project": "Project: {value}",
        "revision": "Revision: base {base}; head {head}",
        "state": "Analysis state: {state} ({meaning}); freshness: {freshness}",
        "threshold": "Minimum confidence: {value}",
        "changed": "Changed files: {value}",
        "revision_action": (
            "Revision action: use a clean checkout whose HEAD exactly matches {revision}, then "
            "run intentatlas changes --commit HEAD --report there."
        ),
        "requirements": (
            "Requirements: {selected} selected / {total} candidates; {filtered} below threshold; "
            "{limited} omitted by result limit; {shown}/{omitted} omission details shown"
        ),
        "tests": (
            "Tests: {selected} selected / {total} candidates; {filtered} below threshold; "
            "{limited} omitted by result limit; {shown}/{omitted} omission details shown"
        ),
        "selected_requirement": (
            "- requirement {id}: {score}/100 ({confidence}); reason {reason}; evidence {evidence}"
        ),
        "selected_test": (
            "- test {id}: {score}/100 ({confidence}); reasons {reason}; evidence {evidence}"
        ),
        "omissions": (
            "Omissions shown: requirements {requirements}; tests {tests}. Not selected never means "
            "unaffected or unnecessary."
        ),
        "strategy": "Test strategy: {strategy} - {meaning}",
        "tests_executed": "Tests executed: 0",
        "advisory": "Advisory: {value}",
        "atlas_ready": "Atlas ready: {nodes} nodes; {relations} relations; {orphans} disconnected",
        "layers": (
            "Layers: requirements {requirements}; decisions {decisions}; issues {issues}; "
            "code {code}; tests {tests}; evidence {evidence}; missing {missing}"
        ),
        "actions": (
            "1 reasons | 2 omissions | 3 complete details | 4 open exact interactive Atlas | "
            "5 another scope | 6 commands | L Language/Dil | Enter or Q exit: "
        ),
        "reasons_title": "Selection reasons from this snapshot:",
        "omissions_title": "Omitted candidates from this snapshot:",
        "none": "none",
        "commands_title": "Commands shown only; none were executed:",
        "viewer_error": "Browser/viewer unavailable; the terminal result remains valid: {value}",
        "bye": "Exited without persistent output.",
        "interrupted": "Cancelled safely; no persistent output was created.",
    },
    "tr": {
        "title": "IntentAtlas rehberli değişiklik analizi",
        "path_prompt": "Yerel proje dizini veya public GitHub repository URL: ",
        "remote_source": "Public kaynak: {value}",
        "remote_consent": (
            "Enter  Sınırlı HTTPS edinimini yönetilen yerel cache'e ve analizi onayla | "
            "Q  Çık: "
        ),
        "remote_trust": (
            "Bu işlem github.com ile iletişim kurabilir ve yalnız yönetilen OS cache'ine yazar. "
            "History sınırı {history}; credentials/private repositories reddedilir; hooks, "
            "filters, submodules, LFS smudging, plugins ve proje kodu devre dışıdır; "
            "atlas/Private hariçtir. Sınırlar: {files} dosya, {bytes} checkout byte, "
            "{seconds} saniye."
        ),
        "acquiring": "Aşama: onaylanan public repository ediniliyor",
        "cache": (
            "Yönetilen cache: {state}; ID {id}; exact revision {revision}; history "
            "{commits}/{depth} commit"
        ),
        "root": "Depo kökü: {value}",
        "scope": "Önerilen kapsam: {value}",
        "trust": (
            "Yerel ve harici istek yok; yazma, test, hook, proje kodu, eklenti, indexer, "
            "derleyici veya paket yöneticisi çalıştırılmaz; atlas/Private hariç tutulur."
        ),
        "trust_network_path": (
            "IntentAtlas harici istek yapmaz; bu yola işletim sistemi erişimi ağ destekli "
            "olabilir. Yazma, test, hook, proje kodu, eklenti, indexer, derleyici veya paket "
            "yöneticisi çalıştırılmaz; atlas/Private hariç tutulur."
        ),
        "cancel": "Ctrl+C kalıcı çıktı oluşturmadan güvenle iptal eder.",
        "readiness": (
            "Hazırlık sınırları: unsupported languages {unsupported}; oversized supported files "
            "{oversized}; discovery truncated {truncated}; workspace ambiguity {ambiguity}."
        ),
        "ambiguity_scope": (
            "Workspace ambiguity bir hazırlık sezgisidir; symbol resolution'ın abstain ettiğini "
            "kanıtlamaz. Exact edge için workspace, module ve symbol kimliği unique olmalıdır."
        ),
        "confirm": "Enter  Önerilen kapsamı analiz et | S  Kapsam seç | Q  Çık: ",
        "scope_menu": (
            "W worktree | S staged | H exact HEAD | C açık commit | R açık range | Q çık: "
        ),
        "commit_prompt": "Commit revision: ",
        "base_prompt": "Base revision: ",
        "head_prompt": "Head revision: ",
        "checking": "Aşama: depo denetleniyor",
        "selecting": "Aşama: kapsam seçiliyor",
        "building": "Aşama: yerel kanıt oluşturuluyor",
        "ranking": "Aşama: gereksinimler ve testler sıralanıyor",
        "project": "Proje: {value}",
        "revision": "Revision: base {base}; head {head}",
        "state": "Analysis state: {state} ({meaning}); freshness: {freshness}",
        "threshold": "Minimum confidence: {value}",
        "changed": "Değişen dosyalar: {value}",
        "revision_action": (
            "Revision eylemi: HEAD'i tam olarak {revision} ile eşleşen temiz bir checkout kullan, "
            "ardından orada intentatlas changes --commit HEAD --report çalıştır."
        ),
        "requirements": (
            "Gereksinimler: {selected} seçildi / {total} aday; {filtered} threshold altında; "
            "{limited} result limit nedeniyle atlandı; {shown}/{omitted} omission ayrıntısı "
            "gösteriliyor"
        ),
        "tests": (
            "Testler: {selected} seçildi / {total} aday; {filtered} threshold altında; "
            "{limited} result limit nedeniyle atlandı; {shown}/{omitted} omission ayrıntısı "
            "gösteriliyor"
        ),
        "selected_requirement": (
            "- requirement {id}: {score}/100 ({confidence}); neden {reason}; evidence {evidence}"
        ),
        "selected_test": (
            "- test {id}: {score}/100 ({confidence}); nedenler {reason}; evidence {evidence}"
        ),
        "omissions": (
            "Gösterilen omissions: requirements {requirements}; tests {tests}. Seçilmemek hiçbir "
            "zaman etkilenmemek veya gereksiz olmak anlamına gelmez."
        ),
        "strategy": "Test strategy: {strategy} - {meaning}",
        "tests_executed": "Tests executed: 0",
        "advisory": "Advisory: {value}",
        "atlas_ready": "Atlas hazır: {nodes} node; {relations} relation; {orphans} disconnected",
        "layers": (
            "Katmanlar: requirements {requirements}; decisions {decisions}; issues {issues}; "
            "code {code}; tests {tests}; evidence {evidence}; eksik {missing}"
        ),
        "actions": (
            "1 nedenler | 2 omissions | 3 tüm ayrıntılar | 4 exact interactive Atlas aç | "
            "5 başka kapsam | 6 komutlar | L Language/Dil | Enter veya Q çık: "
        ),
        "reasons_title": "Bu snapshot içindeki seçim nedenleri:",
        "omissions_title": "Bu snapshot içindeki atlanan adaylar:",
        "none": "yok",
        "commands_title": "Komutlar yalnız gösterildi; hiçbiri çalıştırılmadı:",
        "viewer_error": "Browser/viewer kullanılamadı; terminal sonucu geçerlidir: {value}",
        "bye": "Kalıcı çıktı oluşturmadan çıkıldı.",
        "interrupted": "Güvenle iptal edildi; kalıcı çıktı oluşturulmadı.",
    },
}


LAYOUT_TEXT: dict[str, dict[str, str]] = {
    "en": {
        "subtitle": "Guided source-to-atlas analysis",
        "source": "SOURCE AND SCOPE",
        "safety": "SAFETY BOUNDARY",
        "analysis": "ANALYSIS RESULT",
        "recommendations": "RECOMMENDATIONS",
        "atlas": "ATLAS SNAPSHOT",
        "actions": "NEXT ACTION",
        "scope_options": "SCOPE OPTIONS",
        "choice": "Choice: ",
        "confirm_enter": "[Enter] Analyze the recommended scope",
        "confirm_scope": "[S] Select a different scope",
        "remote_enter": "[Enter] Approve bounded HTTPS acquisition and analyze",
        "scope_worktree": "[W] worktree",
        "scope_staged": "[S] staged",
        "scope_head": "[H] exact HEAD",
        "scope_commit": "[C] explicit commit",
        "scope_range": "[R] explicit range",
        "exit": "[Q] Exit",
        "action_reasons": "[1] Show selection reasons",
        "action_omissions": "[2] Show bounded omissions",
        "action_details": "[3] Show complete JSON details",
        "action_viewer": "[4] Open this exact snapshot in the interactive Atlas",
        "action_scope": "[5] Analyze another scope",
        "action_commands": "[6] Show commands without executing them",
        "action_language": "[L] Language / Dil",
        "action_exit": "[Enter/Q] Exit",
        "reason": "reason",
        "evidence": "evidence",
    },
    "tr": {
        "subtitle": "Rehberli source-to-atlas analizi",
        "source": "KAYNAK VE KAPSAM",
        "safety": "GÜVENLİK SINIRI",
        "analysis": "ANALİZ SONUCU",
        "recommendations": "ÖNERİLER",
        "atlas": "ATLAS SNAPSHOT",
        "actions": "SONRAKİ EYLEM",
        "scope_options": "KAPSAM SEÇENEKLERİ",
        "choice": "Seçim: ",
        "confirm_enter": "[Enter] Önerilen kapsamı analiz et",
        "confirm_scope": "[S] Farklı kapsam seç",
        "remote_enter": "[Enter] Sınırlı HTTPS edinimini onayla ve analiz et",
        "scope_worktree": "[W] worktree",
        "scope_staged": "[S] staged",
        "scope_head": "[H] exact HEAD",
        "scope_commit": "[C] açık commit",
        "scope_range": "[R] açık range",
        "exit": "[Q] Çık",
        "action_reasons": "[1] Seçim nedenlerini göster",
        "action_omissions": "[2] Sınırlı omissions listesini göster",
        "action_details": "[3] Tüm JSON ayrıntılarını göster",
        "action_viewer": "[4] Bu exact snapshot'ı interaktif Atlas'ta aç",
        "action_scope": "[5] Başka bir kapsamı analiz et",
        "action_commands": "[6] Komutları çalıştırmadan göster",
        "action_language": "[L] Language / Dil",
        "action_exit": "[Enter/Q] Çık",
        "reason": "neden",
        "evidence": "kanıt",
    },
}


STATE_MEANINGS = {
    "en": {
        "analyzed": "the selected changes were structurally analyzed",
        "fallback": "some evidence is not exact; conservative fallback applies",
        "unknown": "targeted ranking is withheld because evidence is insufficient",
    },
    "tr": {
        "analyzed": "seçilen değişiklikler yapısal olarak analiz edildi",
        "fallback": "bazı kanıtlar exact değil; ihtiyatlı fallback uygulanır",
        "unknown": "kanıt yetersiz olduğundan targeted sıralama sunulmaz",
    },
}


STRATEGY_MEANINGS = {
    "en": {
        "targeted": "start with listed tests; the subset is not proof of sufficiency",
        "targeted-plus-full-suite": "start with listed tests, then run the full suite",
        "full-suite-fallback": "no safe targeted set was proven; run the full suite",
        "abstain-and-full-suite": "targeted ranking is withheld; run the full suite",
        "no-targets-found": "no linked test was proven; follow the normal/full test policy",
        "no-changes": "the selected scope has no changes; choose another scope or exit",
    },
    "tr": {
        "targeted": "listelenen testlerle başla; bu küme yeterlilik kanıtı değildir",
        "targeted-plus-full-suite": "listelenen testlerle başla, sonra tüm suite'i çalıştır",
        "full-suite-fallback": "güvenli targeted küme kanıtlanmadı; tüm suite'i çalıştır",
        "abstain-and-full-suite": "targeted sıralama sunulmaz; tüm suite'i çalıştır",
        "no-targets-found": "bağlı test kanıtlanmadı; normal/tam test politikasını uygula",
        "no-changes": "seçilen kapsamda değişiklik yok; başka kapsam seç veya çık",
    },
}


@dataclass(slots=True)
class TerminalIO:
    input: IO[str]
    output: IO[str]

    @classmethod
    def system(cls) -> TerminalIO:
        return cls(sys.stdin, sys.stdout)

    @property
    def interactive(self) -> bool:
        return bool(self.input.isatty() and self.output.isatty())

    def write(self, value: str = "") -> None:
        rendered = _terminal_text(value)
        encoding = getattr(self.output, "encoding", None) or "utf-8"
        rendered = rendered.encode(encoding, errors="backslashreplace").decode(
            encoding, errors="replace"
        )
        self.output.write(rendered + "\n")
        self.output.flush()

    def read(self, prompt: str) -> str | None:
        self.output.write(_terminal_text(prompt))
        self.output.flush()
        value = self.input.readline()
        if value == "":
            return None
        return value.rstrip("\r\n")


def _render_banner(terminal: TerminalIO, language: str) -> None:
    terminal.write("=" * 68)
    terminal.write("  I N T E N T A T L A S")
    terminal.write(f"  {LAYOUT_TEXT[language]['subtitle']}")
    terminal.write("=" * 68)


def _render_section(terminal: TerminalIO, language: str, key: str) -> None:
    terminal.write("")
    terminal.write(f"--- {LAYOUT_TEXT[language][key]} ---")


def _read_menu(terminal: TerminalIO, language: str, *keys: str) -> str | None:
    for key in keys:
        terminal.write(f"  {LAYOUT_TEXT[language][key]}")
    return terminal.read(LAYOUT_TEXT[language]["choice"])


def _write_wrapped(
    terminal: TerminalIO,
    value: str,
    *,
    subsequent_indent: str = "",
    width: int = 120,
) -> None:
    safe = _terminal_text(value)
    lines = textwrap.wrap(
        safe,
        width=width,
        subsequent_indent=subsequent_indent,
        break_long_words=False,
        break_on_hyphens=False,
    )
    for line in lines or [""]:
        terminal.write(line)


@dataclass(frozen=True, slots=True)
class GuideScope:
    scope: str
    revision: str | None = None
    base: str | None = None
    head: str | None = None

    def display(self) -> str:
        if self.scope == "commit":
            return f"commit {self.revision}"
        if self.scope == "range":
            return f"range {self.base}..{self.head}"
        return self.scope


@dataclass(frozen=True, slots=True)
class GuideSnapshot:
    root: Path
    diagnostic: RepositoryDiagnostic
    change_set: ChangeSet
    graph: AtlasGraph
    report: ChangeReport
    graph_document: bytes
    report_document: bytes
    source: CacheEntry | None = None


def run_guide(
    path: str | Path | None = None,
    *,
    language: str | None = None,
    terminal: TerminalIO | None = None,
    cache: ManagedRepositoryCache | None = None,
) -> int:
    """Run one no-write guided session on an explicitly interactive terminal."""

    active_terminal = terminal or TerminalIO.system()
    if not active_terminal.interactive:
        raise ValueError(
            "guided mode requires interactive stdin and stdout. In a non-interactive shell, "
            "use `intentatlas diagnose PATH`, then `intentatlas changes PATH --commit HEAD "
            "--report` (or `--worktree --report` for uncommitted changes)."
        )
    active_language = _language(language)
    try:
        _render_banner(active_terminal, active_language)
        active_terminal.write(_message(active_language, "checking"))
        root, source = _session_source(
            path,
            active_terminal,
            active_language,
            cache or ManagedRepositoryCache(),
        )
        diagnostic = diagnose_repository(root)
        if diagnostic.git_state not in {"ready", "empty"}:
            raise ValueError(f"repository is not ready for guided analysis: {diagnostic.git_state}")
        config = ProjectConfig.load(root)
        _reject_private_target(root, root, config)
        active_terminal.write(_message(active_language, "selecting"))
        scope = select_default_scope(root)
        if source is not None:
            _render_confirmation(active_terminal, active_language, root, scope, diagnostic)
            snapshot = _collect_snapshot(
                root,
                diagnostic,
                config,
                scope,
                active_terminal,
                active_language,
                source,
            )
            _render_summary(snapshot, active_terminal, active_language)
            action = _post_result(snapshot, active_terminal, active_language)
            while isinstance(action, str):
                active_language = action
                _render_summary(snapshot, active_terminal, active_language)
                action = _post_result(snapshot, active_terminal, active_language)
            if action is None:
                return 0
            scope = action
        while True:
            _render_confirmation(active_terminal, active_language, root, scope, diagnostic)
            choice = _read_menu(
                active_terminal,
                active_language,
                "confirm_enter",
                "confirm_scope",
                "exit",
            )
            if choice is None or choice.strip().casefold() == "q":
                active_terminal.write(_message(active_language, "bye"))
                return 0
            if choice.strip().casefold() == "s":
                selected = _select_scope(root, active_terminal, active_language)
                if selected is None:
                    active_terminal.write(_message(active_language, "bye"))
                    return 0
                scope = selected
                continue
            if choice.strip():
                continue
            snapshot = _collect_snapshot(
                root,
                diagnostic,
                config,
                scope,
                active_terminal,
                active_language,
            )
            _render_summary(snapshot, active_terminal, active_language)
            action = _post_result(snapshot, active_terminal, active_language)
            while isinstance(action, str):
                active_language = action
                _render_summary(snapshot, active_terminal, active_language)
                action = _post_result(snapshot, active_terminal, active_language)
            if action is None:
                return 0
            scope = action
    except KeyboardInterrupt:
        active_terminal.write(_message(active_language, "interrupted"))
        return 130


def select_default_scope(root: Path) -> GuideScope:
    """Select the conservative default from bounded Git metadata."""

    executable = shutil.which("git")
    if executable is None:
        raise ValueError("Git is required for guided analysis")
    head = _try_resolve_revision(root, executable, "HEAD")
    conflict = bool(
        _git_output(
            root,
            executable,
            "diff",
            "--name-only",
            "--diff-filter=U",
            "-z",
            "--no-ext-diff",
            "--ignore-submodules=all",
        )
    )
    unstaged = _git_changed(
        root,
        executable,
        "diff",
        "--quiet",
        "--no-ext-diff",
        "--ignore-submodules=all",
    )
    untracked = bool(
        _git_output(root, executable, "ls-files", "--others", "--exclude-standard", "-z")
    )
    staged = _git_changed(
        root,
        executable,
        "diff",
        "--cached",
        "--quiet",
        "--no-ext-diff",
        "--ignore-submodules=all",
    )
    if conflict or unstaged or untracked:
        return GuideScope("worktree")
    if staged:
        return GuideScope("staged")
    if head is not None:
        return GuideScope("commit", revision=head)
    return GuideScope("worktree")


def resolve_git_root(value: str | Path, *, cwd: Path | None = None) -> Path:
    """Resolve one explicit/nearest root without scanning sibling filesystem locations."""

    raw = _normalized_path(value)
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = (cwd or Path.cwd()) / candidate
    lexical = Path(os.path.abspath(candidate))
    if _is_private_path(lexical):
        raise ValueError("atlas/Private paths are excluded from guided analysis")
    try:
        if candidate.is_symlink() or not candidate.exists():
            raise ValueError(f"project directory does not exist or is unsafe: {raw}")
        if not candidate.is_dir():
            raise ValueError(f"project path is not a directory: {raw}")
        resolved = candidate.resolve(strict=True)
    except OSError as exc:
        raise ValueError(f"cannot resolve project directory: {raw}") from exc
    if resolved != lexical:
        raise ValueError(f"project directory crosses a symbolic-link or junction boundary: {raw}")
    for current in (resolved, *resolved.parents):
        if _is_private_path(current):
            raise ValueError("atlas/Private paths are excluded from guided analysis")
        marker = current / ".git"
        try:
            exists = marker.exists()
        except OSError as exc:
            raise ValueError("cannot inspect Git repository boundary") from exc
        if not exists:
            continue
        if marker.is_symlink() or (marker.is_dir() and marker.resolve() != marker.absolute()):
            raise ValueError("Git repository marker is an unsafe link")
        executable = shutil.which("git")
        if executable is None:
            raise ValueError("Git is required for guided analysis")
        top = _git_output(current, executable, "rev-parse", "--show-toplevel").strip()
        if not top or Path(top).resolve() != current:
            raise ValueError("nearest Git repository boundary is invalid")
        config = ProjectConfig.load(current)
        _reject_private_target(current, resolved, config)
        return current
    raise ValueError(f"no enclosing Git repository was found for: {raw}")


def _session_source(
    path: str | Path | None,
    terminal: TerminalIO,
    language: str,
    cache: ManagedRepositoryCache,
) -> tuple[Path, CacheEntry | None]:
    if path is not None:
        return _resolve_source(path, terminal, language, cache)
    try:
        return resolve_git_root(Path.cwd()), None
    except ValueError:
        supplied = terminal.read(_message(language, "path_prompt"))
        if supplied is None or supplied.strip().casefold() == "q":
            raise ValueError("no Git repository was selected") from None
        return _resolve_source(supplied, terminal, language, cache)


def _resolve_source(
    source: str | Path,
    terminal: TerminalIO,
    language: str,
    cache: ManagedRepositoryCache,
) -> tuple[Path, CacheEntry | None]:
    if not is_github_url(source):
        return resolve_git_root(source), None
    url = normalize_github_url(str(source))
    limits = cache.limits
    _render_section(terminal, language, "source")
    terminal.write(_message(language, "remote_source", value=url))
    _render_section(terminal, language, "safety")
    _write_wrapped(
        terminal,
        _message(
            language,
            "remote_trust",
            history=limits.history_depth,
            files=limits.max_checkout_files,
            bytes=limits.max_checkout_bytes,
            seconds=limits.timeout_seconds,
        )
    )
    choice = _read_menu(terminal, language, "remote_enter", "exit")
    if choice is None or choice.strip().casefold() == "q":
        raise ValueError("public repository acquisition was not approved")
    if choice.strip():
        raise ValueError("public repository acquisition requires Enter approval")
    terminal.write(_message(language, "acquiring"))
    entry = cache.acquire(url)
    terminal.write(
        _message(
            language,
            "cache",
            state=entry.cache_state,
            id=entry.cache_id,
            revision=entry.revision,
            commits=entry.history_commit_count,
            depth=entry.history_depth,
        )
    )
    return resolve_git_root(entry.repository_root), entry


def _collect_snapshot(
    root: Path,
    diagnostic: RepositoryDiagnostic,
    config: ProjectConfig,
    scope: GuideScope,
    terminal: TerminalIO,
    language: str,
    source: CacheEntry | None = None,
) -> GuideSnapshot:
    terminal.write(_message(language, "building"))
    private_paths = _private_paths(root, config)
    if scope.scope == "commit":
        change_set = collect_change_set(
            root,
            scope="commit",
            revision=scope.revision,
            excluded_paths=private_paths,
        )
    elif scope.scope == "range":
        change_set = collect_change_set(
            root,
            scope="range",
            base=scope.base,
            head=scope.head,
            excluded_paths=private_paths,
        )
    else:
        change_set = collect_change_set(root, scope=scope.scope, excluded_paths=private_paths)
    terminal.write(_message(language, "ranking"))
    graph, report = collect_change_report_context(root, change_set, config)
    graph_document = (
        json.dumps(graph.to_dict(), ensure_ascii=False, sort_keys=True) + "\n"
    ).encode("utf-8")
    report_document = render_change_report(report, "json").encode("utf-8")
    return GuideSnapshot(
        root,
        diagnostic,
        change_set,
        graph,
        report,
        graph_document,
        report_document,
        source,
    )


def _render_confirmation(
    terminal: TerminalIO,
    language: str,
    root: Path,
    scope: GuideScope,
    diagnostic: RepositoryDiagnostic | None = None,
) -> None:
    _render_section(terminal, language, "source")
    terminal.write(_message(language, "root", value=str(root)))
    terminal.write(_message(language, "scope", value=scope.display()))
    _render_section(terminal, language, "safety")
    trust_key = "trust_network_path" if _is_unc_path(root) else "trust"
    _write_wrapped(terminal, _message(language, trust_key))
    if diagnostic is not None:
        _write_wrapped(
            terminal,
            _message(
                language,
                "readiness",
                unsupported=", ".join(diagnostic.unsupported_languages) or "none",
                oversized=diagnostic.oversized_supported_file_count,
                truncated="yes" if diagnostic.discovery_truncated else "no",
                ambiguity=(
                    ", ".join(diagnostic.ambiguity_reasons)
                    if diagnostic.ambiguity_reasons
                    else "none"
                ),
            )
        )
        if diagnostic.ambiguity_reasons:
            _write_wrapped(terminal, _message(language, "ambiguity_scope"))
    terminal.write(_message(language, "cancel"))


def _render_summary(snapshot: GuideSnapshot, terminal: TerminalIO, language: str) -> None:
    report = snapshot.report
    payload = report.to_dict()
    change_set = report.analysis.change_set
    _render_section(terminal, language, "source")
    if snapshot.source is not None:
        source = snapshot.source
        terminal.write(_message(language, "remote_source", value=source.url))
        terminal.write(
            _message(
                language,
                "cache",
                state=source.cache_state,
                id=source.cache_id,
                revision=source.revision,
                commits=source.history_commit_count,
                depth=source.history_depth,
            )
        )
    terminal.write(_message(language, "project", value=str(snapshot.root)))
    terminal.write(_message(language, "scope", value=change_set.scope))
    terminal.write(
        _message(
            language,
            "revision",
            base=change_set.base_revision or "n/a",
            head=change_set.head_revision or "worktree",
        )
    )
    _render_section(terminal, language, "analysis")
    terminal.write(
        _message(
            language,
            "state",
            state=report.analysis.state,
            meaning=STATE_MEANINGS[language].get(report.analysis.state, report.analysis.state),
            freshness=report.freshness,
        )
    )
    terminal.write(_message(language, "threshold", value=report.minimum_confidence))
    terminal.write(_message(language, "changed", value=len(change_set.files)))
    action_revision = change_set.head_revision or change_set.base_revision
    if report.revision_action is not None and action_revision is not None:
        _write_wrapped(
            terminal,
            _message(language, "revision_action", revision=action_revision),
        )
    _render_section(terminal, language, "recommendations")
    terminal.write(
        _message(
            language,
            "requirements",
            selected=len(report.requirements),
            total=report.requirement_candidate_count,
            filtered=report.requirement_filtered_count,
            limited=report.requirement_limit_omitted_count,
            shown=len(report.omitted_requirements),
            omitted=(
                report.requirement_filtered_count
                + report.requirement_limit_omitted_count
            ),
        )
    )
    for requirement_item in report.requirements[:5]:
        terminal.write(
            f"  - requirement {requirement_item.requirement.id} | "
            f"{requirement_item.score}/100 | {requirement_item.confidence}"
        )
        _write_wrapped(
            terminal,
            f"    {LAYOUT_TEXT[language]['reason']}: confidence-meets-minimum-threshold",
            subsequent_indent="      ",
        )
        _write_wrapped(
            terminal,
            f"    {LAYOUT_TEXT[language]['evidence']}: "
            f"{', '.join(requirement_item.evidence) or 'none'}",
            subsequent_indent="      ",
        )
    terminal.write(
        _message(
            language,
            "tests",
            selected=len(report.tests),
            total=report.test_candidate_count,
            filtered=report.test_filtered_count,
            limited=report.test_limit_omitted_count,
            shown=len(report.omitted_tests),
            omitted=report.test_filtered_count + report.test_limit_omitted_count,
        )
    )
    for test_item in report.tests[:5]:
        primary = test_item.primary_reason
        terminal.write(
            f"  - test {test_item.test.id} | {test_item.score}/100 | "
            f"{test_item.confidence}"
        )
        _write_wrapped(
            terminal,
            f"    {LAYOUT_TEXT[language]['reason']}: "
            f"{primary.signal} ({primary.score}/100): {primary.summary}",
            subsequent_indent="      ",
        )
        _write_wrapped(
            terminal,
            f"    path: {_recorded_path(primary.path)}",
            subsequent_indent="      ",
        )
        _write_wrapped(
            terminal,
            f"    {LAYOUT_TEXT[language]['evidence']}: "
            f"{', '.join(primary.evidence) or 'none'}",
            subsequent_indent="      ",
        )
        terminal.write(f"    additional signals: {len(test_item.reason_details) - 1}")
    terminal.write(
        _message(
            language,
            "omissions",
            requirements=len(report.omitted_requirements),
            tests=len(report.omitted_tests),
        )
    )
    terminal.write(
        _message(
            language,
            "strategy",
            strategy=report.test_strategy,
            meaning=STRATEGY_MEANINGS[language].get(report.test_strategy, report.test_strategy),
        )
    )
    terminal.write(_message(language, "tests_executed"))
    _write_wrapped(
        terminal,
        _message(language, "advisory", value=payload["advisory"]),
        subsequent_indent="  ",
    )
    _render_section(terminal, language, "atlas")
    layer_counts = _layer_counts(snapshot.graph)
    missing = [
        name
        for name in ("requirements", "decisions", "issues", "evidence")
        if not layer_counts[name]
    ]
    disconnected = sum(
        snapshot.graph.degree(node_id) == 0 for node_id in snapshot.graph.nodes
    )
    terminal.write(
        _message(
            language,
            "atlas_ready",
            nodes=len(snapshot.graph.nodes),
            relations=snapshot.graph.edge_count,
            orphans=disconnected,
        )
    )
    terminal.write(
        _message(
            language,
            "layers",
            **layer_counts,
            missing=", ".join(missing) or "none",
        )
    )


def _layer_counts(graph: AtlasGraph) -> dict[str, int]:
    kinds = {
        "requirements": {"requirement"},
        "decisions": {"decision"},
        "issues": {"issue"},
        "code": {"file", "symbol"},
        "tests": {"test"},
        "evidence": {"evidence", "commit"},
    }
    return {
        layer: sum(node.kind in accepted for node in graph.nodes.values())
        for layer, accepted in kinds.items()
    }


def _post_result(
    snapshot: GuideSnapshot,
    terminal: TerminalIO,
    language: str,
) -> GuideScope | str | None:
    while True:
        _render_section(terminal, language, "actions")
        choice = _read_menu(
            terminal,
            language,
            "action_reasons",
            "action_omissions",
            "action_details",
            "action_viewer",
            "action_scope",
            "action_commands",
            "action_language",
            "action_exit",
        )
        folded = "" if choice is None else choice.strip().casefold()
        if choice is None or folded in {"", "q"}:
            terminal.write(_message(language, "bye"))
            return None
        if folded == "1":
            terminal.write(_message(language, "reasons_title"))
            _render_reasons(snapshot.report, terminal, language)
        elif folded == "2":
            terminal.write(_message(language, "omissions_title"))
            _render_omissions(snapshot.report, terminal, language)
        elif folded == "3":
            for line in render_change_report(snapshot.report, "json").splitlines():
                terminal.write(line)
            terminal.write(_message(language, "tests_executed"))
        elif folded == "4":
            try:
                serve_graph(
                    None,
                    host="127.0.0.1",
                    port=0,
                    open_browser=True,
                    graph_document=snapshot.graph_document,
                    change_report_document=snapshot.report_document,
                )
            except (OSError, ValueError) as exc:
                terminal.write(_message(language, "viewer_error", value=str(exc)))
        elif folded == "5":
            return _select_scope(snapshot.root, terminal, language)
        elif folded == "6":
            _render_commands(snapshot, terminal, language)
        elif folded == "l":
            return "tr" if language == "en" else "en"


def _render_reasons(report: ChangeReport, terminal: TerminalIO, language: str) -> None:
    if not report.requirements and not report.tests:
        terminal.write(_message(language, "none"))
        return
    for requirement_item in report.requirements:
        terminal.write(
            f"requirement {requirement_item.requirement.id}: score={requirement_item.score}; "
            f"confidence={requirement_item.confidence}; "
            f"evidence={','.join(requirement_item.evidence) or 'none'}"
        )
    for test_item in report.tests:
        primary = test_item.primary_reason
        terminal.write(
            f"test {test_item.test.id}: score={test_item.score}; "
            f"confidence={test_item.confidence}; "
            f"primary={primary.signal}; primary_score={primary.score}; "
            f"summary={primary.summary}; path={_recorded_path(primary.path)}; "
            f"evidence={','.join(primary.evidence) or 'none'}; "
            f"additional_signals={len(test_item.reason_details) - 1}"
        )


def _render_omissions(report: ChangeReport, terminal: TerminalIO, language: str) -> None:
    omitted = (*report.omitted_requirements, *report.omitted_tests)
    if not omitted:
        terminal.write(_message(language, "none"))
    for item in omitted:
        primary = item.primary_reason
        terminal.write(
            f"{item.candidate_type} {item.node.id}: selection_reason={item.selection_reason}; "
            f"score={item.score}; confidence={item.confidence}; "
            f"ranking_reason={primary.signal}; ranking_score={primary.score}; "
            f"path={_recorded_path(primary.path)}; "
            f"evidence={','.join(primary.evidence) or 'none'}"
        )
    terminal.write(
        _message(
            language,
            "omissions",
            requirements=len(report.omitted_requirements),
            tests=len(report.omitted_tests),
        )
    )


def _recorded_path(path: object) -> str:
    nodes = tuple(getattr(path, "nodes", ()))
    relations = tuple(getattr(path, "relations", ()))
    if not nodes or len(relations) != len(nodes) - 1:
        return "none"
    parts = [str(nodes[0])]
    for relation, node in zip(relations, nodes[1:], strict=True):
        parts.extend((f"-[{relation}]->", str(node)))
    return " ".join(parts)


def _render_commands(snapshot: GuideSnapshot, terminal: TerminalIO, language: str) -> None:
    scope = snapshot.change_set
    root = _shell_display(snapshot.root)
    if scope.scope == "commit":
        selector = f"--commit {scope.head_revision}"
    elif scope.scope == "range":
        selector = f"--base {scope.base_revision} --head {scope.head_revision}"
    elif scope.scope == "staged":
        selector = "--staged"
    else:
        selector = "--worktree"
    terminal.write(_message(language, "commands_title"))
    terminal.write(f"intentatlas changes {root} {selector} --report --format text")
    terminal.write(f"intentatlas changes {root} {selector} --report --format json")
    terminal.write(f"intentatlas init {root}")
    terminal.write(f"intentatlas scan {root}")


def _select_scope(
    root: Path,
    terminal: TerminalIO,
    language: str,
) -> GuideScope | None:
    _render_section(terminal, language, "scope_options")
    choice = _read_menu(
        terminal,
        language,
        "scope_worktree",
        "scope_staged",
        "scope_head",
        "scope_commit",
        "scope_range",
        "exit",
    )
    if choice is None or choice.strip().casefold() == "q":
        return None
    folded = choice.strip().casefold()
    if folded == "w":
        return GuideScope("worktree")
    if folded == "s":
        return GuideScope("staged")
    executable = shutil.which("git")
    if executable is None:
        raise ValueError("Git is required for guided analysis")
    if folded == "h":
        head = _try_resolve_revision(root, executable, "HEAD")
        if head is None:
            raise ValueError("HEAD does not exist in this repository")
        return GuideScope("commit", revision=head)
    if folded == "c":
        revision = terminal.read(_message(language, "commit_prompt"))
        if revision is None:
            return None
        return GuideScope("commit", revision=_resolve_revision(root, executable, revision))
    if folded == "r":
        base = terminal.read(_message(language, "base_prompt"))
        head = terminal.read(_message(language, "head_prompt"))
        if base is None or head is None:
            return None
        return GuideScope(
            "range",
            base=_resolve_revision(root, executable, base),
            head=_resolve_revision(root, executable, head),
        )
    return select_default_scope(root)


def _language(value: str | None) -> str:
    if value in MESSAGES:
        return value
    if value is not None:
        raise ValueError(f"unsupported guide language: {value}")
    current = locale.getlocale()[0] or ""
    return "tr" if current.casefold().startswith("tr") else "en"


def _message(language: str, key: str, **values: Any) -> str:
    return MESSAGES[language][key].format(**values)


def _terminal_text(value: object) -> str:
    text = str(value)[:MAX_TERMINAL_VALUE]
    rendered: list[str] = []
    for character in text:
        code = ord(character)
        if character in _BIDI_CONTROLS:
            rendered.append(f"\\u{code:04x}")
        elif character == "\n":
            rendered.append("\\n")
        elif character == "\r":
            rendered.append("\\r")
        elif character == "\t":
            rendered.append(" ")
        elif code < 32 or code == 127:
            rendered.append(f"\\x{code:02x}")
        else:
            rendered.append(character)
    return "".join(rendered)


def _normalized_path(value: str | Path) -> str:
    rendered = str(value).strip()
    if len(rendered) > MAX_TERMINAL_VALUE or "\x00" in rendered:
        raise ValueError("project path is invalid")
    if len(rendered) >= 2 and rendered[0] == rendered[-1] and rendered[0] in {'"', "'"}:
        rendered = rendered[1:-1]
    if not rendered:
        raise ValueError("project path is empty")
    return rendered


def _is_unc_path(path: Path) -> bool:
    return str(path).startswith("\\\\")


def _is_private_path(path: Path) -> bool:
    folded = tuple(part.casefold() for part in path.parts)
    return any(
        folded[index : index + 2] == ("atlas", "private")
        for index in range(len(folded) - 1)
    )


def _reject_private_target(root: Path, target: Path, config: ProjectConfig) -> None:
    canonical_root = root.resolve()
    private_roots = {
        canonical_root / "atlas" / "Private",
        config.vault_path(canonical_root) / "Private",
    }
    if any(target == private or private in target.parents for private in private_roots):
        raise ValueError("atlas/Private paths are excluded from guided analysis")


def _private_paths(root: Path, config: ProjectConfig) -> tuple[str, ...]:
    canonical = root.resolve()
    return tuple(
        path.relative_to(canonical).as_posix()
        for path in sorted(
            {canonical / "atlas" / "Private", config.vault_path(canonical) / "Private"},
            key=lambda item: item.as_posix().casefold(),
        )
    )


def _git_command(root: Path, executable: str, *arguments: str) -> list[str]:
    return [
        executable,
        "-c",
        f"safe.directory={root.as_posix()}",
        "-c",
        "core.quotePath=false",
        "-C",
        str(root),
        *arguments,
    ]


def _git_run(root: Path, executable: str, *arguments: str) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(  # noqa: S603  # nosec B603
            _git_command(root, executable, *arguments),
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
            shell=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise ValueError("cannot inspect Git repository") from exc
    if len(result.stdout.encode("utf-8")) > MAX_GIT_OUTPUT_BYTES:
        raise ValueError("Git metadata exceeds the guided analysis limit")
    return result


def _git_output(root: Path, executable: str, *arguments: str) -> str:
    result = _git_run(root, executable, *arguments)
    if result.returncode != 0:
        raise ValueError("cannot inspect Git repository")
    return result.stdout


def _git_changed(root: Path, executable: str, *arguments: str) -> bool:
    result = _git_run(root, executable, *arguments)
    if result.returncode not in {0, 1}:
        raise ValueError("cannot inspect Git repository")
    return result.returncode == 1


def _resolve_revision(root: Path, executable: str, revision: str) -> str:
    normalized = revision.strip()
    if not _REVISION.fullmatch(normalized) or ".." in normalized:
        raise ValueError(f"unsafe Git revision: {revision!r}")
    value = _git_output(
        root,
        executable,
        "rev-parse",
        "--verify",
        "--end-of-options",
        f"{normalized}^{{commit}}",
    ).strip()
    if not re.fullmatch(r"[0-9a-f]{40,64}", value):
        raise ValueError(f"Git revision did not resolve to a commit: {revision}")
    return value


def _try_resolve_revision(root: Path, executable: str, revision: str) -> str | None:
    try:
        return _resolve_revision(root, executable, revision)
    except ValueError:
        return None


def _shell_display(path: Path) -> str:
    rendered = _terminal_text(path)
    return f'"{rendered}"' if any(character.isspace() for character in rendered) else rendered
