# Spec 0001 — Walking skeleton (yürüyen iskelet): sağlık durumu uçtan uca

- Status: Shipped
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
- [x] AC-1 — Uygulama ve veri deposu çalışırken sağlık sorgusu "sağlıklı" durumunu ve veri deposunun erişilebilir olduğunu (veri deposuna basit bir okuma başarılı) döner.
- [x] AC-2 — Veri deposuna erişilemezken sağlık sorgusu "kullanılamıyor" durumunu döner ve cevapta stack trace, SQL veya dosya yolu bulunmaz.
- [x] AC-3 — Sağlık sorgusu oturum olmadan yanıt verir; cevap yalnızca durum alanlarını içerir.
- [x] AC-4 — Ana sayfa, sağlık sorgusu sürerken "Durum kontrol ediliyor…" gösterir.
- [x] AC-5 — Ana sayfa, sağlıklı cevapta "Sistem çalışıyor" gösterir.
- [x] AC-6 — Ana sayfa, "kullanılamıyor" cevabında "Veritabanına erişilemiyor" gösterir.
- [x] AC-7 — Ana sayfa, sunucuya ulaşamadığında veya beklenmeyen bir cevap aldığında (ağ hatası, 5xx cevap ya da JSON olmayan gövde) "Sunucuya ulaşılamıyor" gösterir.
- [x] AC-8 — Sayfa dili Türkçedir ve durum metni ekran okuyuculara duyurulan bir canlı bölgededir.
- [x] AC-9 — `./scripts/check` 7 planlı adımın hepsini çalıştırıp yeşil biter; `./scripts/check --fast` yalnızca `[fast]` adımlarını çalıştırır; residue testi iki profilde de temizdir.
- [x] AC-10 — Yasak bağımlılık 1–4'ten herhangi birinin ihlali `./scripts/check`'i kırmızıya düşürür.
- [x] AC-11 — README'deki komutlarla, depo dışındaki temiz bir klonda ortam kurulur, uygulama başlatılır ve ana sayfa "Sistem çalışıyor" gösterir.

## Evidence (VERIFY, 2026-11-07)
Full green: CHECK GREEN (full) — CI run https://github.com/somer81/leavemanagercoursedemo/actions/runs/42374100561 @2b3e273 (check + doctor --strict success); sonraki commit'ler yalnızca `specs/` (rule 6). Yerel: CHECK GREEN (full, 7 steps, 1 s) @5d45c56; RESIDUE CLEAN (full + fast) @98ece20.

| Acceptance criterion | Evidence | Status |
|---|---|---|
| AC-1 | `test_check_returns_ok_when_probe_succeeds`, `test_health_reports_ok_when_database_reachable` — `./scripts/check` | PASS |
| AC-2 | `test_check_returns_unavailable_when_probe_fails`, `test_health_reports_unavailable_without_internal_details` — `./scripts/check` | PASS |
| AC-3 | `test_health_requires_no_session_and_returns_only_status_fields` — `./scripts/check` | PASS |
| AC-4 | `shows loading text while the health request is pending` — `./scripts/check`; S-2 | PASS |
| AC-5 | `shows system running on an ok response` — `./scripts/check`; S-1 | PASS |
| AC-6 | `shows database unreachable on an unavailable response` — `./scripts/check`; S-3 | PASS |
| AC-7 | `shows server unreachable on network error`, `… on 5xx`, `… on non-JSON body` — `./scripts/check`; S-4 | PASS |
| AC-8 | `page language is Turkish and status lives in a live region` — `./scripts/check`; S-1…S-4'te gerçek tarayıcıda okundu | PASS |
| AC-9 | CI full (7 adım) + `./scripts/check --fast` 6 adım (`skip integration (full only)`) + residue satırları (plan Build evidence) | PASS |
| AC-10 | Kasıtlı bozma (depo dışı klon @a6ab9bb): ihlal 1, 2, 3a `sqlite3`, 3b `fastapi`, 4a `pydantic`, 4b → her biri `BROKEN`, exit 1; check düzeyinde `CHECK FAILED (full) at step: architecture` | PASS |
| AC-11 | Depo dışı temiz klon @a6ab9bb, README adımları (tek sapma `--port`); `/api/health` 200; ana sayfa "Sistem çalışıyor" (S-1) | PASS |

UI: S-1…S-4 agent-captured, judged by somer81 at SHIP, 2026-11-07 (görüntüler repoda tutulmaz; SHIP sonrası silindi).

## Definition of Done
- [x] Every acceptance criterion mapped to proof (test or reproducible observation)
- [x] `scripts/check` green
- [x] Independent review done; real findings fixed, noise rejected with written rationale, deferred ones in `specs/backlog.md`
- [x] Docs / ADRs updated if behavior or architecture changed
- [x] Spec moved to `specs/done/` (it becomes immutable there)

## Scorecard (fill at ship — honest numbers make the process improvable)
| Metric | Value |
|---|---|
| Spec revisions | 1 (taslak → onay, öz eleştiri katlandı) |
| Fix rounds | 1 |
| Review findings: real / noise / deferred | 4 / 0 / 1 (B-2) |
| Regressions introduced | 0 |
| Bugs escaped to production | 0 (henüz üretimde değil) |
