from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from info import CHANNELS, MOVIE_UPDATE_CHANNEL, ADMINS, LOG_CHANNEL
from database.ia_filterdb import save_file, unpack_new_file_id
import re
from database.users_chats_db import db

processed_movies = set()
media_filter = filters.document | filters.video

@Client.on_message(filters.chat(CHANNELS) & media_filter)
async def media(bot, message):
    try:
        bot_id = bot.me.id
        media = message.document or message.video  # Fetch document or video

        if media and media.mime_type in ['video/mp4', 'video/x-matroska']:
            file_id = media.file_id
            file_name = media.file_name
            caption = message.caption or ""

            success_sts = await save_file(media)

            if success_sts == 'suc' and await db.get_send_movie_update_status(bot_id):
                file_id, file_ref = unpack_new_file_id(file_id)
                await send_movie_updates(bot, file_name=file_name, caption=caption, file_id=file_id)

    except Exception as e:
        await bot.send_message(LOG_CHANNEL, f"Error in media handler: {str(e)}")

async def movie_name_format(file_name):
    filename = re.sub(r'http\S+', '', file_name)
    filename = re.sub(r'[@#]\w+', '', filename)
    filename = re.sub(r'[{}().;:\'!_-]', ' ', filename).strip()
    return filename

async def check_qualities(text, qualities):
    quality = [q for q in qualities if q in text]
    return ", ".join(quality) if quality else "HDRip"

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

        qualities = ["ORG", "org", "hdcam", "HDCAM", "HQ", "hq", "HDRip", "hdrip", 
                     "camrip", "WEB-DL", "CAMRip", "hdtc", "predvd", "DVDscr", "dvdscr", 
                     "dvdrip", "HDTC", "dvdscreen", "HDTS", "hdts"]
        quality = await check_qualities(caption, qualities)

        languages = ["Hindi", "Bengali", "English", "Marathi", "Tamil", "Telugu", 
                     "Malayalam", "Kannada", "Punjabi", "Gujarati", "Korean", 
                     "Japanese", "Bhojpuri", "Dual", "Multi"]
        language = ", ".join([lang for lang in languages if lang.lower() in caption.lower()]) or "Unknown"

        movie_name = await movie_name_format(file_name)
        if movie_name in processed_movies:
            return

        processed_movies.add(movie_name)
        
        caption_message = (
            f"<b>#𝖬𝗈𝗏𝗂𝖾/𝖲𝖾𝗋𝗂𝖾𝗌 𝖠𝖽𝖽𝖾𝖽✅\n\n"
            f"🎬 𝖭𝖺𝗆𝖾:- <code>{movie_name}</code>\n\n"
            f"<blockquote>🎙️ 𝖫𝖺𝗇𝗀𝗎𝖺𝗀𝖾:- {language}\n\n"
            f"🎚️ 𝖰𝗎𝖺𝗅𝗂𝗍𝗒:- {quality}</blockquote></b>"
        )

        search_movie = movie_name.replace(" ", '-')
        movie_update_channel = await db.movies_update_channel_id() or MOVIE_UPDATE_CHANNEL

        buttons = [
            [InlineKeyboardButton('📂 𝖦𝖾𝗍 𝖥𝗂𝗅𝖾 📂', url=f'https://telegram.me/{temp.U_NAME}?start=getfile-{search_movie}')],
            [InlineKeyboardButton('📤 𝖧𝗈𝗐 𝖳𝗈 𝖣𝗈𝗐𝗇𝗅𝗈𝖺𝖽 📤', url='https://t.me/How2download_Cpflix_Files/4')]
        ]

        reply_markup = InlineKeyboardMarkup(buttons)

        await bot.send_message(movie_update_channel, text=caption_message, reply_markup=reply_markup)

    except Exception as e:
        await bot.send_message(LOG_CHANNEL, f"Failed to send movie update. Error - {str(e)}")