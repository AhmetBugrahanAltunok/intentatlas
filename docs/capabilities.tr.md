# Yetenekler, ayrıntılı

Her adaptörün, içe aktarıcının ve sorgunun gerçekte neyi kapsadığı ve nerede çekimser kaldığı.
Kısa hâli [README](../README.tr.md)'de; tasarım gerekçesi [mimari](architecture.md)'de.

İngilizcesi: [capabilities.md](capabilities.md).

## Durum

Python, TypeScript/JavaScript ve Go analizi aynı dil-bağımsız adaptör sözleşmesini kullanır. `.ts`,
`.tsx`, `.js` ve `.jsx` dosyalarında adlandırılmış semboller, yerel import/re-export bağlantıları
ve test ilişkileri çıkarılır. Go adaptörü `.go` dosyalarını, `go.mod` modül sınırlarını,
adlandırılmış türleri, fonksiyonları, metotları, modül-içi paket importlarını ve testleri kapsar.
Aynı klasördeki testler yalnızca tek bir üretim dosyasına ait, gerçekten başvurulan dışa açık
bildirimler için yapısal kanıt kazanır; belirsiz adlar bağlanmaz ve dosya adı eşleşmesi zayıf yedek
olarak kalır. Hiçbir adaptör dil çalışma zamanını veya proje kodunu çalıştırmaz.
Doğrudan test edilen bir Go sarmalayıcısı değişen sembolü çağırıyorsa yalnızca bir kesin
`calls`/`called-by` adımı izlenir; sınırsız çağrı grafiği yayılımı yapılmaz.

İsteğe bağlı Cobertura coverage ve JUnit test raporları `intentatlas.json` içindeki proje-göreli
`coverage_reports` ve `test_reports` listeleriyle içe aktarılabilir. IntentAtlas testleri çalıştırmaz;
yalnızca dosya başına sınırlı özetleri grafiğe ekler. `intentatlas diff` komutu da mevcut grafiği bir
temel grafikle karşılaştırarak CI için deterministik ve zaman damgasız JSON üretir.

SCIP protobuf-JSON, SARIF 2.1.0 ve commit-kimli test execution map raporları da sırasıyla
`scip_reports`, `sarif_reports` ve `test_execution_reports` listeleriyle açıkça etkinleştirilebilir.
İkili SCIP bu fazda desteklenmez. SCIP ve SARIF yalnız dosya gözlemi olarak kalır; etki veya test
zorunluluğu iddiası üretmez. Execution map yalnız tam commit kimliği güncel Git HEAD ile eşleşir ve
eşlenen tüm dosyalar o HEAD'e göre takip edilen/değişmemiş durumdaysa testten kaynak dosyaya
çalışma-zamanı kanıtı ekler; eski ya da kimliği çözülemeyen rapor önerileri etkilemez. Ham semboller,
tanılar, mesajlar, snippet'ler, düzeltmeler, kod akışları ve kaynak metni
saklanmaz. Ayrıntılar [açık kanıt belgesinde](open-evidence.md) açıklanır.

Issue ve pull request bağlamı da isteğe bağlı yerel JSON snapshot dosyalarından içe aktarılabilir.
`delivery_reports` kaynakları gereksinim ve kararları issue, pull request, değişen dosya ve bilinen
commitlerle bağlar. Gövdeler, yorumlar ve ham API yanıtları saklanmaz; ayrıntılar
[yerel teslimat şemasında](delivery-schema.md) açıklanır.

Yakın Git geçmişinde değişen yeni taraf satırları, doğrulanmış AST aralıklarıyla kesiştiğinde ve
güncel dosya incelenen commit blobuyla eşleştiğinde Python sınıf, fonksiyon ve metot sembollerine
doğrudan `modifies` ilişkisi eklenir. Eski dosya sürümü, silme, modül-seviyesi değişiklik, span
desteği olmayan adaptör veya belirsizlik durumunda mevcut dosya-seviyesi `changes` ilişkisi güvenli
yedek olarak korunur.

`recommend-tests`, doğrulanmış grafik ilişkilerinden test dosyalarını `high`, `medium` veya `low`
güvenle sıralar. Manifesti olmayan kök `src/` düzeninde hem `from auth import ...` gibi geleneksel
hem de `from src.auth import ...` gibi namespace importları tek bir yerel modülü gösterdiğinde
çözülür. Setuptools, Hatch veya Flit source-root bilgisi taşıyan `pyproject.toml` varsa bu bilgi
önceliklidir. Belirsiz modül veya sembol kimlikleri bilinçli olarak bağlanmaz; kesin Python
sembol→test bağlantılarını görmek için `scan` sonrasında `diagnose` çalıştırın.
güvenle sıralar ve her sonucun neden yolunu gösterir. Python testleri, sınırlı paket yeniden
dışa-aktarımları üzerinden tam içe aktarılan sembole bağlanabilir; iç içe bir değişiklikte test adı
uyuşuyorsa sahibi olan sembolün odaklı testi kullanılabilir. JavaScript/TypeScript için adlandırılmış
ve varsayılan statik içe aktarımlar kaydedilir; yalnızca tam sembolü içe aktaran tek bir bağımlı
kaynaktan doğrudan bağlı teste gidilir. Seçilen dosya veya sembolün en son incelenen dar
eş-değişimindeki testler ayrı bir düşük-güven kanıtıdır; 20 artifact'tan geniş commitler abstain
eder. Yalnız filename eşleşmesine dayanan ikinci hop düşük kalır. Python dosyaları ancak sınırlı
pytest filename desenleri ile güvenle okunan `python_files` veya `testpaths` bildirimleri bu rolü kanıtlarsa
doğrudan çalıştırılabilir hedeftir; `conftest.py`, package marker, typing fixture ve eşleşmeyen
ilan edilmiş test köklerinin dışındaki dosyalar ve diğer support dosyaları graph artifact olarak kalır fakat çalıştırılacak komut diye sunulmaz.
JavaScript/TypeScript ve Go mevcut adapter davranışını korur.

`low` keşif modudur: zayıf filename, fallback ve co-change sinyalleri yüksek fan-out ve düşük
precision üretebilir. Otomatik CI seçimi için `medium veya üzeri` eşik kullanın; varsayılan ve
guided akış `medium` kalır. Exact statik direct-reference bilinçli olarak `80/medium` değerindedir;
`high`, doğrudan değişiklik kümesi içindeki test gibi daha güçlü kanıtlara ayrılmıştır. Sorgu
sınırsız geçişli dolaşım yapmaz.

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
Üçüncü taraf kaynak kodu, logosu veya vault içeriği paketlenmez.

MIT lisanslıdır. Katkı göndermeden önce [CONTRIBUTING.md](../CONTRIBUTING.md) belgesini okuyun.
