import discord
from discord.ext import commands

from utils.settings import *
from datetime import datetime
from signal import signal, SIGHUP, SIGINT, SIGTERM
from asyncio import get_event_loop
from app_commands.Staff import Staff

from atexit import register


logger = logging.getLogger('bot')
bot = commands.Bot(intents=discord.Intents.all(), command_prefix="bald ")

# Checks if the bot is online, if yes sends a log message to logging channel
async def is_bot_ready():
    if bot.is_ready():
        logging_channel = bot.get_channel(LOGGING_CHANNEL)
        embed = discord.Embed(
            color=discord.Color.red(),
            description="I am up and running now!",
            timestamp= datetime.now()
        )
        await logging_channel.send(embed=embed)


# Sends a message when the bot is being shut down due to any critical reason or because of host disconnection
async def shutdown_message(message):
    logging_channel = bot.get_channel(LOGGING_CHANNEL)

    embed = discord.Embed(
        color=discord.Color.red(),
        description= message
    )
    await logging_channel.send(embed=embed)
    await bot.close()


# Loophole to add the signal handler as coroutine functions can't be called
def handle_exit(message: str):
    loop = get_event_loop()
    loop.create_task(shutdown_message(message))


# Main function that calls the bot
def run_bot():
    @bot.event
    async def on_ready():
        try:
            # Loads every file in cogs directory which is not an __init__.py file
            for cog_files in COGS_DIR:
                if cog_files != "__init__.py" and cog_files.endswith('.py'):
                    await bot.load_extension(f'cogs.{cog_files[:-3]}')

            bot.tree.add_command(Staff(bot))
            await bot.change_presence(activity=discord.Game(name='Moderation'), status=discord.Status.dnd)
            print('Bot is ready')

        except Exception as e:
            logger.error(f'Error loading extension: {e}')

    
        logger.info(f"Logged in as {bot.user} with ID {bot.user.id}")
        await bot.tree.sync()    

        # Calls the function which checks if the bot is online or not
        # If anyone asks for an explaination, dont give them one cause you yourself don't know how this works
        await is_bot_ready()


    # Handles member joining
    @bot.event
    async def on_member_join(member):
        # Get the welcome channel
        welcome_channel = member.guild.get_channel(WELCOME_CHANNEL_ID)

        if welcome_channel:
            # Send a welcome message
            await welcome_channel.send(f'Welcome to the server, {member.mention}!\n'
                                       f'You joined on {datetime.now().strftime('%c')}\n'
                                       'bOnk')


    # Sends 'read #faq' image when someone asks about Intrest's Badlion profile or Texture pack
    @bot.event
    async def on_message(message: discord.Message):
        responses = ['blc profile', 'badlion profile', 'texture pack', 'resource pack', 'sb pack']
        if message.author == bot.user: return

        for i in responses:
            if i in message.content:
                with open('images/readfaq.jpeg', 'rb') as faq:
                    await message.reply(file=discord.File(faq))
                    await message.channel.send('This is an automated message, please ignore if you did not ask about Intrest\'s profile')
        
    # Runs the bot
    bot.run(TOKEN)

    
# Signal handlers that check if any type of interuption has occured, if yes it shut downs the bot
# When Ctrl+C is entered (KeyboardInterrupt Error) into terminal
signal(SIGINT, lambda s, f: handle_exit("CTRL+C was pressed (Bot shutting down from terminal)"))


# Terminaltion signal
signal(SIGTERM, lambda s,f : handle_exit("Bot Shutting down for development"))


# Hangup detected on controlling terminal or death of controlling process
signal(SIGHUP, lambda s,f: handle_exit("Terminal closed, contact host to identify problem."))


# Shift F5 is pressed in VS code
register(lambda :handle_exit('Bot shut down by developer or hosting site.'))


# Calls the function that runs the bot
if __name__ == "__main__":  
    run_bot()