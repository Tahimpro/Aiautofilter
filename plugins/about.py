from pyrogram import Client, filters
from pyrogram.types import Message

@Client.on_message(filters.command("about") & filters.private)
async def about_handler(bot, message: Message):
    about_text = (
        "📌 <b>About 🇹ᴏɴʏ 🇸ᴛᴀʀᴋ</b>\n"
        "〰〰〰〰〰〰〰〰〰〰〰\n\n"
        "<blockquote><b>❗️𝖠𝖽𝗆𝗂𝗇            - @Mr_Official_300\n"
        "❗️𝖫𝗈𝗀𝗌   - @TonyStark_Logs_Channel\n"
        "❗️𝖧𝗈𝗌𝗍𝖾𝖽 𝖲𝖾𝗋𝗏𝖾𝗋 - 𝖧𝖾𝗋𝗈𝗄𝗎\n"
        "❗️Database        - 𝖬𝗒𝖲𝖰𝖫</b></blockquote>"
    )

    # Reply with about message
    await message.reply_text(about_text, quote=True, disable_web_page_preview=True)

    # Delete the incoming /about command message
    await message.delete()
