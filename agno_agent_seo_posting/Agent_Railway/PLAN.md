# Railway Deployment Plan - WordPress SEO Publishing System

## Document Info
- **Created:** 2025-12-08
- **Status:** READY FOR APPROVAL
- **Version:** 1.2.0

---

## 1. Project Overview

### Current State
- **Platform:** Streamlit Cloud
- **Database:** Supabase (PostgreSQL)
- **UI Language:** Vietnamese
- **Features:** 9 pages, 6-step publishing workflow

### Target State
- **Platform:** Railway (Full-stack deployment)
- **Frontend:** Next.js 14+ (React)
- **Backend:** FastAPI (Python) - **Reuses existing code**
- **Database:** Railway PostgreSQL (or keep Supabase)

---

## 2. Tech Stack (Simplified)

### Architecture: Next.js + FastAPI (Hybrid)

```
┌─────────────────┐     HTTP      ┌─────────────────┐
│   Next.js       │ ←──────────→  │   FastAPI       │
│   (Frontend)    │   JSON API    │   (Backend)     │
│   React UI      │               │   Python        │
└─────────────────┘               └─────────────────┘
        │                                 │
        │                                 │
        ▼                                 ▼
   Browser/User                    ┌─────────────────┐
                                   │   PostgreSQL    │
                                   │   (Railway)     │
                                   └─────────────────┘
                                          │
                    ┌─────────────────────┼─────────────────────┐
                    ▼                     ▼                     ▼
             ┌───────────┐         ┌───────────┐         ┌───────────┐
             │ WordPress │         │  Claude   │         │  Google   │
             │ REST API  │         │    API    │         │ Docs API  │
             └───────────┘         └───────────┘         └───────────┘
```

### Frontend (Next.js)
| Technology | Purpose | Why Needed |
|------------|---------|------------|
| **Next.js 14** | React framework | Modern UI, routing, fast |
| **Tailwind CSS** | Styling | Like CSS but faster to write |
| **shadcn/ui** | UI components | Pre-built buttons, forms, tables |

### Backend (FastAPI - Python)
| Technology | Purpose | Why Needed |
|------------|---------|------------|
| **FastAPI** | Python web framework | Like Flask but faster, auto-docs |
| **Your existing code** | Business logic | Reuse services, workflow, utils |
| **Pillow** | Image processing | Already using this |
| **Anthropic SDK** | Claude API | Already using this |

### Database
| Option | Recommendation |
|--------|----------------|
| **Keep Supabase** | Simpler - no migration needed |
| **Railway PostgreSQL** | Single platform - requires data migration |

### Why This Architecture?
1. **Keep all Python code** - services, workflow, utils unchanged
2. **Better UI** - React is more flexible than Streamlit
3. **Separation** - Frontend and backend can scale independently
4. **Same external APIs** - Claude, WordPress, Google Docs (unchanged)

---

## 3. Folder Structure

```
Agent_Railway/
├── PLAN.md                    # This document
├── SESSION_STATE.md           # Progress tracking
│
├── backend/                   # FastAPI Python Backend
│   ├── main.py               # FastAPI entry point
│   ├── requirements.txt      # Python dependencies
│   ├── Dockerfile            # For Railway deployment
│   │
│   ├── routers/              # API endpoint handlers
│   │   ├── projects.py       # /api/projects endpoints
│   │   ├── publish.py        # /api/publish endpoints
│   │   ├── patterns.py       # /api/patterns endpoints
│   │   └── history.py        # /api/history endpoints
│   │
│   ├── services/             # Business logic (FROM STREAMLIT)
│   │   ├── google_docs.py    # Copy from src/tools/google_docs_converter.py
│   │   ├── image_processor.py# Copy from src/tools/image_processor.py
│   │   ├── wordpress.py      # Copy from src/tools/wordpress_uploader.py
│   │   ├── html_transformer.py # Copy from src/tools/html_transformer.py
│   │   ├── workflow.py       # Copy from src/workflows/publishing_workflow.py
│   │   └── ai_patterns.py    # Copy from src/utils/pattern_modifier.py
│   │
│   ├── database/             # Database operations (FROM STREAMLIT)
│   │   └── project_manager.py# Copy from src/database/project_manager.py
│   │
│   └── utils/                # Utilities (FROM STREAMLIT)
│       ├── html_extractor.py # Copy from src/utils/html_extractor.py
│       └── pattern_engine.py # Copy from src/utils/pattern_engine.py
│
├── frontend/                  # Next.js React Frontend
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── Dockerfile            # For Railway deployment
│   │
│   ├── app/                  # Next.js App Router (Pages)
│   │   ├── layout.tsx        # Root layout with sidebar
│   │   ├── page.tsx          # Home/Dashboard
│   │   ├── projects/
│   │   │   ├── page.tsx      # Projects list
│   │   │   ├── new/page.tsx  # Create project
│   │   │   └── [id]/
│   │   │       ├── edit/page.tsx     # Edit project
│   │   │       ├── patterns/page.tsx # AI Pattern Editor
│   │   │       └── scan/page.tsx     # Scan Template
│   │   ├── publish/
│   │   │   ├── page.tsx      # Publish Content
│   │   │   └── batch/page.tsx# Batch Publish
│   │   └── history/
│   │       └── page.tsx      # Publishing History
│   │
│   ├── components/           # React components
│   │   ├── ui/               # shadcn/ui components
│   │   ├── layout/           # Sidebar, Header
│   │   └── forms/            # Project form, Publish form
│   │
│   └── lib/                  # Frontend utilities
│       └── api.ts            # API client to call FastAPI
│
└── railway.toml              # Railway deployment config
```

### What Gets Reused (From Streamlit)

| Streamlit File | → | Backend File |
|----------------|---|--------------|
| `src/tools/google_docs_converter.py` | → | `backend/services/google_docs.py` |
| `src/tools/image_processor.py` | → | `backend/services/image_processor.py` |
| `src/tools/wordpress_uploader.py` | → | `backend/services/wordpress.py` |
| `src/tools/html_transformer.py` | → | `backend/services/html_transformer.py` |
| `src/workflows/publishing_workflow.py` | → | `backend/services/workflow.py` |
| `src/utils/pattern_modifier.py` | → | `backend/services/ai_patterns.py` |
| `src/database/project_manager.py` | → | `backend/database/project_manager.py` |
| `src/utils/html_extractor.py` | → | `backend/utils/html_extractor.py` |
| `src/utils/pattern_engine.py` | → | `backend/utils/pattern_engine.py` |

**~80% of Python code is reused directly!**

---

## 4. Feature Mapping

### Pages (Frontend - Next.js)

| # | Page | Route | What It Does |
|---|------|-------|--------------|
| 1 | Home | `/` | Dashboard, stats, quick links |
| 2 | Projects | `/projects` | List all projects |
| 3 | Create Project | `/projects/new` | Form to add new project |
| 4 | Edit Project | `/projects/[id]/edit` | Form to edit project |
| 5 | AI Pattern Editor | `/projects/[id]/patterns` | Edit patterns with AI |
| 6 | Scan Template | `/projects/[id]/scan` | Generate patterns from HTML |
| 7 | Publish | `/publish` | Publish single post |
| 8 | Batch Publish | `/publish/batch` | Publish multiple posts |
| 9 | History | `/history` | View publishing history |

### API Endpoints (Backend - FastAPI)

| Endpoint | Method | What It Does |
|----------|--------|--------------|
| `/api/projects` | GET | List all projects |
| `/api/projects` | POST | Create new project |
| `/api/projects/{id}` | GET | Get single project |
| `/api/projects/{id}` | PUT | Update project |
| `/api/projects/{id}` | DELETE | Delete project |
| `/api/publish` | POST | Run publishing workflow |
| `/api/publish/batch` | POST | Run batch publishing |
| `/api/patterns/generate` | POST | AI generates patterns |
| `/api/patterns/modify` | POST | AI modifies patterns |
| `/api/history` | GET | Get publishing history |
| `/api/google-docs/convert` | POST | Test Google Docs conversion |

---

## 5. Implementation Phases

### Phase 1: Backend Setup (FastAPI)
**Goal:** Set up FastAPI backend with existing Python code

- [ ] Create `backend/` folder structure
- [ ] Set up FastAPI with main.py
- [ ] Copy existing services from Streamlit (no rewrite needed)
- [ ] Create API routers (projects, publish, patterns, history)
- [ ] Connect to Supabase (same as Streamlit)
- [ ] Test all API endpoints with Swagger docs
- [ ] Create Dockerfile for backend

**What gets copied (no changes needed):**
- `services/` - All business logic
- `database/` - Database operations
- `utils/` - Utility functions

**What gets created (new):**
- `routers/` - FastAPI endpoint handlers
- `main.py` - FastAPI app entry point

### Phase 2: Frontend Setup (Next.js)
**Goal:** Set up Next.js frontend with basic pages

- [ ] Initialize Next.js 14 project
- [ ] Configure Tailwind CSS
- [ ] Install shadcn/ui components
- [ ] Create layout with sidebar
- [ ] Create Home page (dashboard)
- [ ] Create Projects list page
- [ ] Create API client (`lib/api.ts`)

### Phase 3: Project Management Pages
**Goal:** Complete project CRUD functionality

- [ ] Create Project form page
- [ ] Edit Project form page
- [ ] Delete project functionality
- [ ] Form validation
- [ ] Success/error messages

### Phase 4: Publishing Pages
**Goal:** Complete publishing functionality

- [ ] Publish Content page
- [ ] Progress indicator during publishing
- [ ] Result display (success/error)
- [ ] Batch Publish page
- [ ] Publishing History page

### Phase 5: AI Pattern Features
**Goal:** AI-powered pattern management

- [ ] AI Pattern Editor page
- [ ] Scan HTML Template page
- [ ] Pattern preview functionality

### Phase 6: Railway Deployment
**Goal:** Deploy both apps to Railway

- [ ] Create Railway project
- [ ] Deploy backend (FastAPI)
- [ ] Deploy frontend (Next.js)
- [ ] Configure environment variables
- [ ] Test production deployment

---

## 6. Environment Variables

### Backend (.env)
```env
# Database (Railway PostgreSQL)
DATABASE_URL="postgresql://user:password@host:port/database"

# Claude API
ANTHROPIC_API_KEY="sk-ant-..."

# Image Processing
DEFAULT_IMAGE_WIDTH=800
IMAGE_QUALITY=92
IMAGE_FORMAT="JPEG"

# CORS (allow frontend)
FRONTEND_URL="http://localhost:3000"
```

### Frontend (.env.local)
```env
# Backend API URL
NEXT_PUBLIC_API_URL="http://localhost:8000"
```

### Data Migration Note
Need to migrate data from Supabase to Railway PostgreSQL:
- Export `projects` table
- Export `publishing_history` table
- Import to Railway PostgreSQL

---

## 7. User Decisions (Confirmed)

| Question | Decision |
|----------|----------|
| **Database** | Railway PostgreSQL (migrate from Supabase) |
| **Authentication** | Single-user (no login) |
| **Google OAuth** | Published URLs only |
| **UI Language** | Vietnamese |

---

## 8. Approval Checklist

- [x] Tech stack approved (Next.js + FastAPI)
- [x] Architecture approved
- [x] Questions answered
- [ ] Ready to execute (awaiting user approval)

---

## Change Log

| Date | Version | Changes |
|------|---------|---------|
| 2025-12-08 | 1.0.0 | Initial plan created |
| 2025-12-08 | 1.1.0 | Changed to FastAPI + Next.js hybrid architecture |
| 2025-12-08 | 1.2.0 | User decisions finalized: PostgreSQL, single-user, published URLs, Vietnamese |

---

*This document will be updated as the project progresses. See SESSION_STATE.md for daily progress tracking.*
