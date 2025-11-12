# Lark Base Setup Guide

**Complete guide to integrate WordPress SEO Publishing API with Lark Base**

This enables your team to publish content via a visual interface with button-driven workflows.

---

## 🎯 What You'll Build

```
┌─────────────────────────────────────────────────────────┐
│                      LARK BASE                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Table 1: Project Configurations  (Read-Only View)      │
│  - List of all WordPress projects                       │
│  - Click to view details                                │
│                                                          │
│  Table 2: Content Publishing Queue  (Interactive)       │
│  - Add Google Docs URLs                                 │
│  - Select project                                       │
│  - Click [Process] button → Publishes automatically     │
│  - Status updates in real-time                          │
│  - Bulk process: Select multiple → Process all          │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 Prerequisites

1. **API Server Running**
   - FastAPI server deployed and accessible
   - API keys generated
   - URL: `http://your-server:8000`

2. **Larksuite Admin Access**
   - Permission to create Lark Base
   - Permission to create automations
   - Permission to use webhooks

3. **API Key**
   - Generate API key: `python api/core/security.py`
   - Add to Lark Base webhook configuration

---

## 🏗️ Step 1: Create Lark Base

### 1.1 Create New Base

1. Open Larksuite
2. Go to **Lark Base**
3. Click **+ Create** → **New Base**
4. Name: `WordPress SEO Publishing`
5. Description: `Multi-project WordPress content publishing system`

---

## 📊 Step 2: Table 1 - Project Configurations

### 2.1 Create Table

1. Click **+ Add Table**
2. Name: `Projects`
3. Description: `WordPress project configurations`

### 2.2 Add Columns

| Column Name | Field Type | Description | Configuration |
|-------------|------------|-------------|---------------|
| `project_id` | Text | Project identifier | Primary key |
| `project_name` | Text | Display name | - |
| `wordpress_url` | URL | WordPress site URL | - |
| `wordpress_username` | Text | WP username | - |
| `html_patterns_count` | Number | Number of patterns | Read-only |
| `image_width` | Number | Image width (px) | - |
| `status` | Select | Project status | Options: Active, Inactive |
| `last_published_at` | Date | Last publish time | Auto-update |
| `created_at` | Date | Creation date | Auto-fill on create |
| `notes` | Long Text | Project notes | - |

### 2.3 Add Buttons

#### Button: "View Details"
- **Action**: Open URL
- **URL**: `http://your-server:8000/api/v1/projects/{{project_id}}`
- **Description**: View full project configuration

#### Button: "Refresh from API"
- **Action**: Run Automation
- **Automation**: Sync projects from API (see Step 4)

---

## 📝 Step 3: Table 2 - Content Queue

### 3.1 Create Table

1. Click **+ Add Table**
2. Name: `Content Queue`
3. Description: `Publishing queue with automated workflow`

### 3.2 Add Columns

| Column Name | Field Type | Description | Configuration |
|-------------|------------|-------------|---------------|
| `id` | Auto Number | Unique ID | Auto-increment |
| `google_docs_url` | URL | Google Docs link | Required |
| `project` | Link to Table | Link to Projects table | Required |
| `status` | Select | Publishing status | Options: Queued, Processing, Success, Failed |
| `post_title` | Text | WordPress post title | Auto-fill after publish |
| `post_url` | URL | Published post URL | Auto-fill after publish |
| `wordpress_post_id` | Number | WP post ID | Auto-fill after publish |
| `images_processed` | Number | Number of images | Auto-fill after publish |
| `error_message` | Long Text | Error details | Auto-fill on failure |
| `submitted_by` | Person | Who submitted | Auto-fill with current user |
| `submitted_at` | Date | Submission time | Auto-fill on create |
| `processed_at` | Date | Processing time | Auto-fill after process |
| `execution_time` | Number | Time taken (seconds) | Auto-fill after process |

### 3.3 Set Default Values

- `status` → Default: **Queued**
- `submitted_by` → Default: **Current User**
- `submitted_at` → Default: **Now()**

### 3.4 Add Buttons

#### Button: "Process" (Single Row)
- **Placement**: Row action button
- **Label**: `🚀 Process`
- **Action**: Run Automation → `Publish Single Content`
- **Confirmation**: "Publish this content to WordPress?"

#### Button: "Process Selected" (Bulk)
- **Placement**: Table toolbar
- **Label**: `⚡ Process Selected`
- **Action**: Run Automation → `Batch Publish`
- **Confirmation**: "Publish {count} selected items?"

#### Button: "View Post"
- **Placement**: Row action button (conditional: show if `post_url` not empty)
- **Label**: `📄 View Post`
- **Action**: Open URL → `{{post_url}}`

---

## 🤖 Step 4: Create Automations

### Automation 1: Publish Single Content

**Trigger**: Button click on "Process"

**Steps**:

1. **Update Status**
   - Field: `status`
   - Value: `Processing`

2. **HTTP Request**
   - Method: `POST`
   - URL: `http://your-server:8000/api/v1/publish`
   - Headers:
     ```json
     {
       "X-API-Key": "your-api-key-here",
       "Content-Type": "application/json"
     }
     ```
   - Body:
     ```json
     {
       "google_docs_url": "{{google_docs_url}}",
       "project_id": "{{project.project_id}}"
     }
     ```

3. **Condition: If Success**
   - **Update Record**:
     - `status` → `Success`
     - `post_title` → `{{response.data.post_title}}`
     - `post_url` → `{{response.data.post_url}}`
     - `wordpress_post_id` → `{{response.data.wordpress_post_id}}`
     - `images_processed` → `{{response.data.images_processed}}`
     - `processed_at` → `Now()`
     - `execution_time` → `{{response.data.execution_time}}`

4. **Condition: If Failed**
   - **Update Record**:
     - `status` → `Failed`
     - `error_message` → `{{response.error}}`
     - `processed_at` → `Now()`

5. **Send Notification**
   - To: `{{submitted_by}}`
   - Message: `✅ Published: {{post_title}} - {{post_url}}` (if success)
   - Or: `❌ Failed: {{error_message}}` (if failed)

---

### Automation 2: Batch Publish

**Trigger**: Button click on "Process Selected"

**Steps**:

1. **Update Status (All Selected)**
   - Field: `status`
   - Value: `Processing`

2. **HTTP Request**
   - Method: `POST`
   - URL: `http://your-server:8000/api/v1/publish/batch`
   - Headers:
     ```json
     {
       "X-API-Key": "your-api-key-here",
       "Content-Type": "application/json"
     }
     ```
   - Body:
     ```json
     {
       "items": [
         {{#each selectedRecords}}
         {
           "google_docs_url": "{{google_docs_url}}",
           "project_id": "{{project.project_id}}",
           "item_id": "{{id}}"
         }{{#unless @last}},{{/unless}}
         {{/each}}
       ]
     }
     ```

3. **For Each Result**
   - **Find Record by ID**: `{{item_id}}`
   - **Condition: If result.success = true**
     - Update: `status` → `Success`
     - Update: `post_url` → `{{result.post_url}}`
     - Update: `processed_at` → `Now()`
   - **Condition: If result.success = false**
     - Update: `status` → `Failed`
     - Update: `error_message` → `{{result.error}}`
     - Update: `processed_at` → `Now()`

4. **Send Summary Notification**
   - To: `{{current_user}}`
   - Message: `✅ Batch complete: {{response.data.successful}}/{{response.data.total}} successful`

---

### Automation 3: Sync Projects from API

**Trigger**: Manual button click or schedule (daily)

**Steps**:

1. **HTTP Request**
   - Method: `GET`
   - URL: `http://your-server:8000/api/v1/projects`
   - Headers:
     ```json
     {
       "X-API-Key": "your-api-key-here"
     }
     ```

2. **For Each Project in Response**
   - **Find or Create Record**
     - Search by: `project_id` = `{{project.project_id}}`
     - If found: Update
     - If not found: Create

   - **Update Fields**:
     - `project_id` → `{{project.project_id}}`
     - `project_name` → `{{project.project_name}}`
     - `wordpress_url` → `{{project.wordpress_url}}`
     - `wordpress_username` → `{{project.wordpress_username}}`
     - `html_patterns_count` → `{{project.html_patterns_count}}`
     - `image_width` → `{{project.image_width}}`
     - `status` → `{{project.status}}`
     - `last_published_at` → `{{project.last_published_at}}`

---

## 🎨 Step 5: Views and Filters

### View 1: Active Projects (Table 1)
- **Filter**: `status` = `Active`
- **Sort**: `last_published_at` DESC

### View 2: Queued Content (Table 2)
- **Filter**: `status` = `Queued`
- **Sort**: `submitted_at` ASC
- **Purpose**: See what's waiting to be processed

### View 3: Processing (Table 2)
- **Filter**: `status` = `Processing`
- **Auto-refresh**: Every 30 seconds
- **Purpose**: Monitor active publishes

### View 4: Recent Success (Table 2)
- **Filter**: `status` = `Success`
- **Sort**: `processed_at` DESC
- **Limit**: Last 50

### View 5: Failed (Table 2)
- **Filter**: `status` = `Failed`
- **Sort**: `processed_at` DESC
- **Highlight**: Red background
- **Purpose**: Review and retry failures

---

## 📱 Step 6: Mobile App Setup

### Enable Mobile Access

1. **Lark Mobile App**
   - Install Lark on mobile devices
   - Log in with company account

2. **Add Widget**
   - Add "Lark Base" widget to home screen
   - Pin "Content Queue" table

3. **Mobile Workflow**
   - User submits Google Docs URL from mobile
   - Click Process button
   - Receive notification when published

---

## 👥 Step 7: User Permissions

### Configure Access Levels

**Table 1 (Projects)**:
- **Admin**: Full edit access
- **Editors**: Read-only (can't modify project configs)
- **Viewers**: Read-only

**Table 2 (Content Queue)**:
- **Admin**: Full access
- **Editors**: Can add rows, click Process buttons
- **Viewers**: Read-only

### Sharing Settings

1. Go to Base Settings → Sharing
2. Add team members
3. Set permission level per user
4. Enable "Anyone with link can view" (optional)

---

## 🔔 Step 8: Notifications

### Configure Notification Rules

**On Publish Success**:
- **Trigger**: `status` changes to `Success`
- **Notify**: `submitted_by`
- **Message**: `✅ Your content "{post_title}" was published! View at: {post_url}`
- **Channels**: Lark message + Email

**On Publish Failure**:
- **Trigger**: `status` changes to `Failed`
- **Notify**: `submitted_by` + `@admins`
- **Message**: `❌ Publishing failed for {google_docs_url}. Error: {error_message}`
- **Channels**: Lark message

**Daily Summary**:
- **Trigger**: Schedule (daily at 9 AM)
- **Notify**: `@channel`
- **Message**: `📊 Yesterday: {count_success} published, {count_failed} failed`

---

## 📊 Step 9: Dashboard & Analytics

### Create Dashboard View

1. **Add Dashboard Page**
   - Name: `Publishing Analytics`

2. **Add Widgets**:

   **Widget 1: Success Rate**
   - Type: Pie Chart
   - Data: Count of `status` (Success vs Failed)

   **Widget 2: Publishes Over Time**
   - Type: Line Chart
   - X-axis: `processed_at` (by day)
   - Y-axis: Count of records

   **Widget 3: By Project**
   - Type: Bar Chart
   - X-axis: `project.project_name`
   - Y-axis: Count of successful publishes

   **Widget 4: Avg Execution Time**
   - Type: Number
   - Value: Average of `execution_time`

   **Widget 5: Active Queue**
   - Type: Number (Large)
   - Value: Count where `status` = `Queued`

---

## 🧪 Step 10: Testing

### Test Workflow

1. **Add Test Content**
   - Table 2 → Add New
   - Google Docs URL: (paste test doc)
   - Project: Select test project
   - Status: Auto-fills to `Queued`

2. **Click Process Button**
   - Watch status change: `Queued` → `Processing`
   - Wait 30-60 seconds
   - Status should change to `Success` or `Failed`

3. **Verify Result**
   - If Success: `post_url` should be filled
   - Click "View Post" button
   - Verify post is on WordPress

4. **Test Bulk Processing**
   - Add 3-5 test rows
   - Select all
   - Click "Process Selected"
   - All should process in parallel (~1 minute)

---

## 🚀 Step 11: Training & Rollout

### Training Materials

1. **Quick Start Guide** (for employees):
   ```
   HOW TO PUBLISH CONTENT
   ======================
   1. Write your article in Google Docs
   2. Click "Share" → "Copy link"
   3. Go to Lark Base "Content Queue" table
   4. Click "+ New" row
   5. Paste Google Docs URL
   6. Select your project
   7. Click "🚀 Process" button
   8. Wait for notification (30-60 seconds)
   9. Done! ✅
   ```

2. **Video Tutorial** (5 minutes):
   - Screen recording showing full workflow
   - Share in team chat

3. **FAQ Document**:
   - Common errors and solutions
   - Who to contact for help

### Rollout Plan

**Week 1**: Pilot with 2-3 power users
- Gather feedback
- Fix any issues

**Week 2**: Expand to full team (20 users)
- Announce in team meeting
- Share training materials
- Monitor closely

**Week 3**: Review and optimize
- Analyze usage patterns
- Optimize workflows
- Add requested features

---

## 🔧 Troubleshooting

### Issue: "Process" button does nothing
**Solution**: Check automation is enabled and API key is correct

### Issue: Status stuck on "Processing"
**Solution**:
1. Check API server is running
2. Check network connectivity
3. Manually update status to "Queued" and retry

### Issue: "Failed" status with error message
**Solution**:
1. Read error_message field
2. Common errors:
   - "Invalid API key" → Update API key in automation
   - "Project not found" → Check project_id exists
   - "Google Docs access denied" → Check doc is shared publicly

### Issue: Batch publish times out
**Solution**:
- Reduce batch size (max 10-15 items at once)
- Process in multiple batches

---

## 📚 Advanced Features

### Custom Views

**My Content**:
- Filter: `submitted_by` = `Current User`
- Sort: `submitted_at` DESC

**By Client** (grouped view):
- Group by: `project.project_name`
- Collapse all groups by default

### Scheduled Publishing

1. Add column: `scheduled_for` (Date)
2. Create automation:
   - Trigger: Schedule (every hour)
   - Filter: `status` = `Queued` AND `scheduled_for` <= `Now()`
   - Action: Run "Publish Single Content"

### Approval Workflow

1. Add columns: `requires_approval`, `approved_by`, `approved_at`
2. Add button: "Request Approval"
3. Add automation: Notify manager when approval requested
4. Manager clicks "Approve" → Auto-processes

---

## 🎉 Success Metrics

Track these KPIs:

- **Daily Publishes**: Average content pieces published per day
- **Success Rate**: % of publishes that succeed
- **Avg Time**: Average execution time
- **User Adoption**: Number of unique users publishing
- **Error Rate**: % of failures (target: < 5%)

**Target Goals** (after 1 month):
- 20+ pieces published daily
- 95%+ success rate
- < 60 seconds avg processing time
- All 20 team members actively using

---

## 🔗 Resources

- **API Documentation**: See `API_DOCUMENTATION.md`
- **API Server**: `http://your-server:8000/api/v1/docs`
- **Lark Base Docs**: https://open.larksuite.com/document/home/integrating-lark-base-with-automations
- **Support**: Contact IT team or check internal wiki

---

**Last Updated**: 2025-11-13
**Version**: 1.0.0
**Status**: Ready for Implementation ✅
