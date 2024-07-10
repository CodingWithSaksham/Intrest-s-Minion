import discord
from discord.ext import commands

from math import sqrt, ceil
from random import randint
from sqlite3 import connect
from utils.settings import BOT_CMD_ID
from datetime import datetime

database = connect('database.sqlite')
database.autocommit = True
cursor = database.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS Level(user_id INT PRIMARY KEY, exp INT, level INT, last_level INT)""")


class Leveling(commands.Cog):
    def __init__(self, bot: discord.Client) -> None:
        self.bot = bot
        self.BOT_CMD_CHANNEL = self.bot.get_channel(BOT_CMD_ID)
    

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot : return
        exp, level, last_level =  fetch_user_info(message)

        exp += randint(1,20)
        level = 0.1 * sqrt(exp)

        cursor.execute(f"""
                        UPDATE Level
                        SET exp = {exp}, level = {level}
                        WHERE user_id = {message.author.id}
                    """)
    
        if level > last_level:
            embed = discord.Embed(
                color= discord.Color.red(),
                timestamp= datetime.now(),
                description=f"{message.author.mention} has leveled up to *Level {level}*. GGS"
            )
            embed.thumbnail(url = message.author.display_avatar())
            await self.BOT_CMD_CHANNEL.send(embed=embed)

            cursor.execute(f"""
                            UPDATE Level 
                            SET last_level = {last_level}
                            WHERE user_id = {message.author.id}
                        """)


    @commands.hybrid_command(name='rank')
    async def rank(self, ctx, member: discord.Member):
        user = member or ctx.author


class Leveling_Debugger(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot


    @commands.hybrid_group(name="exp",
                           hidden = True)
    @commands.is_owner()
    async def exp_debugger(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.author.message("No subcommand used")
    

    @exp_debugger.command(name='add_exp')
    async def add_exp(self, ctx, exp_amount: int):
        if ctx.author.bot : return
        
        exp, level, last_level =  fetch_user_info(ctx)
        exp += exp_amount
        level = 0.1 * sqrt(exp)
        
        if level > last_level:
            await self.BOT_CMD_CHANNEL.send(f'Fiery, you leveled up, ab exp hain {exp}')    

        cursor.execute(f"""
                        UPDATE Level
                        SET exp = {exp}, level = {level}, last_level = {ceil(level)}
                        WHERE user_id = {ctx.author.id}
                    """)


    @exp_debugger.command(name='remove_exp')
    async def remove_exp(self, ctx, exp_amount: int):
        if ctx.author.bot: return
        exp, level, last_level =  fetch_user_info(ctx)

        exp -= exp_amount
        level = 0.1 * sqrt(exp)

        if level < last_level:
            await self.BOT_CMD_CHANNEL.send(f'Fiery, you leveled down, ab exp hain {exp}')

        cursor.execute(f"""
                        UPDATE Level
                        SET exp = {exp}, level = {level}, last_level = {ceil(level)}
                        WHERE user_id = {ctx.author.id}
                    """)


def fetch_user_info(message: discord.Message):
    cursor.execute(f"""
                    SELECT * FROM Level
                    WHERE user_id = {message.author.id}
                """)

    result = cursor.fetchone()

    if result is None:
        cursor.execute(f"""
                        INSERT INTO Level
                        VALUES({message.author.id}, 1, 0 , 1)
                    """)

    return result[1], result[2], result[3]


async def setup(bot):
    await bot.add_cog(Leveling(bot))
    await bot.add_cog(Leveling_Debugger(bot))