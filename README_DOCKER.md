# Docker Deployment Guide

## Local Testing with Docker

### Build the Docker image locally:

```bash
docker build -t atlan-governance:latest .
```

### Run the container locally:

```bash
docker run -p 5000:5000 \
  -e SNOWFLAKE_ACCOUNT=your_account \
  -e SNOWFLAKE_USER=your_user \
  -e SNOWFLAKE_PASSWORD=your_password \
  -e SNOWFLAKE_WAREHOUSE=your_warehouse \
  -e SNOWFLAKE_DATABASE=your_database \
  -e SNOWFLAKE_SCHEMA=your_schema \
  atlan-governance:latest
```

Your API will be available at: **http://localhost:5000**

---

## Deploy to Render (Free)

### 1. Create GitHub Repository

```bash
git init
git add .
git commit -m "Initial commit with Docker support"
git remote add origin https://github.com/YOUR_USERNAME/atlan-governance.git
git push -u origin main
```

### 2. Deploy to Render

1. Go to https://render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `atlan-governance`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python src/atlan_api_server.py`
   - **Instance Type**: Free tier
5. Add Environment Variables:
   - `SNOWFLAKE_ACCOUNT`
   - `SNOWFLAKE_USER`
   - `SNOWFLAKE_PASSWORD`
   - `SNOWFLAKE_WAREHOUSE`
   - `SNOWFLAKE_DATABASE`
   - `SNOWFLAKE_SCHEMA`

6. Deploy!

Your API URL: `https://your-app-name.onrender.com`

---

## Environment Variables

| Variable              | Required | Description                   |
| --------------------- | -------- | ----------------------------- |
| `SNOWFLAKE_ACCOUNT`   | Yes      | Snowflake account ID          |
| `SNOWFLAKE_USER`      | Yes      | Snowflake username            |
| `SNOWFLAKE_PASSWORD`  | Yes      | Snowflake password            |
| `SNOWFLAKE_WAREHOUSE` | Yes      | Snowflake warehouse name      |
| `SNOWFLAKE_DATABASE`  | Yes      | Snowflake database name       |
| `SNOWFLAKE_SCHEMA`    | Yes      | Snowflake schema name         |
| `FLASK_ENV`           | No       | `production` or `development` |

---

## Test the Deployed API

### Using curl:

```bash
curl -X POST https://your-app-name.onrender.com/api/process \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mask ssn in accounts table",
    "nl_mode": "autonomous"
  }'
```

### Using Postman:

1. Create POST request to: `https://your-app-name.onrender.com/api/process`
2. Set Body (JSON):

```json
{
  "query": "mask balance in Accounts table for analyst role",
  "nl_mode": "autonomous"
}
```

---

## Share with Your Friend

**Share this URL**: `https://your-app-name.onrender.com`

Your friend can test the API immediately without any setup!

---

## Notes

- **Free tier limitation**: Render free tier goes to sleep after 15 min of inactivity (takes ~30s to wake up)
- **For production**: Upgrade to paid tier for always-on service
- **Data security**: Make sure to use environment variables for credentials, NOT hardcoded values
