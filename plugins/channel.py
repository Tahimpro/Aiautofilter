from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from info import CHANNELS, MOVIE_UPDATE_CHANNEL, ADMINS, LOG_CHANNEL
from database.ia_filterdb import save_file, unpack_new_file_id
from utils import get_poster, temp
import re
from database.users_chats_db import db

processed_movies = set()
media_filter = filters.document | filters.video

@Client.on_message(filters.chat(CHANNELS) & media_filter)
async def media(bot, message):
    bot_id = bot.me.id
    media = getattr(message, message.media.value, None)

    if media and media.mime_type in ['video/mp4', 'video/x-matroska']:
        media.file_type = message.media.value
        media.caption = message.caption
        success_sts = await save_file(media)

        if success_sts == 'suc' and await db.get_send_movie_update_status(bot_id):
            file_id, file_ref = unpack_new_file_id(media.file_id)
            await send_movie_updates(bot, file_name=media.file_name, caption=media.caption, file_id=file_id)


async def movie_name_format(file_name):
    filename = re.sub(r'http\S+', '', re.sub(r'@\w+|#\w+', '', file_name))
    filename = filename.replace('_', ' ') \
                      .replace('[', '') \
                      .replace(']', '') \
                      .replace('(', '') \
                      .replace(')', '') \
                      .replace('{', '') \
                      .replace('}', '') \
                      .replace('.', ' ') \
                      .replace('@', '') \
                      .replace(':', '') \
                      .replace(';', '') \
                      .replace("'", '') \
                      .replace('-', '') \
                      .replace('!', '').strip()
    return filename


async def check_qualities(text, qualities: list):
    quality = [q for q in qualities if q in text]
    return ", ".join(quality) if quality else None


async def send_movie_updates(bot, file_name, caption, file_id):
    try:
        year_match = re.search(r"\b(19|20)\d{2}\b", caption)
        year = year_match.group(0) if year_match else None

        pattern = r"(?i)(?:s|season)0*(\d{1,2})"
        season = re.search(pattern, caption) or re.search(pattern, file_name)

        if year:
            file_name = file_name[:file_name.find(year) + 4]
        elif season:
            season = season.group(1)
            file_name = file_name[:file_name.find(season) + 1]

        qualities = [
    "ORG", "org", "HDcam", "HDCAM", "HQ", "hq", "HDRip", "hdrip", "Camrip", "CAMRip", "hdtc", "HDTC",
    "predvd", "PreDVD", "DVDscr", "dvdscr", "DVDScreen", "dvdscreen", "HDTS", "hdts", "WEB-DL", "web-dl",
    "WEBRip", "webrip", "BluRay", "bluray", "BRRip", "brrip", "DVDRip", "dvdrip", "TS", "ts", "R5", "r5",
    "SCR", "scr", "Screener", "screener", "TC", "tc", "Telecine", "telecine", "PPV", "ppv", "TVRip", "tvrip",
    "VHSRip", "vhsrip", "PDTV", "pdtv", "DVDR", "dvdr", "BDRip", "bdrip", "BDRemux", "bdremux", "Remux", "remux",
    "WEB", "web", "WEB-DLRip", "web-dlrip", "WEB-HDRip", "web-hdrip", "HMAX", "hmax", "NF", "nf", "AMZN", "amzn",
    "DSNP", "dsnp", "iTunes", "itunes", "VODRip", "vodrip", "SCREENER", "screener", "Workprint", "workprint",
    "TCRip", "tcrip", "Festival", "festival", "Final", "final", "Unrated", "unrated", "Extended", "extended", 
    "Director's Cut", "director's cut", "HEVC", "hevc", "x265", "X265", "x264", "X264", "AVC", "avc", "h264", "H264",
    "h265", "H265", "VP9", "vp9", "AV1", "av1", "DivX", "divx", "XviD", "xvid", "MPEG2", "mpeg2", "MPEG4", "mpeg4",
    "AMZN", "amzn", "NF", "nf", "HMAX", "hmax", "DSNP", "dsnp", "HULU", "hulu", "iTunes", "itunes", "AppleTV", "appletv",
    "Scene", "scene", "P2P", "p2p", "Repack", "repack", "Proper", "proper", "REAL", "real", "Line", "line", "Internal", "internal"
]

        quality = await check_qualities(caption, qualities) or "HDRip"

        caption = caption.lower().replace("hin", "hindi").replace("eng", "english").replace("tam", "tamil") \
            .replace("tel", "telugu").replace("mal", "malayalam").replace("kan", "kannada") \
            .replace("pun", "punjabi").replace("ben", "bengali").replace("mar", "marathi") \
            .replace("guj", "gujrati").replace("kor", "korean").replace("jap", "japanese") \
            .replace("bho", "bhojpuri")

        language = ""
        nb_languages = [
            "Hindi", "Bengali", "English", "Marathi", "Tamil", "Telugu", "Malayalam",
            "Kannada", "Punjabi", "Gujrati", "Korean", "Japanese", "Bhojpuri", "Dual", "Multi"
        ]

        for lang in nb_languages:
            if lang.lower() in caption:
                language += f"{lang}, "
        language = language.strip(", ") or "Original Language"

        movie_name = await movie_name_format(file_name)
        if movie_name in processed_movies:
            return
        processed_movies.add(movie_name)

        imdb = await get_poster(movie_name)
        imdb_url = imdb.get("url") if imdb else "N/A"
        kind = imdb.get("kind", "Unknown").strip().upper().replace(" ", "") if imdb else "#UPDATED"
        genres = imdb.get("genres", "Unknown").strip() if imdb else "UNKNOWN"

        caption_message = (
            f"<b>✅ {movie_name} #{kind}</b>\n\n"
            f"<blockquote>🎙️{language}</blockquote>\n\n"
            f"<b>🌟[IMDB Info]({imdb_url})</b>\n"
            f"<b>📽️Genre : {genres}</b>"
        )

        search_movie = movie_name.replace(" ", '-')
        movie_update_channel = await db.movies_update_channel_id()

        btn = [
            [InlineKeyboardButton('𝖦𝖾𝗍 𝖥𝗂𝗅𝖾 🔎', url=f'https://telegram.me/{temp.U_NAME}?start=getfile-{search_movie}')]
        ]

        reply_markup = InlineKeyboardMarkup(btn)

        await bot.send_message(
            movie_update_channel if movie_update_channel else MOVIE_UPDATE_CHANNEL,
            text=caption_message, reply_markup=reply_markup, disable_web_page_preview=True
        )

    except Exception as e:
        print('Failed to send movie update. Error - ', e)
        await bot.send_message(LOG_CHANNEL, f'Failed to send movie update. Error - {e}')