# SME_Operations_Orchestrator-PortoDing
## Folder Structure
```
SME-Ops-Orchestrator/
├── docs/                        # Documentation & Diagrams
│   ├── README.md
│   ├── CONTRIBUTING.md
│   ├── architecture_diag.png    # System flow (Router, RAG, Tools)
│   ├── api_spec.yaml            # OpenAPI/Swagger specs
│   └── pii_governance.md        # How you handle PII masking/security
│
├── backend/                     # FastAPI Backend (The Orchestrator)
│   ├── app/
│   │   ├── api/                 # API Route Handlers
│   │   │   ├── auth.py          # Role-based login (RBAC)
│   │   │   │── tickets.py       # Task/State management logic
│   │   │   ├── chatbot.py       # RAG & Copilot endpoints
│   │   │   └── inventory.py     # Google Sheets proxy
│   │   │
│   │   ├── core/                # The "Brain" (Orchestration logic)
│   │   │   ├── orchestrator.py  # Main ReAct loop & Router
│   │   │   ├── security.py      # PII masking & Permission checks
│   │   │   └── config.py        # Env vars (Z.AI API Keys, etc.)
│   │   │
│   │   ├── services/            # Framework-independent business logic
│   │   │   ├── parser.py        # OCR + GLM Master JSON Extraction
│   │   │   ├── rag_service.py   # Vector DB (Chroma/Pinecone) logic
│   │   │   └── google_sheets.py # Google Sheets API integration
│   │   │
│   │   ├── models/              # Database & Pydantic Schemas
│   │   │   ├── schemas.py       # Master Extraction JSON Schema
│   │   │   └── database.py      # Logs & User Role relational DB
│   │   │
│   │   └── utils/               # Helpers
│   │       └── hashing.py       # Binary content hashing for deduplication
│   │
│   ├── tests/                   # Unit & Integration tests
│   ├── main.py                  # Entry point
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/                    # Website (React/Next.js)
│   ├── src/
│   │   ├── components/          # Reusable UI (TaskCards, SourcePanel)
│   │   ├── hooks/               # API call logic
│   │   ├── pages/               # Dashboard, Inventory, Logs, Login
│   │   └── context/             # Auth & Global State
│   ├── public/                  # Assets & Icons
│   └── package.json
│
└── vault/                       # (Ignored in Git) Local storage for raw files
```