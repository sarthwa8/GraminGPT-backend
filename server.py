# server.py (Final Version)

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import llm  # Your existing llm.py

# --- This is new ---
# We define a Pydantic model to specify the structure
# of the incoming request body. It expects a JSON object
# with a single key "text".
class Query(BaseModel):
    text: str

# Initialize the FastAPI app
app = FastAPI(title="GraminGPT API")

@app.get("/")
def read_root():
    """A simple endpoint to check if the server is running."""
    return {"status": "ok", "message": "Welcome to the Rural Healthcare Assistant API!"}

# --- This endpoint is now simplified ---
@app.post("/ask-rural-assistant/")
async def handle_query(query: Query):
    """
    This endpoint receives a text query in a JSON object, gets a response
    from the LLM, and returns the AI's answer as text.
    """
    # Extract the text from the request body
    user_query = query.text
    print(f"📝 Received query: '{user_query}'")

    # Check if the text is empty
    if not user_query:
        raise HTTPException(status_code=400, detail="Query text cannot be empty.")

    try:
        # 1. Get a response from the LLM (this is now the backend's main job)
        print("🤖 Querying LLM...")
        ai_response = llm.query_llm(user_query)
        print(f"💬 LLM Response: '{ai_response}'")
        
        # Handle cases where the LLM might fail
        if not ai_response:
             raise HTTPException(status_code=500, detail="AI model failed to generate a complete response.")

        # 2. Return the final answer in a JSON format
        return {"answer": ai_response}

    except Exception as e:
        # Catch any unexpected errors during the process
        print(f"❌ An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="An unexpected internal server error occurred.")

# This block allows you to run the server locally for testing
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
