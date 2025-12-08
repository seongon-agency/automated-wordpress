# Session State - Railway Deployment Project

## Current Status
- **Date:** 2025-12-08
- **Phase:** Phase 2 - Frontend Setup (COMPLETE)
- **Status:** Frontend pages created, ready for testing

---

## Project Overview

Deploying WordPress SEO Publishing System to Railway using:
- **Frontend:** Next.js 14+ (React)
- **Backend:** FastAPI (Python) - **Reuses existing Streamlit code**
- **Database:** Railway PostgreSQL
- **UI Framework:** Tailwind CSS + shadcn/ui
- **UI Language:** Vietnamese

---

## Architecture

```
Next.js (Frontend) ←→ FastAPI (Backend) ←→ PostgreSQL (Railway)
                            ↓
                    [Your existing Python code]
```

**Key benefit:** ~80% of Python code is reused directly!

---

## Progress Tracker

### Planning Phase ✅
- [x] Analyzed current Streamlit codebase
- [x] Created PLAN.md with full architecture
- [x] Created SESSION_STATE.md for tracking
- [x] User chose Option A (Next.js + FastAPI)
- [x] User answers clarification questions
- [x] User approved plan ("execute")

### Phase 1: Backend Setup (FastAPI) ✅
- [x] Create backend/ folder structure
- [x] Set up FastAPI with main.py
- [x] Copy existing services from Streamlit
- [x] Create API routers (projects, publish, patterns, history)
- [x] Update database code for PostgreSQL (psycopg2)
- [x] Create requirements.txt
- [x] Create Dockerfile
- [ ] Test endpoints with Swagger

### Phase 2: Frontend Setup (Next.js) ✅
- [x] Initialize Next.js project
- [x] Configure Tailwind + shadcn/ui
- [x] Create layout with sidebar
- [x] Create Home page
- [x] Create Projects list page
- [x] Create New Project page
- [x] Create Edit Project page
- [x] Create Publish page
- [x] Create Batch Publish page
- [x] Create History page
- [x] Create AI Patterns page
- [x] Create Scan Template page
- [x] Create environment config files
- [x] Create Dockerfile for frontend

### Phase 3: Testing ⏳
- [ ] Test backend locally
- [ ] Test frontend locally
- [ ] Test API integration

### Phase 4: Deploy to Railway
- [ ] Create Railway project
- [ ] Deploy backend service
- [ ] Deploy frontend service
- [ ] Set up PostgreSQL database
- [ ] Configure environment variables
- [ ] Test production deployment

---

## User Decisions (Confirmed)

| Question | Decision |
|----------|----------|
| Database | Railway PostgreSQL |
| Authentication | Single-user (no login) |
| Google OAuth | Published URLs only |
| UI Language | Vietnamese |

---

## Backend Files Created

```
backend/
├── main.py                 # FastAPI entry point
├── requirements.txt        # Python dependencies
├── Dockerfile              # Railway deployment
├── .env.example            # Environment template
├── database/
│   ├── __init__.py
│   └── db.py               # PostgreSQL operations (psycopg2)
├── routers/
│   ├── __init__.py
│   ├── projects.py         # /api/projects endpoints
│   ├── publish.py          # /api/publish endpoints
│   ├── patterns.py         # /api/patterns endpoints
│   └── history.py          # /api/history endpoints
├── services/
│   ├── __init__.py
│   ├── google_docs.py      # Google Docs conversion
│   ├── image_processor.py  # Image download/resize
│   ├── wordpress.py        # WordPress upload
│   ├── html_transformer.py # HTML transformation
│   ├── ai_patterns.py      # Claude AI patterns
│   └── workflow.py         # Publishing workflow
└── utils/
    ├── __init__.py
    ├── html_extractor.py   # HTML utilities
    └── pattern_engine.py   # Regex pattern engine
```

---

## Frontend Files Created

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx          # Main layout with sidebar
│   │   ├── page.tsx            # Home page (dashboard)
│   │   ├── globals.css         # Global styles
│   │   ├── projects/
│   │   │   ├── page.tsx        # Projects list
│   │   │   ├── new/
│   │   │   │   └── page.tsx    # Create new project
│   │   │   └── [id]/
│   │   │       └── page.tsx    # Edit project
│   │   ├── publish/
│   │   │   ├── page.tsx        # Single publish
│   │   │   └── batch/
│   │   │       └── page.tsx    # Batch publish
│   │   ├── history/
│   │   │   └── page.tsx        # Publishing history
│   │   └── patterns/
│   │       ├── page.tsx        # AI pattern editor
│   │       └── scan/
│   │           └── page.tsx    # Scan HTML template
│   ├── components/
│   │   ├── app-sidebar.tsx     # Navigation sidebar
│   │   └── ui/                 # shadcn/ui components
│   ├── lib/
│   │   ├── api.ts              # API client
│   │   └── utils.ts            # Utilities
│   └── hooks/
│       └── use-mobile.ts       # Mobile detection
├── next.config.ts              # Next.js config (standalone output)
├── Dockerfile                  # Railway deployment
├── .env.example                # Environment template
├── package.json
└── tailwind.config.ts
```

---

## API Endpoints (Backend)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/projects` | GET | List all projects |
| `/api/projects` | POST | Create new project |
| `/api/projects/{id}` | GET | Get single project |
| `/api/projects/{id}` | PUT | Update project |
| `/api/projects/{id}` | DELETE | Delete project |
| `/api/publish` | POST | Run publishing workflow |
| `/api/publish/batch` | POST | Batch publishing |
| `/api/publish/convert` | POST | Test Google Docs conversion |
| `/api/patterns/modify` | POST | AI modify patterns |
| `/api/patterns/generate` | POST | AI generate patterns |
| `/api/patterns/{project_id}` | GET | Get project patterns |
| `/api/history` | GET | Get publishing history |

---

## Frontend Pages (Vietnamese UI)

| Route | Page Name | Description |
|-------|-----------|-------------|
| `/` | Trang chủ | Dashboard with stats & quick actions |
| `/projects` | Danh sách dự án | Projects list with CRUD |
| `/projects/new` | Tạo dự án mới | New project form |
| `/projects/[id]` | Chỉnh sửa dự án | Edit project form |
| `/publish` | Xuất bản đơn | Single post publishing |
| `/publish/batch` | Xuất bản hàng loạt | Batch publishing |
| `/history` | Lịch sử xuất bản | Publishing history |
| `/patterns` | Chỉnh sửa Pattern | AI pattern editor |
| `/patterns/scan` | Quét mẫu HTML | Generate patterns from template |

---

## Change Log

### 2025-12-08
- **Created:** Agent_Railway folder
- **Created:** PLAN.md v1.0.0 - Initial plan
- **Updated:** PLAN.md v1.1.0 - Changed to FastAPI + Next.js hybrid
- **Updated:** PLAN.md v1.2.0 - User decisions finalized
- **Started:** Phase 1 execution
- **Created:** Backend folder structure
- **Created:** Database module with PostgreSQL (psycopg2)
- **Copied:** Services from Streamlit (google_docs, image_processor, wordpress, html_transformer)
- **Created:** AI patterns service (Claude integration)
- **Created:** Publishing workflow service
- **Created:** FastAPI main.py with CORS
- **Created:** API routers (projects, publish, patterns, history)
- **Created:** requirements.txt and Dockerfile
- **Started:** Phase 2 execution
- **Created:** Next.js project with TypeScript
- **Configured:** Tailwind CSS + shadcn/ui
- **Created:** App layout with Vietnamese sidebar navigation
- **Created:** All frontend pages (Home, Projects, Publish, History, Patterns)
- **Created:** API client library
- **Created:** Frontend Dockerfile for Railway

---

## Next Steps

1. Test backend locally:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload
   # Open http://localhost:8000/docs for Swagger
   ```

2. Test frontend locally:
   ```bash
   cd frontend
   npm install
   npm run dev
   # Open http://localhost:3000
   ```

3. Create Railway project and deploy services

---

## Environment Variables Required

### Backend (.env)
```env
DATABASE_URL=postgresql://user:password@host:port/database
ANTHROPIC_API_KEY=sk-ant-...
FRONTEND_URL=http://localhost:3000
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

*Updated: 2025-12-08*
