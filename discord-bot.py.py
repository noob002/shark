
from bs4 import BeautifulSoup
import discord
from discord import FFmpegPCMAudio
from discord.colour import Color
from discord.ext import commands
from discord.utils import get
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from youtube_dl import YoutubeDL, options
import asyncio
import time
from urllib import request
import os

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print('다음으로 로그인합니다: ')
    print(bot.user.name)
    print('connection was succesful')
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("!명령어"))

@bot.command()
async def 상어야(ctx, *, text):
    await ctx.send(text)

@bot.command()
async def 들어와(ctx):
    try:
        global vc
        vc = await ctx.message.author.voice.channel.connect()
    except:
        try:
            await vc.move_to(ctx.message.author.voice.channel)
        except:
            await ctx.send("당신은 현재 음성 채널에 있지 않아요...")

@bot.command()    
async def 해제(ctx):
    try:
        await vc.disconnect()
    except:
        await ctx.send("나는 지금 음성 채널에 있지 않아요...")
    
@bot.command()
async def 재생(ctx, *, url):
    YDL_OPTIONS = {'format': 'bestaudio','noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    if not vc.is_playing():
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']
        await ctx.send(embed = discord.Embed(title= "노래 재생", description = "현재 " + url + "을(를) 재생하고 있습니다.", color = 0x00ff00))
        vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
        await subtitle_song(ctx, url)
    else:
        await ctx.send("노래가 이미 재생되고 있습니다!")

@bot.command()
async def 검색(ctx, *, msg):
    if not vc.is_playing():
        global entireText
        YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
            
        chromedriver_dir = r"C:\Users\ckuk7\Downloads\chromedriver_win32\chromedriver.exe"
        driver = webdriver.Chrome(chromedriver_dir)
        driver.get("https://www.youtube.com/results?search_query="+msg+"+lyrics")
        source = driver.page_source
        bs = BeautifulSoup(source, 'lxml')
        entire = bs.find_all('a', {'id': 'video-title'})
        entireNum = entire[0]
        entireText = entireNum.text.strip()
        musicurl = entireNum.get('href')
        url = 'https://www.youtube.com'+musicurl 

        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']
        await ctx.send(embed = discord.Embed(title= "노래 재생", description = "현재 " + entireText + "을(를) 재생하고 있습니다.", color = 0x00ff00))
        vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
    else:
        await ctx.send("이미 노래가 재생 중이라 노래를 재생할 수 없어요!")

async def subtitle_song(ctx, suburl):
    TEXT = suburl
    rink = TEXT[-11:]
    target = request.urlopen("http://video.google.com/timedtext?type=list&v="+rink)

    soup = BeautifulSoup(target, "html.parser")
    sub = 0
    kor = 0
    for track in soup.select("track"):
        if sub == 0:
            firstsub = track['lang_code']
        if track['lang_code'] == 'ko':
            kor += 1
        sub += 1

    if sub == 0: #자막이 없음
        await ctx.send("""
        ```
        유튜브 자막이 포함되지 않은 영상입니다!
        ```
        """)
        return 0

    elif kor == 0 and sub != 0: #한글이 아닌 자막 재생
        target = request.urlopen("http://video.google.com/timedtext?lang="+firstsub+"&v="+rink)
        
    elif kor == 1 and sub != 0:  #한글 자막 재생
        target = request.urlopen("http://video.google.com/timedtext?lang=ko&v="+rink)

    soup = BeautifulSoup(target, "html.parser")
    subtimedur = []
    subtimelast = []
    last_time = 0
    subtext = []

    for text in soup.select("text"):
        subtimedur.append(text['start'])
        subtimelast.append(text['dur'])
        subtext.append(text.string)
    
    for i in range(len(subtext)):
        last_time += 1
        embed = discord.Embed(description=subtext[i], color=0x00ff00)
        if i == 0:
            time.sleep(float(subtimedur[i]))
            sub_message = await ctx.send(embed = embed)
        else:
            time.sleep(float(subtimedur[i]) - float(subtimedur[i-1]) - float(0.1))
            await sub_message.edit(embed = embed)
        
    time.sleep(subtimelast[last_time])

    await sub_message.delete()
    del subtimedur [:]
    del subtext [:]  
def play(ctx):
    global vc
    YDL_OPRIONS = {'format': 'destaudio', 'noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    URL = song_queue[0]
    del user[0]
    del musictitle[0]
    del song_queue[0]
    vc = get(bot.voice_clients, guild=ctx.guild)
    if not vc.is_playing():
        vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after=lambda e: play_next(ctx))
        client.loop.create_tesk(sudtitle_song(ctx, URL))

def play_next(ctx):
    if len(musicnow) - len(user)>= 2:
        for i in range(len(musicnow) - len(user) - 1):
            del musicnow[0]
    YDL_OPTIONS = {'format': 'destaudio', 'noplaylist':'True'}  
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}    
    if len(user) >= 1:
        if not vc.is_playing():
            del musicnow[0]
            URL = song_queue[0]
            del user[0]
            del musictitle[0]
            del song_queue[0]
            vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after=lambda e: play_next(ctx))
            client.loop.create_tesk(sudtitle_song(ctx, URL))      

@bot.command()
async def 일시정지(ctx):
    if vc.is_playing():
        vc.pause()
        await ctx.send(embed = discord.Embed(title= "일시정지", description = entiretext + "을(를) 일시정지 했습니다.", color = 0x00ff00))
    else:
            await ctx.send("지금 노래가 재생되지 않네요.")

@bot.command()
async def 다시재생(ctx):
    try:
        vc.resume()
    except:
         await ctx.send("지금 노래가 재생되어 있지않아요...")
    else:
         await ctx.send(embed = discord.Embed(title= "다시재생", description = entireText  + "을(를) 다시 재생했습니다.", color = 0x00ff00))

@bot.command()
async def 노래끄기(ctx):
    if vc.is_playing():
        vc.stop()
        await ctx.send(embed = discord.Embed(title= "노래끄기", description = entireText  + "을(를) 종료했습니다.", color = 0x00ff00))
    else:
        await ctx.send("지금 노래가 재생되어 있지않아요...")

@bot.command()
async def 명령어(ctx):
    await ctx.send(embed = discord.Embed(title='도움말',description="""
\n!도움말 -> 상어봇의 모든 명령어를 볼 수 있습니다.
\n!들어와 -> 상어봇을 자신이 속한 채널로 부릅니다.
\n!해제 -> 상어봇을 자신이 속한 채널에서 내보냅니다.
\n!재생 [노래링크] -> 유튜브URL를 입력하면 상어봇이 노래를 틀어줍니다.
\n!검색 -> 듣고 싶은 노래 제목을 적어으면 상어봇이 노래를 검색 하여 틀어줌니다
\n!노래끄기 -> 현재 재생중인 노래를 끕니다.
\n!일시정지 -> 현재 재생중인 노래를 일시정지시킵니다.
\n!다시재생 -> 일시정지 또는 끈 노래은다시 노래를 재생합니다.
\n!상어야 -> 상어봇이 당신이 한 말은 따라합니다.
\n음질 음악 속도가 맞지 않을 수 있습니다.
\n검색은 정확하지 않으니 주의 하세요.
\nURL 에서만 자막이 작동 합니다.""", color = 0x00ff00))

access_token  = os.environ['BOT_TOKEN']
bot.run(access_token)
