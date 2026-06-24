import discord
from discord.ext import commands
import random
import os
from flask import Flask
from threading import Thread

# 1. Create a tiny background web server so Railway/Render stays happy
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. Your actual Bot Code
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

# Standard Prefix Commands
@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong!")

@bot.command(name="8ball")
async def eight_ball(ctx, *, question: str):
    responses = ["It is certain.", "Reply hazy, try again.", "Don't count on it.", "Without a doubt.", "My sources say no.", "Yes definitely."]
    await ctx.send(f"🔮 **Question:** {question}\n**Answer:** {random.choice(responses)}")

@bot.command()
async def roll(ctx, sides: int = 6):
    await ctx.send(f"🎲 You rolled a **{random.randint(1, sides)}**!")

# --- Custom Message Listener ---
@bot.event
async def on_message(message):
    # Prevent the bot from replying to itself
    if message.author == bot.user:
        return

    # Convert sentence to lowercase so it catches "Starry", "STARRY", etc.
    content_lower = message.content.lower()

    # Check if the word "starry" is anywhere in the sentence
    if "starry" in content_lower:
        await message.channel.send("Who dares speaks about my master's name")

    # CRUCIAL: This allows your normal prefix commands (!ping, !roll, etc.) to keep working!
    await bot.process_commands(message)

# Start the web server right before launching the bot
keep_alive()

token = os.getenv("DISCORD_TOKEN")
bot.run(token)
