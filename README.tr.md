<p align="center">
  <img src="docs/assets/logo.svg" width="132" alt="IntentAtlas logosu">
</p>

<h1 align="center">IntentAtlas</h1>

<p align="center"><strong>Yazılım projeleri için yaşayan niyet haritası.</strong></p>

<p align="center"><a href="README.md">English</a> · <a href="atlas/Brain/Product%20Roadmap.md">Ürün yol haritası</a></p>

IntentAtlas bir sistemin neden var olduğunu, onu gerçekleştiren kod ve kanıtlarla bağlar:

```text
Gereksinim → Karar → İş → Kod → Test → Kanıt → Commit
```

Standart kod grafikleri “ne neyi çağırıyor?” sorusuna cevap verir. IntentAtlas ise bir
değişikliğin **neden var olduğunu, neyin doğruladığını ve sırada neyi etkileyebileceğini**
gösterir. Yerel çalışır, API anahtarı istemez ve proje hafızasını Obsidian uyumlu,
Git ile izlenebilir Markdown dosyalarında tutar.

Güncel fazlar ve tamamlanma durumları
[Ürün Yol Haritası](atlas/Brain/Product%20Roadmap.md) belgesinde izlenir. Repo kökündeki
`ROADMAP.md`, ilk 0.1–0.3 teknik planının açıkça arşivlenmiş tarihsel kaydıdır.

## Hızlı başlangıç

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\intentatlas.exe init
.\.venv\Scripts\intentatlas.exe scan
.\.venv\Scripts\intentatlas.exe open
```

Ardından `atlas/` klasörünü Obsidian’da vault olarak açın. Graph View; gereksinimleri,
kararları, kodu, testleri, kanıtları ve commit’leri renkli, bağlantılı düğümler olarak
gösterecektir.

## Temel yaklaşım

- Klasörler amaca göre, bağlantılar anlama göre düzenlenir.
- İnsan/ajan notları ile tarayıcının ürettiği kod notlarının sahipliği ayrıdır.
- `Issues/` dahil kalıcı niyet notları kullanıcıya aittir ve taramalarda korunur.
- `Private/` Git’e girmez ve IntentAtlas tarafından okunmaz.
- Kalıcı ama bağlantısız notlar sağlık sorunu olarak raporlanır.
- Obsidian zorunlu değildir; aynı grafik yerel web görünümünde açılabilir.

Anlamı belirtilmiş bağlantılar `relation:: [[hedef]]` biçimini kullanır. Normal wikilinkler
güvenli ve genel `references` ilişkileri olarak çalışmaya devam eder.

Vault-first hafıza yaklaşımı
[breferrari/obsidian-mind](https://github.com/breferrari/obsidian-mind) projesinden
esinlenmiştir. IntentAtlas buna kod, test, Git ve teslimat niyeti katmanını ekler.
