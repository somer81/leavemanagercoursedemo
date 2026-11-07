# Architecture

> Bootstrap 2026-11-07'de karara bağlandı. Ajanlar planlamadan önce bu dosyayı okur.

## System overview
İzin Yöneticisi tek süreçte çalışan bir web uygulamasıdır: FastAPI hem JSON API'yi (`/api/...`) hem
de framework'süz statik frontend'i sunar. Stil **klasik katmanlı (n-layer) mimaridir**: Sunum →
API → Servis → Repository, tüm katmanların kullandığı saf bir Domain katmanıyla. Veri tek bir SQLite
veritabanında tutulur. Gerekçe: bu boyuttaki bir kurs demosu için en tanıdık ve yeterli yapı;
modüler monolit bilinçli olarak seçilmedi (bootstrap kararı). Kompozisyon kökleri — katman dışında,
katmanları birbirine bağlayan tek yerler — `backend/app/main.py` (sunucu) ve `backend/app/seed.py`
(demo kullanıcıları komutu). Giriş noktası `backend/app/main.py`
katmanları birbirine bağlar ve statik dosyaları sunar.

## Modules / components and ownership

| Module | Single responsibility | Owns |
|---|---|---|
| Sunum — `frontend/` | Tarayıcı arayüzü (statik HTML, CSS, ES modules); veriyi yalnızca JSON API'den alır | Veri yok |
| API — `backend/app/api/` | FastAPI router'ları, istek/cevap şemaları (Pydantic), domain istisnalarını HTTP'ye eşleme, oturumdan kimliği alma | HTTP sözleşmesi |
| Servis — `backend/app/services/` | İş kuralları BR-1…BR-9, yetki kontrolü, iş günü hesabı; repository'leri Protocol arayüzü üzerinden kullanır | İş mantığı |
| Repository — `backend/app/repositories/` | `sqlite3` ile parametreli düz SQL; satırları domain nesnelerine çevirme | Tablolar, `schema.sql` |
| Domain — `backend/app/domain/` | Saf veri tipleri ve enum'lar (Employee, LeaveRequest, RequestStatus…), domain istisnaları | Davranış ve bağımlılık yok |

Testler: `backend/tests/unit/`, `backend/tests/integration/`, `frontend/tests/` (`docs/testing.md`).

## Communication rules
- Katmanlar arası iletişim aynı süreçte doğrudan fonksiyon çağrısıdır; event, kuyruk ya da mesaj yok.
- Her istek API → Servis → Repository yolunu izler; frontend backend'e yalnızca `/api/...` HTTP
  uçlarıyla erişir.
- Yetki kontrolü yalnızca servis katmanında yapılır; API katmanı kimliği servise iletir.

## Forbidden dependencies (make them testable)
import-linter sözleşmeleriyle `scripts/check` içinde denetlenir (1–4); 5 review'da denetlenir.
1. **Tek yön:** `app.api` → `app.services` → `app.repositories`. Alttaki katman üsttekini import etmez.
2. **Katman atlanmaz:** `app.api`, `app.repositories` paketini import etmez.
3. `app.services` paketi `fastapi` ve `sqlite3` import etmez.
4. `app.domain` hiçbir `app.*` katmanını ve hiçbir üçüncü taraf framework'ü (`fastapi`, `pydantic`,
   `sqlite3`) import etmez; tüm katmanlar `app.domain` paketini kullanabilir.
5. Frontend sunucu tarafı şablon kullanmaz; HTML statiktir, veri yalnızca JSON API'den gelir.

## Deliberately out of scope
Mikroservisler, arka plan işleri ve kuyruklar, önbellek, çoklu kiracı (multi-tenant), e-posta
bildirimi, takvim senkronizasyonu, bordro entegrasyonu, frontend build adımı.
