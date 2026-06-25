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

# --- Global Databases & Configurations ---
# ⚠️ REPLACE THIS WITH YOUR ACTUAL DISCORD ID (e.g., 123456789012345678)
OWNER_ID = 711196330105503824  

user_credits = {}       # Stores {user_id: credit_amount}
earn_cooldowns = {}     # Stores {user_id: last_earn_timestamp}
last_play_time = 0      # Track the last time someone ran the -play command globally

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

# --- Helper Functions and Classes for Blackjack ---

SUITS = ['♠️', '♥️', '♦️', '♣️']
VALUES = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

def create_deck():
    deck = [{'value': v, 'suit': s} for v in VALUES for s in SUITS]
    random.shuffle(deck)
    return deck

def calculate_hand(hand):
    total = 0
    aces = 0
    for card in hand:
        if card['value'] in ['J', 'Q', 'K']:
            total += 10
        elif card['value'] == 'A':
            aces += 1
            total += 11
        else:
            total += int(card['value'])
            
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total

def format_hand(hand, hide_first=False):
    if hide_first:
        return f"🃏,  {hand[1]['value']}{hand[1]['suit']}"
    return ",  ".join([f"{c['value']}{c['suit']}" for c in hand])

class BlackjackView(discord.ui.View):
    def __init__(self, author, bet):
        super().__init__(timeout=60.0)
        self.author = author
        self.bet = bet
        self.deck = create_deck()
        self.player_hand = [self.deck.pop(), self.deck.pop()]
        self.dealer_hand = [self.deck.pop(), self.deck.pop()]
        self.doubled = False
        self.message = None

    def make_embed(self, title="🎰 Blackjack Table", description="Choose your action!", color=0x3498db, show_dealer=False):
        p_total = calculate_hand(self.player_hand)
        
        if show_dealer:
            d_total = calculate_hand(self.dealer_hand)
            d_cards = format_hand(self.dealer_hand)
        else:
            d_total = "?"
            d_cards = format_hand(self.dealer_hand, hide_first=True)

        embed = discord.Embed(title=title, description=description, color=color)
        embed.add_field(name=f"Dealer's Hand (Total: {d_total})", value=f"`{d_cards}`", inline=False)
        embed.add_field(name=f"{self.author.display_name}'s Hand (Total: {p_total})", value=f"`{format_hand(self.player_hand)}`", inline=False)
        
        footer_text = f"💰 Active Bet: {self.bet} credits"
        if self.doubled:
            footer_text += " | Double Down active!"
        embed.set_footer(text=footer_text)
        return embed

    async def check_initial_blackjack(self):
        p_total = calculate_hand(self.player_hand)
        d_total = calculate_hand(self.dealer_hand)
        
        if p_total == 21 and d_total == 21:
            user_credits[self.author.id] += self.bet  # Return bet
            await self.end_game("Push!", "Both you and the dealer got Blackjack! Bet returned.", 0x7f8c8d)
            return True
        elif p_total == 21:
            payout = int(self.bet * 2.5) # Natural Blackjack pays 3:2
            user_credits[self.author.id] += payout
            await self.end_game("💥 Blackjack!", f"You hit Natural 21! You win `{payout}` credits!", 0x2ecc71)
            return True
        elif d_total == 21:
            await self.end_game("❌ Dealer Blackjack!", "The dealer has Natural 21. You lost your bet!", 0xe74c3c)
            return True
        return False

    async def end_game(self, status, reason, color):
        for child in self.children:
            child.disabled = True
        embed = self.make_embed(title=status, description=reason, color=color, show_dealer=True)
        await self.message.edit(embed=embed, view=self)
        self.stop()

    async def dealer_turn(self):
        while calculate_hand(self.dealer_hand) < 17:
            self.dealer_hand.append(self.deck.pop())
            
        p_score = calculate_hand(self.player_hand)
        d_score = calculate_hand(self.dealer_hand)

        if d_score > 21:
            user_credits[self.author.id] += self.bet * 2
            await self.end_game("🎉 Dealer Busted!", f"Dealer rolled over 21 with a `{d_score}`. You won `{self.bet * 2}` credits!", 0x2ecc71)
        elif p_score > d_score:
            user_credits[self.author.id] += self.bet * 2
            await self.end_game("🏆 You Win!", f"Your `{p_score}` beat the dealer's `{d_score}`! Won `{self.bet * 2}` credits!", 0x2ecc71)
        elif p_score < d_score:
            await self.end_game("❌ You Lose!", f"The dealer's `{d_score}` beat your `{p_score}`. Lost your bet.", 0xe74c3c)
        else:
            user_credits[self.author.id] += self.bet
            await self.end_game("🤝 Push!", f"It's a tie at `{p_score}`! Credits returned.", 0x7f8c8d)

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.grey, custom_id="hit")
    async def hit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.author:
            await interaction.response.send_message("This isn't your card table, partner! 🤠", ephemeral=True)
            return

        self.player_hand.append(self.deck.pop())
        p_score = calculate_hand(self.player_hand)

        # Double down is disallowed after hitting once
        for child in self.children:
            if child.custom_id == "double":
                child.disabled = True

        if p_score > 21:
            await interaction.response.defer()
            await self.end_game("💥 Busted!", f"You went over 21 with a total of `{p_score}`. House wins!", 0xe74c3c)
        else:
            await interaction.response.edit_message(embed=self.make_embed(), view=self)

    @discord.ui.button(label="Stand", style=discord.ButtonStyle.blurple, custom_id="stand")
    async def stand_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.author:
            await interaction.response.send_message("This isn't your card table, partner! 🤠", ephemeral=True)
            return

        await interaction.response.defer()
        await self.dealer_turn()

    @discord.ui.button(label="Double", style=discord.ButtonStyle.success, custom_id="double")
    async def double_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.author:
            await interaction.response.send_message("This isn't your card table, partner! 🤠", ephemeral=True)
            return

        current_bal = user_credits.get(self.author.id, 0)
        if current_bal < self.bet:
            await interaction.response.send_message("You don't have enough credits left in your balance to double down!", ephemeral=True)
            return

        # Deduct the second matching bet layout
        user_credits[self.author.id] -= self.bet
        self.bet *= 2
        self.doubled = True
        
        self.player_hand.append(self.deck.pop())
        p_score = calculate_hand(self.player_hand)

        await interaction.response.defer()
        if p_score > 21:
            await self.end_game("💥 Busted on Double!", f"You went over 21 with a total of `{p_score}`. House wins!", 0xe74c3c)
        else:
            await self.dealer_turn()

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        if self.message:
            try:
                await self.message.edit(content="⏰ Game abandoned! Table cleared due to inactivity. Credits lost.", view=self)
            except discord.HTTPException:
                pass

# --- Button View Class for the Quiz ---
class QuizView(discord.ui.View):
    def __init__(self, quiz_item, original_author):
        super().__init__(timeout=15.0)
        self.quiz_item = quiz_item
        self.correct_answer = quiz_item['correct']
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
        correct_text = self.quiz_item['choices'][self.correct_answer]
        
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True
                if child.custom_id == self.correct_answer:
                    child.style = discord.ButtonStyle.green
                else:
                    child.style = discord.ButtonStyle.danger
                    
        await self.message.edit(view=self)

        if selected_choice == self.correct_answer:
            await interaction.response.send_message(f"🎉 Correct, {interaction.user.mention}! You nailed it! The answer was **{self.correct_answer}) {correct_text}**.")
        else:
            await interaction.response.send_message(f"❌ Incorrect, {interaction.user.mention}! The correct answer was choice **{self.correct_answer}) {correct_text}**.")
        
        self.stop()

    async def on_timeout(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True
                if child.custom_id == self.correct_answer:
                    child.style = discord.ButtonStyle.green
                else:
                    child.style = discord.ButtonStyle.danger
        if self.message:
            try:
                await self.message.edit(view=self)
                correct_text = self.quiz_item['choices'][self.correct_answer]
                await self.message.channel.send(f"⏰ Time's up! Nobody answered in time. The correct answer was **{self.correct_answer}) {correct_text}**.")
            except discord.HTTPException:
                pass

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
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

# Custom Help Command Embed
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="🤖 Starry's N00b — Command Menu",
        description="Here is a full layout of my configuration! Active prefixes use `-`, while text triggers respond dynamically in regular chat.",
        color=0xFFD700
    )
    
    embed.add_field(name="⚙️ Prefix Commands", value=(
        "`-help` ➜ Shows this helpful configuration list.\n\n"
        "`-earn` ➜ Claims 5 free system credits once every 12 hours.\n\n"
        "`-bal` ➜ Displays your current overall arcade credit balances.\n\n"
        "`-lb` ➜ Shows the server credit leaderboard from high to low.\n\n"
        "`-21 [amount / all]` ➜ Bet credits in a classic match of Blackjack.\n\n"
        "`-play` ➜ Launches a 4-option trivia mini-game (15s cooldown).\n\n"
        "`-time` ➜ Displays the current time adjusted directly to your device.\n\n"
        "`-ping` ➜ Tests bot responsiveness with latency calculation.\n\n"
        "`-roll [sides]` ➜ Rolls a dice. Defaults to 6 sides.\n\n"
        "`-8ball [question]` ➜ Ask a question and receive a mystery prediction."
    ), inline=False)
    
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

    view = QuizView(quiz_item=quiz, original_author=ctx.author)
    view.message = await ctx.send(embed=embed, view=view)

# --- Credit System Functional Commands ---

@bot.command(name="earn")
async def earn_credits(ctx):
    user_id = ctx.author.id
    current_time = time_module.time()
    cooldown_seconds = 12 * 3600  # 12 hours converted to seconds
    
    if user_id in earn_cooldowns:
        elapsed = current_time - earn_cooldowns[user_id]
        if elapsed < cooldown_seconds:
            remaining = cooldown_seconds - elapsed
            hours = int(remaining // 3600)
            minutes = int((remaining % 3600) // 60)
            await ctx.send(f"⏳ **Cooldown active!** You can claim free credits again in **{hours}h {minutes}m**.")
            return

    earn_cooldowns[user_id] = current_time
    user_credits[user_id] = user_credits.get(user_id, 0) + 5
    await ctx.send(f"💰 {ctx.author.mention}, you've claimed **5 free credits**! Your balance is now `{user_credits[user_id]}` credits.")

@bot.command(name="bal")
async def balance(ctx):
    bal = user_credits.get(ctx.author.id, 0)
    await ctx.send(f"💳 {ctx.author.mention}, your current total wallet holds: `{bal}` credits.")

# Blackjack Command with Betting Extensions
@bot.command(name="21")
async def blackjack(ctx, bet_input: str = None):
    user_id = ctx.author.id
    current_bal = user_credits.get(user_id, 0)

    if bet_input is None:
        await ctx.send("❌ Please provide a wager amount! Usage: `-21 [number]` or `-21 all`")
        return

    # Parse standard values vs 'all' string arguments
    if bet_input.lower() == "all":
        bet = current_bal
    else:
        try:
            bet = int(bet_input)
        except ValueError:
            await ctx.send("❌ Invalid bet amount format. Please input a positive full number or `all`.")
            return

    if bet <= 0:
        await ctx.send("❌ Your wager amount must be higher than 0 credits!")
        return

    if current_bal < bet:
        await ctx.send(f"❌ Transaction declined! You do not have enough credits. Current balance: `{current_bal}`")
        return

    # Deduct the bet amount upfront
    user_credits[user_id] -= bet

    view = BlackjackView(ctx.author, bet)
    view.message = await ctx.send(embed=view.make_embed(), view=view)
    
    # Check if someone lands a natural Blackjack off the starting cards
    await view.check_initial_blackjack()

# Leaderboard Command
@bot.command(name="lb")
async def leaderboard(ctx):
    if not user_credits:
        await ctx.send("🏆 The leaderboard is completely empty right now! Run `-earn` to get started.")
        return

    # Filter out users who have 0 or fewer credits to keep it clean, then sort from high to low
    sorted_credits = sorted(
        [(uid, amt) for uid, amt in user_credits.items() if amt > 0], 
        key=lambda item: item[1], 
        reverse=True
    )

    if not sorted_credits:
        await ctx.send("🏆 No active balances recorded yet!")
        return

    embed = discord.Embed(
        title="🏆 Server Credit Leaderboard",
        color=0xFFD700,
        description="Here are the top high-rollers on the server right now!"
    )

    leaderboard_text = ""
    # Look up usernames safely across cache or fallback API fetches up to top 10 positions
    for rank, (u_id, amount) in enumerate(sorted_credits[:10], start=1):
        user = bot.get_user(u_id)
        if not user:
            try:
                user = await bot.fetch_user(u_id)
            except discord.HTTPException:
                user = None
        
        name = user.display_name if user else f"Unknown User ({u_id})"
        leaderboard_text += f"**#{rank}** {name} ➜ `{amount}` credits\n"

    embed.add_field(name="Top Players", value=leaderboard_text, inline=False)
    await ctx.send(embed=embed)

# --- Administrative Owner Commands ---

@bot.command(name="addcredits")
async def add_credits(ctx, member: discord.Member = None, amount: int = None):
    if ctx.author.id != OWNER_ID:
        await ctx.send("⛔ Authorization Denied. Only the bot master can handle direct bank overrides.")
        return

    if member is None or amount is None or amount <= 0:
        await ctx.send("ℹ️ Usage configuration standard format: `-addcredits @User [positive number]`")
        return

    user_credits[member.id] = user_credits.get(member.id, 0) + amount
    await ctx.send(f"✅ System Update: Added `{amount}` credits to {member.mention}'s vault. New Balance: `{user_credits[member.id]}`")

@bot.command(name="removecredits")
async def remove_credits(ctx, member: discord.Member = None, amount: int = None):
    if ctx.author.id != OWNER_ID:
        await ctx.send("⛔ Authorization Denied. Only the bot master can handle direct bank overrides.")
        return

    if member is None or amount is None or amount <= 0:
        await ctx.send("ℹ️ Usage configuration standard format: `-removecredits @User [positive number]`")
        return

    current_bal = user_credits.get(member.id, 0)
    user_credits[member.id] = max(0, current_bal - amount)
    await ctx.send(f"🛑 System Update: Stripped `{amount}` credits from {member.mention}'s vault. New Balance: `{user_credits[member.id]}`")

# Custom Message Listener
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # If it is a prefix command, process it immediately and skip custom chat triggers
    if message.content.startswith(bot.command_prefix):
        await bot.process_commands(message)
        return

    content_lower = message.content.lower()
    clean_content = re.sub(r'<a?:[a-zA-Z0-9_]+:[0-9]+>', '', content_lower)

    if "starry hates me" in clean_content:
        await message.channel.send("No he doesn't")
    elif "you hate me" in clean_content:
        await message.channel.send("No I don't")
    elif "cute" in clean_content:
        await message.channel.send("<:Cutestarry:1519456531173871686>")
    elif "gay" in clean_content:
        await message.channel.send("Yes, indeed Starry is gay")
    elif "starry" in clean_content:
        starry_responses = [
            "Who is it that dares cast their tongue upon my master?",
            "Who amongst you possesses the effrontery to utter my master’s name?",
            "Who dares breathe a word concerning my liege?",
            "Who assumes the audacity to speak of my master?"
        ]
        await message.channel.send(random.choice(starry_responses))

# Run Background Tasks and Launch Bot
keep_alive()

token = os.getenv("DISCORD_TOKEN")
bot.run(token)
