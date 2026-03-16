# sevgili-dm-bot (Python)

İki kişi için DM botu (Discord, Python):
- `!mesaj <yazı>`: yazdığını **diğer kişiye** DM atar (kullanana atmaz)
- `!topkelime [n]`: en çok kullanılan kelimeler (DM’e yazdıklarınızdan)
- `!tatli`: bugünün tatlı mesajı + ilişki gününüz
- `!film`: birlikte film önerisi
- `!sayac`: başlangıç, toplam gün, sonraki yıldönümüne kalan gün
- `!soru`: bugünün sorusu

Bot hem **sunucuya ekli** olabilir hem de **sadece DM** üzerinden çalışır; komutları DM’den yazmanız yeterli.

## Kurulum (local, Windows)

1) Python 3.11+ kurulu olsun.

2) Bu klasörde sanal ortam isteğe bağlı:
```bash
python -m venv venv
venv\Scripts\activate
```

3) Bağımlılıkları yükle:
```bash
pip install -r requirements.txt
```

4) `.env.example` dosyasını `.env` yapıp doldurun:
- **DISCORD_TOKEN**
- **USER_A_ID**, **USER_B_ID**
- **REL_START_DATE** (örn: `2025-03-12`)
- **DAILY_AT** (örn: `10:00`)
- (opsiyonel) **STATE_PATH** (örn: `C:\Users\...\sevgili\data\state.json`)

5) Çalıştırın:
```bash
python bot.py
```

## Discord (sunucuya ekleme)

Bot DM üzerinden çalışır ama botu bir sunucuya eklemen için Discord Developer Portal tarafında ayarlar gerekir:

- **Privileged Gateway Intents**:
  - **Message Content Intent**: AÇIK (DM komutlarını okumak için)
- **Bot Permissions**:
  - Minimumda **Send Messages** ve **Read Message History** yeterli (DM için).

Sunucuya eklemek için “OAuth2 → URL Generator” kısmında:
- Scopes: **bot**
- Permissions: (en az) **Send Messages**

## Railway Deploy (Python)

1. Projeyi GitHub’a yükle (bu klasörün tamamı, `.env` HARİÇ).
2. Railway’de yeni proje oluştur → “Deploy from GitHub Repo”.

### Variables (Railway)

Railway → Variables kısmına ekle:
- **DISCORD_TOKEN**
- **USER_A_ID**
- **USER_B_ID**
- **REL_START_DATE** (örn `2025-03-12`)
- **DAILY_AT** (örn `10:00`)

> Not: Repoda `runtime.txt` ve `nixpacks.toml` olduğu için Railway otomatik **Python 3.11** ile build eder.
> Bu yüzden `NIXPACKS_PYTHON_VERSION` gibi ekstra bir variable eklemene gerek yok.

### Kalıcı veri (kelime istatistiği kaybolmasın)

Railway’de dosya sistemi genelde kalıcı değildir; bu yüzden volume önerilir.

- Railway’de bir **Volume** (Disk) ekle ve mount path’i örn: `/data` yap.
- Variables’a şunu ekle:
  - **STATE_PATH**=`/data/state.json`

Bu sayede `!topkelime` için tutulan geçmiş restart sonrası da kalır.

### Start command

Railway otomatik olarak Python ortamını kurup `requirements.txt`’i görecektir.

Start komutu:
- Railway settings → Start command: `python bot.py`

## Notlar

- Bot, sadece `.env` / env değişkenlerindeki iki kullanıcıdan gelen DM’leri dinler.
- Kelime istatistiği, bota DM’den yazdığınız mesajlardan (komutlar dahil) hesaplanır.
- Günlük tatlı mesaj + günlük soru + film önerisi, `DAILY_AT` saatine yakın bir anda **iki kişiye de** DM olarak gider.

# sevgili-dm-bot

İki kişi için DM botu:
- `!mesaj <yazı>`: yazdığını **diğer kişiye** DM atar (kullanana atmaz)
- `!topkelime [n]`: en çok kullanılan kelimeler (DM’e yazdıklarınızdan)
- `!tatli`: bugünün tatlı mesajı + ilişki gününüz
- `!film`: birlikte film önerisi
- `!sayac`: başlangıç, toplam gün, sonraki yıldönümüne kalan gün
- `!soru`: bugünün sorusu

## Kurulum

1) Node.js 18+ kurulu olsun.

2) Bu klasörde:

```bash
npm install
```

3) `.env.example` dosyasını `.env` yapıp doldurun:
- **DISCORD_TOKEN**
- **USER_A_ID**, **USER_B_ID**
- **REL_START_DATE** (örn: `2025-03-12`)
- **DAILY_AT** (örn: `10:00`)

4) Çalıştırın:

```bash
npm start
```

## Discord (sunucuya ekleme)

Bot DM üzerinden çalışır ama botu bir sunucuya eklemen için Discord Developer Portal tarafında ayarlar gerekir:

- **Privileged Gateway Intents**:
  - **Message Content Intent**: AÇIK (DM komutlarını okumak için)
- **Bot Permissions**:
  - Minimumda **Send Messages** ve **Read Message History** yeterli (DM için).

Sunucuya eklemek için “OAuth2 → URL Generator” kısmında:
- Scopes: **bot**
- Permissions: (en az) **Send Messages**

## Railway Deploy

Bu proje Railway’de iki şekilde deploy olur: Nixpacks (otomatik) veya Dockerfile.

### 1) Railway’de proje oluştur

- GitHub’a projeyi koy (veya Railway “Deploy from repo” kullan).
- Railway’de yeni proje oluşturup repoyu bağla.

### 2) Environment Variables (Railway)

Railway → Variables kısmına ekle:
- **DISCORD_TOKEN**
- **USER_A_ID**
- **USER_B_ID**
- **REL_START_DATE** (örn `2025-03-12`)
- **DAILY_AT** (örn `10:00`)

### 3) Kalıcı veri (kelime istatistiği kaybolmasın)

Railway’de dosya sistemi genelde kalıcı değildir; bu yüzden volume önerilir.

- Railway’de bir **Volume** (Disk) ekle ve mount path’i örn: `/data` yap.
- Variables’a şunu ekle:
  - **STATE_PATH**=`/data/state.json`

Bu sayede `!topkelime` için tutulan geçmiş restart sonrası da kalır.

### 4) Start command

Railway otomatik olarak `npm start` çalıştırır (package.json içinde hazır).

## Notlar

- Bot, sadece `.env` içindeki iki kullanıcıdan gelen DM’leri dinler.
- Kelime istatistiği, bota DM’den yazdığınız mesajlardan (komutlar dahil) hesaplanır.
- Günlük tatlı mesaj ve günlük soru, `DAILY_AT` saatinde **iki kişiye de** DM olarak gider.

