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

Kurulumdan hemen sonra eksiksiz niyet-kanıt zincirini deneyin:

```powershell
intentatlas demo
```

Yerleşik örnek özgün, çevrimdışı ve geçicidir; geçerli klasörü taramaz. Kendi deponuz için:

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

Bir commit, dosya veya sembol için test dosyalarını çalıştırmadan sıralamak için:

```text
intentatlas recommend-tests commit:TAM_SHA --minimum-confidence medium
intentatlas recommend-tests src/auth.py --minimum-confidence low --format json
```

Puanlar sabit ve incelenebilir yapısal kanıtlara dayanır. Kesin sembol değişikliği ile statik test
bağlantısı, yalnız dosya veya adlandırma kuralı kanıtından daha yüksek sıralanır. Sonuçlar
tavsiyedir; listede olmayan bir test, davranışın etkilenmediğini kanıtlamaz.

Öneri kalitesini eksiksiz olduğu açıkça belirtilen, insan incelemeli yerel etiketlerle ölçmek için:

```text
intentatlas evaluate-recommendations benchmarks/intentatlas-recommendations.json
intentatlas evaluate-recommendations benchmarks/intentatlas-recommendations.json --minimum-confidence high --format json
```

Değerlendirme testleri çalıştırmadan ve sıralama puanlarını değiştirmeden TP, FP, FN, precision ve
recall üretir. Birlikte gelen iki vakalık temel ölçüm yalnızca regresyon yardımcısıdır; başka
repolardaki doğruluğu kanıtlamaz. Şema ve metrik sözleşmesi
[değerlendirme belgesinde](docs/recommendation-evaluation.md) açıklanır.

Özgün Python, TypeScript ve Go grafik senaryolarında bütün güven eşiklerini karşılaştırmak için:

```text
intentatlas evaluate-corpus benchmarks/recommendation-corpus.json
intentatlas evaluate-corpus benchmarks/recommendation-corpus.json --format json
```

Corpus çıktısı proje başına ve mikro toplamları birlikte gösterir. Bu küçük özgün fixture’lar
agregasyon ile güven davranışını doğrular; kopyalanmış repo veya gerçek dünya doğruluk kanıtı
değildir. Ayrıntılar [corpus şemasında](docs/recommendation-corpus.md) bulunur.

Lisansı incelenmiş gerçek projelerde yeniden üretilebilir doğrulama için, onaylı altı açık kaynak
depoyu yalnızca ağ izninden sonra manifestteki commit’lere sabitleyin ve şunu çalıştırın:

```text
intentatlas evaluate-real-world benchmarks/real-world/manifest.json .intentatlas/real-world/checkouts
```

Komut taramadan önce origin, commit, temiz çalışma ağacı ve incelenmiş lisans özetini doğrular.
Repo klonlamaz, bağımlılık kurmaz, test veya proje kodu çalıştırmaz; üçüncü taraf kaynak, Git
geçmişi, logo ya da üretilmiş grafiği üründe saklamaz. Ayrıntılar
[gerçek proje doğrulama protokolünde](docs/real-world-validation.md) bulunur. On sekiz sabit vaka
yalnızca seçilen Python, JavaScript ve Go değişiklikleri için kanıttır; genel doğruluk iddiası
değildir.

Bir projeyi okumadan veya çalıştırmadan çevrimdışı ölçek kontrolü yapmak için:

```text
intentatlas benchmark-scale
intentatlas benchmark-scale --unrelated-edges 50000 --iterations 500 --format json
```

Benchmark kararlı grafik/sonuç/iş sayılarını ve ortama bağlı süreleri raporlar. Taşınabilir gecikme
garantisi değil, regresyon ve tanılama aracıdır. Ayrıntılar
[ölçek benchmark sözleşmesinde](docs/query-scale-benchmark.md) bulunur.

Yerel görüntüleyici, seçilen düğümden testlere, kanıtlara, coverage sonuçlarına, test sonuçlarına,
commit'lere ve pull request'lere giden sınırlı en kısa yapısal yolları da gösterir. Bu yollar grafik
bağlantısını açıklar; nedensellik, eksiksizlik, güncellik veya test zorunluluğu iddia etmez.
`intentatlas demo`, aynı üretim görüntüleyicisini dokuz düğümlü özgün bir örnek üzerinde açar ve
görüntüleyici kapandığında geçici grafiği temizler.

## Temel yaklaşım

- Klasörler amaca göre, bağlantılar anlama göre düzenlenir.
- İnsan/ajan notları ile tarayıcının ürettiği kod notlarının sahipliği ayrıdır.
- `Issues/` dahil kalıcı niyet notları kullanıcıya aittir ve taramalarda korunur.
- `Private/` Git’e girmez ve IntentAtlas tarafından okunmaz.
- Kalıcı ama bağlantısız notlar sağlık sorunu olarak raporlanır.
- Obsidian zorunlu değildir; aynı grafik yerel web görünümünde açılabilir.

Üretilmiş notların senkronizasyonu, dosyalara dokunmadan önce hedef görünümün tamamını hazırlar.
Bayt düzeyinde aynı notları yeniden yazmaz; değişen notları geçici dosya kilitleri için sınırlı
tekrarlarla atomik olarak değiştirir ve eski notları ancak bütün hedef notlar yerindeyken siler.
Kalıcı hata bu nedenle önceki üretilmiş görünümü baştan silmeden açıkça raporlanır.

Anlamı belirtilmiş bağlantılar `relation:: [[hedef]]` biçimini kullanır. Normal wikilinkler
güvenli ve genel `references` ilişkileri olarak çalışmaya devam eder.

## Durum

Python, TypeScript/JavaScript ve Go analizi aynı dil-bağımsız adaptör sözleşmesini kullanır. `.ts`,
`.tsx`, `.js` ve `.jsx` dosyalarında adlandırılmış semboller, yerel import/re-export bağlantıları
ve test ilişkileri çıkarılır. Go adaptörü `.go` dosyalarını, `go.mod` modül sınırlarını,
adlandırılmış türleri, fonksiyonları, metotları, modül-içi paket importlarını ve testleri kapsar.
Aynı klasördeki testler yalnızca tek bir üretim dosyasına ait, gerçekten başvurulan dışa açık
bildirimler için yapısal kanıt kazanır; belirsiz adlar bağlanmaz ve dosya adı eşleşmesi zayıf yedek
olarak kalır. Hiçbir adaptör dil çalışma zamanını veya proje kodunu çalıştırmaz.

İsteğe bağlı Cobertura coverage ve JUnit test raporları `intentatlas.json` içindeki proje-göreli
`coverage_reports` ve `test_reports` listeleriyle içe aktarılabilir. IntentAtlas testleri çalıştırmaz;
yalnızca dosya başına sınırlı özetleri grafiğe ekler. `intentatlas diff` komutu da mevcut grafiği bir
temel grafikle karşılaştırarak CI için deterministik ve zaman damgasız JSON üretir.

Issue ve pull request bağlamı da isteğe bağlı yerel JSON snapshot dosyalarından içe aktarılabilir.
`delivery_reports` kaynakları gereksinim ve kararları issue, pull request, değişen dosya ve bilinen
commitlerle bağlar. Gövdeler, yorumlar ve ham API yanıtları saklanmaz; ayrıntılar
[yerel teslimat şemasında](docs/delivery-schema.md) açıklanır.

Yakın Git geçmişinde değişen yeni taraf satırları, doğrulanmış AST aralıklarıyla kesiştiğinde ve
güncel dosya incelenen commit blobuyla eşleştiğinde Python sınıf, fonksiyon ve metot sembollerine
doğrudan `modifies` ilişkisi eklenir. Eski dosya sürümü, silme, modül-seviyesi değişiklik, span
desteği olmayan adaptör veya belirsizlik durumunda mevcut dosya-seviyesi `changes` ilişkisi güvenli
yedek olarak korunur.

`recommend-tests`, doğrulanmış grafik ilişkilerinden doğrudan test dosyalarını `high`, `medium`
veya `low` güvenle sıralar ve her sonucun neden yolunu gösterir. İlk sürüm yanlış pozitifleri
azaltmak için geçişli bağımlılık tahminleri yapmaz ve varsayılan olarak `medium` eşiğini kullanır.

`evaluate-recommendations`, aynı üretim sorgusunu değiştirmeden katı ve kapalı-dünya yerel
etiketleriyle karşılaştırır. Zaman damgasız şema-1 çıktısı eşik farklarını ve regresyonları görünür
kılar; tanımsız metrikleri açıkça `null`/`n/a` olarak korur.

`evaluate-corpus`, aynı sorguyu birden fazla kayıtlı grafiğe uygular ve `low`, `medium`, `high`
eşiklerini yan yana raporlar. Herhangi bir grafik veya etiket geçersizse corpus’un tamamı açıkça
başarısız olur; eski veya bozuk bir proje toplam metriği sessizce iyileştiremez.

Etki ve test önerisi sorguları aynı tembel ve deterministik adjacency indeksini kullanır. Tekrarlı
yerel sorgular yalnız eşleşen giriş/çıkış bucket’larını inceler; yeni kenar eklenirse bellek içi
indeks geçersizleştirilip güvenle yeniden kurulur.

Vault-first hafıza yaklaşımı
[breferrari/obsidian-mind](https://github.com/breferrari/obsidian-mind) projesinden
esinlenmiştir. IntentAtlas buna kod, test, Git ve teslimat niyeti katmanını ekler.
