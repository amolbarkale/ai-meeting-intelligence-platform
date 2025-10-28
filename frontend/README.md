# ai-meeting-intelligence-platform
1. Project Goal:
To build a highly scalable AI Meeting Intelligence Platform using Python (FastAPI) for the backend. The platform will take meeting recordings (audio/video), process them through an AI pipeline, and present structured insights on a React frontend.
2. High-Level Architecture:
We'll design a decoupled, service-oriented architecture. The FastAPI backend will expose a RESTful API that the React frontend can consume. The AI processing will happen asynchronously to avoid blocking the API and to handle potentially long-running tasks.
3. The AI Pipeline:
This is the heart of the project. For each uploaded file, the pipeline will execute the following steps in order:
1. File Ingestion & Storage: Securely receive the file and store it.
2. Audio Extraction: If the file is a video, we'll first need to extract the audio stream.
3. Transcription: The audio will be fed to Whisper.cpp to get a highly accurate transcript with speaker diarization (identifying who spoke when).
4. Enrichment Layer (LLM): The transcript will then be processed by an LLM via Ollama to:
* Generate a concise summary.
* Extract key topics, decisions, and action items.
* Perform sentiment analysis on the conversation.
* Suggest tags for topic modeling.
5. Vectorization & Storage: The generated insights and transcript chunks will be converted into vector embeddings and stored in ChromaDB to power the search functionality.
6. Data Persistence: All the generated data (summary, action items, sentiment, etc.) will be saved in the SQLite database, linked to the original meeting.
4. API Design:
We will design a clean, well-documented API. Here are some of the key endpoints we will need to create:
POST /api/v1/meetings/upload: To upload a new audio/video file. This will be an asynchronous endpoint.
GET /api/v1/meetings/{meeting_id}/status: To check the processing status of a meeting (e.g., "transcribing", "summarizing", "completed").
GET /api/v1/meetings/{meeting_id}: To retrieve all the processed data for a single meeting (transcript, summary, action items, etc.).
GET /api/v1/meetings: To get a list of all past meetings.
GET /api/v1/search?query={search_term}: To search across all meetings for specific keywords or concepts using the vector database.
5. Getting Started: The Project Structure
Before we write a single line of code for the features, it's critical to set up a professional project structure. This is a key part of "Code quality and organization." A good structure will make the application easier to maintain, scale, and test.
Here is a proposed directory structure for our FastAPI backend:

ai-meeting-intelligence-platform/
├── app/
│   ├── __init__.py
│   ├── main.py             # Main FastAPI app instance and startup events
│   ├── api/                # API endpoint definitions
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── endpoints/
│   │       │   ├── __init__.py
│   │       │   ├── meetings.py
│   │       │   └── search.py
│   │       └── schemas.py      # Pydantic models for request/response
│   ├── core/               # Core logic and configuration
│   │   ├── __init__.py
│   │   ├── config.py         # Configuration management
│   │   └── security.py       # API keys, CORS, etc.
│   ├── services/           # Business logic for AI pipeline
│   │   ├── __init__.py
│   │   ├── transcription_service.py
│   │   ├── llm_service.py
│   │   └── storage_service.py
│   ├── db/                 # Database setup and models
│   │   ├── __init__.py
│   │   ├── database.py       # Database session management
│   │   └── models.py         # SQLAlchemy models
│   └── tests/              # Unit and integration tests
│       ├── __init__.py
│       └── test_meetings.py
├── .env                    # Environment variables
├── .gitignore
├── requirements.txt
└── README.md