# Akışlar

Rehberli akış, public depo analizi, paketli demo, iz bırakmayan uzman önizlemesi ve kalıcı
vault'a bilinçli geçiş. Kurulum ve ilk komut için [README](../README.tr.md).

İngilizcesi: [workflows.md](workflows.md).

Etkileşimli terminalde gerçek bir repo içinden tek komut çalıştırın:

```powershell
intentatlas
```

IntentAtlas analizden önce en yakın güvenli Git kökünü ve ihtiyatlı kapsamı gösterir. Kabul etmek
için bir kez Enter'a basın. Conflict, unstaged veya untracked durum `worktree`; yalnız staged durum
`staged`; temiz repo exact `HEAD`; unborn repo `worktree` seçer. Sonuç production Change Report'u
kullanır ve hiçbir şey yazmaz. Pipe, redirect, CI veya başka non-TTY çağrılar mevcut argparse
stderr/exit-2 davranışını korur; prompt açmaz ve tarama yapmaz. Açık bir yol için aynı akışı
`intentatlas guide [PATH]` ile başlatın. Ayrıntılar [rehberli CLI sözleşmesindedir](guided-cli.md).

Etkileşimli çıktı büyük bir IntentAtlas başlığı; açık kaynak/güvenlik/analiz/öneri/Atlas bölümleri;
satıra sığdırılmış kanıt ve her satırda tek seçenek kullanır. Browser viewer'da **Change report** ve
**Fit graph** tekrarlandığında sayfa ile graph geometrisi sabit kalır.

Public bir GitHub repository'yi elle clone etmeden analiz etmek için gerçek bir etkileşimli
terminal kullanın:

```text
intentatlas https://github.com/OWNER/REPOSITORY
# veya: intentatlas guide https://github.com/OWNER/REPOSITORY
```

IntentAtlas ağ veya cache etkisinden önce normalize URL'yi, yönetilen cache yazmasını,
shallow/resource sınırlarını ve devre dışı çalıştırma davranışını gösterir. Yalnız boş Enter onay
verir. Sonuç exact cache revision'ını gösterir ve aynı production no-write Change Report ile
immutable viewer snapshot'ını kullanır. Private/authenticated repository, redirect, repository
sayfası URL'si, hook, filter, LFS, submodule ve proje kodu çalıştırma desteklenmez. Ayrıntılar
[yönetilen repository cache belgesindedir](managed-repository-cache.md).

Exact aday wheel'i geçici pipx köklerinde install/reinstall/uninstall kapısından geçer; ancak paket
yayımlanmamıştır ve sıfır-önkoşullu Windows installer yoktur. Bkz.
[kurulum durumu](installation.md).

Hiçbir depoya dokunmadan paketlenmiş sentetik sözleşmeyi değerlendirmek için:

```powershell
intentatlas demo --report text
intentatlas demo --report json
intentatlas demo
```

Yerleşik örnek özgün, çevrimdışı ve geçicidir. Sentetik grafiği ve ilişkileri önceden hazırlanır;
üretim graph, öneri, rapor ve görüntüleyici katmanlarını çalıştırır ancak repo keşfi, AST ayrıştırma
veya Git diff çıkarımını sınamaz. İnteraktif görünümde **Change report** düğmesini açarak seçilen
`tests/test_auth_rotation.py` testini, gösterilen uyarı sınırını ve grafikte bulunmasına rağmen
sıralanmayan `tests/test_auth_audit.py` testini karşılaştırın. Ayrıntılı tur için
[yönlendirmeli demo belgesine](guided-demo.md) bakın. Geçerli klasörü taramaz.

Açık uzman komutları sıfır-izli önizleme için kullanılmaya devam eder:

```powershell
intentatlas diagnose C:\projenizin\yolu
# Sonra yazdırdığı kesin Next safe command satırını çalıştırın. Örnekler:
intentatlas changes C:\projenizin\yolu --worktree --report
intentatlas changes C:\projenizin\yolu --commit HEAD --report --format json
```

Bu komutlar çevrimdışı ve salt okunurdur. Tanı; sınırlı yetenekleri, belirsizliği, kanıt
hazırlığını ve sonraki güvenli komutu bildirir. Rapor kesin revision/kapsamı, güncelliği, güven
eşiğini, seçilen ve atlanan adayları, kaydedilmiş sıralama yollarını ve yedek test stratejisini
gösterir. Atlanmak, niyetin etkilenmediğini veya testin gereksiz olduğunu kanıtlamaz. Kayıtlı
grafik varsa `diagnose`, bulunan Python test dosyası ve kesin `python-symbol-reference`
bağlantısı sayılarını da gösterir. `missing-exact-links`, testlerin bulunduğu fakat kesin sembol→test
bağının kurulmadığı anlamına gelir; hazır sonucu değildir. Grafik güncelliği yine ayrıca doğrulanmaz.
Sonraki komut için `diagnose`; unstaged, untracked veya conflicted değişikliklerde `worktree`, yalnız
index değiştiğinde `staged`, çalışma kopyası temizse exact `HEAD`, henüz commit yoksa `worktree`
seçer. Böylece kirli çalışma kopyası yanlışlıkla commit edilmiş `HEAD` görüntüsü sanılmaz.
Yalnız açıkça verilen `--open`, aynı bellek içi rapor anlık görüntüsü için loopback görüntüleyicisini
başlatır.
[Güven-öncelikli önizleme](trust-first-preview.md) ve [belge dizini](index.md) ayrıntıları
açıklar.

Önizlemeyi yorumladıktan sonra kalıcı vault akışını bilinçli olarak benimseyin:

```powershell
intentatlas init C:\projenizin\yolu
intentatlas scan C:\projenizin\yolu
intentatlas open C:\projenizin\yolu
```

Aktif reponuza henüz yazmak istemiyorsanız bu üç komutu önce atılabilir bir kopya veya küçük test
reposunda deneyin. `init`; `intentatlas.json`, başlangıç Markdown klasörleri, taşınabilir Obsidian
ayarları ve eksik yerel-durum `.gitignore` kurallarını oluşturur. `scan`, atılabilir `.intentatlas/`
cache'ini ve `atlas/` altındaki üretilmiş alanları yazar; proje kodunu çalıştırmaz ve kullanıcıya
ait notların üzerine yazmaz. Her şeyi commit etmeden önce `git status` ile inceleyin.

`init`, genel yönlendirme ile boş niyet klasörleri oluşturur; IntentAtlas'ın kendi gereksinim,
karar, kanıt, inceleme veya tarihli oturumlarını hedef depoya örnek veri olarak eklemez.
Mevcut `.gitignore` dosyasını korur; yalnız `.intentatlas/`, `.venv-intentatlas/` ve Obsidian'ın
makineye özel workspace/cache dosyaları için eksik kuralları ekler. Kalıcı `atlas/` notları ve
taşınabilir Obsidian ayarları Git tarafından izlenebilir kalır.
Obsidian isteğe bağlıdır: `atlas/` kalıcı akışın Markdown katmanıdır; Obsidian kurmadan aynı
üretilmiş grafiği `intentatlas open` ile inceleyebilirsiniz.

`status`, `impact`, `recommend-tests`, `diff` ve öneri değerlendirme komutları kalıcı grafiği okur;
bu nedenle önce `scan` çalıştırılmalıdır. `diagnose`, `guide` ve `changes --report` kendi salt-okunur
incelemesini yapar ve kayıtlı grafik gerektirmez.

`impact` için `TARGET`; kesin grafik kimliği (`commit:TAM_SHA` veya
`symbol:src/auth.py::rotate_session`), `src/auth.py` gibi proje-göreli yol, kesin etiket veya tekil
kısmi eşleşme olabilir:

```text
intentatlas impact src/auth.py C:\projenizin\yolu --depth 2
intentatlas impact symbol:src/auth.py::rotate_session C:\projenizin\yolu --direction upstream
```

Çıktıdaki her iki boşluk, asıl hedeften bir ilişki hop'u demektir. Satırlar düz bir traversal
sonucudur; girintili satır hemen üstündeki satırın çocuğu değildir.
İsteğe bağlı `[PATH]` verilmezse komutlar geçerli klasörü kullanır. `impact` ve `recommend-tests`,
yanlış klasörün grafiği kullanılıyorsa bunun görülebilmesi için çözümlenen proje kökünü yazdırır.

Tekrarlanan CLI taramaları, değişmeyen her yerleşik dil adaptörü için sınırlı ve içerik-karmalı bir
parçayı yeniden kullanır. Komut, yeniden kullanılan ve yeniden üretilen adaptör sayılarını gösterir.
Bu cache kaynak metni değil yalnızca grafik metadata'sını taşır ve güvenle silinebilir; bozuk veya
eski kayıt yeniden üretilir. Grafik ve cache dosyaları atomik olarak değiştirilir. Ayrıntılar için
[artımlı tarama belgesine](incremental-scanning.md) bakın.

Yönetilen public GitHub cache kayıtlarında önce kimliği listeleyin, sonra kesin kimliği kullanın:

```text
intentatlas cache list
intentatlas cache info CACHE_ID
intentatlas cache clear CACHE_ID
```

Obsidian kullanıyorsanız `atlas/` klasörünü vault olarak açın. Graph View; gereksinimleri, kararları,
kodu, testleri, kanıtları ve commit’leri renkli, bağlantılı düğümler olarak gösterecektir.

macOS veya Linux'ta `/projenizin/yolu` gibi açık bir hedef yol kullanın. Ortam etkin değilse
kurulumda seçtiğiniz ortam klasörünün içindeki `intentatlas` executable'ını çağırın.

Python 3.11, 3.12 ve 3.13 desteklenir. Tam test paketi Linux üzerinde; kurulmuş wheel ile CLI,
tarama, test önerisi ve yerel görüntüleyici akışı ise en eski ve en yeni desteklenen Python
sürümlerinde Linux, Windows ve macOS üzerinde CI tarafından doğrulanır. Yerel, tekrarlanabilir
paket kontrollerine ek olarak sabit tohumlu property/mutasyon testleri, gerçek Chrome tabanlı
görüntüleme, statik tip ve değişmez Action referansı kapıları uygulanır. Doğrulanan paket
hash'lerini kesin Git revision ve sabit derleme zamanına bağlayan deterministik provenance kaydı
üretilir; yayınlama ayrı onay gerektirir. Ayrıntılar için [sürüm sürecine](../RELEASING.md) bakın.

Pull request veya CI denemelerinde aynı değişiklik analizi salt-okunur gölge modunda çalıştırılabilir:

```text
intentatlas review --base origin/main --head HEAD
intentatlas review --base origin/main --head HEAD --format json
intentatlas review --base origin/main --head HEAD --format sarif
intentatlas review --base origin/main --head HEAD --test-outcomes .intentatlas/test-outcomes.json
intentatlas review --base origin/main --head HEAD --open
```

Komut aynı revision-aralığı ChangeSet ve Change Report verisini kullanır. Geçerli bulgular süreci
başarısız yapmaz; pull request yayımlamaz veya değiştirmez, sağlayıcı kimlik bilgisi ve ağ erişimi
istemez. SARIF yalnız güvenli proje-göreli konumları ve hunk satır aralıklarını taşır; kaynak
parçası veya mutlak yol içermez. Sınırlar [CI gölge inceleme belgesinde](ci-shadow-review.md)
açıklanır.

İsteğe bağlı outcome JSON’u tam commit kimliğiyle eşleşirse seçilen ve gerçekten çalıştırılan test
yolları gözlemsel olarak karşılaştırılır. Commit farklıysa veri `stale` kalır ve karşılaştırma
üretilmez; bu kümeler doğruluk, zorunluluk veya yeterlilik iddiası değildir.
`--open`, komutun kullandığı aynı bellek içi grafik ve review raporunu yerel arayüzde açar.

Aynı deterministik ChangeSet şeması commit, revision aralığı, index veya mevcut çalışma ağacını
kapsar:

```text
intentatlas changes --commit HEAD
intentatlas changes --base main --head HEAD --format json
intentatlas changes --staged
intentatlas changes --worktree
intentatlas changes --staged --analyze --format json
intentatlas changes --staged --report --format json
intentatlas changes --worktree --report --open
```

Neyi incelemek istediğinize göre kapsam seçin: `--worktree` mevcut staged, unstaged ve untracked
değişiklikleri birlikte kapsar; `--staged` yalnız index'i; `--commit HEAD` commit edilmiş HEAD
görüntüsünü inceler ve etkilenen dosyaların hâlâ o revision ile eşleşmesini bekler. Kirli repoda
tahmin yürütmek yerine `diagnose` çıktısındaki komutu kullanın.

| Çıktı terimi | Anlamı |
| --- | --- |
| `aligned` | Seçilen değişiklik tarafı, güvenle taranan mevcut dosyayla eşleşiyor. |
| `stale` | Seçilen commit/index içeriği mevcut dosyadan farklı; kesin iddialardan kaçınılıyor. |
| `analyzed` | Değişen dosya için desteklenen kesin artifact kanıtı kuruldu. |
| `fallback` | Yalnız daha geniş dosya-seviyesi kanıt var; gösterilen tam-paket politikasını izleyin. |
| `unknown` | Artifact güvenle eşleştirilemedi veya analiz edilemedi; hedefli yeterlilik iddiası yok. |

`--analyze`, dosya başına durum, güncellik, güven ve artifact kimliklerini verir. `--report`, aynı
taze analize ek olarak gereksinim etkilerini ve testleri sıralar, test stratejisini seçer ve
atlamaları açıklar. `--report --open`, aynı bellek-içi raporu yerel görüntüleyicide gösterir.

`--open`, aynı bellek içi raporu ikinci bir grafik veya rapor dosyası kaydetmeden yalnızca yerel
arayüzde açar.

Çıktı yalnız durumları, güvenli proje-göreli yolları, çözümlenmiş commit kimliklerini ve yeni taraf
satır aralıklarını taşır; ham diff satırlarını saklamaz. Worktree modu ignore kurallarına uyan
takip edilmeyen yolları gösterir ancak içeriklerini okumaz veya yazmaz. `--analyze`, açıkça yeni ve
sınırlı bir yerel tarama yaparak her dosyayı `analyzed`, `fallback` veya `unknown`; güncelliği
`aligned` veya `stale` olarak işaretler ve güven, eser kimliği ile kanıtı gösterir. Bu seçenek normal
tarayıcı üzerinden desteklenen çalışma ağacı dosyalarını okuyabilir ancak proje kodunu çalıştırmaz
ve ham kaynağı saklamaz. Yapılandırılmış vault'un `Private/` alanı Git meta verisi toplanmadan önce
kapsam dışında bırakılır.

`--report` aynı hizalanmış analizi kullanarak olası gereksinim etkilerini ve aday testleri sıralar.
Kesin sembol-niyet yolu varsayılan orta güven eşiğine ulaşabilir; yalnızca aynı dosyada bulunmaya
dayanan ilişki düşük güvenli kalır. `fallback` durumunda hedefli testler tek başına yeterli sayılmaz
ve tam test paketi de istenir. `unknown` durumunda sistem sıralama iddiasından kaçınır ve tam test
paketine yönlendirir. Rapor tavsiye niteliğindedir; listede olmayan gereksinim veya testlerin
etkilenmediğini kanıtlamaz.

Bir commit, dosya veya sembol için test dosyalarını çalıştırmadan sıralamak için:

```text
intentatlas recommend-tests commit:TAM_SHA --minimum-confidence medium
intentatlas recommend-tests src/auth.py --minimum-confidence low --format json
```

Puanlar sabit ve incelenebilir yapısal kanıtlara dayanır. Kesin sembol değişikliği ile kesin statik
test bağlantısı, yalnız dosya veya adlandırma kuralı kanıtından daha yüksek sıralanır. Dosya
düzeyindeki bir ilişki, aynı dosyadaki ilgisiz bir sembol için varsayılan orta güvenli iddiaya
dönüşmez; bu yedek kanıt düşük güvenli kalır veya çelişen kesin sembol kanıtı varsa elenir.
Sonuçlar tavsiyedir; listede olmayan bir test, davranışın etkilenmediğini kanıtlamaz.

Tam IntentAtlas repo checkout'unda, öneri kalitesini eksiksiz olduğu açıkça belirtilen insan
incelemeli yerel etiketlerle ölçmek için:

```text
intentatlas evaluate-recommendations benchmarks/intentatlas-recommendations.json
intentatlas evaluate-recommendations benchmarks/intentatlas-recommendations.json --minimum-confidence high --format json
```

Değerlendirme testleri çalıştırmadan ve sıralama puanlarını değiştirmeden TP, FP, FN, precision ve
recall üretir. Yalnız tam repoda bulunan iki vakalık temel ölçüm regresyon yardımcısıdır; sdist
corpus'una dahil değildir ve başka repolardaki doğruluğu kanıtlamaz. Şema ve metrik sözleşmesi
[değerlendirme belgesinde](recommendation-evaluation.md) açıklanır.

Özgün Python, TypeScript ve Go grafik senaryolarında bütün güven eşiklerini karşılaştırmak için:

```text
intentatlas evaluate-corpus benchmarks/recommendation-corpus.json
intentatlas evaluate-corpus benchmarks/recommendation-corpus.json --format json
```

Corpus çıktısı proje başına ve mikro toplamları birlikte gösterir. Bu küçük özgün fixture’lar
agregasyon ile güven davranışını doğrular; kopyalanmış repo veya gerçek dünya doğruluk kanıtı
değildir. Ayrıntılar [corpus şemasında](recommendation-corpus.md) bulunur.

Tam IntentAtlas repo checkout'unda lisansı incelenmiş gerçek projelerle yeniden üretilebilir
doğrulama için, onaylı altı açık kaynak depoyu yalnızca ağ izninden sonra yalnız repoda bulunan
manifestteki commit’lere sabitleyin ve şunu çalıştırın:

```text
intentatlas evaluate-real-world benchmarks/real-world/manifest.json .intentatlas/real-world/checkouts
```

Komut taramadan önce origin, commit, temiz çalışma ağacı ve incelenmiş lisans özetini doğrular.
Repo klonlamaz, bağımlılık kurmaz, test veya proje kodu çalıştırmaz; üçüncü taraf kaynak, Git
geçmişi, logo ya da üretilmiş grafiği üründe saklamaz. Ayrıntılar
[gerçek proje doğrulama protokolünde](real-world-validation.md) bulunur. On sekiz sabit vaka
yalnızca seçilen Python, JavaScript ve Go değişiklikleri için kanıttır; genel doğruluk iddiası
değildir.

Bir projeyi okumadan veya çalıştırmadan çevrimdışı ölçek kontrolü yapmak için:

```text
intentatlas benchmark-scale
intentatlas benchmark-scale --unrelated-edges 50000 --iterations 500 --format json
```

Benchmark kararlı grafik/sonuç/iş sayılarını ve ortama bağlı süreleri raporlar. Taşınabilir gecikme
garantisi değil, regresyon ve tanılama aracıdır. Ayrıntılar
[ölçek benchmark sözleşmesinde](query-scale-benchmark.md) bulunur.

Yerel görüntüleyici, seçilen düğümden testlere, kanıtlara, coverage sonuçlarına, test sonuçlarına,
commit'lere ve pull request'lere giden sınırlı en kısa yapısal yolları da gösterir. Bu yollar grafik
bağlantısını açıklar; nedensellik, eksiksizlik, güncellik veya test zorunluluğu iddia etmez.
`intentatlas demo`, aynı üretim görüntüleyicisini aynı-dosya karşı örneği içeren on iki düğümlü
özgün bir grafik üzerinde açar ve görüntüleyici kapandığında geçici grafiği temizler.
`intentatlas demo --report text` ve `--report json`, listener başlatmadan aynı sınırlı kanıt
hikâyesini üretir.

Büyük depolarda görüntüleyici, grafiğin tamamını yerel gezinme için bellekte korur; aynı anda en
fazla 240 düğüm ve 900 kenardan oluşan deterministik bir pencere çizer. Genel görünüm katmanları
dengeler; genel arama, rapor ve ilişki bağlantıları gizli bir düğümün iki adımlı sınırlı çevresini
açabilir. Toplam/gösterilen sayıları görünür kalır ve ilişki ayrıntıları sınırsız tarayıcı öğesi
üretmek yerine kaç sonucun gösterilmediğini açıkça belirtir.

Adapter conformance sözleşmesi sürüm 1, ortak adapter sınırını çalıştırılabilir bir denetime
dönüştürür. Yeni ve cache’den okunan fragment’lar grafiğe katılmadan önce aynı sınırlı sembol,
ilişki, uç nokta, kanıt, sıralama ve determinizm kurallarını geçmelidir. Built-in adapter’lar aynı
fixture tabanlı yardımcıyla doğrulanır; bu özellik harici plugin yükleyicisi değildir. Ayrıntılar
[dil adapter conformance belgesinde](adapter-conformance.md) bulunur.


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

