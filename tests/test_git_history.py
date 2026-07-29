from intentatlas.git_history import parse_git_log


def test_parse_git_log_collects_paths_and_redacts_subjects() -> None:
    output = (
        "\x1eabc123\x1fabc123\x1f2026-07-30\x1ffeat: token=super-secret\n"
        "src/app.py\nREADME.md\n\n"
        "\x1edef456\x1fdef456\x1f2026-07-29\x1finitial commit\nREADME.md\n"
    )
    commits = parse_git_log(output)
    assert len(commits) == 2
    assert commits[0].subject == "feat: token=[REDACTED]"
    assert commits[0].paths == ("README.md", "src/app.py")
    assert commits[1].short == "def456"


def test_parse_git_log_ignores_malformed_blocks() -> None:
    assert parse_git_log("\x1enot-a-header\nfile.py") == []
