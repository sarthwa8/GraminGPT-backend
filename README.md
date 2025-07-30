GraminGPT Backend API
This repository contains the backend server for GraminGPT, a voice-based AI healthcare assistant designed to provide accessible and location-aware health information for rural communities.

🌟 Features
AI-Powered Health Assistance: Utilizes the Sarvam AI model to understand and answer general health-related questions in simple Hindi.

Location-Aware Healthcare Directory: Finds nearby hospitals, clinics, and pharmacies using the user's location via the free and open-source OpenStreetMap API.

Intelligent Recommendations: Enhances AI responses by providing context-aware recommendations for local healthcare facilities when relevant.

Built for Voice: Designed to be the "brain" for a voice-first mobile application, receiving queries and providing text answers ready for Text-to-Speech (TTS) conversion on the frontend.

🏗️ Architecture
This project follows a modern client-server architecture:

Backend (This Repository): A robust API built with Python and FastAPI. It handles all business logic, including communication with the Sarvam AI and the OpenStreetMap API.

Frontend (Separate Project): A mobile application built with Flutter. The frontend is responsible for handling all user interactions, including speech-to-text, getting the user's GPS location, and text-to-speech for the final answer.

🔌 API Endpoints
The server exposes two primary endpoints:

1. POST /nearby-health-centers/
   Provides a simple directory of nearby healthcare facilities.

Request Body:

{
"latitude": 30.7333,
"longitude": 76.7794,
"place_type": "hospital"
}

Success Response:

{
"places": [
{
"name": "PGIMER",
"address": "Madhya Marg, Sector 12, Chandigarh",
"rating": "N/A"
}
]
}

2. POST /ask-rural-assistant/
   The core endpoint for asking health-related questions. It can optionally use the user's location to provide smarter, context-aware answers.

Request Body:

{
"text": "मुझे डेंगू हो गया है, मैं क्या करूँ?",
"latitude": 30.7333,
"longitude": 76.7794
}

Success Response:

{
"answer": "डेंगू होने पर आपको तुरंत डॉक्टर से सलाह लेनी चाहिए... आपके पास कुछ नजदीकी अस्पताल हैं जैसे PGIMER..."
}

🚀 Setup and Local Installation
To run this server on your local machine, follow these steps:

Clone the Repository:

git clone https://github.com/your-username/your-repository-name.git
cd your-repository-name

Create and Activate a Virtual Environment:

# Create the environment

python3 -m venv venv

# Activate it (macOS/Linux)

source venv/bin/activate

# Or activate it (Windows)

.\venv\Scripts\activate

Install Dependencies:

pip install -r requirements.txt

Create an Environment File:

Create a file named .env in the project's root directory.

Add your Sarvam API key to this file:

SARVAM_API_KEY="your_sarvam_api_key_here"

Run the Server:

uvicorn server:app --reload

The server will now be running at http://127.0.0.1:8000. You can access the interactive API documentation at http://127.0.0.1:8000/docs.

☁️ Deployment
This project is ready for deployment and includes a Dockerfile for easy containerization.

Push to GitHub: Ensure all your code is pushed to a GitHub repository.

Deploy on a Cloud Platform: Use a service like Render to deploy the project.

Connect your GitHub repository to Render.

Render will automatically detect and use the Dockerfile.

Remember to add SARVAM_API_KEY as a secret environment variable in your Render service settings.
