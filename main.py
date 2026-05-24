import signal
import sys

import uvicorn
from fastapi import FastAPI

from logger import setup_logging, get_logger
from routes.webhook import router as webhook_router
from config import HOST, PORT, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, LOG_DIR

setup_logging(log_dir=LOG_DIR)
logger = get_logger(__name__)

app = FastAPI(title="Telegram Bot Gateway", version="1.0.0")
app.include_router(webhook_router)


@app.get("/")
async def root():
    return {"service": "Telegram Bot Gateway", "status": "running"}


def handle_sigterm(sig, frame):
    print("\n[Server] 收到停止信号，正在退出...")
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, handle_sigterm)
    signal.signal(signal.SIGINT, handle_sigterm)

    logger.info("Telegram Bot Gateway 启动中...")
    logger.info("Telegram Bot Token | 已配置=%s", bool(TELEGRAM_BOT_TOKEN))
    logger.info("Telegram Chat ID | 已配置=%s", bool(TELEGRAM_CHAT_ID))
    from config import AI_API_KEY, WEBHOOK_SECRET
    logger.info("AI API Key | 已配置=%s", bool(AI_API_KEY))
    logger.info("Webhook Secret | 已配置=%s", bool(WEBHOOK_SECRET))
    logger.info("日志目录 | %s", LOG_DIR)

    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=False,
        log_config=None,  # 由 setup_logging() 全权管理日志
    )
