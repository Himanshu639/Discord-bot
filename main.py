import discord
import syncedlyrics
import yt_dlp
import re
from datetime import datetime
import time
import asyncio
from youtubesearchpython import VideosSearch
from spotify_recommendation_engine import *
# from discord.ext import commands
import os

from keep_alive import keep_alive
keep_alive()
#important lines for discord bot to work
# - - - - - - - - - - - - - - - - - - - - - - - - -
discord.opus.load_opus("./libopus.so.0.8.0")
intents = discord.Intents.default()
intents.message_content = True

bot = discord.Bot()
token = os.environ['token']
stop_lyrics = True
# - - - - - - - - - - - - - - - - - - - - - - - - -

#global variables
# - - - - - - - - - - - - - - - - - - - - - - - - -
ydl_opts = {
    "extract_flat":True,
    'outtmpl': "song.m4a",
    'format': 'm4a/bestaudio/best',
    'postprocessors': [{  # Extract audio using ffmpeg
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'm4a',
    }]
}

path = "/home/runner/clicker"
song_queue = []
recommendations = False
last_played_song = ""
start = 0
lyrics = None
# - - - - - - - - - - - - - - - - - - - - - - - - -

# On ready Function
# - - - - - - - - - - - - - - - - - - - - - - - - -
@bot.event
async def on_ready():
  print('Ready!')
  # await bot.tree.sync()
# - - - - - - - - - - - - - - - - - - - - - - - - -

# User Info Function
# - - - - - - - - - - - - - - - - - - - - - - - - -
@bot.command(name="user-info", description="Gives information about user")
async def userinfo(interaction: discord.Interaction, member: discord.Member):

  embed = discord.Embed(
    title="User Info",
    description=f"Here's is the user info on the user {member.mention}",
    color=discord.Color.dark_blue(),
    timestamp=interaction.created_at)
  embed.set_thumbnail(url=member.avatar)
  embed.set_footer(text=f"Requested by {interaction.user.name}",
                   icon_url=interaction.user.avatar)
  await interaction.response.send_message(embed=embed)
# - - - - - - - - - - - - - - - - - - - - - - - - -

# VC Joining Helper Function
# - - - - - - - - - - - - - - - - - - - - - - - - -
async def joinhelper(interaction: discord.Interaction):
  voice = interaction.user.voice
  if not voice:
    await interaction.response.send_message(
      content="You need to be in a voice channel to use this command.")
    return False

  elif bot.voice_clients and bot.voice_clients[0].channel.id == voice.channel.id:
    return 1

  else:
    await voice.channel.connect()
    return 2
# - - - - - - - - - - - - - - - - - - - - - - - - -

# VC Join Function
# - - - - - - - - - - - - - - - - - - - - - - - - -
@bot.command(name="join", description="Joins the VC")
async def join(interaction: discord.Interaction):
  voice = interaction.user.voice
  return_code = await joinhelper(interaction)
  if return_code == 1:
    await interaction.response.send_message(
      content=f"Already joined {voice.channel.name}")
  elif return_code == 2:
    await interaction.response.send_message(
      content=f"Joined {voice.channel.name}")  
# - - - - - - - - - - - - - - - - - - - - - - - - -

# VC Leave Function
# - - - - - - - - - - - - - - - - - - - - - - - - -
@bot.command(name="leave", description="Leaves the VC")
async def leave(interaction: discord.Interaction):
  if interaction.guild.voice_client:
    await interaction.guild.voice_client.disconnect()
    await interaction.response.send_message(content="Left the voice channel.")
  else:
    await interaction.response.send_message(content="I'm not in a voice channel.")
# - - - - - - - - - - - - - - - - - - - - - - - - -

# VC Song Player Helper Function
# - - - - - - - - - - - - - - - - - - - - - - - - -
async def player(interaction:discord.Interaction, info: dict):
  if os.path.exists("song.m4a"):
    os.remove("song.m4a")
  with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    msg = await interaction.channel.send(content=f"## 📥 Getting the song `{info['result'][0]['title']}`")
    # info = ydl.extract_info(query, download=True)
    ydl.download(info['result'][0]['link'])

    global last_played_song
    last_played_song = info['result'][0]["title"]
    embed = discord.Embed(title=f"**{last_played_song}**",
      colour=0x2c77d8,
      timestamp=datetime.now())

    embed.add_field(name="🧑‍🎤 Publisher",
    value=f"```{info['result'][0]['channel']['name']}```",
    inline=True)
    embed.add_field(name="⌛ Duration",
    value=f"```{info['result'][0]['duration']}```",
    inline=True)
    embed.add_field(name="📈 Views",
    value=f"```{info['result'][0]['viewCount']['text'].split()[0]}```",
    inline=True)
    embed.add_field(name="👤 Requested By",
    value=f"<@{interaction.user.id}>",
    inline=True)
    embed.add_field(name="▶️ Watch On YouTube",
    value=f"[🔗 YouTube Link]({info['result'][0]['link']})",
    inline=True)

    embed.set_thumbnail(url=f"https://img.youtube.com/vi/{info['result'][0]['id']}/0.jpg")

    embed.set_footer(icon_url="https://cdn-icons-png.flaticon.com/512/1382/1382065.png")
    await msg.edit(content="## 🔊 Currently Playing",embed=embed)

  source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("song.m4a"))
  global start
  start = time.time()

  token = get_token()
  
  global lyrics
  lyrics = syncedlyrics.search(get_track_name(token,track_to_trackid(token,last_played_song)))
  
  interaction.guild.voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_next_song(interaction,msg), bot.loop).result())

# - - - - - - - - - - - - - - - - - - - - - - - - -

# VC Song player Function
# - - - - - - - - - - - - - - - - - - - - - - - - -
@bot.command(name="play", description="Plays any audio in the VC")
async def play(interaction: discord.Interaction, query: str):
  if await joinhelper(interaction) == False:
    return

  result = VideosSearch(query+"official audio", limit = 1).result()
  title = result['result'][0]['title']
  embed = discord.Embed(
    title="🎶 Song Added to Queue",
  )
  embed.add_field(name="Song Name",value=f"{title}")
  embed.add_field(name="Queue Position", value=f"#{len(song_queue)}", inline=True)
  embed.set_footer(text="Enjoy the music!")

  await interaction.response.send_message(embed=embed)
  if not interaction.guild.voice_client.is_playing():
    await player(interaction,result)
  else:
    song_queue.append(result)
# - - - - - - - - - - - - - - - - - - - - - - - - -

# VC Next Song Search Function
# - - - - - - - - - - - - - - - - - - - - - - - - -
async def play_next_song(interaction: discord.Interaction, msg:discord.Message):
  if interaction.guild.voice_client:
    await msg.edit(content="")
    if song_queue:
      next_song = song_queue.pop(0)
      await player(interaction, next_song)
    else:
      global recommendations
      if recommendations:
        msg = await interaction.channel.send("## 🔍 Finding Song Recommendations")
        try:
          token = get_token()
          next_song = get_recommendations(token,last_played_song)
          await msg.delete()
          result = VideosSearch(next_song, limit=1).result()
          await player(interaction, result)
        except:
          msg.edit(content="## ❎ Couldn't Find Song")
      else:
        embed = discord.Embed(title="❎ No more songs in the Queue!")
        await interaction.channel.send(embed=embed)
# - - - - - - - - - - - - - - - - - - - - - - - - -

# VC Song Skip Function
# - - - - - - - - - - - - - - - - - - - - - - - - -
@bot.command(name="skip", description="Skips the current song")
async def skip(interaction: discord.Interaction):
    if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
        global stop_lyrics
        stop_lyrics = False
        interaction.guild.voice_client.stop()
        embed = discord.Embed(title="✅ Skipped the current song.")
        await interaction.response.send_message(embed=embed)
        # await play_next_song(interaction)

    else:
        embed = discord.Embed(title="😐 No song is currently playing.")
        await interaction.response.send_message(embed=embed)
# - - - - - - - - - - - - - - - - - - - - - - - - -

# Toggling VC Song Recommendations
# - - - - - - - - - - - - - - - - - - - - - - - - -
@bot.command(name="recommendations", description="Toggles VC Song Recommendations")
async def song_recommendations(interaction: discord.Interaction, autoplay:bool):
  global recommendations
  recommendations = autoplay

  embed = None
  if autoplay:
    embed = discord.Embed(title="✅ Turned ON Song Recommendations")
  else:
    embed = discord.Embed(title="✅ Turned OFF Song Recommendations")

  await interaction.response.send_message(embed=embed)
# - - - - - - - - - - - - - - - - - - - - - - - - -

# Lyrics Function helper
# - - - - - - - - - - - - - - - - - - - - - - - - -
async def lyricshelper(th:discord.Thread):
  global start
  global lyrics
  global stop_lyrics
  stop_lyrics = True
  ourtime = 0
  entries = re.findall(r'\[(\d+:\d+\.\d+)?\]\s*(.*?)\s*(?=\[\d+:\d+\.\d+\]|$)', lyrics, re.DOTALL)

  i = 0
  while i<len(entries):
      timestamp, line = entries[i]
      total_seconds = (datetime.strptime(timestamp, "%M:%S.%f") - datetime(1900, 1, 1)).total_seconds()

      if not stop_lyrics:
        return
      while ourtime>=total_seconds:
        if line!='':
          await th.send(line)
          print(line)
        i+=1
        ourtime = time.time() - start
        break
      else:
        ourtime = time.time() - start

      await asyncio.sleep(0.5)
# - - - - - - - - - - - - - - - - - - - - - - - - -

# Synced Lyrics Function
# - - - - - - - - - - - - - - - - - - - - - - - - -
@bot.command(name="get-lyrics",description="Creates a new thread for showing synced lyrics")
# - - - - - - - - - - - - - - - - - - - - - - - - -
async def getlyrics(interaction: discord.Interaction):
  global lyrics
  if lyrics:
    await interaction.response.send_message(content=f"Lyrics of {last_played_song}")
    msg = await interaction.channel.send("### Lyrics will appear here")
    th = await msg.create_thread(name="Lyrics", auto_archive_duration=60)
    asyncio.run(await lyricshelper(th))
  else:
    await interaction.response.send_message("Lyrics Not Available")
  
# Anonymous Messaging Function
# - - - - - - - - - - - - - - - - - - - - - - - - -
@bot.command(name="anonymous-message", description="Sends the Message anonymously")
async def anonymous(interaction: discord.Interaction,msg:str,msg_id:str = None):
  if interaction.user.id == 620943253444755466:

    if msg_id == None:
      await interaction.channel.send(msg)
    else:
      message = await interaction.channel.fetch_message(int(msg_id))
      await message.reply(msg)

    await interaction.response.send_message("✅✅",ephemeral=True,delete_after=0.0)
# - - - - - - - - - - - - - - - - - - - - - - - - -

# - - - - - - - - - - - - - - - - - - - - - - - - -
bot.run(token)
# - - - - - - - - - - - - - - - - - - - - - - - - -

