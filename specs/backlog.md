# Backlog — deferred findings

Findings a human triaged as **defer**: real, but fixed later by decision (`workflows/feature-development.md`,
step 7). Nothing lands here without that decision; noise is rejected in the triage record, not parked here.

- A criterion moved out at the ship gate (R-08, `→ moved to B-<n>`) lands here too, by the
  human's ship decision; the entry names the spec and criterion.
- One entry per finding, newest last. Delete the entry in the commit of the work that closes it.
- An entry that grows into new behavior becomes a spec (`specs/active/`), not a fix.

<!-- Format (labels stay English):
- **B-<n>** — <finding, one line> — Source: spec <NNNN>, review round <n> (<file:line>) — Severity: <…>
  — Recommendation: <the reviewer's action> — Deferred by: <name>, <YYYY-MM-DD>, <why>
  A decision deferred at bootstrap (its REPORT) uses Source: bootstrap <YYYY-MM-DD>.
-->

- **B-1** — Güvenlik başlıkları (`Content-Security-Policy: default-src 'self'`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: same-origin`; `docs/security.md` "Input & output") henüz uygulanmadı — Source: spec 0001, plan risk R6 — Severity: Medium
  — Recommendation: oturum/giriş spec'inde (Yetkilendirme hassas alanı) entegrasyon testiyle ekle — Deferred by: somer81, 2026-11-07, walking skeleton kapsamı dışında (spec'te kriter yok)

- **B-2** — starlette 1.x `TestClient`, httpx ile kullanımda `StarletteDeprecationWarning` veriyor ("install httpx2 instead") — Source: spec 0001, review round 1 (`requirements.lock`: starlette 1.10.0 + httpx 0.28.1) — Severity: Info
  — Recommendation: httpx2'ye geçişi ayrı bir bağımlılık kararı olarak planla (`docs/security.md` Dependencies) — Deferred by: somer81, 2026-11-07, bugün bir şey kırmıyor; walking skeleton kapsamı dışında

- **B-3** — ANEW betikleri (`scripts/check`, `doctor`, `residue`) macOS `/bin/sh` (bash 3.2) ile ayrıştırılamıyor; geçici çözüm `dash` + residue için `sh → dash` PATH (`docs/conventions.md` Known traps) — Source: bootstrap 2026-11-07 — Severity: Medium
  — Recommendation: upstream issue'yu aç (metin bootstrap raporunda: engindemirog/ai-native-engineering-workspace); düzeltme içeren bir ANEW sürümüne yükseltince Known traps satırını ve README'deki dash notunu kaldır — Deferred by: somer81, 2026-11-07, upstream düzeltmesi bekleniyor
- **B-4** — Entegrasyon adımı ~0 s sürüyor; bootstrap'taki "entegrasyon full-only" varsayımı ölçüldü (medyan: full 2 s, fast 1 s) — Source: spec 0001, BUILD adım 5 — Severity: Info
  — Recommendation: entegrasyon suite'i büyüyüp bir dakikaya yaklaşana kadar `integration` adımını `[fast]` yapmayı değerlendir; seçici ayrımı (`-m integration`) korunur — Deferred by: somer81, 2026-11-07, profil kararı ayrı ve küçük bir değişiklik
- **B-5** — AC-3 testi oturumsuz erişimi yalnızca olumlu yönden kanıtlıyor (henüz oturum yok); "giriş ve sağlık dışındaki her uç oturumsuz reddedilir" negatif kapsamı yok — Source: spec 0001, review round 1 (Tests notu) — Severity: Info
  — Recommendation: oturum/giriş spec'inde (Yetkilendirme hassas alanı) herkese açık uçların tam listesini doğrulayan bir test ekle (B-1 ile birlikte) — Deferred by: somer81, 2026-11-07, oturum mekanizması bu spec'in kapsamı dışında
