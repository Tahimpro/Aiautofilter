import asyncio
from pyrogram import Client, filters
from pyrogram.types import *

# Replace this with your own channel ID
CHANNEL_ID = -1001797797270  

@Client.on_message(filters.channel & filters.media)
async def add_button(client, message):
    if message.chat.id == CHANNEL_ID:
        button = InlineKeyboardMarkup(
            [[InlineKeyboardButton("📥 𝖬𝗈𝗏𝗂𝖾 𝖱𝖾𝗊𝗎𝖾𝗌𝗍 𝖦𝗋𝗈𝗎𝗉 📥", url="https://t.me/CpFlicks_Movies")]]
        )
        
        try:
            # Try to add the button to the message
            await message.edit_reply_markup(reply_markup=button)
            await asyncio.sleep(0.5)  # Small delay to handle rapid messages
        except Exception as e:
            print(f"Failed to add button: {e}")
