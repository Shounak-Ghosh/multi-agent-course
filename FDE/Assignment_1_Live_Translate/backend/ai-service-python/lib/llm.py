"""
lib/llm.py — the LLM translation call  (TODO: you implement)
============================================================
One job: turn an English string into Mexican Spanish using an LLM.

Provider is your choice. The default example below is Anthropic Claude
(`pip install anthropic`, set ANTHROPIC_API_KEY). Hamza's launched version
used Google Gemini — either is fine. Whatever you pick:

  - Write a PROMPT that pins the register to Mexican Spanish (es-MX), not
    generic/Castilian Spanish. Ask for ONLY the translation, no preamble.
  - Keep numbers, prices ($), and product/model codes unchanged.
  - Return a clean string (strip quotes/whitespace the model may add).

FAIL LOUD: do NOT wrap the call in a try/except that returns `text` on error.
If the provider fails, let the exception propagate so the caller returns a 502.
Silently returning the untranslated input is an automatic fail on this
assignment (and a real production bug — it ships English while looking healthy).
"""
import os

from openai import AsyncOpenAI

MODEL_DEFAULT = os.getenv("MODEL", "gpt-4o-mini")

SYSTEM_PROMPT = (
    "You are a professional translator. Translate the user's English text into "
    "natural MEXICAN Spanish (es-MX) — the register spoken in Mexico, not "
    "Castilian or generic Spanish. Return ONLY the translation — no quotes, no "
    "notes, no preamble. Keep numbers, prices ($), URLs, and product/model codes "
    "(e.g. SKU-4471) exactly as they appear."
)

_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    # lazy so the key is read after load_dotenv() has run in app.py
    global _client
    if _client is None:
        _client = AsyncOpenAI()  # reads OPENAI_API_KEY
    return _client


async def translate_text(text: str, target: str = "es-MX", model: str = MODEL_DEFAULT) -> str:
    """Return `text` translated into `target` (Mexican Spanish by default).

    FAIL LOUD: provider errors propagate to the caller (which returns a 502);
    this function never falls back to returning the untranslated input.
    """
    resp = await _get_client().chat.completions.create(
        model=model,
        max_tokens=1024,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Translate into {target}:\n{text}"},
        ],
    )
    translated = (resp.choices[0].message.content or "").strip()
    # strip a matching pair of wrapping quotes the model may add
    for open_q, close_q in (('"', '"'), ("'", "'"), ("“", "”"), ("«", "»")):
        if len(translated) >= 2 and translated[0] == open_q and translated[-1] == close_q:
            translated = translated[1:-1].strip()
            break
    return translated
