# Conventions

> Bootstrap 2026-11-07'de karara bağlandı. Buradaki her kural ya araçla zorlanır (tercih edilen)
> ya da review'da denetlenir.

## Language
- Chat language (interviews, sessions): Türkçe (`tr`)
- Document language (docs/, specs, plans, ADRs, review and verify reports): Türkçe (`tr`)
- Always English (protocol, not prose): ANEW core files, template headings and field labels,
  `Status:` values (Draft / Approved / In progress / Shipped), `Approved by / on:`, `Source:`.
- Code identifiers, branch names, commit messages: İngilizce. API alanları ve DB kolonları da
  İngilizce. Kullanıcıya görünen arayüz metinleri ve hata mesajları Türkçe.
- Agent messages (handoff summaries, refusals, `Next:` lines): chat language; command names, file
  paths and protocol fields verbatim.

## Language & framework versions
- Python **3.13** (CPython). venv açıkça `python3.13 -m venv .venv` ile kurulur.
- FastAPI (0.1xx) + Uvicorn, Pydantic 2.x.
- Veritabanı: SQLite, standart kütüphane `sqlite3`; ORM yok. Şema: `backend/app/repositories/schema.sql`.
- Frontend: build adımı olmadan framework'süz HTML/CSS/ES modules; modern evergreen tarayıcılar.
- Test: pytest 9.x (≥ 9.0.3; 8.x PYSEC-2026-1845 taşır) + FastAPI `TestClient`; frontend için Node ≥ 22 `node --test` + jsdom.
- Araçlar: ruff (lint + format), mypy `--strict`, import-linter.
- Bağımlılıklar `pyproject.toml` (major sabit) + `requirements.lock` (tam sürümler); frontend dev
  bağımlılığı `package.json` + `package-lock.json`. Kesin sürümler walking skeleton PLAN'ında seçilir.

## Naming
- Python: modül/fonksiyon `snake_case`, sınıf `PascalCase`, sabit `UPPER_CASE` (PEP 8, ruff).
- JS: dosya `kebab-case.js`, değişken/fonksiyon `camelCase`; CSS sınıfları `kebab-case`.
- API yolları çoğul isim: `/api/leave-requests/{id}/approve`; JSON alanları `snake_case`.
- Domain terimlerinin kod karşılıkları `docs/domain.md` sözlüğündedir (`balance`, `entitlement`,
  `RequestStatus.PENDING/APPROVED/REJECTED/CANCELLED`).
- Testler `test_<davranış>`; bir iş kuralını kanıtlayan test adında taşır:
  `test_br2_request_exceeding_balance_is_rejected`.

## Error handling
- Servis katmanı iş kuralı ihlalinde `DomainError` alt sınıfları fırlatır (`app.domain`):
  `InsufficientBalance`, `OverlappingRequest`, `NotAuthorized`, `NotFound`, `InvalidTransition`.
- API katmanında **tek** exception handler (`backend/app/api/errors.py`) bunları eşler: 422 kural
  ihlali / biçim hatası (`INVALID_INPUT`), 401 kimlik yok (`INVALID_CREDENTIALS`, `UNAUTHENTICATED`,
  `SESSION_EXPIRED`), 403 yetkisiz (başkasının verisi), 404 bulunamadı, 409 çakışma / geçersiz durum
  geçişi, 415 JSON olmayan durum değiştiren istek (GET/HEAD/OPTIONS dışı), 503 veri deposuna
  erişilemiyor (`DATA_STORE_UNAVAILABLE`), 500 beklenmeyen hata (`INTERNAL_ERROR`). Doğrulama hatası (`INVALID_INPUT`) gönderilen değeri asla geri
  yansıtmaz (FastAPI'nin varsayılan 422 gövdesi parolayı yansıtır).
- Hata gövdesi her zaman: `{"error": {"code": "INSUFFICIENT_BALANCE", "message": "<Türkçe mesaj>"}}`.
  Tek istisna: sağlık ucu bir hata değil durum raporudur; sorunlu durumda 503 ile
  `{"status": "unavailable", "database": "unavailable"}` döner (spec 0001).
- Kullanıcıya stack trace, SQL, dosya yolu veya başka bir çalışanın verisi asla sızmaz. Beklenmeyen
  hata → 500 + genel mesaj; ayrıntı yalnızca sunucu logunda, kişisel veri içermeden (`docs/security.md`).
- SQLite hataları (`backend/app/repositories/connection.py`): yalnızca erişilebilirlik hataları
  (bağlantı açılamıyor, `OperationalError`, tam tipi `DatabaseError` olanlar — "file is not a
  database", bozuk dosya) ERROR seviyesinde loglanıp `DataStoreUnavailable` (503) olur.
  `IntegrityError` ve `DatabaseError`'ın diğer alt sınıfları bir hata ya da iş kuralı ihlalidir:
  maskelenmez, yayılır → 500 + log (spec 0002 review round 2 N-2, round 3 N3-1). Bir iş kuralı kısıtı (ör. çakışma) serviste
  kendi `DomainError`'ına çevrilir, 503'e değil.

## Data rules
- İzin tarihleri saatsiz `date`, ISO 8601 `YYYY-MM-DD`; saat dilimine göre kaymaz.
- Zaman damgaları (oluşturulma, onay) UTC, ISO 8601.
- Gün sayıları `int`; yarım gün yok.
- ID'ler SQLite `INTEGER PRIMARY KEY`.
- Durumlar Python `Enum`; DB'de metin olarak saklanır.
- "Bugün" bilgisi servise bir `Clock` bağımlılığıyla verilir; servis ve repository'de doğrudan
  `date.today()` / `datetime.now()` çağrısı yasaktır.
- Tüm SQL parametrelidir; string birleştirme veya f-string ile SQL yasaktır.

## Known traps
- SQLite foreign key'leri varsayılan kapalıdır — her bağlantıda `PRAGMA foreign_keys = ON` — from bootstrap 2026-11-07.
- Her `:memory:` bağlantısı ayrı, boş bir veritabanıdır — test başına tek bağlantı açıp şemayı ona yükle, FastAPI dependency override ile uygulamaya ver — from bootstrap 2026-11-07.
- `sqlite3` bağlantıyı başka thread'den kullanmayı reddeder, `TestClient` ayrı thread'de çalışır — test bağlantısında `check_same_thread=False` — from bootstrap 2026-11-07.
- `sqlite3`'ün varsayılan tarih adapter'ları Python 3.12'den beri deprecated — tarihleri repository'de açıkça ISO metne ve geri çevir, `detect_types` kullanma — from bootstrap 2026-11-07.
- Makinedeki varsayılan `python3` anaconda'nınkidir — venv'i `python3.13 -m venv .venv` ile kur, check her zaman `.venv/bin/python -m …` çağırır — from bootstrap 2026-11-07.
- `app.openapi()` `include_in_schema=False` rotaları göstermez; FastAPI 0.16x `include_router` ise `app.routes`'a düz rota değil sarmalayıcı (`original_router`) ekler ve `original_router.routes` yolları include önekini içermez (`include_context.prefix`) — güvenlik amaçlı rota taramasında rota ağacını önekleri biriktirerek yürü (`backend/tests/integration/test_default_deny.py`) — from spec 0002 review round 1 F-1, round 2 N-1.
- Starlette'te `Exception` handler'ı `ServerErrorMiddleware`'de çalışır: zarfı döndükten sonra istisnayı yeniden fırlatır, uvicorn da traceback'i ayrıca loglar (500'ler iki kez loglanır); testte `TestClient(..., raise_server_exceptions=False)` kullan, istisna mesajına kişisel veri koyma — from spec 0002 review round 3 N3-3.
- macOS'ta `/bin/sh` bash 3.2'dir ve ANEW betiklerini ayrıştıramaz (`$( … )` içindeki `case` dalları, syntax error) — bu makinede `dash ./scripts/check` (`--fast`), `dash ./scripts/doctor`, `dash ./scripts/residue` kullan; residue check'i içeride `sh` ile çağırır, bu yüzden PATH'in başına `sh → /bin/dash` symlink'i olan bir dizin koy (`PATH="<dizin>:$PATH" dash ./scripts/residue`); CI (Ubuntu, sh = dash) etkilenmez; çekirdek betikler yerelde yamanmaz, upstream'e bildirildi — from bootstrap 2026-11-07.

## Enforced by tooling
`scripts/check.conf` adımları (spec 0001):
- ruff: PEP 8 isimlendirme, import sırası, format, güvenlik kuralları (`S`); satır 100 karakter.
  N818 kapalı: domain hata adları bu belgede sabit (`InsufficientBalance`…).
- mypy `--strict`: tip doğruluğu.
- import-linter: `docs/architecture.md` yasak bağımlılıklar 1–4 (`pyproject.toml` sözleşmeleri).
- pytest `--strict-markers`: tanımsız marker hata verir (eski Known traps maddesi).
