import signal
import sys

import uvicorn
from fastapi import FastAPI

from routes.webhook import router as webhook_router
from config import HOST, PORT

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

    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=False,
        log_level="info",
        access_log=True,
    )
