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

# Cleaned up question bank for the quiz
QUIZ_QUESTIONS = [
    {"question": "What is the capital of France?", "choices": ["London", "Berlin", "Paris", "Madrid"], "correct": "Paris"},
    {"question": "Which planet is known as the Red Planet?", "choices": ["Earth", "Mars", "Jupiter", "Venus"], "correct": "Mars"},
    {"question": "What is the largest ocean on Earth?", "choices": ["Atlantic Ocean", "Indian Ocean", "Arctic Ocean", "Pacific Ocean"], "correct": "Pacific Ocean"},
    {"question": "How many colors are there in a rainbow?", "choices": ["6", "7", "8", "9"], "correct": "7"},
    {"question": "What sweet food do bees make?", "choices": ["Sugar", "Honey", "Syrup", "Chocolate"], "correct": "Honey"},
    {"question": "Which animal is known as the 'Ship of the Desert'?", "choices": ["Horse", "Camel", "Elephant", "Donkey"], "correct": "Camel"},
    {"question": "How many legs does a spider have?", "choices": ["6", "8", "10", "12"], "correct": "8"},
    {"question": "Which is the tallest animal on Earth?", "choices": ["Elephant", "Giraffe", "Dinosaur", "Ostrich"], "correct": "Giraffe"},
    {"question": "What is the freezing point of water?", "choices": ["0°C", "10°C", "50°C", "100°C"], "correct": "0°C"},
    {"question": "How many days are there in a normal year?", "choices": ["360", "364", "365", "366"], "correct": "365"},
    {"question": "What is the color of an emerald?", "choices": ["Blue", "Red", "Yellow", "Green"], "correct": "Green"},
    {"question": "Which fast food chain features a smiling clown?", "choices": ["Burger King", "Wendy's", "McDonald's", "Subway"], "correct": "McDonald's"},
    {"question": "What is the hardest natural substance on Earth?", "choices": ["Gold", "Iron", "Diamond", "Stone"], "correct": "Diamond"},
    {"question": "Which country is home to the kangaroo?", "choices": ["Canada", "Australia", "South Africa", "Brazil"], "correct": "Australia"},
    {"question": "How many letters are there in the English alphabet?", "choices": ["24", "25", "26", "27"], "correct": "26"},
    {"question": "Which fruit is traditionally given to teachers?", "choices": ["Banana", "Apple", "Orange", "Grape"], "correct": "Apple"},
    {"question": "What is the largest country in the world by land size?", "choices": ["Canada", "USA", "China", "Russia"], "correct": "Russia"},
    {"question": "What shape is a stop sign?", "choices": ["Hexagon", "Octagon", "Triangle", "Square"], "correct": "Octagon"},
    {"question": "Which gaseous element do humans need to breathe to survive?", "choices": ["Nitrogen", "Carbon Dioxide", "Oxygen", "Hydrogen"], "correct": "Oxygen"},
    {"question": "Who painted the famous 'Mona Lisa'?", "choices": ["Vincent van Gogh", "Leonardo da Vinci", "Pablo Picasso", "Claude Monet"], "correct": "Leonardo da Vinci"}
]

# Button View Class for the Quiz
class QuizView(discord.ui.View):
    def __init__(self, correct_answer, original_author):
        super().__init__(timeout=15.0)
        self.correct_answer = correct_answer
        self.original_author = original_author
        self.message = None

        for label in ["A", "B", "C", "D"]:
            button = discord.ui.Button(label=label, style=discord.ButtonStyle.blurple, custom_id=label)
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

# Custom Help Command Embed
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="🤖 Starry's N00b — Command Menu",
        description="Here is a full list of everything I can do! Make sure to prefix everything with `-`.",
        color=discord.Color.teal()
    )
    embed.add_field(name="`-help`", value="Shows this helpful menu layout.", inline=False)
    embed.add_field(name="`-play`", value="Launches a fun, 4-option trivia mini-game with buttons (15s cooldown).", inline=False)
    embed.add_field(name="`-time`", value="Displays the current time adjusted directly to your screen's timezone.", inline=False)
    embed.add_field(name="`-ping`", value="Tests bot latency with a classic pong response.", inline=False)
    embed.add_field(name="`-roll [sides]`", value="Rolls a dice. Defaults to 6 sides if left blank.", inline=False)
    embed.add_field(name="`-8ball [question]`", value="Ask a magic question and receive a mysterious prediction.", inline=False)
    
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
    prefixes = ["A", "B", "C", "D"]
    
    formatted_choices = [f"**{prefixes[i]}** - {quiz['choices'][i]}" for i in range(4)]
    choices_text = "\n".join(formatted_choices)
    
    correct_index =
