from pyrogram import Client, filters
from pyrogram.types import Message

@Client.on_message(filters.command("about") & filters.private)
async def about_handler(bot, message: Message):
    about_text = (
        "📌 <b><blockquote><u>About Tᴏɴʏ Sᴛᴀʀᴋ</u></blockquote></b>\n"
        "〰〰〰〰〰〰〰〰〰〰〰\n\n"
        "<b>❗️𝖠𝖽𝗆𝗂𝗇            - @Mr_Official_300\n"
        "❗️𝖫𝗈𝗀𝗌   - @TonyStark_Logs_Channel\n"
        "❗️𝖧𝗈𝗌𝗍𝖾𝖽 𝖲𝖾𝗋𝗏𝖾𝗋 - <a href='https://www.heroku.com/'>Heroku</a>\n"
        "❗️Database        - <a href='https://www.mysql.com/'>MySQL</a></b>"
    )

    # Reply with about message
    await message.reply_text(about_text, quote=True, disable_web_page_preview=True)

    # Delete the incoming /about command message
    await message.delete()