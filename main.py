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

bot = commands.Bot(command_prefix="-", intents=intents)
bot.remove_command('help')

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
        
        for child in self.children:
            child.disabled = True
        await self.message.edit(view=self)

        if selected_choice == self.correct_answer:
            await interaction.response.send_message(f"🎉 Correct, {interaction.user.mention}! You nailed it!")
        else:
            await interaction.response.send_message(f"❌ Incorrect, {interaction.user.mention}! The correct answer was choice **{self.correct_answer}**.")
        
        self.stop()

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
                await self.message.channel.send("⏰ Time's up! Nobody answered in time.")
            except discord.HTTPException:
                pass

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    
    # Rich Presence configuration (Listening Status)
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening, 
            name="prefix commands (-help) 🎧"
        )
    )

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

@bot.command()
async def time(ctx):
    current_timestamp = int(time_module.time())
    await ctx.send(f"⏰ **Your Local Time:** <t:{current_timestamp}:F>")

# Custom Help Command Embed (With added spacing for clean look)
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="🤖 Starry's N00b — Command Menu",
        description="Here is a full layout of my configuration! Active prefixes use `-`, while text triggers respond dynamically in regular chat.",
        color=0xFFD700
    )
    
    # Prefix Commands Section (Double line breaks added)
    embed.add_field(name="⚙️ Prefix Commands", value=(
        "`-help` ➜ Shows this helpful configuration list.\n\n"
        "`-play` ➜ Launches a 4-option trivia mini-game (15s cooldown).\n\n"
        "`-time` ➜ Displays the current time adjusted directly to your device.\n\n"
        "`-ping` ➜ Tests bot responsiveness with latency calculation.\n\n"
        "`-roll [sides]` ➜ Rolls a dice. Defaults to 6 sides.\n\n"
        "`-8ball [question]` ➜ Ask a question and receive a mystery prediction."
    ), inline=False)
    
    # Chat Trigger Words Section (Double line breaks added)
    embed.add_field(name="💬 Chat Trigger Words (No Prefix)", value=(
        "🗣️ Mention **\"starry\"** ➜ Custom master protective responses.\n\n"
        "❤️ Say **\"starry hates me\"** ➜ Bot replies: *\"No he doesn't\"*\n\n"
        "🛡️ Say **\"you hate me\"** ➜ Bot replies: *\"No I don't\"*\n\n"
        "✨ Say **\"cute\"** ➜ Bot replies with your custom creature emoji.\n\n"
        "🌈 Say **\"gay\"** ➜ Bot replies: *\"Yes, indeed Starry is gay\"*"
    ), inline=False)
    
    if bot.user.avatar:
        embed.set_footer(text="Built with ❤️ for Starry's server", icon_url=bot.user.avatar.url)
    else:
        embed.set_footer(text="Built with ❤️ for Starry's server")
        
    await ctx.send(embed=embed)

# Quiz Command
@bot.command()
async def play(ctx):
    global last_play_time
    current_time = time_module.time()
    
    if current_time - last_play_time < 15:
        cooldown_embed = discord.Embed(
            title="🤠 Whoa there!",
            description="Hold your horses partner, let me cool down a bit.",
            color=discord.Color.orange()
        )
        await ctx.send(embed=cooldown_embed)
        return

    last_play_time = current_time

    quiz = random.choice(QUIZ_QUESTIONS)
    
    choices_text = (
        f"**A)** {quiz['choices']['A']}\n"
        f"**B)** {quiz['choices']['B']}\n"
        f"**C)** {quiz['choices']['C']}\n"
        f"**D)** {quiz['choices']['D']}"
    )

    embed = discord.Embed(
        title="🧠 Trivia Time!",
        description=f"**{quiz['question']}**\n\n{choices_text}\n\n*Click your answer choice below within 15 seconds!*",
        color=0xFFD700
    )

    view = QuizView(correct_answer=quiz['correct'], original_author=ctx.author)
    view.message = await ctx.send(embed=embed, view=view)

# Custom Message Listener
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    content_lower = message.content.lower()
    clean_content = re.sub(r'<a?:[a-zA-Z0-9_]+:[0-9]+>', '', content_lower)

    # Trigger configurations
    if "starry hates me" in clean_content:
        await message.channel.send("No he doesn't")
    elif "you hate me" in clean_content:
        await message.channel.send("No I don't")
    elif "cute" in clean_content:
        # REPLACE THE STRING BELOW with your actual Discord emoji text code
        await message.channel.send("<:Cutestarry:1519456531173871686>")
    elif "gay" in clean_content:
        await message.channel.send("Yes, indeed Starry is gay")
    # General master mention check
    elif "starry" in clean_content:
        starry_responses = [
            "Who is it that dares cast their tongue upon my master?",
            "Who amongst you possesses the effrontery to utter my master’s name?",
            "Who dares breathe a word concerning my liege?",
            "Who assumes the audacity to speak of my master?"
        ]
        await message.channel.send(random.choice(starry_responses))

    await bot.process_commands(message)

# Run Background Tasks and Launch Bot
keep_alive()

token = os.getenv("DISCORD_TOKEN")
bot.run(token)
