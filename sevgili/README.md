# ❤️ Sevgili Botu (Discord)

Bu bot, çiftler için özel olarak hazırlanmış bir Discord botudur. Sevgililik yıl dönümü sayacı, rastgele film önerileri ve birbirinize gizli mesaj gönderme özellikleri sunar.

## Özellikler

- **Yıl Dönümü Sayacı:** Her sabah saat 09:00'da yıl dönümüne kaç gün kaldığını her iki kullanıcıya da DM yoluyla bildirir.
- **Rastgele Film Önerileri:** Günün belirlenmiş saatlerinde (12:00, 15:00, 18:00, 21:00) her iki kullanıcıya da rastgele film önerileri gönderir.
- **Gizli Mesaj Komutu:** `!mesaj <mesajınız>` komutu ile partnerinize bot üzerinden mesaj gönderebilirsiniz. Komutu kullandığınız kanal temizlenir (mesajınız silinir) ve mesaj sadece partnerinize gider.

## Kurulum ve Çalıştırma

### 1. Discord Bot Oluşturma
- [Discord Developer Portal](https://discord.com/developers/applications) adresine gidin.
- "New Application" butonuna tıklayarak yeni bir uygulama oluşturun.
- "Bot" sekmesine geçin, bir isim ve avatar belirleyin.
- **Privileged Gateway Intents** bölümünden `Message Content Intent` seçeneğini aktif edin.
- Bot token'ınızı kopyalayın.

### 2. CSV ve ID'leri Alma
- Discord'da "Ayarlar -> Gelişmiş -> Geliştirici Modu"nu aktif edin.
- Kendi üzerinize sağ tıklayıp "Kullanıcı Kimliğini Kopyala" diyerek kendi ID'nizi alın.
- Partnerinizin üzerine sağ tıklayıp onun da ID'sini alın.

### 3. Yerel Kurulum
- `.env` dosyasını açın ve şu bilgileri doldurun:
  - `DISCORD_TOKEN`: Kopyaladığınız bot token'ı.
  - `USER_ID_1`: Kendi Discord ID'niz.
  - `USER_ID_2`: Partnerinizin Discord ID'niz.
  - `ANNIVERSARY_DATE`: Yıl dönümü tarihiniz (`YYYY-AA-GG` formatında, örn: `2023-01-01`).

### 4. Railway ve GitHub Deployment
- Bu projeyi bir GitHub deposuna (repository) yükleyin.
- [Railway.app](https://railway.app/) adresine gidin.
- Yeni bir proje oluşturun ve "Deploy from GitHub repo" seçeneğini seçin.
- GitHub deponuzu bağlayın.
- Railway panelinde "Variables" sekmesine gidin ve `.env` dosyanızdaki değişkenleri (`DISCORD_TOKEN`, `USER_ID_1`, vb.) buraya tek tek ekleyin.
- Railway otomatik olarak projeyi algılayacak ve `python main.py` komutuyla botu çalıştıracaktır.

## Bağımlılıklar
- `discord.py`
- `python-dotenv`
- `apscheduler`
