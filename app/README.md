youtube-chat-app/
├── app/
│   ├── main.py                  # FastAPI “entrypoint”
│   ├── core/
│   │   └── config.py            # API keys, constants
│   ├── services/
│   │   ├── transcription.py     # fetch & cache YouTube transcripts
│   │   ├── chunking.py          # split text into overlapping windows
│   │   ├── embedding.py         # embed chunks & build/lookup vector store
│   │   ├── summarizer.py        # map-reduce summary chain
│   │   └── rag.py               # build & run ConversationalRetrievalChain
│   ├── api/
│   │   └── routers/
│   │       ├── summary.py       # `/summarize/{video_id}` endpoint
│   │       └── chat.py          # `/chat/{video_id}` endpoint
│   └── models/
│       └── schemas.py           # Pydantic models for request/response
├── requirements.txt             # FastAPI, langchain, openai, yt-transcript-api, chromadb…
├── .env                         # OPENAI_API_KEY, (optionally) YT_API creds
└── README.md