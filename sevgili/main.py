import discord
from discord.ext import commands, tasks
import os
import json
import random
from datetime import datetime, date
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
USER1_ID = int(os.getenv('USER_ID_1'))
USER2_ID = int(os.getenv('USER_ID_2'))
ANNIVERSARY_DATE_STR = os.getenv('ANNIVERSARY_DATE')

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Load movies
with open('movies.json', 'r') as f:
    MOVIES = json.load(f)

def get_days_until_anniversary():
    anniversary_date = datetime.strptime(ANNIVERSARY_DATE_STR, '%Y-%m-%d').date()
    today = date.today()
    
    # Get the next anniversary occurrence
    next_anniversary = anniversary_date.replace(year=today.year)
    if next_anniversary < today:
        next_anniversary = next_anniversary.replace(year=today.year + 1)
    
    delta = next_anniversary - today
    return delta.days

async def send_anniversary_message():
    days_left = get_days_until_anniversary()
    message = f"❤️ Günaydın! Sevgililik yıl dönümümüze tam **{days_left}** gün kaldı! Seni çok seviyorum. ❤️"
    
    user1 = await bot.fetch_user(USER1_ID)
    user2 = await bot.fetch_user(USER2_ID)
    
    await user1.send(message)
    await user2.send(message)

async def send_random_movie():
    movie = random.choice(MOVIES)
    message = f"🎬 Rastgele Film Önerisi: **{movie}**. Bu akşam izlemeye ne dersin? 🍿"
    
    user1 = await bot.fetch_user(USER1_ID)
    user2 = await bot.fetch_user(USER2_ID)
    
    await user1.send(message)
    await user2.send(message)

@bot.event
async def on_ready():
    print(f'Bot {bot.user.name} olarak giriş yaptı!')
    
    # Setup Scheduler
    scheduler = AsyncIOScheduler()
    
    # Daily anniversary countdown at 09:00
    scheduler.add_job(send_anniversary_message, CronTrigger(hour=9, minute=0))
    
    # Random movie suggestions (e.g., 3-5 times a day at random times)
    # For simplicity, we can schedule them at specific times OR keep adding jobs
    times = ["12:00", "15:00", "18:00", "21:00"]
    for t in times:
        h, m = map(int, t.split(':'))
        scheduler.add_job(send_random_movie, CronTrigger(hour=h, minute=m))
        
    scheduler.start()

@bot.command(name='mesaj')
async def send_private_message(ctx, *, message_content):
    # Determine the recipient
    if ctx.author.id == USER1_ID:
        recipient_id = USER2_ID
    elif ctx.author.id == USER2_ID:
        recipient_id = USER1_ID
    else:
        return # Only defined users can use this
    
    recipient = await bot.fetch_user(recipient_id)
    await recipient.send(f"💌 **{ctx.author.name}** sana bir mesaj gönderdi:\n\n{message_content}")
    await ctx.message.delete() # Hide the command
    await ctx.author.send("Mesajın başarıyla gönderildi! ✅", delete_after=5)

if __name__ == "__main__":
    bot.run(TOKEN)
