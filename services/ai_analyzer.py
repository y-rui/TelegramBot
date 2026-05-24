from openai import AsyncOpenAI
from config import AI_API_KEY, AI_API_BASE, AI_MODEL
from logger import get_logger

logger = get_logger(__name__)

client = AsyncOpenAI(api_key=AI_API_KEY, base_url=AI_API_BASE) if AI_API_KEY else None

SYSTEM_PROMPT = """你是一个专业的量化交易分析助手。用户会将来自聚宽（JoinQuant）量化平台的交易信号、策略日志或市场数据发送给你。

请对每条消息进行简洁的分析，包括：
1. **信号解读**：如果是交易信号，解读其含义
2. **风险评估**：评估潜在风险
3. **操作建议**：给出简短的操作建议（如有必要）

如果消息不是交易相关内容，直接简短回复即可。"""


async def analyze_message(content: str) -> str | None:
    if client is None:
        logger.debug("AI_API_KEY 未配置，跳过分析")
        return None
    logger.info("开始 AI 分析 | model=%s | content=%s", AI_MODEL, content[:80])
    try:
        response = await client.chat.completions.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": content},
            ],
            temperature=0.3,
            max_tokens=1000,
        )
        result = response.choices[0].message.content
        logger.info("AI 分析完成 | result=%s", result[:80] if result else "(空)")
        return result
    except Exception as e:
        logger.error("AI 分析失败 | error=%s", e)
        return None
