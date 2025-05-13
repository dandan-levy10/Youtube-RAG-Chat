### YouTube-RAG FastAPI Service
A FastAPI backend for on-demand summarization and RAG-style chat over YouTube video transcripts, powered by LangChain and your choice of LLM.

#### Features
- Lazy ingestion: transcripts are downloaded, chunked, embedded, and stored in Chroma only once per video.

- Summary endpoint (POST /api/summarize): fetches (or reuses cached) transcript and returns a concise summary via a “stuff” chain.

- Chat endpoint (POST /api/chat): on first use builds a vector index, then serves conversational Q&A that retrieves the most relevant chunks.

- Caching: summary cache + vectorstore with idempotent ingestion logic.

- Modular: clear separation of services, routers, and data models.

### Repository Structure

your_project/
├── app/
│   ├── main.py            # FastAPI app entrypoint
│   ├── core/
│   │   └── config.py      # Environment & settings
│   ├── services/
│   │   ├── chunking.py         # Process transcript documents into chunks
│   │   ├── embedding.py        # Embed chunks and upload to vector db
│   │   ├── rag.py              # RAG QA chat with history
│   │   ├── summariser.py       # Summarise video transcripts
│   │   └── transcription.py    # Retrieve transcript (from cache or download)
│   └── api/
│       └── routers/
│           ├── summary.py  # /api/summarize endpoint
│           └── chat.py     # /api/chat endpoint
├── transcript_cache/      # Raw transcript JSON files
├── summary_cache/         # Summary JSON files
├── chroma_db/             # Persisted Chroma vectorstore
├── .env                   # API keys & config
├── requirements.txt
└── README.md

### Setup
Clone & install

git clone https://github.com/yourusername/your_project.git
cd your_project
pip install -r requirements.txt


### Environment
Copy .env.example to .env and fill in your keys:

OPENAI_API_KEY=sk-…
CHROMA_DIR=./chroma_db
TRANSCRIPT_CACHE=./transcript_cache
SUMMARY_CACHE=./summaries_cache

### Run

uvicorn app.main:app --reload
The API will be available at http://127.0.0.1:8000.

### Interactive docs
Open http://127.0.0.1:8000/docs for Swagger UI.

### Usage
Summarize a Video
Request:
POST /api/summarize

{
  "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}

Response:

{
  "video_id": "dQw4w9WgXcQ",
  "summary": "Rick Astley's “Never Gonna Give You Up” was released in 1987…"
}

Chat with a Video
Request:
POST /api/chat

{
  "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "question": "Who is the singer?",
  "history": []
}

Response:

{
  "answer": "Rick Astley",
  "history": [
    ["Who is the singer?", "Rick Astley"]
  ]
}

### Next Steps

Frontend: build a simple React/Vue/HTML UI with two stages: “Get Summary” then “Chat.”

Performance: integrate background ingestion tasks or WebSockets for progress updates.

Model Swap: switch between local LLM (Ollama) and OpenAI via configuration.

Monitoring: add logging, metrics, and error tracking (e.g. Sentry).

📄 License
MIT © [Daniel Levy]
Feel free to fork and customize!