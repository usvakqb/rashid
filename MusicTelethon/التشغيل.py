import asyncio
import math
import os
import time
import aiofiles
import aiohttp
import wget
import aiohttp
from io import BytesIO
from traceback import format_exc
from pyrogram import Client, filters
from pyrogram.types import Message
from Python_ARQ import ARQ
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import StreamType
from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio,    HighQualityVideo,    LowQualityVideo,    MediumQualityVideo
from youtubesearchpython import VideosSearch
from config import REKU, bot, call_py
from MusicTelethon.helpers.queues import QUEUE, add_to_queue, get_queue, clear_queue
from MusicTelethon.helpers.decorators import authorized_users_only
from MusicTelethon.helpers.handlers import skip_current_song, skip_item
from pyrogram.errors import FloodWait, MessageNotModified
from youtubesearchpython import SearchVideos
from yt_dlp import YoutubeDL
from config import REKU, SUDO_USERS
from MusicTelethon.helpers.merrors import capture_err
ARQ_API_KEY = "QFOTZM-GSZUFY-CHGHRX-TDEHOZ-ARQ"
aiohttpsession = aiohttp.ClientSession()
arq = ARQ("https://thearq.tech", ARQ_API_KEY, aiohttpsession)
def ytsearch(query):
    try:
        search = VideosSearch(query, limit=1).result()
        data = search["result"][0]
        songname = data["title"]
        url = data["link"]
        duration = data["duration"]
        thumbnail = f"https://i.ytimg.com/vi/{data['id']}/hqdefault.jpg"
        return [songname, url, duration, thumbnail]
    except Exception as e:
        print(e)
        return 0
async def ytdl(link):
    proc = await asyncio.create_subprocess_exec(        "yt-dlp",        "-g",        "-f",                "bestaudio",        f"{link}",        stdout=asyncio.subprocess.PIPE,        stderr=asyncio.subprocess.PIPE,    )
    stdout, stderr = await proc.communicate()
    if stdout:
        return 1, stdout.decode().split("\n")[0]
    else:
        return 0, stderr.decode()
def ytsearch(query):
    try:
        search = VideosSearch(query, limit=1).result()
        data = search["result"][0]
        songname = data["title"]
        url = data["link"]
        duration = data["duration"]
        thumbnail = f"https://i.ytimg.com/vi/{data['id']}/hqdefault.jpg"
        return [songname, url, duration, thumbnail]
    except Exception as e:
        print(e)
        return 0
async def ytdl(link):
    proc = await asyncio.create_subprocess_exec(        "yt-dlp",        "-g",        "-f",              "best[height<=?720][width<=?1280]",        f"{link}",        stdout=asyncio.subprocess.PIPE,        stderr=asyncio.subprocess.PIPE,    )
    stdout, stderr = await proc.communicate()
    if stdout:
        return 1, stdout.decode().split("\n")[0]
    else:
        return 0, stderr.decode()
@Client.on_message(    filters.user(SUDO_USERS) & filters.command([""], prefixes=f"{REKU}"))
@authorized_users_only
async def play(client, m: Message):
    replied = m.reply_to_message
    chat_id = m.chat.id
    m.chat.title
    if replied:
        if replied.audio or replied.voice:
            await m.delete()
            huehue = await replied.reply("**    **")
            dl = await replied.download()
            link = replied.link
            if replied.audio:
                if replied.audio.title:
                    songname = replied.audio.title[:35] + "..."
                else:
                    songname = replied.audio.file_name[:35] + "..."
            elif replied.voice:
                songname = "Voice Note"
            if chat_id in QUEUE:
                pos = add_to_queue(chat_id, songname, dl, link, "Audio", 0)
                await huehue.delete()
                # await m.reply_to_message.delete()
                await m.reply_photo(
                    photo="https://telegra.ph/file/8fe4f047bcf3921590a74.jpg",
                    caption=f"""
**  : [{songname}]({link})
   : {chat_id}
   : {m.from_user.mention}**
""",                )
            else:
                await call_py.join_group_call(                    chat_id,                    AudioPiped(                        dl,                    ),                    stream_type=StreamType().pulse_stream,                )
                add_to_queue(chat_id, songname, dl, link, "Audio", 0)
                await huehue.delete()
                await m.reply_photo(
                    photo="https://telegra.ph/file/8fe4f047bcf3921590a74.jpg",
                    caption=f"""
**  : [{songname}]({link})
   : {chat_id}
   : {m.from_user.mention}**
""",                )

    else:
        if len(m.command) < 2:
            await m.reply("       ")
        else:
            await m.delete()
            huehue = await m.reply("   ")
            query = m.text.split(None, 1)[1]
            search = ytsearch(query)
            if search == 0:
                await huehue.edit("     ")
            else:
                songname = search[0]
                url = search[1]
                duration = search[2]
                thumbnail = search[3]
                hm, ytlink = await ytdl(url)
                if hm == 0:
                    await huehue.edit(f"**    ** \n\n`{ytlink}`")
                else:
                    if chat_id in QUEUE:
                        pos = add_to_queue(chat_id, songname, ytlink, url, "Audio", 0)
                        await huehue.delete()
                        await m.reply_photo(
                            photo=f"{thumbnail}",
                            caption=f"""
**   : [{songname}]({url})
   : {duration}
   : {chat_id}
   : {m.from_user.mention}**
""",
                        )
                    else:
                        try:
                            await call_py.join_group_call(
                                chat_id,
                                AudioPiped(
                                    ytlink,
                                ),
                                stream_type=StreamType().pulse_stream,
                            )
                            add_to_queue(chat_id, songname, ytlink, url, "Audio", 0)
                            await huehue.delete()
                            # await m.reply_to_message.delete()
                            await m.reply_photo(
                                photo=f"{thumbnail}",
                                caption=f"""
**   : [{songname}]({url})
   : {duration}
   : {chat_id}
   : {m.from_user.mention}**
""",
                            )
                        except Exception as ep:
                            await huehue.edit(f"`{ep}`")

@Client.on_message(    filters.user(SUDO_USERS) & filters.command(["_"], prefixes=f"{REKU}"))
@authorized_users_only
async def vplay(client, m: Message):
    replied = m.reply_to_message
    chat_id = m.chat.id
    m.chat.title
    if replied:
        if replied.video or replied.document:
            await m.delete()
            huehue = await replied.reply("**    **")
            dl = await replied.download()
            link = replied.link
            if len(m.command) < 2:
                Q = 720
            else:
                pq = m.text.split(None, 1)[1]
                if pq == "720" or "480" or "360":
                    Q = int(pq)
                else:
                    Q = 720
                    await huehue.edit(                        "    :  720  480  360 \n     720    "                 )

            if replied.video:
                songname = replied.video.file_name[:35] + "..."
            elif replied.document:
                songname = replied.document.file_name[:35] + "..."

            if chat_id in QUEUE:
                pos = add_to_queue(chat_id, songname, dl, link, "Video", Q)
                await huehue.delete()
                # await m.reply_to_message.delete()
                await m.reply_photo(
                    photo="https://telegra.ph/file/8fe4f047bcf3921590a74.jpg",
                    caption=f"""
**  : [{songname}]({link})
   : {chat_id}
   : {m.from_user.mention}**
""",
                )
            else:
                if Q == 720:
                    hmmm = HighQualityVideo()
                elif Q == 480:
                    hmmm = MediumQualityVideo()
                elif Q == 360:
                    hmmm = LowQualityVideo()
                await call_py.join_group_call(
                    chat_id,
                    AudioVideoPiped(dl, HighQualityAudio(), hmmm),
                    stream_type=StreamType().pulse_stream,
                )
                add_to_queue(chat_id, songname, dl, link, "Video", Q)
                await huehue.delete()
                # await m.reply_to_message.delete()
                await m.reply_photo(
                    photo="https://telegra.ph/file/8fe4f047bcf3921590a74.jpg",
                    caption=f"""
**  : [{songname}]({link})
   : {chat_id}
   : {m.from_user.mention}**
""",                )

    else:
        if len(m.command) < 2:
            await m.reply(                "**       **"            )
        else:
            await m.delete()
            huehue = await m.reply("**  ")
            query = m.text.split(None, 1)[1]
            search = ytsearch(query)
            Q = 720
            hmmm = HighQualityVideo()
            if search == 0:
                await huehue.edit(                    "**    **"                )
            else:
                songname = search[0]
                url = search[1]
                duration = search[2]
                thumbnail = search[3]
                hm, ytlink = await ytdl(url)
                if hm == 0:
                    await huehue.edit(f"**    ** \n\n`{ytlink}`")
                else:
                    if chat_id in QUEUE:
                        pos = add_to_queue(chat_id, songname, ytlink, url, "Video", Q)
                        await huehue.delete()
                        await m.reply_photo(
                            photo=f"{thumbnail}",
                            caption=f"""
**   : [{songname}]({url})
   : {duration}
   : {chat_id}
   : {m.from_user.mention}**
""",                        )
                    else:
                        try:
                            await call_py.join_group_call(                                chat_id,                                AudioVideoPiped(ytlink, HighQualityAudio(), hmmm),                                stream_type=StreamType().pulse_stream,                            )
                            add_to_queue(chat_id, songname, ytlink, url, "Video", Q)
                            await huehue.delete()
                            await m.reply_photo(
                                photo=f"{thumbnail}",
                                caption=f"""
**   : [{songname}]({url})
   : {duration}
   : {chat_id}
   : {m.from_user.mention}**
""",                            )
                        except Exception as ep:
                            await huehue.edit(f"`{ep}`")

@Client.on_message(    filters.user(SUDO_USERS) & filters.command([" "], prefixes=f"{REKU}"))
@authorized_users_only
async def playfrom(client, m: Message):
    chat_id = m.chat.id
    if len(m.command) < 2:
        await m.reply(            f"** :** \n\n`{REKU}   [        ]` \n"        )
    else:
        args = m.text.split(maxsplit=1)[1]
        if ";" in args:
            chat = args.split(";")[0]
            limit = int(args.split(";")[1])
        else:
            chat = args
            limit = 10
            lmt = 9
        await m.delete()
        hmm = await m.reply(f" {limit}    {chat}**")
        try:
            async for x in bot.search_messages(chat, limit=limit, filter="audio"):
                location = await x.download()
                if x.audio.title:
                    songname = x.audio.title[:30] + "..."
                else:
                    songname = x.audio.file_name[:30] + "..."
                link = x.link
                if chat_id in QUEUE:
                    add_to_queue(chat_id, songname, location, link, "Audio", 0)
                else:
                    await call_py.join_group_call(                        chat_id,                        AudioPiped(location),                        stream_type=StreamType().pulse_stream,                    )
                    add_to_queue(chat_id, songname, location, link, "Audio", 0)
                    await m.reply_photo(
                        photo="https://telegra.ph/file/8fe4f047bcf3921590a74.jpg",
                        caption=f"""
**     {chat}
  : [{songname}]({link})
  : {chat_id}
   : {m.from_user.mention}**
""",                    )
            await hmm.delete()
            await m.reply(                f"  {lmt}     \n�  {REKU}_     **"            )
        except Exception as e:
            await hmm.edit(f"**  ** \n`{e}`")

@Client.on_message(    filters.user(SUDO_USERS) & filters.command([" ", "queue"], prefixes=f"{REKU}"))
@authorized_users_only
async def playlist(client, m: Message):
    chat_id = m.chat.id
    if chat_id in QUEUE:
        chat_queue = get_queue(chat_id)
        if len(chat_queue) == 1:
            await m.delete()
            await m.reply(                f"**   :** \n[{chat_queue[0][0]}]({chat_queue[0][2]}) | `{chat_queue[0][3]}`",                disable_web_page_preview=True,            )
        else:
            QUE = f"**   :** \n[{chat_queue[0][0]}]({chat_queue[0][2]}) | `{chat_queue[0][3]}` \n\n**   :**"
            l = len(chat_queue)
            for x in range(1, l):
                hmm = chat_queue[x][0]
                hmmm = chat_queue[x][2]
                hmmmm = chat_queue[x][3]
                QUE = QUE + "\n" + f"**#{x}** - [{hmm}]({hmmm}) | `{hmmmm}`\n"
            await m.reply(QUE, disable_web_page_preview=True)
    else:
        await m.reply("**    **")
@Client.on_message(filters.user(SUDO_USERS) & filters.command([""], prefixes=f"{REKU}"))
@authorized_users_only
async def skip(client, m: Message):
    await m.delete()
    chat_id = m.chat.id
    if len(m.command) < 2:
        op = await skip_current_song(chat_id)
        if op == 0:
            await m.reply("**        !**")
        elif op == 1:
            await m.reply("      **")
        else:
            await m.reply(                f"**   ** \n**  ** - [{op[0]}]({op[1]}) | `{op[2]}`",                disable_web_page_preview=True,            )
    else:
        skip = m.text.split(None, 1)[1]
        OP = "**        : -**"
        if chat_id in QUEUE:
            items = [int(x) for x in skip.split(" ") if x.isdigit()]
            items.sort(reverse=True)
            for x in items:
                if x == 0:
                    pass
                else:
                    hm = await skip_item(chat_id, x)
                    if hm == 0:
                        pass
                    else:
                        OP = OP + "\n" + f"**{x}** - {hm}"
            await m.reply(OP)

@Client.on_message(    filters.user(SUDO_USERS) & filters.command(["", ""], prefixes=f"{REKU}"))
@authorized_users_only
async def stop(client, m: Message):
    await m.delete()
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.leave_group_call(chat_id)
            clear_queue(chat_id)
            await m.reply("**     **")
        except Exception as e:
            await m.reply(f"**  ** \n`{e}`")
    else:
        await m.reply("**     !**")
@Client.on_message(    filters.user(SUDO_USERS) & filters.command([""], prefixes=f"{REKU}"))
@authorized_users_only
async def pause(client, m: Message):
    await m.delete()
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.pause_stream(chat_id)
            await m.reply(                f"**    .**\n\n�        � `{REKU}_`"            )
        except Exception as e:
            await m.reply(f"**  ** \n`{e}`")
    else:
        await m.reply("**     !**") 
@Client.on_message(    filters.user(SUDO_USERS) & filters.command(["_"], prefixes=f"{REKU}"))
@authorized_users_only
async def resume(client, m: Message):
    await m.delete()
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.resume_stream(chat_id)
            await m.reply(                f"**     **"            )
        except Exception as e:
            await m.reply(f"**  ** \n`{e}`")
    else:
        await m.reply("**      !**")
