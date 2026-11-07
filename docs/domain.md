# Domain

> Bootstrap 2026-11-07'de karara bağlandı. İş, insanlar ve ajanlar arasındaki ortak dil.
> Bir terim burada yoksa ajan ona kendi anlamını uydurur.

## Ubiquitous language

| Term | Meaning | Notes / not to be confused with |
|---|---|---|
| Çalışan (`Employee`) | İzin talep eden kişi; tam olarak bir yöneticiye bağlıdır. | Kullanıcı hesabı değildir; rol hesaptan ayrıdır. |
| Yönetici (`Manager`) | Kendi ekibindeki çalışanların taleplerini onaylayan/reddeden çalışan. | Admin değildir. |
| İK/Admin (`Admin`) | İzin türlerini ve yıllık hakları tanımlar; talep onaylamaz. | Yönetici değildir. |
| İzin türü (`LeaveType`) | Yıllık, Mazeret, Ücretsiz vb.; bakiyeden düşüp düşmediği türe bağlıdır. | |
| İzin hakkı (`Entitlement`) | Bir çalışanın bir takvim yılında bir izin türü için toplam gün sayısı. | Bakiye değildir. |
| Bakiye (`balance`) | Hak − onaylanmış günler − bekleyen günler; kullanılabilir gün sayısı. | Hak değildir. |
| İzin talebi (`LeaveRequest`) | Bir çalışanın bir tarih aralığı ve izin türü için başvurusu. | |
| Talep durumu (`RequestStatus`) | `PENDING` (Beklemede) → `APPROVED` (Onaylandı) / `REJECTED` (Reddedildi); çalışan ayrıca `CANCELLED` (İptal edildi) yapabilir. | Spec'lerdeki `Status:` protokol alanı değildir. |
| İş günü | Hafta sonu ve tanımlı resmi tatil dışındaki gün; talep süresi iş günüyle ölçülür. | Takvim günü değildir. |
| Resmi tatil (`PublicHoliday`) | İş günü hesabından düşülen tanımlı tarih. | |

## Business rules
- **BR-1:** Talep süresi, başlangıç ve bitiş dahil, aralıktaki iş günü sayısıdır.
- **BR-2:** Bakiyeden düşen bir türde talep süresi mevcut bakiyeyi aşamaz; aşan talep oluşturulamaz.
- **BR-3:** Aynı çalışanın `PENDING` veya `APPROVED` talepleri tarih olarak çakışamaz.
- **BR-4:** Talebi yalnızca çalışanın kendi yöneticisi onaylayabilir veya reddedebilir; kimse kendi
  talebini onaylayamaz.
- **BR-5:** Reddetmek gerekçe ister.
- **BR-6:** Çalışan, başlangıç tarihi gelmemiş `PENDING` veya `APPROVED` talebini iptal edebilir;
  günler bakiyeye geri döner.
- **BR-7:** `REJECTED` ve `CANCELLED` son durumlardır; o talep bir daha değişmez.
- **BR-8:** Başlangıç tarihi bitiş tarihinden sonra olamaz; geçmiş tarihe talep açılamaz.
- **BR-9:** Haklar takvim yılı bazındadır; yıllar arası devir yoktur.

Bilinçli olarak yok (ileride ayrı spec): yarım gün izin, yıl devri, vekil onaycı, resmi tatil
yönetim ekranı.

## Key domain invariants
- Bakiye hiçbir zaman negatif olmaz.
- Bir çalışanın bir yıl ve türdeki onaylanmış günleri toplamı hakkı aşmaz.

## Sensitive areas
- **Yetkilendirme** — kimin hangi talebi onaylayıp reddedebileceği (BR-4) ve kimin hangi çalışanın
  verisini görebileceği. Hata, kendi iznini onaylamaya veya başkasının verisini görmeye yol açar.
- **Kişisel veri (KVKK)** — çalışan adı, izin geçmişi, izin gerekçesi (özel nitelikli veri
  içerebilir). Loglara, hata mesajlarına ve test fixture'larına gerçek veri girmez.

Bakiye hesabı hassas alan değildir; invariant'lar ve normal testlerle korunur.
