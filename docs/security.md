# Security

> Bootstrap 2026-11-07'de karara bağlandı. Ajanlar her plan ve review'da bu kurallara uyar.

## Secrets
- Secrets never enter the repo, specs, prompts, or chat. `.env` is gitignored; provide `.env.example`.
- Agents never print secret values, even when debugging.
- Demo kullanıcı parolaları kodda değil `.env` içindedir (`DEMO_PASSWORD`); repoda yalnızca `.env.example`.

## Input & output
- Sınır doğrulaması API katmanında Pydantic şemalarıyla (tip, uzunluk, tarih biçimi); iş kuralı
  doğrulaması serviste.
- Tüm SQL parametrelidir.
- Frontend kullanıcı verisini DOM'a yalnızca `textContent` ile yazar; `innerHTML` yasaktır (XSS).
- Güvenlik başlıkları: `Content-Security-Policy: default-src 'self'`, `X-Content-Type-Options: nosniff`,
  `Referrer-Policy: same-origin`.
- CSRF: `SameSite=Strict` oturum cookie'si; durum değiştiren uçlar yalnızca `application/json` kabul eder.
- Hata cevapları `docs/conventions.md` "Error handling" biçimindedir; stack trace, SQL, dosya yolu
  veya kişisel veri sızmaz.
- **KVKK:** loglara isim veya izin gerekçesi yazılmaz, yalnızca ID; test ve seed verisi uydurmadır.

## AuthN / AuthZ
- **AuthN:** kullanıcı adı + parola. Parolalar `hashlib.scrypt` + kullanıcı başına salt ile saklanır;
  düz parola asla. Sunucu tarafı oturum: `secrets.token_urlsafe` token, SQLite'ta saklanır; cookie
  `HttpOnly`, `SameSite=Strict`, production'da `Secure`; 8 saatte geçersiz olur, çıkışta silinir.
  Giriş hatası tek mesaj: "kullanıcı adı veya parola hatalı".
- **AuthZ (hassas alan):** varsayılan red — oturum gerektirmeyen uçlar yalnızca giriş
  (`/api/auth/login`) ve sağlık (`/api/health`, yalnızca durum alanları döner; spec 0001 R-3); diğer her uç oturum ister.
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
