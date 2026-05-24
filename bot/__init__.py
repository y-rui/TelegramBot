from telegram import Bot
from telegram.error import TelegramError
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

bot = Bot(token=TELEGRAM_BOT_TOKEN)


async def send_message(text: str, parse_mode: str = "Markdown") -> bool:
    """发送消息到 Telegram"""
    try:
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=text,
            parse_mode=parse_mode,
        )
        return True
    except TelegramError as e:
        print(f"[TelegramBot] 发送消息失败: {e}")
        return False


async def send_raw_message(text: str) -> bool:
    """发送纯文本消息（不使用 Markdown 解析，避免格式化错误）"""
    return await send_message(text, parse_mode=None)
