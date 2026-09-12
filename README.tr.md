<p align="center">
  <img src="docs/assets/logo.svg" width="132" alt="IntentAtlas logosu">
</p>

<h1 align="center">IntentAtlas</h1>

<p align="center"><strong>Yazılım projeleri için yaşayan niyet haritası.</strong></p>

<p align="center">
  <img alt="Durum: beta" src="https://img.shields.io/badge/durum-beta-orange">
  <img alt="Sürüm 0.3.0b1" src="https://img.shields.io/badge/s%C3%BCr%C3%BCm-0.3.0b1-blue">
  <img alt="Python 3.11+" src="https://img.shields.io/badge/python-3.11%2B-blue">
</p>

<p align="center"><a href="README.md">English</a> · <a href="https://github.com/AhmetBugrahanAltunok/IntentAtlas/blob/main/atlas/Brain/Product%20Roadmap.md">Ürün yol haritası</a></p>

IntentAtlas bir değişikliğin **neden var olduğunu, hangi gereksinimi etkileyebileceğini ve hangi
testin buna dair kanıt taşıdığını** gösterir. Depoyu yerel olarak analiz eder; kaynak kodu yüklemez
ve API anahtarı istemez.

```text
Gereksinim → Karar → İş → Kod → Test → Kanıt → Commit
```

<p align="center">
  <img src="docs/assets/intentatlas-demo.gif" width="960" alt="Niyet grafiğini, değişiklik raporunu ve test kanıt yollarını gösteren IntentAtlas demosu">
</p>

## İlk demoyu iki dakikada görün

Gerekenler: Python 3.11, 3.12 veya 3.13. Git, gerçek depo analizi için gereklidir; yerleşik demo
için gerekli değildir. Kurulum adımı, derleme bağımlılıklarını almak için ayarlı Python paket
indeksinize bağlanabilir.

> **Windows: bu depoyu klonlamadan önce uzun yolları açın.** IntentAtlas kendi `atlas/` kasasını
> taşır ve üretilmiş sembol notlarının 51 tanesinin yolu 120 karakterden uzundur. Kısa olmayan bir
> klasöre klonlamak 260 karakterlik `MAX_PATH` sınırını aşar; checkout `Filename too long` ile
> durur ve çalışma ağacı boş kalır. Bir kez
> `git config --global core.longpaths true` çalıştırın ya da `C:\src\intentatlas` gibi kısa bir
> yola klonlayın. Bu yalnızca IntentAtlas'ı klonlamayı etkiler, analiz ettiği depoları değil.

İki dakikalık hedef, ilk metin demosu göründüğünde biter. Çıktıyı okumak ve aşağıdaki gerçek repo
akışlarını denemek daha uzun sürer.

IntentAtlas şu anda henüz yayımlanmamış bir beta sürümüdür. Ortam klasörünü bir kez seçin; `.venv`
başka bir kuruluma aitse ilk satırı `$IntentAtlasVenv = ".venv-intentatlas"` olarak değiştirin:

```powershell
$IntentAtlasVenv = ".venv"
python -m venv $IntentAtlasVenv
& "$IntentAtlasVenv\Scripts\python.exe" -m pip install .
& "$IntentAtlasVenv\Scripts\intentatlas.exe" demo --report text
```

Python var olan ortam klasörünü yeniden kullanır. Aşağıdaki kısa `intentatlas` komutları, yukarıda
seçilen klasör etkinleştirildikten sonra çalışır:

```powershell
& "$IntentAtlasVenv\Scripts\Activate.ps1"
```

macOS veya Linux'ta `IntentAtlasVenv=.venv` (veya başka bir ad) ayarlayın;
`$IntentAtlasVenv/bin/python` ile `$IntentAtlasVenv/bin/intentatlas` yollarını kullanın ve
`source "$IntentAtlasVenv/bin/activate"` çalıştırın. Etkinleştirme kullanılamıyorsa seçtiğiniz
klasördeki tam executable yolunu kullanın.

Demo mevcut klasörü taramaz ve ağa erişmez. Bir öneri ile kanıtını içeren küçük, yerleşik bir
senaryo yazdırır. Kısaltılmış çıktı:

```text
Exact changed symbol: rotate_session (src/auth.py)
Recommended tests:
- tests/test_auth_rotation.py [medium 80]
  Why: The test directly references an exactly modified symbol.
  Path: commit → rotate_session → tests/test_auth_rotation.py
```

`medium 80`, 80 puanın orta bantta olduğunu gösterir: low 0–64, medium 65–84, high 85–100.
Güven puanı mevcut yapısal kanıtı sıralar; doğruluk olasılığı değildir.

Rehberli akış gerçek bir etkileşimli terminal ister; pipe, yönlendirme ve etkileşimsiz kabukları
reddeder. Etkileşimsiz kabukta `intentatlas diagnose PATH` çalıştırın, ardından yazdırdığı kesin
**Next safe command** satırını kopyalayın. Yerel bir Git deposunu proje dosyalarına yazmadan
etkileşimli incelemek için:

```powershell
intentatlas guide C:\projenizin\yolu
```

Ya da açıkça onayladığınız public GitHub deposunu elle klonlamadan inceleyin:

```powershell
intentatlas guide https://github.com/OWNER/REPOSITORY
```

IntentAtlas Enter ile onay istemeden önce kesin kapsamı, güvenlik sınırlarını ve olası ağ/cache
etkisini gösterir. Sonuç; olası gereksinim etkisini, aday testleri, güven düzeyini ve kaydedilmiş
kanıt yolunu açıklar. Rehberden çıkmak için Quit seçeneğini kullanın; yerel görüntüleyiciyi
açarsanız terminal sürecini Ctrl+C ile durdurun. Bkz. [rehberli CLI turu](docs/guided-cli.md).

### Gerçek bir depodan örnek

Deponun incelenmiş benchmark'ında kullanılan sabit Click commit'i üzerinde salt-okunur rapor tek
bir test seçer ve kesin yapısal yolu açıklar. Kısaltılmış çıktı:

```text
$ intentatlas changes /click/deposunun/yolu --commit HEAD --report
Changed: __exit__ (src/click/core.py)
Run 1 test:

  tests/test_context.py   [medium confidence]
    The test references the owning symbol of an exactly modified nested symbol.
    __exit__ -> Context -> tests/test_context.py

No requirement is linked to this change.

Impact and test recommendations are bounded structural evidence, not proof that an
omitted requirement is unaffected or that a suggested test is sufficient.
Full detail: --explain    Machine-readable: --format json
```

`--explain` bu cevabın arkasındaki revizyonları, güven bantlarını, aday ve atlama sayılarını,
grafik kimliklerini ve kanıt etiketlerini ekler. `--format json` araçlar için değişmeyen şema-1
belgesidir; varsayılan bu özete dönerken ne JSON ne de `--explain` metni değişti.

Bu çıktı tavsiye niteliğindedir. Checkout yeniden üretilebilirlik için sabitlenmiş ve lisansı
incelenmiştir; proje kodu ve testler çalıştırılmaz. Bkz.
[gerçek dünya doğrulama protokolü](docs/real-world-validation.md).

Güven, mevcut yapısal kanıtın sıralamasıdır; doğruluk olasılığı değildir. `high` (85-100) en güçlü
yapısal kanıtı gösterir; örneğin testin kendisinin değişiklik kümesinde olması. `medium` (65-84)
doğrudan bağlantıları kapsar; `80/medium` bir statik sembol referansıdır. `low` (65 altı) yüksek
dağılımlı bir keşif düzeyidir; otomatik seçim için medium veya üzeri kullanın. `--minimum-confidence
low` daha zayıf adayları gösterir, onları güçlendirmez.

## IntentAtlas nedir, ne değildir?

| IntentAtlas nedir? | IntentAtlas ne değildir? |
| --- | --- |
| Niyet, kod, test ve Git geçmişini bağlayan yerel bir kanıt grafiğidir | Kod üreten yapay zekâ veya otonom kodlama ajanı değildir |
| Kalıcı vault'u benimsemeden önce kullanılabilen salt-okunur değişiklik önizlemesidir | Deponuzu yükleyen barındırılmış bir servis değildir |
| Güven düzeyi açıklanmış test öneri aracıdır | Test çalıştırıcısı veya önerilen testlerin yeterli olduğuna dair kanıt değildir |
| Git'te saklanabilen, isteğe bağlı Markdown/Obsidian proje hafızasıdır | Git'in, issue tracker'ın, CI'ın veya Obsidian'ın yerine geçmez |

Gösterilmeyen bir gereksinimin etkilenmediği, gösterilmeyen bir testin de gereksiz olduğu kanıtlanmış
olmaz. IntentAtlas mevcut yapısal kanıtı görünür kılar ve kanıt yeterli değilse iddiada bulunmaz.

Güncel fazlar ve tamamlanma durumları
[Ürün Yol Haritası](https://github.com/AhmetBugrahanAltunok/IntentAtlas/blob/main/atlas/Brain/Product%20Roadmap.md) belgesinde izlenir. Repo kökündeki
`ROADMAP.md`, ilk 0.1–0.3 teknik planının açıkça arşivlenmiş tarihsel kaydıdır.

## Bugün ne çalışıyor

- Python, TypeScript/JavaScript ve Go depolarını determinist bir ilişki grafiğine tarar.
- Dosyaları, sembolleri, import'ları, testleri, Markdown belgelerini ve Git commit'lerini bağlar.
- Amaca göre klasörlenmiş, wikilink'li bir Obsidian vault üretir.
- Aynı grafiği yerel, bağımlılıksız bir web görüntüleyicide gezdirir.
- Komut satırından yukarı ve aşağı yönlü etkiyi izler.
- Mevcut Cobertura kapsam ve JUnit test kanıtlarını, proje kodunu çalıştırmadan içe aktarır.
- CI için determinist, sürümlenmiş bir grafik diff'i üretir.
- Açık yerel JSON snapshot'larından sınırlı issue ve pull-request verisini içe aktarır.
- Sıfır bağlamlı diff aralıkları doğrulanmış Python AST span'leriyle ya da muhafazakâr biçimde
  dengelenmiş JavaScript/TypeScript ve Go bildirim span'leriyle kesiştiğinde ve çalışma
  kopyasındaki dosya o commit'in blob'uyla eşleştiğinde, commit'leri tam değişen sembollere
  bağlar; belirsiz durumlarda dosya düzeyi geçmişi güvenli geri dönüş olarak kalır.
- Bir commit, dosya ya da sembol için test dosyalarını sabit güven düzeyleri, tam kanıt yolları ve
  determinist metin veya JSON çıktısıyla sıralar.
- Önerileri, insan tarafından incelenmiş kapsamlı yerel etiketlere karşı ölçer; vaka başına ve
  mikro-toplam kesinlik/duyarlılık verir.
- Etiketli yerel grafiklerden oluşan sınırlı bir korpusta düşük, orta ve yüksek güveni karşılaştırır.
- Değişmemiş öneri sorgusunu, temiz ve sabitlenmiş, lisansı incelenmiş public checkout'lara karşı
  üçüncü taraf kodu paketlemeden veya çalıştırmadan yeniden koşar.
- Kurulu wheel akışını Windows, macOS ve Linux CI'da doğrular; tekrarlanan wheel veya kaynak
  build'leri bayt bayt farklıysa sürüm adayını reddeder.
- Grafik ve güvenilmeyen JSON sınırlarını tekrar oynatılabilir sabit tohumlu property/mutation
  testleriyle zorlar; sınırlı büyük grafik penceresini CI'da gerçek bir Chrome ailesi tarayıcıda
  render eder.
- Doğrulanmış artifact hash'lerini tam bir Git revizyonuna ve sabit build epoch'una bağlayan
  determinist yayın provenance'ı üretir; paket yayımı ayrıca onay gerektirir.
- Go testlerini gerçekten referans verdikleri, tek bir dosyaya ait dışa açık bildirimlere bağlar;
  belirsiz ve yalnızca dosya adına dayanan eşleşmeleri muhafazakâr tutar.
- Doğrudan test edilen bir sarmalayıcı değişen sembolü çağırdığında tek bir tam Go çağrı adımını izler.
- Etki ve öneri sorguları için tembel, determinist bir komşuluk indeksi kullanır; katkıcılar için
  sınırlı bir sentetik ölçek benchmark'ı sunar.
- Gereksinimleri, kararları, kanıtları, incelemeleri ve proje hafızasını Git'te tutar.

## Beta durumu

Mevcut kaynak kendisini `0.3.0b1` olarak tanımlar. Henüz tag'lenmemiş, paket indeksinde
yayımlanmamış ve uyumluluk sözü vermemiştir. Yukarıdaki hızlı yol mevcut checkout'un davranışını
doğrular; release incelemesi ayrıca kesin revision'ı, tekrarlanabilir artifact'leri, provenance'ı,
hash'leri, kurulu wheel'i ve browser akışını doğrular. Bkz. [kurulum durumu](docs/installation.md)
ve [sürüm süreci](RELEASING.md).

## İlk komutunuzu seçin

| Durumunuz | Kullanın | Projeye yazılanlar | Ağ |
| --- | --- | --- | --- |
| Yalnız fikri görmek istiyorsunuz | `intentatlas demo --report text` | Yok | Yok |
| Etkileşimli terminaliniz var | `intentatlas guide PATH` | Yok | Yerel yol için yok |
| Etkileşimsizsiniz veya Git kapsamından emin değilsiniz | `intentatlas diagnose PATH`, ardından **Next safe command** (`intentatlas changes ...`) | Yok | Yok |
| Kalıcı proje haritası istiyorsunuz | `intentatlas init PATH`, ardından `intentatlas scan PATH` | `intentatlas.json`, `.gitignore`, `.intentatlas/` ve `atlas/` | Yok |

Yalnız açıkça onaylanan public GitHub URL'si ağ ve yönetilen işletim sistemi cache'ini kullanabilir.
Paket kurulumu da ayarlı Python paket indeksine bağlanabilir; yerel analiz çevrimdışıdır.

Sonra:

```powershell
intentatlas            # etkileşimli terminal: rehberli akış
```

Etkileşimsiz bir kabukta `intentatlas diagnose PATH` çalıştırın ve yazdırdığı **Next safe
command** satırını kopyalayın. Varsayılan rapor neyin değiştiği ve hangi testlerin çalıştırılacağıyla
açılır; revizyonlar, güven bantları ve grafik kimlikleri için `--explain`, değişmeyen şema için
`--format json` ekleyin.

## Dokümantasyon

Akışlar ve yetenekler Türkçe; geri kalan ayrıntılı belgeler İngilizcedir:

| | |
| --- | --- |
| [Akışlar](docs/workflows.tr.md) | Rehberli akış, public GitHub analizi, iz bırakmayan önizleme ve kalıcı vault'a geçiş |
| [Yetenekler, ayrıntılı](docs/capabilities.tr.md) | Her adaptör ve içe aktarıcının kapsadığı ve çekimser kaldığı yerler |
| [Komut referansı](docs/commands.md) | Bakım ve benchmark komutları dahil her komut (İngilizce) |
| [Kurulum](docs/installation.md) | Desteklenen sürümler ve güncel kurulum durumu |
| [Mimari](docs/architecture.md) | Güven sınırları ve katmanların nasıl birleştiği |
| [Doküman dizini](docs/index.md) | Geri kalan her şey |

Projenin kendi niyet haritası [`atlas/`](atlas/) içinde: her teslimat fazı için gereksinimler,
kararlar, kanıtlar ve incelemeler — aracın kendisiyle yazıldı. Üretilmiş alanlar
`intentatlas scan` ile yeniden üretilir ve takip edilmez.

## İlham

Obsidian'ın yerel Markdown grafiği, mimari karar kayıtları ve güvenlik-kritik mühendislikten gelen
izlenebilirlik pratiği — gündelik depolara, çevrimdışı ve barındırılan bir servis olmadan uygulandı.
