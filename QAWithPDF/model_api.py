import sys

from llama_index.llms.gemini import Gemini
import google.generativeai as genai
from dotenv import load_dotenv

from QAWithPDF.config import settings
from QAWithPDF.exception import customexception
from logger import logging

load_dotenv()


def _model_candidates(preferred_model: str) -> list[str]:
    candidates = [
        preferred_model,
        "gemini-2.0-flash",
        "gemini-flash-latest",
        "gemini-2.5-flash",
    ]
    unique: list[str] = []
    for model_name in candidates:
        normalized = model_name.strip()
        if normalized and normalized not in unique:
            unique.append(normalized)
    return unique


def load_model():
    try:
        if settings.llm_provider.lower() != "gemini":
            raise ValueError("Only 'gemini' provider is currently configured")

        if not settings.gemini_api_key:
            raise ValueError("GOOGLE_API_KEY is required for Gemini provider")

        genai.configure(api_key=settings.gemini_api_key)
        last_error: Exception | None = None
        for model_name in _model_candidates(settings.gemini_model_name):
            try:
                model = Gemini(model=model_name, api_key=settings.gemini_api_key)
                logging.info("Loaded Gemini model: %s", model_name)
                return model
            except Exception as ex:
                last_error = ex
                logging.warning(
                    "Failed to load Gemini model %s. Trying fallback.", model_name
                )

        if last_error is not None:
            raise last_error
        raise ValueError("No valid Gemini model found")
    except Exception as e:
        raise customexception(e, sys)


def summarize_chat_title(question: str) -> str:
    fallback = " ".join(question.strip().split())[:80] or "New Chat"
    prompt = (
        "Summarize the user's question as a concise chat title. "
        "Return only the title, with 3 to 7 words, no quotes, no punctuation at the end.\n\n"
        f"Question: {question.strip()}"
    )
    try:
        response = load_model().complete(prompt)
        title = " ".join(str(getattr(response, "text", response)).strip().split())
        title = title.strip("\"'`")
        return title[:80] or fallback
    except Exception:
        logging.warning(
            "Unable to summarize chat title with Gemini; using question fallback."
        )
        return fallback
