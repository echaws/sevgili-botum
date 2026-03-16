import os
import json
from datetime import datetime, date, time, timedelta, timezone
from pathlib import Path

import discord
from discord.ext import tasks
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent

# Local geliştirme için .env yükle (Railway'de env değişkenleri zaten geliyor)
load_dotenv(BASE_DIR / ".env")


TOKEN = os.getenv("DISCORD_TOKEN")
USER_A_ID = os.getenv("USER_A_ID")
USER_B_ID = os.getenv("USER_B_ID")
REL_START_DATE = os.getenv("REL_START_DATE")
DAILY_AT = os.getenv("DAILY_AT", "10:00")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN env değişkeni yok.")
if not USER_A_ID or not USER_B_ID:
    raise RuntimeError("USER_A_ID ve USER_B_ID env değişkenleri zorunlu.")
if not REL_START_DATE:
    raise RuntimeError("REL_START_DATE env değişkeni zorunlu (YYYY-MM-DD).")

USER_A_ID = int(USER_A_ID)
USER_B_ID = int(USER_B_ID)


def parse_rel_start(ymd: str) -> date:
    try:
        year, month, day = map(int, ymd.split("-"))
        return date(year, month, day)
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError("REL_START_DATE formatı YYYY-MM-DD olmalı.") from exc


REL_START = parse_rel_start(REL_START_DATE)


def parse_daily_at(value: str) -> time:
    parts = value.split(":")
    if len(parts) != 2:
        raise RuntimeError("DAILY_AT formatı HH:MM olmalı. Örn: 10:00")
    try:
        hh = int(parts[0])
        mm = int(parts[1])
    except ValueError as exc:  # noqa: BLE001
        raise RuntimeError("DAILY_AT formatı HH:MM olmalı. Örn: 10:00") from exc
    if not (0 <= hh <= 23 and 0 <= mm <= 59):
        raise RuntimeError("DAILY_AT 0-23 saat ve 0-59 dakika aralığında olmalı.")
    return time(hour=hh, minute=mm)


DAILY_TIME = parse_daily_at(DAILY_AT)


# ---- Storage (kelime istatistiği + günlük gönderim) ----

STATE_PATH = Path(
    os.getenv("STATE_PATH", os.getenv("DATA_DIR", str(BASE_DIR / "data" / "state.json")))
).resolve()
STATE_PATH.parent.mkdir(parents=True, exist_ok=True)


def load_state() -> dict:
    if not STATE_PATH.exists():
        return {"messages": [], "last_daily_sent": None}
    try:
        with STATE_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"messages": [], "last_daily_sent": None}


def save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with STATE_PATH.open("w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def append_message_log(user_id: int, text: str, created_at: datetime) -> None:
    state = load_state()
    arr = state.setdefault("messages", [])
    arr.append(
        {
            "user_id": user_id,
            "text": text or "",
            "created_at": created_at.isoformat(),
        }
    )
    if len(arr) > 5000:
        # En eski kayıtları sil
        del arr[: len(arr) - 5000]
    save_state(state)


def daily_key(d: date) -> str:
    return d.strftime("%Y-%m-%d")


def get_today_local() -> date:
    return datetime.now().date()


def relationship_stats() -> tuple[str, int, int]:
    today = get_today_local()
    total_days = (today - REL_START).days

    # Bu yılki yıldönümü
    this_year_anniv = date(today.year, REL_START.month, REL_START.day)
    if this_year_anniv <= today:
        next_anniv = date(today.year + 1, REL_START.month, REL_START.day)
    else:
        next_anniv = this_year_anniv

    days_to_next = (next_anniv - today).days

    start_str = REL_START.strftime("%d %B %Y")
    return start_str, total_days, days_to_next


# ---- İçerik (tatlı mesaj, soru, film) ----

SWEET_MESSAGES = [
    "Bugün birlikte bir şey yapmayı unutmayın :)",
    "Bugün birbirinize biraz daha fazla sarılma günü.",
    "Küçük bir mesaj bile büyük bir gün yapar. İyi ki varsın.",
    "Bugün bir anı biriktirelim: mini yürüyüş / kahve / film?",
    "Sıradan bir günü bile güzelleştiren sensin.",
    "Bugün 'biz' olduğumuz için güzel.",
    "Birlikteyken her şey daha kolay. Bugün de öyle olsun.",
    "Bugün bir teşekkür: iyi ki hayatımdasın.",
]

DAILY_QUESTIONS = [
    "Birlikte gitmek istediğiniz ülke neresi?",
    "Şu an birlikte yapabileceğiniz en basit mutluluk ne olurdu?",
    "Birbirinizde en sevdiğiniz küçük alışkanlık ne?",
    "İkiniz için 'mükemmel gün' nasıl başlar?",
    "Birlikte öğrenmek istediğiniz bir şey var mı?",
    "Bir sonraki mini randevunuzu nasıl planlardınız?",
    "Sizi en çok güldüren ortak anınız hangisi?",
    "Birlikte denemek istediğiniz yeni bir aktivite ne?",
]

MOVIES = [
    ("Interstellar", "Bilim Kurgu", "Birlikte izlemek için ideal :)"),
    ("About Time", "Romantik / Komedi", "Tatlı bir akşam filmi :)"),
    ("The Intern", "Komedi / Dram", "Rahat, keyifli ve sıcak."),
    ("Knives Out", "Gizem", "Birlikte tahmin oyunu oynayın."),
    ("Spider-Man: Into the Spider-Verse", "Animasyon", "Görsel şölen + iyi his."),
    ("The Martian", "Bilim Kurgu", "Eğlenceli ve sürükleyici."),
    ("La La Land", "Müzikal / Romantik", "Birlikte izleyip sonra konuşmalık."),
    ("Paddington 2", "Aile / Komedi", "İyi his garantili."),
]


def _daily_seed(d: date) -> int:
    return d.year * 10000 + d.month * 100 + d.day


def _simple_rng(seed: int) -> float:
    # Küçük deterministik RNG (0-1)
    x = (seed ^ 0x9E3779B97F4A7C15) & ((1 << 64) - 1)
    x ^= x >> 30
    x = (x * 0xBF58476D1CE4E5B9) & ((1 << 64) - 1)
    x ^= x >> 27
    x = (x * 0x94D049BB133111EB) & ((1 << 64) - 1)
    x ^= x >> 31
    return (x & ((1 << 53) - 1)) / float(1 << 53)


def pick_daily_sweet_message(d: date | None = None) -> str:
    if d is None:
        d = get_today_local()
    r = _simple_rng(_daily_seed(d))
    idx = int(r * len(SWEET_MESSAGES)) % len(SWEET_MESSAGES)
    return SWEET_MESSAGES[idx]


def pick_daily_question(d: date | None = None) -> str:
    if d is None:
        d = get_today_local()
    r = _simple_rng(_daily_seed(d) ^ 0x12345678)
    idx = int(r * len(DAILY_QUESTIONS)) % len(DAILY_QUESTIONS)
    return DAILY_QUESTIONS[idx]


def pick_daily_movie(d: date | None = None) -> tuple[str, str, str]:
    if d is None:
        d = get_today_local()
    r = _simple_rng(_daily_seed(d) ^ 0xABCDEF01)
    idx = int(r * len(MOVIES)) % len(MOVIES)
    return MOVIES[idx]


# ---- Kelime istatistiği ----

STOPWORDS_TR = {
    "ve",
    "ile",
    "ama",
    "fakat",
    "ancak",
    "ya",
    "da",
    "de",
    "mi",
    "mı",
    "mu",
    "mü",
    "ben",
    "sen",
    "o",
    "biz",
    "siz",
    "onlar",
    "bu",
    "şu",
    "çok",
    "az",
    "bir",
    "iki",
    "üç",
    "daha",
    "en",
    "gibi",
    "için",
    "kadar",
    "diye",
    "ne",
    "niye",
    "neden",
    "nasıl",
    "evet",
    "hayır",
    "ok",
    "tamam",
    "şey",
    "şeyi",
    "şeyler",
}


def tokenize_tr(text: str) -> list[str]:
    if not text:
        return []
    lowered = text.lower()
    # linkleri ve punctuation'ı sil
    import re  # noqa: PLC0415

    cleaned = re.sub(r"https?://\S+", " ", lowered)
    cleaned = re.sub(r"[^\wşŞıİçÇöÖüÜğĞ]+", " ", cleaned, flags=re.UNICODE)
    tokens = [t.strip() for t in cleaned.split() if t.strip()]
    out: list[str] = []
    for t in tokens:
        if len(t) < 3:
            continue
        if t in STOPWORDS_TR:
            continue
        out.append(t)
    return out


def top_words_from_state(limit: int = 10) -> list[tuple[str, int]]:
    state = load_state()
    messages = state.get("messages", [])
    counts: dict[str, int] = {}
    for m in messages:
        tokens = tokenize_tr(str(m.get("text", "")))
        for w in tokens:
            counts[w] = counts.get(w, 0) + 1
    items = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    return items[:limit]


# ---- Discord bot ----

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.dm_messages = True


class LoveBot(discord.Client):
    def __init__(self) -> None:
        super().__init__(intents=intents)
        self.allowed_ids = {USER_A_ID, USER_B_ID}
        self.daily_task.start()  # type: ignore[arg-type]

    async def on_ready(self) -> None:
        print(f"Bot giriş yaptı: {self.user} (ID: {self.user and self.user.id})")
        # Başlangıçta bir kere dene (deploy sonrası günü kaçırmasın)
        await self.maybe_send_daily()

    async def on_message(self, message: discord.Message) -> None:
        # Botun kendi mesajları
        if message.author.bot:
            return
        # Sadece DM kanalları
        if not isinstance(message.channel, discord.DMChannel):
            return
        if message.author.id not in self.allowed_ids:
            return

        text = message.content or ""
        append_message_log(message.author.id, text, message.created_at or datetime.now(timezone.utc))

        if not text.startswith("!"):
            return

        parts = text.strip().split(" ", maxsplit=1)
        command = parts[0].lower()
        arg_text = parts[1] if len(parts) > 1 else ""

        if command == "!mesaj":
            await self.handle_mesaj(message, arg_text)
        elif command == "!sayac":
            await message.channel.send(self.format_sayac())
        elif command == "!tatli":
            await message.channel.send(self.format_tatli())
        elif command == "!soru":
            await message.channel.send(self.format_soru())
        elif command == "!film":
            await message.channel.send(self.format_film())
        elif command == "!topkelime":
            await self.handle_topkelime(message, arg_text)
        else:
            await message.channel.send(
                "Komutlar:\n"
                "- `!mesaj <yazı>`\n"
                "- `!topkelime [n]`\n"
                "- `!tatli`\n"
                "- `!film`\n"
                "- `!sayac`\n"
                "- `!soru`"
            )

    async def handle_mesaj(self, message: discord.Message, arg_text: str) -> None:
        if not arg_text.strip():
            await message.channel.send("Kullanım: `!mesaj <yazı>`")
            return
        target_id = USER_B_ID if message.author.id == USER_A_ID else USER_A_ID
        user = await self.fetch_user(target_id)
        await user.send(arg_text.strip())

    async def handle_topkelime(self, message: discord.Message, arg_text: str) -> None:
        try:
            n = int(arg_text.strip()) if arg_text.strip() else 10
        except ValueError:
            n = 10
        n = max(3, min(30, n))
        top = top_words_from_state(limit=n)
        if not top:
            await message.channel.send("Henüz yeterli mesaj yok.")
            return
        lines = [f"{i+1}) {w} — {c}" for i, (w, c) in enumerate(top)]
        await message.channel.send("En çok kullanılan kelimeler:\n" + "\n".join(lines))

    def format_sayac(self) -> str:
        start_str, total_days, days_to_next = relationship_stats()
        return (
            f"Başlangıç: {start_str}\n"
            f"Toplam gün: {total_days}\n"
            f"Sonraki yıldönümüne: {days_to_next} gün"
        )

    def format_tatli(self) -> str:
        _, total_days, _ = relationship_stats()
        msg = pick_daily_sweet_message()
        return f"Bugün ilişkinizin {total_days}. günü\n{msg}"

    def format_soru(self) -> str:
        return f"Bugünün sorusu:\n{pick_daily_question()}"

    def format_film(self) -> str:
        title, genre, note = pick_daily_movie()
        return f"Film: {title}\nTür: {genre}\n{note}"

    async def maybe_send_daily(self) -> None:
        today = get_today_local()
        state = load_state()
        last = state.get("last_daily_sent")
        if last == daily_key(today):
            return
        payload = (
            self.format_tatli()
            + "\n\n"
            + self.format_soru()
            + "\n\n"
            + self.format_film()
        )

        for uid in (USER_A_ID, USER_B_ID):
            try:
                user = await self.fetch_user(uid)
                await user.send(payload)
            except Exception:
                # DM kapalı olabilir; sessiz geç
                continue

        state["last_daily_sent"] = daily_key(today)
        save_state(state)

    @tasks.loop(minutes=1)
    async def daily_task(self) -> None:
        now = datetime.now()
        target_today = datetime.combine(now.date(), DAILY_TIME)
        # 5 dakika tolerans penceresi
        window_start = target_today
        window_end = target_today + timedelta(minutes=4)
        if window_start <= now <= window_end:
            await self.maybe_send_daily()


def main() -> None:
    client = LoveBot()
    client.run(TOKEN)


if __name__ == "__main__":
    main()

