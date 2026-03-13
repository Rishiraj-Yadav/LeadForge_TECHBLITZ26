"""LLM provider factory using Gemini as primary."""

from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import get_settings

settings = get_settings()


def get_llm(temperature: float = 0.2):
    return ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=temperature,
    )
