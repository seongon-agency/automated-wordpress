# Railway Deployment Plan - WordPress SEO Publishing System

**Version:** 1.1
**Created:** 2025-12-10
**Status:** ARCHITECTURE APPROVED (Option A: Full-stack Next.js)

---

## Overview

Migrate the existing Streamlit-based WordPress SEO Publishing System to a full-stack Next.js application deployed on Railway.

### Current System (Streamlit)
- Single Python file (`app_streamlit.py`) with embedded UI logic
- Supabase database (PostgreSQL)
- Python backend tools for Google Docs conversion, image processing, WordPress publishing
- UI in Vietnamese

### Target System (Next.js + Railway)
- Next.js 15 full-stack application (App Router)
- React frontend with modern UI components
- API routes for backend operations
- **Railway PostgreSQL database** (migrated from Supabase)
- Python microservice for heavy processing (Google Docs, image processing)
- Deployed on Railway with automatic scaling

---

## Architecture Decision

### Option A: Full Next.js (Recommended)
```
┌─────────────────────────────────────────────────────────────┐
│                    RAILWAY PLATFORM                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐   │
│  │           Next.js Application (Node.js)              │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │   │
│  │  │   Frontend  │  │ API Routes  │  │   Server    │  │   │
│  │  │    React    │  │  /api/*     │  │   Actions   │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
│                            │                                 │
│  ┌─────────────────────────┼─────────────────────────────┐  │
│  │    Python Microservice  │  (Image Processing)          │  │
│  │    - Google Docs → HTML │                              │  │
│  │    - Image resize/upload│                              │  │
│  │    - Heavy processing   │                              │  │
│  └─────────────────────────┴─────────────────────────────┘  │
│                            │                                 │
│  ┌─────────────────────────┴─────────────────────────────┐  │
│  │              Railway PostgreSQL                        │  │
│  │              (Database Service)                        │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

**Pros:**
- Single deployment for frontend + API
- Server-side rendering for better SEO
- Type-safe with TypeScript
- Modern developer experience
- Railway's native support for Next.js

**Cons:**
- Need to rewrite Python tools in TypeScript OR create Python microservice

### Option B: Separate Frontend + Backend
```
Frontend (Next.js) ←→ Backend (FastAPI/Python) ←→ Supabase
```

**Pros:**
- Reuse existing Python code directly
- Clear separation of concerns

**Cons:**
- Two services to manage
- More complex deployment
- Additional latency between services

### APPROVED: Option A with Python Microservice

**User approved on 2025-12-10**

Use Next.js for the main application with a lightweight Python microservice for heavy processing tasks that are difficult to port (image processing with Pillow, Google Docs API).

---

## Technology Stack

| Component | Technology | Reason |
|-----------|------------|--------|
| Framework | Next.js 15 (App Router) | Full-stack, SSR, Railway native support |
| Language | TypeScript | Type safety, better DX |
| UI Components | shadcn/ui + Tailwind CSS | Modern, customizable, accessible |
| State Management | React Server Components + Zustand | Minimal client state |
| Database | **Railway PostgreSQL** | Native Railway integration, single platform |
| ORM | **Prisma** | Type-safe queries, excellent PostgreSQL support, migrations |
| Auth | (Optional) Clerk or NextAuth | If needed later |
| Image Processing | Python microservice | Pillow, complex processing |
| Deployment | Railway | Auto-scaling, easy config |

---

## Project Structure

```
railway/
├── frontend/                    # Next.js application
│   ├── src/
│   │   ├── app/                 # App Router pages
│   │   │   ├── page.tsx         # Home/Dashboard
│   │   │   ├── projects/
│   │   │   │   ├── page.tsx     # List projects
│   │   │   │   ├── new/
│   │   │   │   │   └── page.tsx # Create project
│   │   │   │   └── [id]/
│   │   │   │       ├── page.tsx # View project
│   │   │   │       └── edit/
│   │   │   │           └── page.tsx # Edit project
│   │   │   ├── publish/
│   │   │   │   ├── page.tsx     # Publish single
│   │   │   │   └── batch/
│   │   │   │       └── page.tsx # Batch publish
│   │   │   ├── patterns/
│   │   │   │   ├── page.tsx     # AI Pattern Editor
│   │   │   │   └── scan/
│   │   │   │       └── page.tsx # Scan HTML Template
│   │   │   ├── history/
│   │   │   │   └── page.tsx     # Publishing history
│   │   │   ├── api/             # API Routes
│   │   │   │   ├── projects/
│   │   │   │   ├── publish/
│   │   │   │   ├── patterns/
│   │   │   │   └── history/
│   │   │   └── layout.tsx       # Root layout with sidebar
│   │   ├── components/
│   │   │   ├── ui/              # shadcn/ui components
│   │   │   ├── sidebar.tsx
│   │   │   ├── project-form.tsx
│   │   │   ├── publish-form.tsx
│   │   │   └── pattern-editor.tsx
│   │   ├── lib/
│   │   │   ├── db.ts            # Prisma client
│   │   │   ├── actions/         # Server actions
│   │   │   └── utils.ts
│   ├── prisma/
│   │   ├── schema.prisma        # Database schema
│   │   └── migrations/          # Database migrations
│   │   └── types/
│   │       └── index.ts         # TypeScript types
│   ├── public/
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── Dockerfile               # For Railway
│
├── backend/                     # Python microservice
│   ├── main.py                  # FastAPI app
│   ├── routers/
│   │   ├── publish.py           # Publishing workflow
│   │   └── patterns.py          # AI pattern operations
│   ├── services/
│   │   ├── google_docs.py       # Google Docs converter
│   │   ├── image_processor.py   # Image processing
│   │   ├── wordpress.py         # WordPress uploader
│   │   └── ai_patterns.py       # AI pattern modifier
│   ├── requirements.txt
│   ├── Dockerfile
│   └── railway.toml
│
├── PLAN.md                      # This file
└── SESSION_STATE.md             # Session tracking
```

---

## Implementation Phases

### Phase 1: Project Setup & Core Infrastructure
**Estimated Effort:** Foundation work

1. Initialize Next.js 15 project with TypeScript
2. Configure Tailwind CSS and shadcn/ui
3. Set up Railway PostgreSQL database
4. Configure Prisma ORM with database schema
5. Create base layout with Vietnamese navigation
6. Set up Railway project with environment variables
7. Migrate existing data from Supabase to Railway PostgreSQL

**Deliverables:**
- Working Next.js app with sidebar navigation
- Railway PostgreSQL database configured
- Prisma ORM connected and schema migrated
- Basic Railway deployment working
- Data migrated from Supabase

### Phase 2: Project Management Pages
**Estimated Effort:** CRUD operations

1. **Dashboard (Home Page)**
   - System status display
   - Quick stats (project count, ready status)
   - Welcome message in Vietnamese

2. **Projects List Page**
   - Fetch and display all projects
   - Delete project functionality
   - Expandable project details

3. **Create Project Page**
   - Form with all fields (WordPress URL, credentials, image settings)
   - Image resize method selection (radio buttons)
   - Naming method selection
   - Form validation
   - Submit to Supabase

4. **Edit Project Page**
   - Load existing project data
   - Pre-populate form fields
   - Handle password field (keep existing if empty)
   - Save changes

**Deliverables:**
- All project CRUD operations working
- Forms match existing Streamlit functionality

### Phase 3: Python Microservice
**Estimated Effort:** Backend processing

1. Create FastAPI application
2. Port existing Python tools:
   - `google_docs_converter.py`
   - `image_processor.py`
   - `wordpress_uploader.py`
   - `html_transformer.py`
   - `pattern_modifier.py`
3. Create API endpoints:
   - `POST /api/publish` - Execute publishing workflow
   - `POST /api/patterns/scan` - Scan HTML template
   - `POST /api/patterns/modify` - AI pattern modification
4. Configure Docker for Railway deployment
5. Set up inter-service communication

**Deliverables:**
- Python microservice deployed on Railway
- All existing Python functionality working via API

### Phase 4: Publishing Workflow
**Estimated Effort:** Core feature

1. **Publish Single Page**
   - Project selector dropdown
   - Google Docs URL input
   - Main keyword input (optional, for naming)
   - Progress indicator during publishing
   - Result display (post URL, images processed)

2. **Batch Publish Page** (if existing)
   - Multiple URL input
   - Batch processing with progress

3. **Publishing History Page**
   - List all publish attempts
   - Filter by project
   - Show success/failure status
   - Display execution time

**Deliverables:**
- Complete publishing workflow working
- History tracking functional

### Phase 5: AI Pattern Features
**Estimated Effort:** AI integration

1. **AI Pattern Editor Page**
   - Project selector
   - Display current patterns with delete buttons
   - Natural language instruction input
   - AI modification via Claude API
   - Preview changes before saving
   - Save modified patterns

2. **Scan HTML Template Page**
   - HTML textarea input
   - AI analysis to extract patterns
   - Preview generated patterns
   - Save to project

**Deliverables:**
- AI pattern editing working
- HTML template scanning working

### Phase 6: Polish & Production Readiness
**Estimated Effort:** Final touches

1. Error handling and user feedback
2. Loading states and skeleton screens
3. Mobile responsiveness
4. Environment variable configuration
5. Health checks for Railway
6. Documentation updates

**Deliverables:**
- Production-ready application
- Comprehensive error handling
- Responsive design

---

## Database Schema (Railway PostgreSQL + Prisma)

### Prisma Schema (`prisma/schema.prisma`)

```prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

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
  createdAt            DateTime  @default(now()) @map("created_at")
  updatedAt            DateTime  @updatedAt @map("updated_at")
  lastPublishedAt      DateTime? @map("last_published_at")

  publishingHistory PublishingHistory[]

  @@map("projects")
}

model PublishingHistory {
  id                   Int       @id @default(autoincrement())
  projectId            String?   @map("project_id")
  googleDocsUrl        String    @map("google_docs_url")
  wordpressPostId      Int?      @map("wordpress_post_id")
  wordpressPostUrl     String?   @map("wordpress_post_url")
  postTitle            String?   @map("post_title")
  postStatus           String?   @map("post_status")
  imagesProcessed      Int       @default(0) @map("images_processed")
  success              Boolean
  errorMessage         String?   @map("error_message")
  executionTimeSeconds Float?    @map("execution_time_seconds")
  publishedAt          DateTime  @default(now()) @map("published_at")

  project Project? @relation(fields: [projectId], references: [projectId])

  @@map("publishing_history")
}
```

### Equivalent SQL (for reference)

```sql
-- projects table
CREATE TABLE projects (
    project_id TEXT PRIMARY KEY,
    project_name TEXT NOT NULL,
    wordpress_url TEXT NOT NULL,
    wordpress_username TEXT NOT NULL,
    wordpress_app_password TEXT NOT NULL,
    html_configs JSONB,
    image_configs JSONB,
    status TEXT DEFAULT 'active',
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_published_at TIMESTAMP
);

-- publishing_history table
CREATE TABLE publishing_history (
    id SERIAL PRIMARY KEY,
    project_id TEXT REFERENCES projects(project_id),
    google_docs_url TEXT NOT NULL,
    wordpress_post_id INTEGER,
    wordpress_post_url TEXT,
    post_title TEXT,
    post_status TEXT,
    images_processed INTEGER DEFAULT 0,
    success BOOLEAN NOT NULL,
    error_message TEXT,
    execution_time_seconds REAL,
    published_at TIMESTAMP DEFAULT NOW()
);
```

---

## Environment Variables

### Frontend (Next.js)
```env
# Railway PostgreSQL (auto-provided by Railway when you add PostgreSQL service)
DATABASE_URL=postgresql://user:password@host:port/railway

# API Keys
ANTHROPIC_API_KEY=sk-ant-...

# Internal service communication
PYTHON_SERVICE_URL=http://backend.railway.internal:8000
```

### Backend (Python)
```env
# Railway PostgreSQL
DATABASE_URL=postgresql://user:password@host:port/railway

# API Keys
ANTHROPIC_API_KEY=sk-ant-...

# Default WordPress (optional)
WP_BASE_URL=https://...
WP_USERNAME=...
WP_APP_PASS=...
```

### Railway Auto-Configuration
When you add a PostgreSQL service in Railway, it automatically provides:
- `DATABASE_URL` - Full connection string
- `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE` - Individual components

---

## Railway Configuration

### Frontend Service (next.config.js)
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  reactStrictMode: true,
}

module.exports = nextConfig
```

### Backend Service (railway.toml)
```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"

[deploy]
startCommand = "uvicorn main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3
```

---

## API Endpoints (Python Microservice)

### Publishing
```
POST /api/publish
Body: {
  google_docs_url: string,
  project_id: string | null,
  main_keyword: string | null
}
Response: {
  success: boolean,
  post_url?: string,
  post_id?: number,
  post_title?: string,
  images_processed?: number,
  execution_time?: number,
  error?: string,
  step_failed?: string
}
```

### Pattern Operations
```
POST /api/patterns/scan
Body: {
  html_content: string
}
Response: {
  success: boolean,
  patterns?: Pattern[],
  error?: string
}

POST /api/patterns/modify
Body: {
  current_patterns: Pattern[],
  instruction: string
}
Response: {
  success: boolean,
  patterns?: Pattern[],
  changes_made?: string,
  error?: string
}
```

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Python service communication latency | Medium | Medium | Use Railway internal networking |
| Image processing timeouts | Medium | High | Implement progress streaming, increase timeouts |
| Database connection issues | Low | High | Connection pooling, Prisma retry logic |
| AI API rate limits | Low | Medium | Implement retry with backoff |
| Railway deployment issues | Low | Medium | Comprehensive Dockerfile, health checks |
| Data migration from Supabase | Low | Medium | Export/import scripts, verify data integrity |

---

## Success Criteria

1. All existing Streamlit features working in Next.js
2. Vietnamese UI preserved
3. Publishing workflow completes in similar time
4. No data loss during migration
5. Stable Railway deployment with auto-restart
6. Mobile-responsive design

---

## Decisions Made (2025-12-10)

1. **Authentication:** Build later - initial version without auth (same as Streamlit)

2. **Batch Publishing:** YES - Keep all features from Streamlit, including batch publish

3. **Mobile Support:** Not necessary - Desktop-focused like Streamlit version

4. **Error Notifications:** YES - Include error notifications for failed publishes

5. **Monitoring:** Defer to later phase

---

## Next Steps

1. **Review this plan** - Discuss any changes needed
2. **Approve architecture** - Confirm Option A with Python microservice
3. **Begin Phase 1** - Project setup and infrastructure
4. **Iterative development** - Build feature by feature with testing

---

**Status:** READY FOR IMPLEMENTATION - All decisions confirmed.

---

## Sources

- [Railway Quick Start Guide](https://docs.railway.com/quick-start)
- [Deploy NextJS on Railway](https://railway.com/deploy/yDom4a)
- [Railway Full-Stack TypeScript Guide](https://blog.railway.com/p/deploy-full-stack-typescript-apps-architectures-execution-models-and-deployment-choices)
- [Next.js Deployment Docs](https://nextjs.org/docs/app/getting-started/deploying)
