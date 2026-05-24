from openai import AsyncOpenAI
from config import AI_API_KEY, AI_API_BASE, AI_MODEL

client = AsyncOpenAI(api_key=AI_API_KEY, base_url=AI_API_BASE)

SYSTEM_PROMPT = """你是一个专业的量化交易分析助手。用户会将来自聚宽（JoinQuant）量化平台的交易信号、策略日志或市场数据发送给你。

请对每条消息进行简洁的分析，包括：
1. **信号解读**：如果是交易信号，解读其含义
2. **风险评估**：评估潜在风险
3. **操作建议**：给出简短的操作建议（如有必要）

如果消息不是交易相关内容，直接简短回复即可。"""


async def analyze_message(content: str) -> str | None:
    """用 AI 分析消息内容，返回分析结果"""
    if not AI_API_KEY:
        return None
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
        return response.choices[0].message.content
    except Exception as e:
        print(f"[AI] 分析失败: {e}")
        return None
