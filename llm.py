import os
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")

client = OpenAI(
    base_url="https://api.sarvam.ai/v1",
    api_key=SARVAM_API_KEY,
)

# Clean Markdown-style formatting from text before TTS
def clean_for_tts(text: str) -> str:
    # Remove bold and italic
    text = re.sub(r"(\*\*|__)(.*?)\1", r"\2", text)
    text = re.sub(r"(\*|_)(.*?)\1", r"\2", text)

    # NEW: Remove markdown headings (e.g., ###) at the start of lines
    text = re.sub(r"^\s*#+\s?", "", text, flags=re.MULTILINE)

    # NEW: Convert markdown links like [text](url) to just "text"
    text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)

    # NEW: Clean up extra newlines that can result from removing headings
    text = re.sub(r"\n{2,}", "\n", text).strip()

    return text

def query_llm(user_query: str, local_context: str = "") -> str:
    """
    Queries the LLM with the user's query and optional local context.
    """
    # --- UPDATED: The system prompt is now dynamic ---
    # It includes the list of nearby hospitals if local_context is provided.
    system_prompt = f"""
    तुम एक ग्रामीण हेल्थ असिस्टेंट हो। सरल हिंदी में, 1000 शब्दों से कम में, संक्षिप्त उत्तर दो।<think> टैग का इस्तेमाल मत करो।
    {local_context}
    उपयोगकर्ता के सवाल का जवाब देते समय, यदि उपयुक्त हो तो दिए गए स्थानीय स्थानों की सिफारिश करें।
    """
    
    try:
        stream = client.chat.completions.create(
            model="sarvam-m",
            messages=[
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": user_query}
            ],
            reasoning_effort="high",
            max_completion_tokens=4096,
            stream=True
        )

        full_reply = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                full_reply += chunk.choices[0].delta.content

        # Process the reply to remove think tags, etc.
        if "</think>" in full_reply:
            reply = full_reply.split("</think>")[-1].strip("</s>").strip()
        else:
            reply = full_reply.strip("</s>").strip()

        # Graceful Failure Logic for incomplete sentences
        if reply and not reply.strip().endswith(('।', '.', '?', '!')):
             print("⚠️ Detected incomplete response from Sarvam AI. Returning a user-friendly error.")
             return "माफ कीजिए, एआई से पूरा जवाब नहीं मिला। कृपया अपना सवाल छोटा करके फिर से पूछें।"

        # If the response is complete, clean and return it.
        reply_cleaned = clean_for_tts(reply)

        return reply_cleaned

    except Exception as e:
        print(f"❌ Error calling Sarvam API: {e}")
        return "माफ कीजिए, एआई से जवाब नहीं मिला।"
