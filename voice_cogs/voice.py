import discord
from discord.ext import commands
import asyncio
from pydub import AudioSegment
from pydub.playback import play


class Voice(commands.cog):
    @commands.hybridcommand(name='join')
    async def join(self, ctx):
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
            await ctx.send(f'Joined {channel}')
        else:
            await ctx.send('You are not connected to a voice channel.')

    @commands.hybridcommand(name='leave')
    async def leave(self, ctx):
        if ctx.voice_client:
            await ctx.guild.voice_client.disconnect()
            await ctx.send('Disconnected from the voice channel')
        else:
            await ctx.send('I am not connected to a voice channel.')

    @commands.hybridcommand(name='record')
    async def record(self, ctx):
        vc = ctx.voice_client
        if not vc:
            await ctx.send('I am not in a voice channel.')
            return
        
        if not ctx.author.voice:
            await ctx.send('You need to be in a voice channel to record.')
            return

        vc.stop()

        audio_source = discord.PCMAudio('recorded_audio.pcm')
        vc.play(audio_source)

        while vc.is_playing():
            await asyncio.sleep(1)
        
        await ctx.send('Recording complete. Processing audio...')

        # Process the recorded audio
        audio = AudioSegment.from_file('recorded_audio.pcm', format='pcm')
        audio = audio + 20  # Increase volume
        audio.export('processed_audio.wav', format='wav')

        await ctx.send('Audio processed. Playing back...')

        audio_source = discord.FFmpegPCMAudio('processed_audio.wav')
        vc.play(audio_source)

        while vc.is_playing():
            await asyncio.sleep(1)
        
        await ctx.send('Playback complete.')

    @commands.hybridcommand(name='stop')
    async def stop(self, ctx):
        vc = ctx.voice_client
        if vc and vc.is_playing():
            vc.stop()
            await ctx.send('Stopped the playback.')
        else:
            await ctx.send('Nothing is playing.')

async def setup(bot):
    bot.add_cog(Voice(bot))