from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from info import LOG_CHANNEL  # Importing log channel from Info.py

# List of channels to check
HUB_CNL = [
    -1001826628728,  # Replace with your channel IDs
    -1002372412575
]

MOVIE_GROUP_LINK = "https://t.me/CpFlicks_Movies"  # Replace with your Movie Group link

@Client.on_message(filters.command("links"))
async def check_channels_and_send_links(bot, message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    not_joined_channels = []
    invite_links = {}

    for channel in HUB_CNL:
        try:
            member = await bot.get_chat_member(channel, user_id)
            if member.status not in ["member", "administrator", "owner"]:
                not_joined_channels.append(channel)

        except Exception as e:
            # Handle the USER_NOT_PARTICIPANT error by assuming user is not in the channel
            if "USER_NOT_PARTICIPANT" in str(e):
                not_joined_channels.append(channel)
            else:
                error_msg = f"❌ Error checking membership in channel {channel}: {e}"
                print(error_msg)
                await bot.send_message(LOG_CHANNEL, error_msg)

    if not not_joined_channels:
        text = (
            "<b>🎉 𝖢𝗈𝗇𝗀𝗋𝖺𝗍𝗎𝗅𝖺𝗍𝗂𝗈𝗇𝗌 🎉\n\n"
            "𝖸𝗈𝗎 𝖠𝗋𝖾 𝖠𝗅𝗋𝖾𝖺𝖽𝗒 𝖯𝗋𝖾𝗌𝖾𝗇𝗍 𝖨𝗇 𝖠𝗅𝗅 𝖮𝗎𝗋 𝖧𝗎𝖻 𝖢𝗁𝖺𝗇𝗇𝖾𝗅𝗌.</b>"
        )

        buttons = [[InlineKeyboardButton("📂 Movie Group 📂", url=MOVIE_GROUP_LINK)]]
    else:
        text = (
            "<b>🔗 𝖤𝗑𝗉𝗅𝗈𝗋𝖾 𝖺𝗅𝗅 𝗈𝗎𝗋 𝖫𝗂𝗇𝗄𝗌 𝗎𝗌𝗂𝗇𝗀 𝗍𝗁𝖾 𝖻𝗎𝗍𝗍𝗈𝗇𝗌 𝖻𝖾𝗅𝗈𝗐!\n\n"
            "𝖮𝗇𝖼𝖾 𝗒𝗈𝗎𝗋 𝗋𝖾𝗊𝗎𝖾𝗌𝗍 𝗂𝗌 𝗌𝗎𝖻𝗆𝗂𝗍𝗍𝖾𝖽, 𝗒𝗈𝗎'𝗅𝗅 𝖻𝖾 𝗂𝗇𝗌𝗍𝖺𝗇𝗍𝗅𝗒 𝖺𝖽𝖽𝖾𝖽 𝗍𝗈 𝗈𝗎𝗋 Channels!\n\n"
            "⚠️ 𝖭𝗈𝗍𝖾: 𝖳𝗁𝗂𝗌 𝖬𝖾𝗌𝗌𝖺𝗀𝖾 𝖵𝖺𝗅𝗂𝖽𝗂𝗍𝗒 𝖨𝗌 1 𝖬𝗂𝗇𝗎𝗍𝖾. 𝖨𝖿 𝗒𝗈𝗎𝗋 𝗆𝖾𝗌𝗌𝖺𝗀𝖾 𝗀𝗈𝗍 𝖽𝖾𝗅𝖾𝗍𝖾𝖽, 𝖼𝗅𝗂𝖼𝗄 /links 𝗍𝗈 𝗀𝖾𝗇𝖾𝗋𝖺𝗍𝖾 𝖺 𝗇𝖾𝗐 𝗈𝗇𝖾.\n\n"
            "🔥 𝖲𝗍𝖺𝗒 𝗎𝗉𝖽𝖺𝗍𝖾𝖽! 𝖩𝗈𝗂𝗇 @CpFlicks 𝖿𝗈𝗋 𝗆𝗈𝗋𝖾.</b>"
        )

        buttons = []

        for channel in not_joined_channels:
            try:
                invite_link = await bot.create_chat_invite_link(channel, creates_join_request=True)
                invite_links[channel] = invite_link.invite_link
                chat = await bot.get_chat(channel)
                buttons.append([InlineKeyboardButton(f"📌 Request to Join {chat.title}", url=invite_link.invite_link)])
            except Exception as e:
                error_msg = f"❌ Error generating invite link for {channel}: {e}"
                print(error_msg)
                await bot.send_message(LOG_CHANNEL, error_msg)

    reply_markup = InlineKeyboardMarkup(buttons)
    sent_message = await bot.send_message(chat_id, text, reply_markup=reply_markup, disable_web_page_preview=True)

    await asyncio.sleep(60)  # Wait for 1 minute

    # Revoke created invite links
    for channel, link in invite_links.items():
        try:
            await bot.revoke_chat_invite_link(channel, link)
        except Exception as e:
            error_msg = f"❌ Error revoking invite link for {channel}: {e}"
            print(error_msg)
            await bot.send_message(LOG_CHANNEL, error_msg)

    await sent_message.delete()  # Delete message after 1 minute