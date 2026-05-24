"""Telegram Bot 消息发送模块"""

from telegram import Bot
from telegram.error import TelegramError, BadRequest
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from logger import get_logger

logger = get_logger(__name__)
bot = Bot(token=TELEGRAM_BOT_TOKEN)


async def send_message(text: str, parse_mode: str | None = None) -> bool:
    """发送消息到 Telegram。默认纯文本模式，避免 Markdown 解析出错。"""
    try:
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=text,
            parse_mode=parse_mode,
        )
        logger.debug("Telegram 发送成功 | preview=%s", text[:80])
        return True
    except BadRequest as e:
        if parse_mode and "parse" in str(e).lower():
            logger.warning("Markdown 解析失败，降级为纯文本重试")
            try:
                await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)
                return True
            except TelegramError as e2:
                logger.error("Telegram 发送失败(纯文本) | error=%s", e2)
                return False
        logger.error("Telegram 发送失败 | error=%s", e)
        return False
    except TelegramError as e:
        logger.error("Telegram 发送失败 | error=%s", e)
        return False
