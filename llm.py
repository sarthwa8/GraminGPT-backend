import os
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
# Reverting to use the SARVAM_API_KEY from your .env file
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")

# Pointing the client back to Sarvam's servers
client = OpenAI(
    base_url="https://api.sarvam.ai/v1",
    api_key=SARVAM_API_KEY,
)

# The clean_for_tts function remains the same.
def clean_for_tts(text: str) -> str:
    text = re.sub(r"(\*\*|__)(.*?)\1", r"\2", text)
    text = re.sub(r"(\*|_)(.*?)\1", r"\2", text)
    text = re.sub(r"^\s*#+\s?", "", text, flags=re.MULTILINE)
    text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)
    text = re.sub(r"\n{2,}", "\n", text).strip()
    return text

def query_llm(user_query: str) -> str:
    try:
        stream = client.chat.completions.create(
            model="sarvam-m",
            messages=[
                {
                    "role": "system",
                    "content": "तुम एक ग्रामीण हेल्थ असिस्टेंट हो। सरल हिंदी में सीधे उत्तर दो। <think> टैग का इस्तेमाल मत करो।",
                },
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

        # --- NEW: Graceful Failure Logic ---
        # If the reply is not empty but doesn't end with proper punctuation,
        # it's likely cut off. We will return a custom error message instead.
        if reply and not reply.strip().endswith(('।', '.', '?', '!')):
             print("⚠️ Detected incomplete response from Sarvam AI. Returning a user-friendly error.")
             return "माफ कीजिए, एआई से पूरा जवाब नहीं मिला। कृपया अपना सवाल छोटा करके फिर से पूछें।"

        # If the response is complete, clean and return it.
        reply_cleaned = clean_for_tts(reply)

        return reply_cleaned

    except Exception as e:
        print(f"❌ Error calling Sarvam API: {e}")
        return "माफ कीजिए, एआई से जवाब नहीं मिला।"
