# SME_Operations_Orchestrator-PortoDing
## Folder Structure
```
SME-Ops-Orchestrator/
├── .env                         # Environment variables (API Keys, etc.)
├── .gitignore                   # Git exclusion rules
├── main.py                      # FastAPI Entry point
├── requirements.txt             # Python dependencies
│
├── app/                         # Backend Logic (The Orchestrator)
│   ├── api/                     # API Route Handlers
│   │   ├── auth.py              # Role-based login (RBAC)
│   │   ├── customers.py         # Customer management
│   │   ├── intake.py            # Document ingestion & extraction
│   │   ├── inventory.py         # Google Sheets proxy / Inventory
│   │   ├── orders.py            # Order processing
│   │   ├── telegram.py          # Telegram bot integration
│   │   ├── tickets.py           # Task/State management logic
│   │   └── whatsapp.py          # WhatsApp webhook & messaging
│   │
│   ├── core/                    # The "Brain" (Orchestration logic)
│   │   ├── config.py            # Settings & Env loader
│   │   ├── orchestrator.py      # Main ReAct loop & Router
│   │   └── security.py          # PII masking & Permission checks
│   │
│   ├── models/                  # Data Schemas
│   │   └── schemas.py           # Pydantic models (Master JSON, etc.)
│   │
│   ├── services/                # Framework-independent business logic
│   │   ├── gdrive_service.py    # Google Drive file management
│   │   ├── glm_service.py       # GLM-4V Vision / Model interaction
│   │   ├── google_sheets.py     # Google Sheets API integration
│   │   ├── parser.py            # OCR + Document parsing logic
│   │   ├── rag_service.py       # RAG Retrieval logic
│   │   ├── tele_service.py      # Telegram business logic
│   │   ├── ticket_service.py    # Ticket lifecycle & state logic
│   │   ├── vector_db.py         # Qdrant client & Point management
│   │   └── wa_service.py        # WhatsApp business logic
│   │
│   └── utils/                   # Helpers
│       └── hashing.py           # Binary deduplication & content hashing
│
├── tests/                       # Unit & Integration tests
│   ├── conftest.py              # Pytest configuration
│   ├── api/                     # API endpoint tests
│   ├── core/                    # Logic & Orchestrator tests
│   ├── services/                # Service layer tests (Parser, etc.)
│   │   └── test_data/           # Sample files (.pdf, .docx, .xlsx)
│   └── utils/                   # Utility tests
│
├── downloaded_media/            # Local storage for raw files (Ignored in Git)
├── .pytest_cache/               # Pytest runtime cache
│
└── frontend/                    # Website (React/Next.js)
    └── src/
        ├── App.tsx
        ├── index.css
        ├── main.tsx
        ├── types.ts
        ├── components/          
        │   ├── ChatBubble.tsx
        │   ├── DashboardView.tsx
        │   ├── DocumentsView.tsx
        │   ├── InventoryView.tsx
        │   ├── LandingPageView.tsx
        │   └── TicketsView.tsx
        └── lib/
            ├── api.ts
            └── utils.ts

```

## Video Pitching Deck Link
```
https://drive.google.com/file/d/1a8O0h_GueSMaK9GfzrB6BbIXEjs0KhrI/view?usp=sharing
```

## Document Link
```
System Analysis Documentation (SAD)
https://drive.google.com/file/d/1POyn49af8k5esOL-isNv-ZjBa26RWwI_/view?usp=sharing

Product Requirement Documentation (PRD)
https://drive.google.com/file/d/1S9RkSNlRmm6tlpsBDLIFq0IehCarunL2/view?usp=sharing

Sample Testing Analysis Documentation (STAD)
https://drive.google.com/file/d/180eOIT44jumFRSTAdWSP52mRneoPznSO/view?usp=sharing

Pitching Deck Slide PortoDing
https://drive.google.com/file/d/1sEj0vuVv6XmRbRWeA7Ob24emXAde6Jf1/view?usp=sharing
```