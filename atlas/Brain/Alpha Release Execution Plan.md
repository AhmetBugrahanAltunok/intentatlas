---
id: alpha-release-execution-plan
type: memory
status: active
---
# Alpha Release Execution Plan

Updated: 2026-09-07. Canonical phase status: [[Brain/Product Roadmap]].
Current handoff: [[Sessions/2026-09-07 - Alpha readiness checkpoint]].

## Güncel sonuç — 2026-09-07

**Faz 20 tamamlandı.** 595 test geçti, 4 platform testi atlandı; branch ölçümü açık toplam kapsam
%86,47. Ruff, mypy ve Bandit geçti. Obsidian'da 264 bağlantı doğrulandı, 212 kalıcı dosya korundu,
iki taramada 1721 üretilmiş dosya aynı kaldı; bağlantısız kalıcı not sayısı sıfır.
Sıradaki iş **Faz 21: temiz kurulum ve yayın adayı envanteri**. Ayrıntılı sonuçlar:
[[Evidence/EVD-036 - Phase 20 change coverage verification]] ve
[[Reviews/Phase 20 Change Coverage Review]].

Kod/test/ürün dokümantasyonu yerel `041069a` commitinde kaydedildi; kalıcı plan ve güncel vault
ayrı dokümantasyon commitinde korunuyor. GitHub'a push yapılmadı.

## Ürün hedefi

Bir geliştirici kendi deposunda tek bir değişiklik için şu soruların cevabını alabilmeli:
"Neyi etkileyebilir, hangi testler aday ve bunun kanıtı ne?"
İlk fayda için Obsidian kurulumu veya gereksinim yazımı zorunlu olmayacak.
Kalıcı Markdown hafızası ve grafik, raporun ardından isteğe bağlı derinleşme sağlayacak.
Bu hedef [[Brain/North Star]] ve [[Decisions/ADR-028 - Make the change report the primary product surface]]
ile uyumludur. Öneriler danışmanlık niteliğindedir; test yeterliliği garantisi değildir.

## Başlangıç durumu

- Çalışan temel: Python, JS/TS ve Go adaptörleri; değişiklik raporu; çevrimdışı CLI;
  yerel grafik; taşınabilir vault; test/coverage ve yerel teslimat verisi içe aktarma.
- Sürüm: 0.3.0rc1. Bu ifade yayımlanmış paket veya yayın onayı anlamına gelmez.
- Faz 18/19 kayıtları ana yol haritasından kopuktu; bağlantılar 2026-09-07'de tamamlandı.
- Yeniden inceleme: 569 test geçti, 1 tarayıcı testi başarısız, 4 atlandı.
  Ruff, Bandit, mypy ve CLI metin demosu geçti.
- Kısmi diff ve düzenleme+silme örnekleri eksik kapsamı tam gösterdi.
- Çok sayıda önceden mevcut kaynak/test/not ve üretilmiş vault değişikliği var.
  Bunların tamamını yeni çalışma gibi sunmadan yayın envanteri uzlaştırılmalı.

## Teslimat sırası ve çıkış ölçütleri

| Faz | Kullanıcıya değer | Yapılacak iş | Çıkış ölçütü |
| --- | --- | --- | --- |
| 20 | Eksik analizin güvenli görünmesini engellemek | Tam satır kapsamı, iç içe semboller, silme belirsizliği, tarayıcı kanıt yolu | REQ-036 kabul tablosu ve tüm yerel kalite kapıları geçer |
| 21 | Yardımsız kurulabilen ve anlamlı sonuç veren aday | Temiz wheel/sdist kurulumları, EN/TR akışı, kaynak kimliği, katkı/vault politikası | Aynı kaynak revizyonuna bağlı tekrar üretilebilir paketler; CLI/UI ve platform kanıtı; gerçeği yansıtan kurulum metni |
| 22 | Gerçek kullanım değerini ölçmek | En az 5 bağımsız kişi kendi deposunda ilk raporu alır; anlamlandırma ve sonraki kullanım gözlenir | İlk kullanım medyanı 10 dakikanın altında; yardım ve başarısızlıklar dahil raporlanır; kritik sorunlar kapanır |
| 23 | İncelenmiş alpha'yı erişilebilir kılmak | Yayın notu, örnek, güvenlik kanalı, temiz revizyon, doğrulanmış hash'ler ve yayın işlemleri | Faz 11C kapıları, uzaktaki CI/audit ve somut yayın incelemesi geçer; yayımlanan bytes doğrulanır |

Takvim, kanıt yerine geçmez. Bir fazın başarısız kapısı kapanmadan sonraki uygulama fazı başlamaz.
Gelecek fazların ayrıntılı gereksinim/karar/iş kaydı o fazın başlangıcında çıkarılır;
taslak işler yapılmış gibi işaretlenmez.

## Faz 21 için somut kontrol listesi

- [ ] Değişiklik envanterini Faz 18/19/20 olarak ayır; izlenmeyen gerekli dosyaları kaybetme.
- [ ] Testin güncel `src` kodunu, paket testinin ise tam seçilen wheel'i yüklediğini doğrula.
- [ ] Yerel sabit araç zinciriyle iki wheel/sdist üret; kurulum ve yeniden üretim eşitliğini doğrula.
- [ ] Temiz ortamda sürüm, metin/JSON demo, diagnose, değişiklik raporu ve viewer akışlarını dene.
- [ ] Kullanıcı notu veya yapılandırma yazmadan ilk depo raporunu doğrula.
- [ ] README EN/TR kurulum ve hata sonrası devam komutlarını eşleştir.
- [ ] Desteklenen işletim sistemi/Python matrisi için gerçek CI sonuçlarını revizyona bağla.
- [ ] ADR-034 gereği katkı öncesi üretilmiş vault politikası seç: mevcut snapshot, artifact veya
  yerel üretim seçeneklerini kalıcı bağlantı ve geçiş maliyetiyle karşılaştır. Toplu silme yapma.
- [ ] Kanıt, kapsamlı inceleme ve somut yayın adayı envanterini kaydet.

## Faz 22 gözlem protokolü

Katılımcıya ürünü kurup kendi yerel deposunda bir değişikliğin raporunu alması ve önerilen
bir testin nedenini açıklaması görevi verilir. Süre başlangıcı, başarı tanımı ve yardım düzeyi
önceden kaydedilir. Başarısız denemeler sonuçtan çıkarılmaz. En az beş gerçek bağımsız katılımcı
olmadan medyan, kullanıcı başarısı veya kullanım kolaylığı iddiası yayımlanmaz.
Sentetik senaryolar ve mevcut benchmarklar bu kapıyı karşılamaz.

İkinci kullanım ayrı takip edilir: kişi ürünü başka bir değişiklikte tekrar kullandı mı, kararını
etkiledi mi, hangi eksik kanıt işini engelledi? Henüz kullanıcı veya gözlem kaydı yok; sonuç
uydurulmaz. Katılımcılara mesaj gönderimi ve kişisel veri paylaşımı ayrı, somut işlem olarak ele alınır.

## Yayın kapsamı ve ertelenenler

Alpha kapsamı mevcut üç dil, yerel rapor, kanıt açıklaması, isteğe bağlı vault ve viewer'dır.
Yeni dil, hosted servis, model API'si, otomatik blocking CI ve 1.0 garantisi bu yolun dışında.
Yıldız sayısı veya evrensel doğruluk oranı başarı ölçütü değildir. Öncelikli ölçüler:
ilk rapora ulaşma, doğru yorumlama, açıklanabilir öneri ve gerçek tekrar kullanım.

## Riskler ve devamlılık

| Risk | Karşılık |
| --- | --- |
| Eksik kapsamın tam gösterilmesi | Faz 20'de negatif regresyonlar ve full-suite fallback |
| Yeşil eski kanıtın yeni kaynak için kullanılması | Her incelemede kaynak/komut/sonuç ve tarih; yeni hata eski sonucu geçersiz kılmaz ama güncel kapıyı açar |
| Kurulu paketin kaynak testini maskelemesi | Açık import kimliği ve izole paket doğrulaması |
| Üretilmiş notların Git gürültüsü | Faz 21'de ADR-034 yönetişim kararı; tek yazarlı deterministik tarama |
| Gerçek kullanımın bilinmemesi | Faz 22'de insan gözlemi; teknik testleri kullanıcı kanıtı saymama |
| Paket/CI/audit kanıtının eskimesi | Faz 23'te yayın revizyonuna bağlı sonuç ve artifact hash'leri |

Her çalışma sonunda [[Brain/Product Roadmap]], ilgili Evidence/Review ve son Sessions notu
birbirini göstermeli. Sessions kaydı tamamlanan iş, tam komutlar, açık kapılar ve tek sonraki
adımı içermeli. Yeni başlangıçta geçmiş fazları baştan uygulamak yerine bu checkpoint izlenir.

## Links

- [[Requirements/REQ-036 - Require complete change coverage before targeted advice]]
- [[Decisions/ADR-038 - Preserve uncovered change ranges and deletion uncertainty]]
- [[Brain/Phase Completion Protocol]]
- [[Brain/Phase 11 Strategy]]
- [[Decisions/ADR-034 - Retain generated vault outputs under single-writer governance]]
