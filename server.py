import os
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv
from typing import Optional # <-- ADDED THIS IMPORT

import llm  # Your existing llm.py

# Load environment variables from .env file
# Note: We no longer need the GOOGLE_MAPS_API_KEY for this version
load_dotenv()

# --- Pydantic Models for API Request Bodies ---

class AiQuery(BaseModel):
    text: str
    # --- THESE LINES ARE NOW UPDATED FOR COMPATIBILITY ---
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class NearbyQuery(BaseModel):
    latitude: float
    longitude: float
    place_type: str # e.g., "hospital", "pharmacy", "clinic"

# Initialize the FastAPI app
app = FastAPI(title="GraminGPT API")

# --- OpenStreetMap API Helper Function ---

def find_nearby_places(latitude: float, longitude: float, place_type: str, radius: int = 10000):
    """
    Finds nearby places using the OpenStreetMap Overpass API.
    Radius is in meters (default is 10km).
    """
    # The Overpass API endpoint
    overpass_url = "https://overpass-api.de/api/interpreter"
    
    # This is the query in the Overpass Query Language.
    # It looks for nodes, ways, and relations (nwr) with the amenity tag
    # matching our place_type within the specified radius of our coordinates.
    overpass_query = f"""
    [out:json];
    (
      nwr["amenity"="{place_type}"](around:{radius},{latitude},{longitude});
    );
    out center;
    """
    
    try:
        response = requests.post(overpass_url, data=overpass_query)
        response.raise_for_status()
        results = response.json().get("elements", [])
        
        places = []
        for place in results:
            tags = place.get("tags", {})
            name = tags.get("name", "N/A")
            if name != "N/A": # Only include places that have a name
                # OSM address data is split into many tags, we'll combine what we can
                address_parts = [
                    tags.get('addr:street'),
                    tags.get('addr:suburb'),
                    tags.get('addr:city')
                ]
                address = ", ".join(part for part in address_parts if part is not None)
                
                places.append({
                    "name": name,
                    "address": address if address else "Address not available",
                    "rating": "N/A", # OSM does not have a rating system
                })
        return places[:6] # Limit to top 6 results
    except requests.exceptions.RequestException as e:
        print(f"❌ OpenStreetMap API Error: {e}")
        return []


# --- API Endpoints (These remain the same) ---

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Welcome to the Rural Healthcare Assistant API!"}

@app.post("/ask-rural-assistant/")
async def handle_ai_query(query: AiQuery):
    """
    Handles a health query, finds nearby places if location is provided,
    and returns a location-aware AI response.
    """
    user_query = query.text
    print(f"📝 Received query: '{user_query}'")
    
    local_context = ""
    if query.latitude is not None and query.longitude is not None:
        print(f"📍 Location provided. Searching for nearby hospitals...")
        nearby_hospitals = find_nearby_places(query.latitude, query.longitude, "hospital")
        if nearby_hospitals:
            hospital_info = "\n".join([f"- {h['name']} ({h['address']})" for h in nearby_hospitals])
            local_context = f"यहां आसपास के कुछ अस्पताल हैं:\n{hospital_info}\n"

    ai_response = llm.query_llm(user_query, local_context)
    print(f"💬 LLM Response: '{ai_response}'")

    if not ai_response:
        raise HTTPException(status_code=500, detail="AI model failed to generate a complete response.")

    return {"answer": ai_response}


@app.post("/nearby-health-centers/")
async def handle_nearby_query(query: NearbyQuery):
    """
    Finds and returns a list of nearby health centers based on type.
    """
    print(f"📍 Searching for nearby '{query.place_type}'...")
    places = find_nearby_places(query.latitude, query.longitude, query.place_type)
    
    if not places:
        return {"places": []}
        
    return {"places": places}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
