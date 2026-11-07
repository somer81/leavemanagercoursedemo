# Spec 0001 — Walking skeleton (yürüyen iskelet): sağlık durumu uçtan uca

- Status: In progress
- Mode: lite
- Plan: `specs/plans/0001-plan.md`
- Self-critique: done

## Intent
Kurs eğitmeni ve geliştiriciler, İzin Yöneticisi'nin ilk özelliği yazılmadan önce uygulamanın
uçtan uca ayağa kalktığını ve doğrulama sözleşmesinin (`scripts/check`) gerçekten çalıştığını
görmek istiyor. Başarı: tarayıcıda açılan ana sayfa, sistemin çalıştığını ve veri deposuna
erişebildiğini gösterir; bu bilgi tüm katmanlardan (sunum → API → servis → repository → SQLite)
geçerek gelir; `scripts/check` planlanan tüm adımları çalıştırır ve yeşildir, CI aynısını yapar.
Bilinçli olarak yapılmayan: giriş/oturum, izin domain'i (talep, bakiye, onay), görsel tasarım,
dağıtım (deployment). Bu dilim yalnızca sonraki özelliklerin üstüne inşa edileceği iskelettir.

## Requirements
- **R-1:** Sistem, çalışır durumda olduğunu ve veri deposuna erişip erişemediğini bildiren bir
  sağlık bilgisi sunar. Bu bilgi yalnızca durum içerir; kişisel veri, sürüm, yol veya iç ayrıntı içermez.
- **R-2:** Veri deposuna erişilemiyorsa sağlık bilgisi bunu "kullanılamıyor" olarak bildirir;
  hatanın iç ayrıntısı (stack trace, SQL, dosya yolu) kullanıcıya sızmaz.
- **R-3:** Sağlık bilgisi oturum gerektirmez. Bu, `docs/security.md` "varsayılan red" kuralına
  bilinçli ve belgelenmiş bir istisnadır (oturum gerektirmeyen uçlar: giriş ve sağlık).
- **R-4:** Tarayıcıda açılan ana sayfa sağlık durumunu kullanıcıya gösterir.
- **R-5:** Bir geliştirici, README'de belgelenmiş komutlarla ortamı kurar, uygulamayı başlatır ve
  doğrulamayı çalıştırır.
- **R-6:** Doğrulama sözleşmesi, `scripts/check.conf`'ta planlanan tüm adımları (lint, format,
  tipler, mimari, birim, frontend, entegrasyon) gerçekten çalıştırır; hızlı profil yalnızca
  `[fast]` adımlarını çalıştırır; CI aynı sözleşmeyi çalıştırır.
- **R-7:** `docs/architecture.md` yasak bağımlılıklar 1–4 otomatik denetlenir; bir ihlal
  doğrulamayı kırmızıya düşürür.

## User experience
- **Flow:** Kullanıcı ana sayfayı açar → sayfa sağlık durumunu sorgular → sonucu gösterir.
  Başka etkileşim yoktur.
- **States:**
  - Yükleniyor: "Durum kontrol ediliyor…"
  - Başarılı (sağlıklı): "Sistem çalışıyor"
  - Sorunlu (veri deposu kullanılamıyor): "Veritabanına erişilemiyor"
  - Hata (sunucuya ulaşılamıyor veya beklenmeyen cevap): "Sunucuya ulaşılamıyor"
  - Boş: uygulanamaz (liste yok)
  - Yetkisiz: uygulanamaz (R-3, oturum gerekmez)
- **Design reference:** none — the flow above is the design.
- **Accessibility:** sayfa dili Türkçe (`lang="tr"`); durum metni ekran okuyuculara duyurulan bir
  bölgede (canlı bölge); durum yalnızca renkle değil metinle anlatılır; metin kontrastı WCAG AA.

## Constraints & out of scope
- **Sensitive area: none** — kişisel veri işlenmez; yetkilendirme mantığı kurulmaz (henüz oturum
  yok). R-3 istisnası bir politika kararıdır ve bu spec'in onayıyla `docs/security.md`'ye yazılır;
  oturumu kuracak spec (Yetkilendirme hassas alanı) yalnızca giriş ve sağlık uçlarının herkese
  açık olduğunu test edecektir.
- Doğrulama: `scripts/check` her iki profilde residue testinden temiz geçer
  (`docs/testing.md`, Resource hygiene); her profilin süresi en az 3 çalıştırmanın medyanıyla raporlanır.
- Stack ve araçlar `docs/conventions.md`'deki kararlara uyar; bu spec'in getirdiği bağımlılıklar
  plan'da `docs/security.md` "Dependencies" kontrolüyle listelenir.
- Belge güncellemeleri: `docs/security.md` (R-3 istisnası), `docs/conventions.md` "Enforced by
  tooling" (pytest `--strict-markers` maddesi Known traps'ten taşınır).
- **Out of scope:** giriş/oturum, izin domain'i, görsel tasarım ve stil (asgari, okunur CSS hariç),
  dağıtım, Docker, e2e testleri, veritabanı migrasyon aracı.
- Split: proposed 0001a (toolchain + check) / 0001b (sağlık uçtan uca); kept as one — somer81,
  tek kullanıcı yeteneği ve bölünemez iskelet (toolchain'siz ilk parça check'i yeşile getiremez).

## Acceptance criteria
- [ ] AC-1 — Uygulama ve veri deposu çalışırken sağlık sorgusu "sağlıklı" durumunu ve veri deposunun erişilebilir olduğunu (veri deposuna basit bir okuma başarılı) döner.
- [ ] AC-2 — Veri deposuna erişilemezken sağlık sorgusu "kullanılamıyor" durumunu döner ve cevapta stack trace, SQL veya dosya yolu bulunmaz.
- [ ] AC-3 — Sağlık sorgusu oturum olmadan yanıt verir; cevap yalnızca durum alanlarını içerir.
- [ ] AC-4 — Ana sayfa, sağlık sorgusu sürerken "Durum kontrol ediliyor…" gösterir.
- [ ] AC-5 — Ana sayfa, sağlıklı cevapta "Sistem çalışıyor" gösterir.
- [ ] AC-6 — Ana sayfa, "kullanılamıyor" cevabında "Veritabanına erişilemiyor" gösterir.
- [ ] AC-7 — Ana sayfa, sunucuya ulaşamadığında veya beklenmeyen bir cevap aldığında (ağ hatası, 5xx cevap ya da JSON olmayan gövde) "Sunucuya ulaşılamıyor" gösterir.
- [ ] AC-8 — Sayfa dili Türkçedir ve durum metni ekran okuyuculara duyurulan bir canlı bölgededir.
- [ ] AC-9 — `./scripts/check` 7 planlı adımın hepsini çalıştırıp yeşil biter; `./scripts/check --fast` yalnızca `[fast]` adımlarını çalıştırır; residue testi iki profilde de temizdir.
- [ ] AC-10 — Yasak bağımlılık 1–4'ten herhangi birinin ihlali `./scripts/check`'i kırmızıya düşürür.
- [ ] AC-11 — README'deki komutlarla, depo dışındaki temiz bir klonda ortam kurulur, uygulama başlatılır ve ana sayfa "Sistem çalışıyor" gösterir.

## Definition of Done
- [ ] Every acceptance criterion mapped to proof (test or reproducible observation)
- [ ] `scripts/check` green
- [ ] Independent review done; real findings fixed, noise rejected with written rationale, deferred ones in `specs/backlog.md`
- [ ] Docs / ADRs updated if behavior or architecture changed
- [ ] Spec moved to `specs/done/` (it becomes immutable there)

## Scorecard (fill at ship — honest numbers make the process improvable)
| Metric | Value |
|---|---|
| Spec revisions | |
| Fix rounds | |
| Review findings: real / noise / deferred | |
| Regressions introduced | |
| Bugs escaped to production | |
