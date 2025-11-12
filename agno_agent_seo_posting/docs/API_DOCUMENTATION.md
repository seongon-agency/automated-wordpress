# WordPress SEO Publishing API - Documentation

**Version**: 1.0.0
**Base URL**: `http://your-server:8000/api/v1`

---

## 🔐 Authentication

All API endpoints (except `/health` and root `/`) require authentication via API key.

### API Key Header

```http
X-API-Key: your-api-key-here
```

### Generating API Keys

```bash
# Generate API keys
python api/core/security.py

# Or use the built-in generator
python -c "from api.core.security import generate_api_key; print(generate_api_key())"
```

Add generated keys to `.env`:
```env
API_KEYS=key1,key2,key3
```

---

## 📡 Endpoints

### Health & Info

#### `GET /api/v1/health`
Health check endpoint (no authentication required).

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-11-13T10:30:00Z"
}
```

#### `GET /api/v1/info`
Get system information (no authentication required).

**Response**:
```json
{
  "success": true,
  "data": {
    "api_version": "1.0.0",
    "python_version": "3.11.0",
    "database_status": "connected",
    "anthropic_api_configured": true,
    "lark_configured": false
  }
}
```

---

### Projects

#### `POST /api/v1/projects`
Create a new project.

**Headers**:
```http
X-API-Key: your-api-key
Content-Type: application/json
```

**Body**:
```json
{
  "project_id": "acme_blog",
  "project_name": "Acme Corp Blog",
  "wordpress_url": "https://blog.acmecorp.com",
  "wordpress_username": "admin",
  "wordpress_app_password": "xxxx xxxx xxxx xxxx",
  "html_configs": {
    "patterns": [
      {
        "element_type": "p",
        "source_pattern": "<p[^>]*>(.*?)</p>",
        "target_pattern": "<p class=\"article-text\">\\1</p>"
      }
    ]
  },
  "image_configs": {
    "target_width": 1000,
    "quality": 92,
    "format": "JPEG",
    "css_classes": "wp-image aligncenter"
  },
  "notes": "Main company blog"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "project_id": "acme_blog",
    "message": "Project created successfully"
  },
  "timestamp": "2025-11-13T10:30:00Z"
}
```

---

#### `GET /api/v1/projects`
List all projects.

**Query Parameters**:
- `status` (optional): Filter by status (`active`, `inactive`, `all`)
- `limit` (optional): Limit number of results

**Response**:
```json
{
  "success": true,
  "data": {
    "projects": [
      {
        "project_id": "acme_blog",
        "project_name": "Acme Corp Blog",
        "wordpress_url": "https://blog.acmecorp.com",
        "wordpress_username": "admin",
        "html_patterns_count": 8,
        "image_width": 1000,
        "status": "active",
        "created_at": "2025-11-13T10:00:00Z",
        "last_published_at": "2025-11-13T10:25:00Z"
      }
    ],
    "count": 1
  }
}
```

---

#### `GET /api/v1/projects/{project_id}`
Get detailed project information.

**Response**:
```json
{
  "success": true,
  "data": {
    "project_id": "acme_blog",
    "project_name": "Acme Corp Blog",
    "wordpress_url": "https://blog.acmecorp.com",
    "wordpress_username": "admin",
    "html_patterns_count": 8,
    "image_width": 1000,
    "status": "active",
    "html_configs": { ... },
    "image_configs": { ... },
    "notes": "Main company blog"
  }
}
```

---

#### `PUT /api/v1/projects/{project_id}`
Update project configuration.

**Body** (all fields optional):
```json
{
  "project_name": "New Name",
  "wordpress_url": "https://newurl.com",
  "status": "inactive",
  "notes": "Updated notes"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "project_id": "acme_blog",
    "message": "Project updated successfully"
  }
}
```

---

#### `DELETE /api/v1/projects/{project_id}`
Delete a project.

**Response**:
```json
{
  "success": true,
  "data": {
    "project_id": "acme_blog",
    "message": "Project deleted successfully"
  }
}
```

---

#### `GET /api/v1/projects/{project_id}/stats`
Get project statistics.

**Response**:
```json
{
  "success": true,
  "data": {
    "project_id": "acme_blog",
    "project_name": "Acme Corp Blog",
    "total_publishes": 50,
    "successful_publishes": 48,
    "failed_publishes": 2,
    "success_rate": 96.0,
    "avg_execution_time": 45.2,
    "last_publish_date": "2025-11-13T10:25:00Z"
  }
}
```

---

### Publishing

#### `POST /api/v1/publish`
Publish single content from Google Docs to WordPress.

**Body**:
```json
{
  "google_docs_url": "https://docs.google.com/document/d/ABC123/edit",
  "project_id": "acme_blog"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "success": true,
    "post_title": "How to Use Our Product",
    "post_url": "https://blog.acmecorp.com/how-to-use-our-product/",
    "wordpress_post_id": 1234,
    "images_processed": 5,
    "execution_time": 45.2
  }
}
```

---

#### `POST /api/v1/publish/batch` 🔥
Publish multiple pieces of content in parallel.

**Key endpoint for Lark Base integration!**

**Body**:
```json
{
  "items": [
    {
      "google_docs_url": "https://docs.google.com/document/d/ABC123/edit",
      "project_id": "acme_blog",
      "item_id": "row_1"
    },
    {
      "google_docs_url": "https://docs.google.com/document/d/XYZ789/edit",
      "project_id": "client_site",
      "item_id": "row_2"
    }
  ]
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "total": 2,
    "successful": 2,
    "failed": 0,
    "results": [
      {
        "item_id": "row_1",
        "google_docs_url": "https://docs.google.com/document/d/ABC123/edit",
        "success": true,
        "post_url": "https://blog.acmecorp.com/article-1/",
        "error": null
      },
      {
        "item_id": "row_2",
        "google_docs_url": "https://docs.google.com/document/d/XYZ789/edit",
        "success": true,
        "post_url": "https://client-site.com/article-2/",
        "error": null
      }
    ]
  }
}
```

---

#### `GET /api/v1/publish/history`
Get publishing history.

**Query Parameters**:
- `project_id` (optional): Filter by project
- `limit` (optional): Limit results (default: 50)
- `offset` (optional): Offset for pagination

**Response**:
```json
{
  "success": true,
  "data": {
    "history": [
      {
        "id": 1,
        "google_docs_url": "https://docs.google.com/document/d/ABC123/edit",
        "project_id": "acme_blog",
        "project_name": "Acme Corp Blog",
        "success": true,
        "post_title": "Article Title",
        "post_url": "https://blog.acmecorp.com/article/",
        "wordpress_post_id": 1234,
        "images_processed": 5,
        "execution_time": 45.2,
        "published_at": "2025-11-13T10:25:00Z"
      }
    ],
    "count": 1,
    "offset": 0
  }
}
```

---

#### `POST /api/v1/publish/analyze-html`
Analyze HTML sample and extract patterns.

**Body**:
```json
{
  "html_sample": "<p class=\"article\">Sample text</p><h2 class=\"title\">Heading</h2>"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "success": true,
    "html_configs": {
      "patterns": [ ... ]
    },
    "patterns_found": 8
  }
}
```

---

#### `POST /api/v1/publish/modify-patterns`
Modify HTML patterns using natural language.

**Body**:
```json
{
  "project_id": "acme_blog",
  "instruction": "Make all h2 headings blue"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "success": true,
    "previews": [
      {
        "element_type": "h2",
        "current_pattern": "<h2 class=\"title\">\\1</h2>",
        "modified_pattern": "<h2 class=\"title\" style=\"color: blue;\">\\1</h2>",
        "changes_description": "Modified h2 pattern"
      }
    ],
    "modified_html_configs": { ... },
    "message": "Preview generated. Use PUT /projects/{project_id} to save changes."
  }
}
```

---

## 📝 Example Usage

### Python (requests)

```python
import requests

API_URL = "http://localhost:8000/api/v1"
API_KEY = "your-api-key"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# List projects
response = requests.get(f"{API_URL}/projects", headers=headers)
projects = response.json()

# Publish content
data = {
    "google_docs_url": "https://docs.google.com/document/d/ABC123/edit",
    "project_id": "acme_blog"
}
response = requests.post(f"{API_URL}/publish", headers=headers, json=data)
result = response.json()

print(result['data']['post_url'])
```

### cURL

```bash
# Health check
curl http://localhost:8000/api/v1/health

# List projects
curl -H "X-API-Key: your-api-key" \
     http://localhost:8000/api/v1/projects

# Publish content
curl -X POST \
     -H "X-API-Key: your-api-key" \
     -H "Content-Type: application/json" \
     -d '{"google_docs_url":"https://docs.google.com/document/d/ABC123/edit","project_id":"acme_blog"}' \
     http://localhost:8000/api/v1/publish

# Batch publish
curl -X POST \
     -H "X-API-Key: your-api-key" \
     -H "Content-Type: application/json" \
     -d '{"items":[{"google_docs_url":"https://docs.google.com/document/d/ABC123/edit","project_id":"acme_blog","item_id":"row_1"}]}' \
     http://localhost:8000/api/v1/publish/batch
```

---

## 🚀 Deployment

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Generate API keys
python api/core/security.py

# Add keys to .env
echo "API_KEYS=generated-key-here" >> .env

# Run server
python api/main.py

# Or use uvicorn directly
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build manually
docker build -t wordpress-seo-api .
docker run -p 8000:8000 --env-file .env wordpress-seo-api
```

### Production

See `LARK_IMPLEMENTATION_PLAN.md` for production deployment guide including:
- NGINX reverse proxy
- SSL certificates
- Monitoring and logging
- Scaling strategies

---

## 🔗 Interactive Documentation

Once the API is running, visit:

- **Swagger UI**: `http://localhost:8000/api/v1/docs`
- **ReDoc**: `http://localhost:8000/api/v1/redoc`

These provide interactive API documentation where you can test endpoints directly.

---

## 🐛 Error Handling

All endpoints return a standard response format:

**Success**:
```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "timestamp": "2025-11-13T10:30:00Z"
}
```

**Error**:
```json
{
  "success": false,
  "data": null,
  "error": "Error message here",
  "timestamp": "2025-11-13T10:30:00Z"
}
```

**HTTP Status Codes**:
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized (invalid/missing API key)
- `404` - Not Found
- `500` - Internal Server Error

---

## 🔄 Rate Limiting

Default rate limit: 60 requests per minute per API key.

Configure in `.env`:
```env
RATE_LIMIT_PER_MINUTE=60
```

---

## 📊 Monitoring

### Logs

Logs are written to stdout/stderr and can be configured via `LOG_LEVEL` environment variable:

```env
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Health Checks

Use `/health` endpoint for monitoring:

```bash
# Kubernetes liveness probe
livenessProbe:
  httpGet:
    path: /api/v1/health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
```

---

**Last Updated**: 2025-11-13
**Version**: 1.0.0
