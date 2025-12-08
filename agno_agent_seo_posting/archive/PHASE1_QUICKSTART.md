# Phase 1 Quick Start Guide

**Get the FastAPI backend + Lark Base integration running in 30 minutes**

---

## 🎯 What You're Building

Phase 1 adds a REST API layer on top of your existing WordPress publishing system, enabling:
- ✅ Multi-user access via HTTP endpoints
- ✅ Lark Base visual interface with button workflows
- ✅ Bulk/parallel processing (20+ concurrent publishes)
- ✅ Real-time status tracking
- ✅ Team collaboration (20+ users)

---

## ⚡ Quick Start (5 Steps)

### Step 1: Install Dependencies (2 minutes)

```bash
cd agno_agent_seo_posting

# Install new dependencies
pip install -r requirements.txt
```

---

### Step 2: Generate API Keys (1 minute)

```bash
# Generate 3 API keys
python -c "from api.core.security import create_api_keys_file; create_api_keys_file(3)"

# This creates api_keys.txt with 3 keys
cat api_keys.txt
```

Add keys to `.env`:
```env
# Add to your existing .env file
API_KEYS=key1-here,key2-here,key3-here
API_SECRET_KEY=your-secret-key-here
```

---

### Step 3: Start API Server (1 minute)

```bash
# Option A: Direct Python
python api/main.py

# Option B: Uvicorn with auto-reload (development)
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Option C: Docker
docker-compose up --build
```

Server will start at: `http://localhost:8000`

---

### Step 4: Test API (2 minutes)

Open browser: `http://localhost:8000/api/v1/docs`

You'll see interactive Swagger documentation!

**Test health check** (no auth needed):
```bash
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-11-13T..."
}
```

**Test authenticated endpoint**:
```bash
curl -H "X-API-Key: your-api-key-here" \
     http://localhost:8000/api/v1/projects
```

---

### Step 5: Set Up Lark Base (20 minutes)

Follow the comprehensive guide: `docs/LARK_BASE_SETUP.md`

**Quick summary**:
1. Create Lark Base with 2 tables
2. Configure automations with API webhooks
3. Add buttons for processing
4. Test with a sample publish

---

## 📊 Verify Everything Works

### Test 1: List Projects
```bash
curl -H "X-API-Key: your-key" \
     http://localhost:8000/api/v1/projects
```

Should return your existing projects (like `dangbaiseongon`).

### Test 2: Publish Single Content
```bash
curl -X POST \
     -H "X-API-Key: your-key" \
     -H "Content-Type: application/json" \
     -d '{
       "google_docs_url": "https://docs.google.com/document/d/YOUR_DOC_ID/edit",
       "project_id": "dangbaiseongon"
     }' \
     http://localhost:8000/api/v1/publish
```

Should return success with WordPress post URL.

### Test 3: Batch Publish (KEY FEATURE!)
```bash
curl -X POST \
     -H "X-API-Key: your-key" \
     -H "Content-Type: application/json" \
     -d '{
       "items": [
         {"google_docs_url": "https://docs.google.com/document/d/DOC1/edit", "project_id": "dangbaiseongon"},
         {"google_docs_url": "https://docs.google.com/document/d/DOC2/edit", "project_id": "dangbaiseongon"}
       ]
     }' \
     http://localhost:8000/api/v1/publish/batch
```

Should process both documents in parallel!

---

## 🚀 Production Deployment

### Docker Deployment (Recommended)

```bash
# 1. Update .env with production values
cp .env.example .env
nano .env  # Edit with real values

# 2. Build and run
docker-compose up -d

# 3. Check logs
docker-compose logs -f api

# 4. Verify health
curl http://your-server:8000/api/v1/health
```

### Server Requirements

**Minimum**:
- 2 CPU cores
- 4 GB RAM
- 20 GB disk space

**Recommended** (for 20+ concurrent users):
- 4 CPU cores
- 8 GB RAM
- 50 GB disk space

---

## 🔐 Security Checklist

- [ ] API keys generated and stored securely
- [ ] `.env` file not committed to git
- [ ] HTTPS enabled (use NGINX reverse proxy)
- [ ] Firewall configured (allow port 8000 or 443)
- [ ] Rate limiting configured
- [ ] CORS origins restricted (not `*` in production)

---

## 📚 Next Steps

### Immediate (Now)
1. ✅ API running
2. ✅ Test endpoints work
3. ⏳ Set up Lark Base (follow LARK_BASE_SETUP.md)

### This Week
- Train 2-3 pilot users on Lark Base
- Monitor API performance
- Gather feedback

### Next Week
- Roll out to full team (20 users)
- Optimize based on usage patterns
- Consider Phase 2 (Larksuite Bot)

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'fastapi'"
```bash
pip install -r requirements.txt
```

### "Address already in use" (port 8000)
```bash
# Find and kill process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:8000 | xargs kill -9
```

### "401 Unauthorized"
- Check API key is correct
- Check `X-API-Key` header is present
- Verify API_KEYS in .env matches

### "Import errors for src.database"
```bash
# Make sure you're running from project root
cd agno_agent_seo_posting
python api/main.py
```

---

## 📊 Monitoring

### Logs

**View logs** (Docker):
```bash
docker-compose logs -f api
```

**Log levels**:
- `DEBUG`: All requests and responses
- `INFO`: Request summary (default)
- `WARNING`: Warnings only
- `ERROR`: Errors only

Configure in `.env`:
```env
LOG_LEVEL=INFO
```

### Metrics to Watch

- **Request rate**: Requests per minute
- **Error rate**: % of failed requests (target: < 5%)
- **Avg response time**: Time per request (target: < 2s)
- **Active users**: Unique API keys used per day

---

## 🎉 Success Criteria

Phase 1 is successful when:

- [x] API server running and accessible
- [x] All endpoints responding correctly
- [ ] Lark Base tables created and syncing
- [ ] Team members can publish via Lark Base buttons
- [ ] Batch processing works (10+ items in parallel)
- [ ] 20+ team members using system daily

---

## 📞 Support

### Documentation
- **API Reference**: `docs/API_DOCUMENTATION.md`
- **Lark Base Guide**: `docs/LARK_BASE_SETUP.md`
- **Full Roadmap**: `docs/LARK_IMPLEMENTATION_PLAN.md`

### Interactive API Docs
- **Swagger UI**: `http://localhost:8000/api/v1/docs`
- **ReDoc**: `http://localhost:8000/api/v1/redoc`

### Testing Tools
- **Postman Collection**: (create from Swagger)
- **cURL Examples**: See API_DOCUMENTATION.md

---

## 🔄 What's Next? (Phase 2 & 3)

### Phase 2: Larksuite Bot (1-2 weeks)
- Chat commands: `/publish [url] [project]`
- Status queries: `/status`, `/history`
- Direct publishing from Larksuite chat

### Phase 3: AI-Powered Bot (2-3 weeks)
- Natural language: "Publish this doc to dangbaiseongon"
- Conversational project configuration
- Smart suggestions

See `docs/LARK_IMPLEMENTATION_PLAN.md` for full roadmap.

---

**Status**: ✅ Phase 1 Ready for Deployment
**Last Updated**: 2025-11-13
**Version**: 1.0.0
