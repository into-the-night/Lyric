import discord
from discord.ext import commands,tasks
import os
import yt_dlp as yt
import asyncio


discord_token = 'Discord API Key'

intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!lyric ', intents=intents)

yt.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'            # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = yt.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.75):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):            # Gets the title of the video and downloads the music when called
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename


@bot.command(name='join', help='"!lyric join" to join the voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()


@bot.command(name='leave', help='"!lyric leave" to leave the voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        del_webm()
        await voice_client.disconnect()
    else:
        del_webm()
        await ctx.send('Uh oh! It seems something is wrong. Use "!lyric help" for command help.')


@bot.command(name='play', help='"!lyric play (Youtube URL)" to play music from a youtube video')
async def play(ctx, url):
    try:
        server = ctx.message.guild
        voice_channel = server.voice_client

        async with ctx.typing():
            filename = await YTDLSource.from_url(url, loop=bot.loop)
            voice_channel.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=filename))
        await ctx.send('Got it! Your music is playing.')
    except:
        await ctx.send('Uh oh! It seems something is wrong. Use "!lyric help" for command help.')


@bot.command(name='pause', help='"!lyric pause" to pause the music')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        voice_client.pause()
    else:
        await ctx.send('It seems no music is playing right now. Use "!lyric help" for command help.')


@bot.command(name='resume', help='"!lyric resume" to resume the paused music')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        voice_client.resume()
    else:
        await ctx.send('It seems no music is playing right now. Use "!lyric help" for command help.')


@bot.command(name='stop', help='"!lyric stop" to stop playing music')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        voice_client.stop()
    else:
        await ctx.send('It seems no music is playing right now. Use "!lyric help" for command help.')


def del_webm():                                                         # Removes the .webm files in the directory when the leave command is executed
    Direc = os.getcwd()
    files = os.listdir(Direc)
    files = [f for f in files if os.path.isfile(Direc + '/' + f)]

    for f in files:
        temp = os.path.splitext(f)
        if temp[1] == '.webm':
            os.remove(f'{Direc}\{f}')


if __name__ == "__main__":
    bot.run(discord_token)

