import discord
from discord.ext import commands
import random
import os
import re
import asyncio
from flask import Flask
from threading import Thread
import time as time_module

# 1. Background web server for hosting stability
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. Discord Bot Setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Required for changing nicknames

bot = commands.Bot(command_prefix="-", intents=intents)
bot.remove_command('help')

# Store AFK data: {user_id: {"original_name": str, "reason": str}}
afk_users = {}

# Track the last time someone ran the -play command globally
last_play_time = 0

# Expanded question bank mapping keys directly to options
QUIZ_QUESTIONS = [
    {"question": "What is the capital of France?", "choices": {"A": "London", "B": "Berlin", "C": "Paris", "D": "Madrid"}, "correct": "C"},
    {"question": "Which planet is known as the Red Planet?", "choices": {"A": "Earth", "B": "Mars", "C": "Jupiter", "D": "Venus"}, "correct": "B"},
    {"question": "What is the largest ocean on Earth?", "choices": {"A": "Atlantic Ocean", "B": "Indian Ocean", "C": "Arctic Ocean", "D": "Pacific Ocean"}, "correct": "D"},
    {"question": "How many colors are there in a rainbow?", "choices": {"A": "6", "B": "7", "C": "8", "D": "9"}, "correct": "B"},
    {"question": "What sweet food do bees make?", "choices": {"A": "Sugar", "B": "Honey", "C": "Syrup", "D": "Chocolate"}, "correct": "B"},
    {"question": "Which animal is known as the 'Ship of the Desert'?", "choices": {"A": "Horse", "B": "Camel", "C": "Elephant", "D": "Donkey"}, "correct": "B"},
    {"question": "How many legs does a spider have?", "choices": {"A": "6", "B": "8", "C": "10", "D": "12"}, "correct": "B"},
    {"question": "Which is the tallest animal on Earth?", "choices": {"A": "Elephant", "B": "Giraffe", "C": "Dinosaur", "D": "Ostrich"}, "correct": "B"},
    {"question": "What is the freezing point of water?", "choices": {"A": "0°C", "B": "10°C", "C": "50°C", "D": "100°C"}, "correct": "A"},
    {"question": "How many days are there in a normal year?", "choices": {"A": "360", "B": "364", "C": "365", "D": "366"}, "correct": "C"},
    {"question": "What is the color of an emerald?", "choices": {"A": "Blue", "B": "Red", "C": "Yellow", "D": "Green"}, "correct": "D"},
    {"question": "Which fast food chain features a smiling clown?", "choices": {"A": "Burger King", "B": "Wendy's", "C": "McDonald's", "D": "Subway"}, "correct": "C"},
    {"question": "What is the hardest natural substance on Earth?", "choices": {"A": "Gold", "B": "Iron", "C": "Diamond", "D": "Stone"}, "correct": "C"},
    {"question": "Which country is home to the kangaroo?", "choices": {"A": "Canada", "B": "Australia", "C": "South Africa", "D": "Brazil"}, "correct": "B"},
    {"question": "How many letters are there in the English alphabet?", "choices": {"A": "24", "B": "25", "C": "26", "D": "27"}, "correct": "C"},
    {"question": "Which fruit is traditionally given to teachers?", "choices": {"A": "Banana", "B": "Apple", "C": "Orange", "D": "Grape"}, "correct": "B"},
    {"question": "What is the largest country in the world by land size?", "choices": {"A": "Canada", "B": "USA", "C": "China", "D": "Russia"}, "correct": "D"},
    {"question": "What shape is a stop sign?", "choices": {"A": "Hexagon", "B": "Octagon", "C": "Triangle", "D": "Square"}, "correct": "B"},
    {"question": "Which gaseous element do humans need to breathe to survive?", "choices": {"A": "Nitrogen", "B": "Carbon Dioxide", "C": "Oxygen", "D": "Hydrogen"}, "correct": "C"},
    {"question": "Who painted the famous 'Mona Lisa'?", "choices": {"A": "Vincent van Gogh", "B": "Leonardo da Vinci", "C": "Pablo Picasso", "D": "Claude Monet"}, "correct": "B"},
    {"question": "In Minecraft, what do you feed a wolf to tame it?", "choices": {"A": "Fish", "B": "Raw Porkchop", "C": "Bone", "D": "Apple"}, "correct": "C"},
    {"question": "Which game popularised the phrase 'Where we droppin' boys?'", "choices": {"A": "PUBG Mobile", "B": "Fortnite", "C": "Apex Legends", "D": "Call of Duty"}, "correct": "B"},
    {"question": "What is the name of the classic, default map in PUBG?", "choices": {"A": "Sanhok", "B": "Miramar", "C": "Livik", "D": "Erangel"}, "correct": "D"},
    {"question": "Which company created the famous Mario character?", "choices": {"A": "SEGA", "B": "Nintendo", "C": "Sony", "D": "Microsoft"}, "correct": "B"},
    {"question": "What is the default skin name for the male character in Minecraft?", "choices": {"A": "Steve", "B": "Alex", "C": "Jonesy", "D": "Creeper"}, "correct": "A"},
    {"question": "How many infinity stones are there in the Marvel Cinematic Universe?", "choices": {"A": "4", "B": "5", "C": "6", "D": "7"}, "correct": "C"},
    {"question": "Which mythical creature is known as a horse with a single horn?", "choices": {"A": "Pegasus", "B": "Unicorn", "C": "Griffin", "D": "Dragon"}, "correct": "B"},
    {"question": "What is the main ingredient in a traditional Margherita pizza?", "choices": {"A": "Pepperoni", "B": "Mushrooms", "C": "Pineapple", "D": "Basil and Mozzarella"}, "correct": "D"},
    {"question": "Which video game platform uses a digital store known as 'Steam'?", "choices": {"A": "PlayStation", "B": "PC", "C": "Xbox", "D": "Nintendo Switch"}, "correct": "B"},
    {"question": "What color do you get when you mix blue and yellow paint together?", "choices": {"A": "Green", "B": "Purple", "C": "Orange", "D": "Brown"}, "correct": "A"},
    {"question": "What is the maximum number of players in a standard battle royale match in PUBG Mobile?", "choices": {"A": "50", "B": "60", "C": "100", "D": "150"}, "correct": "C"},
    {"question": "Which of these shotguns in PUBG Mobile can equip an AR magazine?", "choices": {"A": "S12K", "B": "S1897", "C": "S686", "D": "DBS"}, "correct": "A"},
    {"question": "In Fortnite, what material has the highest health when fully built?", "choices": {"A": "Wood", "B": "Stone", "C": "Metal", "D": "Gold"}, "correct": "C"},
    {"question": "What is the name of the smaller, fast-paced 2x2km snow and grass map in PUBG Mobile?", "choices": {"A": "Vikendi", "B": "Livik", "C": "Sanhok", "D": "Karakin"}, "correct": "B"},
    {"question": "How many players are in a standard Fortnite squad?", "choices": {"A": "2", "B": "3", "C": "4", "D": "5"}, "correct": "C"},
    {"question": "What is the chemical symbol for gold?", "choices": {"A": "Gd", "B": "Go", "C": "Ag", "D": "Au"}, "correct": "D"},
    {"question": "Which popular streaming platform features a purple logo?", "choices": {"A": "YouTube", "B": "Twitch", "C": "Kick", "D": "TikTok"}, "correct": "B"},
    {"question": "Which language is primarily used to code Discord bots using discord.py?", "choices": {"A": "JavaScript", "B": "Python", "C": "C++", "D": "HTML"}, "correct": "B"},
    {"question": "In the movie 'The Lion King', what kind of animal is Pumbaa?", "choices": {"A": "Meerkat", "B": "Warthog", "C": "Baboon", "D": "Hyena"}, "correct": "B"},
    {"question": "What is the name of the main villain in the Star Wars original trilogy?", "choices": {"A": "Darth Vader", "B": "Kylo Ren", "C": "Darth Maul", "D": "General Grievous"}, "correct": "A"}
]

# Button View Class for the Quiz
class QuizView(discord.ui.View):
    def __init__(self, correct_answer, original_author):
        super().__init__(timeout=15.0)
        self.correct_answer = correct_answer
        self.original_author = original_author
        self.message = None
        for label in ["A", "B", "C", "D"]:
            button = discord.ui.Button(label=label, style=discord.ButtonStyle.grey, custom_id=label)
            button.callback = self.button_callback
            self.add_item(button)

    async def button_callback(self, interaction: discord.Interaction):
        if interaction.user != self.original_author:
            await interaction.response.send_message("This isn't your game session, partner! 🤠", ephemeral=True)
            return
        selected_choice = interaction.data["custom_id"]
        for child in self.children: child.disabled = True
        await self.message.edit(view=self)
        if selected_choice == self.correct_answer:
            await interaction.response.send_message(f"🎉 Correct, {interaction.user.mention}! You nailed it!")
        else:
            await interaction.response.send_message(f"❌ Incorrect, {interaction.user.mention}! The correct answer was choice **{self.correct_answer}**.")
        self.stop()

    async def on_timeout(self):
        for child in self.children: child.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
                await self.message.channel.send("⏰ Time's up! Nobody answered in time.")
            except discord.HTTPException: pass

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="prefix commands (-help) 🎧"))

# --- Commands ---

@bot.command()
async def afk(ctx, *, reason: str = "AFK"):
    # Save original name and change it
    afk_users[ctx.author.id] = {
        "original_name": ctx.author.display_name,
        "reason": reason
    }
    try:
        new_nick = f'¡AFK "{reason}!"'
        await ctx.author.edit(nick=new_nick)
        await ctx.send(f"✅ You are now AFK: **{reason}**")
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to change your nickname!")

@bot.command()
async def ping(ctx): await ctx.send("🏓 Pong!")

@bot.command(name="8ball")
async def eight_ball(ctx, *, question: str):
    responses = ["It is certain.", "Reply hazy, try again.", "Don't count on it.", "Without a doubt.", "My sources say no.", "Yes definitely."]
    await ctx.send(f"🔮 **Question:** {question}\n**Answer:** {random.choice(responses)}")

@eight_ball.error
async def eight_ball_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("🔮 **Please ask a question!** Example: `-8ball Is this bot awesome?`")

@bot.command()
async def roll(ctx, sides: int = 6): await ctx.send(f"🎲 You rolled a **{random.randint(1, sides)}**!")

@bot.command()
async def time(ctx):
    current_timestamp = int(time_module.time())
    await ctx.send(f"⏰ **Your Local Time:** <t:{current_timestamp}:F>")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def delete(ctx, amount):
    def is_not_pinned(m): return not m.pinned
    if amount.lower() == 'all':
        deleted = await ctx.channel.purge(limit=1000, check=is_not_pinned)
        await ctx.send(f"🧹 Nuked {len(deleted)-1} messages (pinned messages were kept safe!)", delete_after=5)
    else:
        try:
            num = int(amount)
            deleted = await ctx.channel.purge(limit=num + 1, check=is_not_pinned)
            await ctx.send(f"🧹 Cleaned up {len(deleted)-1} messages (skipped pins).", delete_after=5)
        except ValueError: await ctx.send("❌ Please provide a valid number or use `-delete all`.")

@delete.error
async def delete_error(ctx, error):
    if isinstance(error, commands.MissingPermissions): await ctx.send("❌ You don't have permission to manage messages, partner!")
    elif isinstance(error, commands.MissingRequiredArgument): await ctx.send("🔢 Please specify how many messages to delete! Example: `-delete 5` or `-delete all`.")

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="🤖 Starry's N00b — Command Menu", description="Active prefixes use `-`.", color=0xFFD700)
    embed.add_field(name="⚙️ Prefix Commands", value=(
        "`-help` ➜ Shows this list.\n`-play` ➜ Trivia.\n`-time` ➜ Local time.\n`-ping` ➜ Latency.\n"
        "`-roll [sides]` ➜ Dice.\n`-8ball [q]` ➜ Prediction.\n`-delete [#/all]` ➜ Clean.\n`-afk [reason]` ➜ Set AFK."
    ), inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def play(ctx):
    global last_play_time
    if time_module.time() - last_play_time < 15:
        await ctx.send("🤠 Hold your horses, let me cool down.")
        return
    last_play_time = time_module.time()
    quiz = random.choice(QUIZ_QUESTIONS)
    view = QuizView(correct_answer=quiz['correct'], original_author=ctx.author)
    view.message = await ctx.send(embed=discord.Embed(title="🧠 Trivia Time!", description=f"**{quiz['question']}**", color=0xFFD700), view=view)

# --- Event Listeners ---

@bot.event
async def on_message(message):
    if message.author == bot.user: return

    # AFK Logic: Mention detection
    if message.mentions:
        for user in message.mentions:
            if user.id in afk_users:
                await message.channel.send(f"⚠️ WOAH THERE, {user.display_name} is AFK: **{afk_users[user.id]['reason']}**")

    # AFK Logic: Remove on return
    if message.author.id in afk_users:
        data = afk_users.pop(message.author.id)
        try:
            await message.author.edit(nick=data["original_name"])
            await message.channel.send(f"👋 Welcome back, {message.author.mention}!", delete_after=5)
        except discord.Forbidden: pass

    if message.content.startswith("-"):
        await bot.process_commands(message)
        return

    # Chat Triggers
    content_lower = message.content.lower()
    if "starry hates me" in content_lower: await message.channel.send("No he doesn't")
    elif "gay" in content_lower: await message.channel.send("Yes, indeed Starry is gay")
    elif "starry" in content_lower: await message.channel.send("Who dares speak my master's name?")

keep_alive()
token = os.getenv("DISCORD_TOKEN")
bot.run(token)
