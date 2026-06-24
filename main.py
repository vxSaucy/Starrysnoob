import discord
from discord.ext import commands
import random
import os
import re
import asyncio
from flask import Flask
from threading import Thread
import time as time_module

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

bot = commands.Bot(command_prefix="-", intents=intents)

# Expanded question bank for the -play command (20 total questions)
QUIZ_QUESTIONS = [
    {"question": "What is the capital of France?", "choices": ["A) London", "B) Berlin", "C) Paris", "D) Madrid"], "correct": "C"},
    {"question": "Which planet is known as the Red Planet?", "choices": ["A) Earth", "B) Mars", "C) Jupiter", "D) Venus"], "correct": "B"},
    {"question": "What is the largest ocean on Earth?", "choices": ["A) Atlantic Ocean", "B) Indian Ocean", "C) Arctic Ocean", "D) Pacific Ocean"], "correct": "D"},
    {"question": "How many colors are there in a rainbow?", "choices": ["A) 6", "B) 7", "C) 8", "D) 9"], "correct": "B"},
    {"question": "What sweet food do bees make?", "choices": ["A) Sugar", "B) Honey", "C) Syrup", "D) Chocolate"], "correct": "B"},
    {"question": "Which animal is known as the 'Ship of the Desert'?", "choices": ["A) Horse", "B) Camel", "C) Elephant", "D) Donkey"], "correct": "B"},
    {"question": "How many legs does a spider have?", "choices": ["A) 6", "B) 8", "C) 10", "D) 12"], "correct": "B"},
    {"question": "Which is the tallest animal on Earth?", "choices": ["A) Elephant", "B) Giraffe", "C) Dinosaur", "D) Ostrich"], "correct": "B"},
    {"question": "What is the freezing point of water?", "choices": ["A) 0°C", "B) 10°C", "C) 50°C", "D) 100°C"], "correct": "A"},
    {"question": "How many days are there in a normal year?", "choices": ["A) 360", "B) 364", "C) 365", "D) 366"], "correct": "C"},
    {"question": "What is the color of an emerald?", "choices": ["A) Blue", "B) Red", "C) Yellow", "D) Green"], "correct": "D"},
    {"question": "Which fast food chain features a smiling clown?", "choices": ["A) Burger King", "B) Wendy's", "C) McDonald's", "D) Subway"], "correct": "C"},
    {"question": "What is the hardest natural substance on Earth?", "choices": ["A) Gold", "B) Iron", "C) Diamond", "D) Stone"], "correct": "C"},
    {"question": "Which country is home to the kangaroo?", "choices": ["A) Canada", "B) Australia", "C) South Africa", "D) Brazil"], "correct": "B"},
    {"question": "How many letters are there in the English alphabet?", "choices": ["A) 24", "B) 25", "C) 26", "D) 27"], "correct": "C"},
    {"question": "Which fruit is traditionally given to teachers?", "choices": ["A) Banana", "B) Apple", "C) Orange", "D) Grape"], "correct": "B"},
    {"question": "What is the largest country in the world by land size?", "choices": ["A) Canada", "B) USA", "C) China", "D) Russia"], "correct": "D"},
    {"question": "What shape is a stop sign?", "choices": ["A) Hexagon", "B) Octagon", "C) Triangle", "D) Square"], "correct": "B"},
    {"question": "Which gaseous element do humans need to breathe to survive?", "choices": ["A) Nitrogen", "B) Carbon Dioxide", "C) Oxygen", "D) Hydrogen"], "correct": "C"},
    {"question": "Who painted the famous 'Mona Lisa'?", "choices": ["A) Vincent van Gogh", "B) Leonardo da Vinci", "C) Pablo Picasso", "D) Claude Monet"], "correct": "B"}
]

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

# --- PLAYFUL QUIZ COMMAND WITH COOLDOWN ---
@bot.command()
@commands.cooldown(1, 15, commands.BucketType.global)
async def play(ctx):
    quiz = random.choice(QUIZ_QUESTIONS)
    choices_text = "\n".join(quiz["choices"])
    
    embed = discord.Embed(
        title="🧠 Trivia Time!",
        description=f"**{quiz['question']}**\n\n{choices_text}\n\n*Type your answer (A, B, C, or D) in chat within 15 seconds!*",
        color=discord.Color.blue()
