import discord
from discord.ext import commands
import random

# Setup intents
intents = discord.Intents.default()
intents.message_content = True  # Allows the bot to read messages

# Define the command prefix (e.g., !ping)
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    print("------")

# Command 1: Simple Ping
@bot.command()
async def ping(ctx):
    """Responds with Pong!"""
    await ctx.send("🏓 Pong!")

# Command 2: Magic 8-Ball
@bot.command(name="8ball")
async def eight_ball(ctx, *, question: str):
    """Ask the magic 8-ball a question."""
    responses = [
        "It is certain.", "Reply hazy, try again.", "Don't count on it.",
        "Without a doubt.", "Ask again later.", "My sources say no.",
        "Yes definitely.", "Better not tell you now.", "Outlook not so good.",
        "Signs point to yes.", "Concentrate and ask again.", "Very doubtful."
    ]
    reply = random.choice(responses)
    await ctx.send(f"🔮 **Question:** {question}\n🎱 **Answer:** {reply}")

# Command 3: Roll a Die
@bot.command()
async def roll(ctx, sides: int = 6):
    """Rolls a die. Defaults to 6 sides."""
    result = random.randint(1, sides)
    await ctx.send(f"🎲 You rolled a **{result}** (1-{sides})!")

# Command 4: Roast/Rate a user
@bot.command()
async def rate(ctx, user: discord.Member = None):
    """Rates how cool a user is."""
    user = user or ctx.author
    rating = random.randint(0, 100)
    
    if rating < 30:
        comment = "Yikes... absolute gremlin energy. 💀"
    elif rating < 70:
        comment = "Pretty average. Not bad, not amazing. 😐"
    else:
        comment = "Absolute legend status! 🔥"
        
    await ctx.send(f"📊 **{user.display_name}** is **{rating}%** cool. {comment}")

# Run the bot (We use an environment variable for safety on cloud hosting)
import os
token = os.getenv("DISCORD_TOKEN")
bot.run(token)
