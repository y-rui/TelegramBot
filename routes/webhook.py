"""聚宽消息 Webhook 路由"""
import hashlib
import hmac

from fastapi import APIRouter, Request, HTTPException, Form
from fastapi.responses import JSONResponse

from bot import send_message
from services.ai_analyzer import analyze_message
from config import WEBHOOK_SECRET
from logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/webhook", tags=["webhook"])


def verify_signature(message: str, signature: str) -> bool:
    if not WEBHOOK_SECRET:
        logger.debug("WEBHOOK_SECRET 未配置，跳过签名验证")
        return True
    expected = hmac.new(
        WEBHOOK_SECRET.encode(), message.encode(), hashlib.sha256
    ).hexdigest()
    ok = hmac.compare_digest(expected, signature)
    if not ok:
        logger.warning(
            "签名验证失败 | 期望=%s | 收到=%s | message=%s",
            expected[:16] + "...", signature[:16] + "..." if signature else "(空)",
            message[:80],
        )
    return ok


@router.post("/joinquant")
async def joinquant_webhook(
    message: str = Form(default=""),
    signature: str = Form(default="", alias="X-Signature"),
):
    logger.info("收到 Form 消息 | content=%s", message[:120])

    if not verify_signature(message, signature):
        raise HTTPException(status_code=403, detail="签名验证失败")

    if not message:
        return JSONResponse({"status": "ok", "detail": "消息为空，跳过"})

    ok = await send_message(f"📩 聚宽消息\n\n{message}")
    logger.info("转发消息到 Telegram | ok=%s", ok)

    analysis = await analyze_message(message)
    if analysis:
        ok2 = await send_message(f"🤖 AI 分析\n\n{analysis}")
        logger.info("AI 分析完成并发送 | ok=%s", ok2)
    else:
        logger.info("AI 分析跳过（未配置或调用失败）")

    return JSONResponse({
        "status": "ok",
        "forwarded": ok,
        "ai_analyzed": analysis is not None,
    })


@router.post("/joinquant/json")
async def joinquant_webhook_json(request: Request):
    try:
        data = await request.json()
    except Exception:
        logger.warning("JSON 解析失败")
        raise HTTPException(status_code=400, detail="Invalid JSON")

    message = data.get("message", "")
    signature = data.get("signature", "")
    logger.info("收到 JSON 消息 | content=%s", message[:120])

    if not verify_signature(message, signature):
        raise HTTPException(status_code=403, detail="签名验证失败")

    if not message:
        return JSONResponse({"status": "ok", "detail": "消息为空"})

    await send_message(f"📩 聚宽消息\n\n{message}")
    logger.info("转发消息到 Telegram | ok=True")

    analysis = await analyze_message(message)
    if analysis:
        await send_message(f"🤖 AI 分析\n\n{analysis}")
        logger.info("AI 分析完成并发送")
    else:
        logger.info("AI 分析跳过")

    return JSONResponse({"status": "ok"})


@router.get("/health")
async def health():
    return {"status": "healthy"}
