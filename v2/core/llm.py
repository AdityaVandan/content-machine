from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from core.config import settings


def call_llm(system_prompt: str, user_prompt: str, config: dict) -> str:
    """Thin LangChain wrapper around OpenRouter. Returns plain text response."""
    llm = ChatOpenAI(
        model=config.get("model", settings.openrouter_model),
        max_tokens=config.get("max_tokens", 2000),
        temperature=config.get("temperature", 0.7),
        openai_api_key=settings.openrouter_api_key,
        openai_api_base="https://openrouter.ai/api/v1",
    )
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ]
    response = llm.invoke(messages)
    return response.content
