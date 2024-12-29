from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from bs4 import BeautifulSoup
import re
import aiohttp  # Using aiohttp for async HTTP requests
from web import keep_alive

BOT_TOKEN = "7289544815:AAHazCIKjEdiDcJb9LneDGGia-5Xpghbwl8"
BASE_URL = "https://opabhik.serv00.net/Watch.php?url="
TERABOX_PATTERN = r"https?://(?:\w+\.)?(terabox|1024terabox|freeterabox|teraboxapp|tera|teraboxlink|mirrorbox|nephobox|1024tera|momerybox|tibibox|terasharelink|teraboxshare|terafileshare)\.\w+"
LOG_CHANNEL_ID = "-1001564742493"  # Replace with your actual log channel's username or chat ID
FSubLink = "https://t.me/+Q8sRUuL-hzUwZGM1"  # Replace this with your private or public channel link

async def check_subscription(user_id, bot):
    """Check if a user is a member of the required channel."""
    try:
        channel_username = FSubLink.split("/")[-1]  # Extract the channel username from the link
        member = await bot.get_chat_member(channel_username, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command to welcome the user with an image and button."""
    user_id = update.message.from_user.id
    is_subscribed = await check_subscription(user_id, context.bot)

    if not is_subscribed:
        button = InlineKeyboardButton("✨ Join Channel", url=FSubLink)
        reply_markup = InlineKeyboardMarkup([[button]])
        await update.message.reply_text(
            "❌ You must join our channel to use this bot.\n"
            "Click the button below to join and then try again.",
            reply_markup=reply_markup,
        )
        return

    image_url = "https://envs.sh/ozm.jpg"  # Replace with the URL or local path
    button = InlineKeyboardButton("✨ Join Channel", url=FSubLink)
    reply_markup = InlineKeyboardMarkup([[button]])

    await update.message.reply_photo(
        photo=image_url,
        caption="👋 Hi! Welcome to the bot! Send a Terabox link, and I’ll create a stream link for you.",
        reply_markup=reply_markup,
    )

async def process_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process a Terabox link, fetch details, and create a new URL with a button."""
    user_id = update.message.from_user.id
    is_subscribed = await check_subscription(user_id, context.bot)

    if not is_subscribed:
        button = InlineKeyboardButton("✨ Join Channel", url=FSubLink)
        reply_markup = InlineKeyboardMarkup([[button]])
        await update.message.reply_text(
            "❌ You must join our channel to use this bot.\n"
            "Click the button below to join and then try again.",
            reply_markup=reply_markup,
        )
        return

    user_message = update.message.text.strip()

    if re.search(TERABOX_PATTERN, user_message):
        file_details = await fetch_file_details(user_message)

        if "error" in file_details:
            await update.message.reply_text(f"❌ Error fetching file details: {file_details['error']}")
            return

        file_name = file_details["file_name"]
        file_size = file_details["file_size"]
        thumbnail_url = file_details["thumbnail_url"]

        MAX_LENGTH = 100
        file_name = file_name[:MAX_LENGTH] + "..." if len(file_name) > MAX_LENGTH else file_name

        new_url = f"{BASE_URL}{user_message}"
        button = InlineKeyboardButton("🌐 Watch Online", url=new_url)
        reply_markup = InlineKeyboardMarkup([[button]])

        reply_text = (
            f"✅ **Here is your stream Link:**\n\n"
            f"📄 **File Name:** {file_name}\n\n"
            f"🔗 Click the button below to open the link."
        )

        if thumbnail_url:
            await update.message.reply_photo(
                photo=thumbnail_url,
                caption=reply_text,
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(reply_text, reply_markup=reply_markup)

        if thumbnail_url:
            await context.bot.send_photo(
                chat_id=LOG_CHANNEL_ID,
                photo=thumbnail_url,
                caption=reply_text,
                reply_markup=reply_markup
            )
        else:
            await context.bot.send_message(
                chat_id=LOG_CHANNEL_ID,
                text=reply_text,
                reply_markup=reply_markup
            )
    else:
        await update.message.reply_text(
            "❌ That doesn't look like a valid Terabox link.\n"
            "💡 Please send a link from domains like *terabox.com* or *terabox.co*."
        )

def main():
    """Run the bot."""
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_link))

    application.run_polling()

if __name__ == "__main__":
    keep_alive()
    main()
