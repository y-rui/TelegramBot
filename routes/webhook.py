"""聚宽消息 Webhook 路由"""
import hashlib
import hmac

from fastapi import APIRouter, Request, HTTPException, Form
from fastapi.responses import JSONResponse

from bot import send_message
from services.ai_analyzer import analyze_message
from config import WEBHOOK_SECRET

router = APIRouter(prefix="/webhook", tags=["webhook"])


def verify_signature(message: str, signature: str) -> bool:
    """验证消息签名: HMAC-SHA256(message, secret)"""
    if not WEBHOOK_SECRET:
        return True
    expected = hmac.new(
        WEBHOOK_SECRET.encode(), message.encode(), hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


@router.post("/joinquant")
async def joinquant_webhook(
    message: str = Form(default=""),
    signature: str = Form(default="", alias="X-Signature"),
):
    """接收聚宽 Form 格式消息"""
    if not verify_signature(message, signature):
        raise HTTPException(status_code=403, detail="签名验证失败")

    if not message:
        return JSONResponse({"status": "ok", "detail": "消息为空，跳过"})

    forwarded = await send_message(f"📩 **聚宽消息**\n\n{message}")

    analysis = await analyze_message(message)
    if analysis:
        ai_sent = await send_message(f"🤖 **AI 分析**\n\n{analysis}")
    else:
        ai_sent = None

    return JSONResponse({
        "status": "ok",
        "forwarded": forwarded,
        "ai_analyzed": ai_sent is not None,
    })


@router.post("/joinquant/json")
async def joinquant_webhook_json(request: Request):
    """接收聚宽 JSON 格式消息: {"message": "xxx", "signature": "xxx"}"""
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    message = data.get("message", "")
    signature = data.get("signature", "")

    if not verify_signature(message, signature):
        raise HTTPException(status_code=403, detail="签名验证失败")

    if not message:
        return JSONResponse({"status": "ok", "detail": "消息为空"})

    await send_message(f"📩 **聚宽消息**\n\n{message}")

    analysis = await analyze_message(message)
    if analysis:
        await send_message(f"🤖 **AI 分析**\n\n{analysis}")

    return JSONResponse({"status": "ok"})


@router.get("/health")
async def health():
    return {"status": "healthy"}
