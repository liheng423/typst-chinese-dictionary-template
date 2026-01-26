import os
import re
from typing import Optional

import config
from constants import PROMPT
from google import genai
from google.genai import types


def _build_prompt(raw_text: str, pagenumber: int, last_word: str) -> str:
    raw_text = raw_text.strip()
    return f"{PROMPT}\n页码:{pagenumber}\n上一页最后一个词条:{last_word}\n原文:\n{raw_text}\n"


def _extract_code_block(text: str) -> str:
    match = re.search(r"```(?:csv)?\s*(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


def format_with_ai_studio(
    raw_text: str,
    last_word: str,
    page_number: int,
    model: str,
    api_key: Optional[str] = None,
) -> str:
    api_key = api_key 
    client = genai.Client(api_key=api_key) if api_key else genai.Client()

    attempts = max(1, config.RETRY_MAX)
    last_error: Optional[Exception] = None
    for _ in range(attempts):
        try:
            response = client.models.generate_content(
                model=model,
                config=types.GenerateContentConfig(
                    temperature=1.0,
                    top_p=0.95,
                    max_output_tokens=5e4,
                ),
                contents=_build_prompt(raw_text, page_number, last_word),
            )

            text = response.text or ""
            if not text.strip():
                raise RuntimeError("AI Studio response was empty.")

            return _extract_code_block(text)
        except Exception as exc:
            last_error = exc

    raise RuntimeError("AI Studio failed after retries.") from last_error
