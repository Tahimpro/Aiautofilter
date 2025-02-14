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


async def get_imdb(file_name):
    imdb_file_name = await movie_name_format(file_name)
    imdb = await get_poster(imdb_file_name)
    if imdb:
        return imdb.get('poster')
    return None


async def movie_name_format(file_name):
    filename = re.sub(r'http\S+', '', re.sub(r'@\w+|#\w+', '', file_name)
                      .replace('_', ' ')
                      .replace('[', '')
                      .replace(']', '')
                      .replace('(', '')
                      .replace(')', '')
                      .replace('{', '')
                      .replace('}', '')
                      .replace('.', ' ')
                      .replace('@', '')
                      .replace(':', '')
                      .replace(';', '')
                      .replace("'", '')
                      .replace('-', '')
                      .replace('!', '')).strip()
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
            "ORG", "org", "hdcam", "HDCAM", "HQ", "hq", "HDRip", "hdrip", "camrip", "WEB-DL",
            "CAMRip", "hdtc", "predvd", "DVDscr", "dvdscr", "dvdrip", "HDTC", "dvdscreen", "HDTS", "hdts"
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
        language = language.strip(", ") or "Not Idea"

        movie_name = await movie_name_format(file_name)
        if movie_name in processed_movies:
            return
        processed_movies.add(movie_name)

        caption_message = (
            f"<b>#𝖬𝗈𝗏𝗂𝖾/𝖲𝖾𝗋𝗂𝖾𝗌-𝖴𝗉𝖽𝖺𝗍𝖾✅\n\n"
            f"🎬 𝖭𝖺𝗆𝖾:- {movie_name}\n\n"
            f"<blockquote>🎙️ 𝖫𝖺𝗇𝗀𝗎𝖺𝗀𝖾:- #{language}\n\n"
            f"🎚️ 𝖰𝗎𝖺𝗅𝗂𝗍𝗒:- #{quality}</blockquote></b>"
        )

        search_movie = movie_name.replace(" ", '-')
        movie_update_channel = await db.movies_update_channel_id()

        btn = [
            [InlineKeyboardButton('📂 𝖦𝖾𝗍 𝖥𝗂𝗅𝖾 📂', url=f'https://telegram.me/{temp.U_NAME}?start=getfile-{search_movie}')],
            [InlineKeyboardButton('📥 𝖧𝗈𝗐 𝖳𝗈 𝖣𝗈𝗐𝗇𝗅𝗈𝖺𝖽 📥', url='https://t.me/How2download_Cpflix_Files/4')]
        ]

        reply_markup = InlineKeyboardMarkup(btn)

        # Uncomment the following lines if you want to send a poster
        # poster_url = await get_imdb(movie_name)
        # if poster_url:
        #     await bot.send_photo(
        #         movie_update_channel if movie_update_channel else MOVIE_UPDATE_CHANNEL,
        #         photo=poster_url, caption=caption_message, reply_markup=reply_markup
        #     )
        # else:
        no_poster = "https://telegra.ph/file/88d845b4f8a024a71465d.jpg"
        await bot.send_message(
            movie_update_channel if movie_update_channel else MOVIE_UPDATE_CHANNEL,
            text=caption_message, reply_markup=reply_markup
        )

    except Exception as e:
        print('Failed to send movie update. Error - ', e)
        await bot.send_message(LOG_CHANNEL, f'Failed to send movie update. Error - {e}')