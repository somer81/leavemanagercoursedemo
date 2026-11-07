# Spec 0002 — Giriş, oturum ve çıkış (arka yüz) + demo kullanıcıları

- Status: In progress
- Mode: lite
- Plan: `specs/plans/0002-plan.md`
- Self-critique: done

## Intent
Çalışan, Yönetici ve Admin kullanıcıları kendi hesaplarıyla giriş yapmalı ki sistem her istekte
kimin işlem yaptığını bilsin; izin talebi, onay ve bakiye gibi sonraki tüm özellikler buna dayanır.
Başarı: kullanıcı adı ve parolayla giriş yapılır, oturum girişten itibaren 8 saat geçerlidir,
kullanıcı çıkış yapabilir, giriş ve sağlık dışındaki her şey oturumsuz isteği reddeder ve kurs için
hazır demo kullanıcıları tek komutla oluşturulur. Bilinçli olarak yapılmayan: giriş ekranı (spec 0003),
rol bazlı yetki kuralları ve ekranlar (ilgili özelliklerin spec'lerinde), kayıt, parola sıfırlama,
e-posta, kaba kuvvet koruması.
Clarify kararları (somer81, 2026-11-07): seed komutu + `DEMO_PASSWORD`; mutlak 8 saat; çoklu oturum
serbest, çıkış yalnızca o oturumu bitirir; kullanıcı adı büyük-küçük harfe duyarsız, 3–32 karakter
`a-z 0-9 . _ -`; kaba kuvvet koruması backlog'a (B-6); B-5 bu spec'e girer.
Spec onayı (somer81, 2026-11-07): parola 5–128 karakter (12 kararının yerine; girişte ve seed'de);
statik sayfa dosyaları herkese açık; seed var olan kullanıcıları değiştirmez; giriş ekranı spec 0003'e bölündü.

## Requirements
- **R-1:** Kullanıcı, kullanıcı adı ve parolasıyla giriş yapar; giriş başarılıysa bir oturum açılır.
- **R-2:** Kullanıcı adı büyük-küçük harfe duyarsız eşleşir.
- **R-3:** Hatalı parola ile bilinmeyen kullanıcı adı aynı cevabı alır ("kullanıcı adı veya parola
  hatalı"); hangi bilginin yanlış olduğu belli edilmez ve oturum açılmaz.
- **R-4:** Biçim kurallarına uymayan kullanıcı adı veya parola girişi reddedilir. Kullanıcı adı 3–32
  karakter `a-z 0-9 . _ -`; parola 5–128 karakter.
- **R-5:** Oturumu olan kullanıcı kim olduğunu sorgulayabilir: görünen adı ve rolü döner.
- **R-6:** Oturum girişten itibaren tam 8 saat geçerlidir; kullanım süreyi uzatmaz. Süresi dolmuş
  oturumla yapılan istek "oturum sona erdi" olarak reddedilir.
- **R-7:** Çıkış yalnızca o anki oturumu sonlandırır; aynı kullanıcının diğer oturumları sürer.
- **R-8:** Varsayılan red: giriş ve sağlık dışındaki her API ucu oturum ister; herkese açık uçların
  listesi tam olarak bu ikisidir. Statik sayfa dosyaları (HTML/CSS/JS) herkese açıktır ve veri içermez.
- **R-9:** Parolalar düz metin olarak saklanmaz; hiçbir cevapta ve logda parola, parola özeti veya
  oturum anahtarı görünmez.
- **R-10:** Demo kullanıcıları tek bir komutla oluşturulur: 1 Admin, 1 Yönetici ve o yöneticiye bağlı
  2 Çalışan; isimler uydurmadır. Parola ortamdan alınır; eksik veya 5 karakterden kısaysa hiçbir
  kullanıcı oluşturulmaz. Komut tekrar çalıştırıldığında eksik kullanıcıları oluşturur; var olanları
  çoğaltmaz ve değiştirmez.

## User experience
none — no user interface. Giriş ekranı spec 0003'ün konusudur (Split, aşağıda).

## Constraints & out of scope
- **Sensitive area: Yetkilendirme** (oturum, varsayılan red) · **Sensitive area: Kişisel veri (KVKK)**
  (kullanıcı adı, görünen ad). Clarify kapısı lite'ta da soruldu; her kriter VERIFY'da kasıtlı bir
  bozmayla kanıtlanır; her fix round yeniden review edilir.
- `docs/security.md` AuthN/AuthZ ve Secrets kurallarına uyulur (parola özeti, sunucu tarafı oturum,
  cookie nitelikleri, demo parolası yalnızca ortamda).
- Saat bilgisi `Clock` bağımlılığından gelir; 8 saat sınırı deterministik test edilir.
- **Out of scope:** giriş ekranı ve güvenlik başlıkları (spec 0003, B-1), rol bazlı yetki kuralları,
  kayıt, parola sıfırlama/değiştirme, "her yerden çıkış", kaba kuvvet koruması / hesap kilitleme
  (backlog'a), e-posta.
- Split: proposed 0002 (arka yüz: giriş, oturum, çıkış, varsayılan red, seed) / 0003 (giriş ekranı +
  güvenlik başlıkları B-1); accepted — somer81, 2026-11-07, tam kapsam 16+ kriter.

## Acceptance criteria
- [ ] AC-1 — Doğru kullanıcı adı ve parolayla giriş bir oturum açar; bu oturumla kimlik sorgusu kullanıcının görünen adını ve rolünü döner.
- [ ] AC-2 — Kullanıcı adı farklı büyük-küçük harfle yazıldığında da giriş başarılı olur.
- [ ] AC-3 — Hatalı parola ve bilinmeyen kullanıcı adı, birebir aynı hata cevabını alır ("kullanıcı adı veya parola hatalı") ve oturum açılmaz.
- [ ] AC-4 — Biçim dışı girişler reddedilir ve oturum açılmaz: boş alan; 2 ve 33 karakterli kullanıcı adı; izin verilmeyen karakter içeren kullanıcı adı; 4 ve 129 karakterli parola. 3 ve 32 karakterli kullanıcı adları ile 5 ve 128 karakterli parolalar biçim olarak kabul edilir.
- [ ] AC-5 — Oturum girişten 7 saat 59 dakika 59 saniye sonra geçerlidir; tam 8 saat sonra yapılan istek "oturum sona erdi" olarak reddedilir.
- [ ] AC-6 — Çıkıştan sonra o oturumla yapılan istek reddedilir; aynı kullanıcının başka bir oturumu geçerli kalır.
- [ ] AC-7 — Oturumsuz, geçersiz veya süresi dolmuş oturumla korumalı bir uca yapılan istek reddedilir; oturumsuz erişilebilen API uçlarının listesi tam olarak giriş ve sağlıktır; statik sayfa dosyaları oturumsuz sunulur.
- [ ] AC-8 — Saklanan parola düz metin değildir; giriş, kimlik sorgusu, çıkış ve hata cevaplarında ve uygulama loglarında parola, parola özeti veya oturum anahtarı bulunmaz.
- [ ] AC-9 — Seed komutu 1 Admin, 1 Yönetici ve o yöneticiye bağlı 2 Çalışan oluşturur; her biri `DEMO_PASSWORD` ile giriş yapabilir.
- [ ] AC-10 — `DEMO_PASSWORD` yoksa veya 5 karakterden kısaysa seed komutu hata verir ve hiçbir kullanıcı oluşturmaz; komut ikinci kez (farklı bir `DEMO_PASSWORD` ile bile) çalıştırıldığında kullanıcı sayısı değişmez ve var olan kullanıcılar eski parolalarıyla giriş yapmaya devam eder.

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
