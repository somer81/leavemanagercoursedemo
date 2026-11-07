# Security

> Bootstrap 2026-11-07'de karara bağlandı. Ajanlar her plan ve review'da bu kurallara uyar.

## Secrets
- Secrets never enter the repo, specs, prompts, or chat. `.env` is gitignored; provide `.env.example`.
- Agents never print secret values, even when debugging.
- Demo kullanıcı parolaları kodda değil `.env` içindedir (`DEMO_PASSWORD`); repoda yalnızca `.env.example`.

## Input & output
- Sınır doğrulaması API katmanında Pydantic şemalarıyla (tip, tarih biçimi); iş kuralı ve biçim
  kuralı doğrulaması serviste. Kimlik bilgisi biçim/uzunluk kurallarının (kullanıcı adı, parola)
  tek kaynağı servis katmanıdır; Pydantic yalnızca tipleri denetler (spec 0002, A-3).
- Tüm SQL parametrelidir.
- Frontend kullanıcı verisini DOM'a yalnızca `textContent` ile yazar; `innerHTML` yasaktır (XSS).
- Güvenlik başlıkları: `Content-Security-Policy: default-src 'self'`, `X-Content-Type-Options: nosniff`,
  `Referrer-Policy: same-origin`.
- CSRF: `SameSite=Strict` oturum cookie'si; durum değiştiren uçlar yalnızca `application/json` kabul eder.
- Hata cevapları `docs/conventions.md` "Error handling" biçimindedir; stack trace, SQL, dosya yolu
  veya kişisel veri sızmaz.
- **KVKK:** loglara isim veya izin gerekçesi yazılmaz, yalnızca ID; test ve seed verisi uydurmadır.

## AuthN / AuthZ
- **AuthN:** kullanıcı adı + parola. Kullanıcı adı 3–32 karakter `a-z 0-9 . _ -`, büyük-küçük harfe
  duyarsız; parola 5–128 karakter (spec 0002). Parolalar `hashlib.scrypt` + kullanıcı başına salt ile
  saklanır; düz parola asla; bilinmeyen kullanıcıda da sahte bir doğrulama yapılır (zamanlama farkı
  olmasın). Sunucu tarafı oturum: `secrets.token_urlsafe` token; SQLite'ta yalnızca SHA-256 özeti
  saklanır. Token yalnızca `session` cookie'sinde taşınır (`HttpOnly`, `SameSite=Strict`, `Path=/`;
  `Secure` yalnızca `LEAVE_COOKIE_SECURE=1` ile — production'da zorunlu); girişten itibaren mutlak
  8 saat geçerli, çıkışta silinir. Giriş hatası tek mesaj: "kullanıcı adı veya parola hatalı".
- **AuthZ (hassas alan):** varsayılan red — oturum gerektirmeyen uçlar yalnızca giriş
  (`/api/auth/login`) ve sağlık (`/api/health`, yalnızca durum alanları döner; spec 0001 R-3); diğer her
  API ucu oturum ister. Yapısal: `backend/app/main.py`'de açık uçlar adıyla izin listesindedir, diğer
  her router `protected` router'ın altına (`dependencies=[Depends(require_session)]`) eklenir — asla
  doğrudan uygulamaya. `backend/tests/integration/test_default_deny.py` rota ağacını yürüyerek
  (gizli rotalar dahil) herkese açık listenin tam olarak bu ikisi olduğunu denetler. Statik sayfa dosyaları (HTML/CSS/JS) herkese açıktır ve
  veri içermez.
  Yetki kontrolü **yalnızca servis katmanında**. Çalışan yalnızca kendi verisini görür; Yönetici
  yalnızca kendi ekibinin taleplerini görür ve onaylar/reddeder; Admin izin türlerini ve hakları
  yönetir, talep onaylamaz; kimse kendi talebini onaylayamaz (BR-4). Başkasının kaydına erişim 403.

## Dependencies
- Yeni bağımlılık yalnızca onaylanmış bir planda gerekçesiyle listelenirse eklenir; plan onayı
  bağımlılık onayıdır.
- Kontrol: izin verici lisans (MIT, BSD, Apache-2.0), son 12 ayda aktif bakım, ekleme anında
  `pip-audit` / `npm audit` temiz. Önce standart kütüphane.
- Sürümler lock dosyasında sabittir (`requirements.lock`, `package-lock.json`).
- `pip-audit` ağ ister; `scripts/check` içinde değil, bağımlılık eklenirken ve (kurulursa) CI'da çalışır.

## Review lens
Security is a mandatory dimension of every independent review (see `prompts/review.md`), not a
separate afterthought phase.
