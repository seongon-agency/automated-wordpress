# Session State - Railway Deployment Project

**Last Updated:** 2025-12-10
**Project:** WordPress SEO Publishing System - Railway Migration
**Status:** PHASE 1 COMPLETE - Ready for Phase 2

---

## Quick Context for New Sessions

This document tracks the progress of migrating the Streamlit-based WordPress SEO Publishing System to a full-stack Next.js application deployed on Railway.

**Read this file first** when starting a new session to understand:
- Current project state
- What has been completed
- What is in progress
- What needs to be done next

---

## Project Overview

### Source System
- **Location:** `../app_streamlit.py` (parent directory)
- **Tech:** Streamlit + Python
- **Database:** Supabase (PostgreSQL)
- **UI Language:** Vietnamese

### Target System
- **Location:** `./` (this railway folder)
- **Tech:** Next.js 15 + Python microservice
- **Database:** **Railway PostgreSQL** (migrated from Supabase)
- **ORM:** Prisma
- **Deployment:** Railway platform

---

## Current Phase

### Phase: PHASE 1 COMPLETE
**Status:** Foundation setup done, ready for Phase 2 (Project Management Pages)

**Plan Document:** `PLAN.md`

---

## Completed Work (Phase 1)

### Frontend (`railway/frontend/`)

1. **Next.js 15 Project Initialized**
   - TypeScript configured
   - App Router structure
   - `tsconfig.json` with proper JSX settings

2. **Tailwind CSS + shadcn/ui Installed**
   - All required components installed:
     - Button, Card, Input, Label, Textarea
     - Select, Table, Tabs, Form, Alert
     - Badge, Dialog, Skeleton, Sheet
     - Separator, Sidebar, Tooltip

3. **Prisma ORM Configured**
   - Schema defined in `prisma/schema.prisma`
   - Models: `Project`, `PublishingHistory`
   - Client configured in `src/lib/db.ts`

4. **Base Layout with Vietnamese Navigation**
   - Root layout in `src/app/layout.tsx`
   - Sidebar component in `src/components/app-sidebar.tsx`
   - All navigation items in Vietnamese:
     - Trang chủ (Home)
     - Dự án (Projects)
     - Xuất bản (Publish)
     - AI Patterns (AI Patterns)
     - Lịch sử (History)

5. **Page Stubs Created**
   - `src/app/page.tsx` - Dashboard
   - `src/app/projects/page.tsx` - Projects list
   - `src/app/projects/new/page.tsx` - Create project
   - `src/app/projects/[id]/page.tsx` - Edit project
   - `src/app/publish/page.tsx` - Single publish
   - `src/app/publish/batch/page.tsx` - Batch publish
   - `src/app/patterns/page.tsx` - AI patterns
   - `src/app/patterns/scan/page.tsx` - Scan HTML
   - `src/app/history/page.tsx` - Publishing history

6. **TypeScript Types Defined**
   - `src/types/index.ts` - All interfaces

7. **Docker Configuration**
   - `Dockerfile` for Railway deployment
   - Multi-stage build for optimization

### Backend (`railway/backend/`)

1. **FastAPI Project Initialized**
   - `main.py` with CORS, routers, health check
   - Database initialization on startup

2. **Router Structure**
   - `routers/projects.py` - Project CRUD
   - `routers/publish.py` - Publishing endpoints
   - `routers/patterns.py` - AI pattern endpoints
   - `routers/history.py` - History endpoints

3. **Core Services Implemented**
   - `services/google_docs.py` - Google Docs to HTML conversion
   - `services/image_processor.py` - Image download/resize
   - `services/wordpress.py` - WordPress upload & post creation
   - `services/html_transformer.py` - HTML transformation
   - `services/ai_patterns.py` - AI pattern scanning/modification
   - `services/workflow.py` - Complete publishing workflow

4. **Database Module**
   - `database/db.py` - SQLAlchemy connection

5. **Configuration Files**
   - `requirements.txt` - Python dependencies (including lxml)
   - `Dockerfile` - With Railway PORT support
   - `railway.toml` - Railway deployment config
   - `.env.example` - Environment template

---

## Critical Issues Fixed

1. **Backend Dockerfile PORT variable**
   - Changed from hardcoded `--port 8000` to `--port ${PORT:-8000}`
   - Allows Railway to inject the PORT environment variable

2. **TSConfig JSX setting**
   - Changed from `"react-jsx"` to `"preserve"` for Next.js

3. **Added lxml to requirements.txt**
   - Required by BeautifulSoup for HTML parsing

4. **Database initialization in FastAPI**
   - Added `init_database()` call in lifespan handler

5. **Removed incorrect prisma.config.ts**
   - Prisma configuration is in `prisma/schema.prisma`

---

## Files Created

### Frontend
| File | Purpose |
|------|---------|
| `frontend/src/app/layout.tsx` | Root layout with sidebar |
| `frontend/src/app/page.tsx` | Dashboard page |
| `frontend/src/app/globals.css` | Global styles |
| `frontend/src/components/app-sidebar.tsx` | Vietnamese navigation |
| `frontend/src/components/ui/*.tsx` | shadcn/ui components |
| `frontend/src/lib/db.ts` | Prisma client |
| `frontend/src/lib/utils.ts` | Utility functions |
| `frontend/src/types/index.ts` | TypeScript interfaces |
| `frontend/prisma/schema.prisma` | Database schema |
| `frontend/next.config.ts` | Next.js config (standalone) |
| `frontend/tsconfig.json` | TypeScript config |
| `frontend/Dockerfile` | Railway deployment |
| `frontend/package.json` | Dependencies |

### Backend
| File | Purpose |
|------|---------|
| `backend/main.py` | FastAPI app entry |
| `backend/routers/projects.py` | Projects API |
| `backend/routers/publish.py` | Publishing API |
| `backend/routers/patterns.py` | Patterns API |
| `backend/routers/history.py` | History API |
| `backend/services/google_docs.py` | Docs conversion |
| `backend/services/image_processor.py` | Image processing |
| `backend/services/wordpress.py` | WordPress integration |
| `backend/services/html_transformer.py` | HTML transformation |
| `backend/services/ai_patterns.py` | AI pattern services |
| `backend/services/workflow.py` | Publishing workflow |
| `backend/database/db.py` | Database connection |
| `backend/requirements.txt` | Python dependencies |
| `backend/Dockerfile` | Railway deployment |
| `backend/railway.toml` | Railway config |
| `backend/.env.example` | Env template |

---

## Next Actions (Phase 2)

### Project Management Pages

1. **Projects List Page** (`/projects`)
   - Fetch and display all projects
   - Status badges (active/inactive)
   - Actions (edit, delete)

2. **Create Project Page** (`/projects/new`)
   - Form for WordPress credentials
   - HTML config section
   - Image config section
   - AI pattern scanning integration

3. **Edit Project Page** (`/projects/[id]`)
   - Load existing project data
   - Update form
   - Delete functionality

4. **Backend API Implementation**
   - Complete CRUD operations in `routers/projects.py`
   - Database queries with Prisma/SQLAlchemy

---

## Key Decisions Made

1. **Architecture:** Next.js 15 with Python microservice (Option A)
2. **UI Framework:** shadcn/ui + Tailwind CSS
3. **Database:** Railway PostgreSQL (migrated from Supabase)
4. **Deployment:** Railway platform
5. **Authentication:** Build later - no auth in initial version
6. **Batch Publishing:** YES - Keep all Streamlit features
7. **Mobile Support:** Not necessary - Desktop-focused
8. **Error Notifications:** YES - Include for failed publishes

---

## Important Notes

### Code Review Requirement
Per user request: **Always use code-reviewer agent** after writing significant code.

### Vietnamese UI
All labels, messages, and content must be in Vietnamese.

### Database Schema
```prisma
model Project {
  projectId            String    @id @map("project_id")
  projectName          String    @map("project_name")
  wordpressUrl         String    @map("wordpress_url")
  wordpressUsername    String    @map("wordpress_username")
  wordpressAppPassword String    @map("wordpress_app_password")
  htmlConfigs          Json?     @map("html_configs")
  imageConfigs         Json?     @map("image_configs")
  status               String    @default("active")
  notes                String?
  createdAt            DateTime  @default(now())
  updatedAt            DateTime  @updatedAt
  lastPublishedAt      DateTime?
  publishingHistory    PublishingHistory[]
}

model PublishingHistory {
  id                   Int       @id @default(autoincrement())
  projectId            String?
  googleDocsUrl        String
  wordpressPostId      Int?
  wordpressPostUrl     String?
  postTitle            String?
  postStatus           String?
  imagesProcessed      Int       @default(0)
  success              Boolean
  errorMessage         String?
  executionTimeSeconds Float?
  publishedAt          DateTime  @default(now())
  project              Project?  @relation(...)
}
```

---

## Commands Reference

```bash
# Navigate to railway folder
cd agno_agent_seo_posting/railway

# Run Next.js dev server
cd frontend && npm run dev

# Run Python backend
cd backend && uvicorn main:app --reload --port 8000

# Generate Prisma client
cd frontend && npx prisma generate

# Push Prisma schema to database
cd frontend && npx prisma db push

# Deploy to Railway
railway up
```

---

## For Claude Code (Next Session)

When starting a new session:

1. **Read this file first** (`railway/SESSION_STATE.md`)
2. **Phase 1 is complete** - proceed to Phase 2
3. **Code review agent required** after significant code
4. **UI language:** Vietnamese
5. **Database:** Railway PostgreSQL

Next: Implement Project Management Pages (Phase 2)

---

**Last Action:** Fixed all critical issues from code review, completed Phase 1
**Next Action:** Implement Phase 2 - Project Management Pages
