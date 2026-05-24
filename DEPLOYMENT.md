# Deployment Guide - GenAI Chat Assistant with RAG

Choose one of the platforms below. **Render** is recommended for quick deployment.

---

## 🎯 Option 1: Deploy to Render (Recommended)

### Why Render?
✓ Free tier available
✓ Easy GitHub integration
✓ Automatic deployments
✓ Built-in environment variables
✓ No credit card required (for free tier)

### Steps

#### 1. Push Code to GitHub

```bash
# Initialize git repo (if not already done)
git init
git add .
git commit -m "Initial commit: RAG Chat Assistant"

# Create new GitHub repo and push
git remote add origin https://github.com/yourusername/rag-chat-assistant.git
git branch -M main
git push -u origin main
```

#### 2. Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub account
3. Click "New +"
4. Select "Web Service"

#### 3. Configure Service

1. **Connect Repository**
   - Select your GitHub repo
   - Grant permissions

2. **Settings**
   - **Name:** rag-chat-assistant
   - **Environment:** Python
   - **Region:** Choose nearest to you
   - **Branch:** main
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Environment Variables**
   - Click "Advanced"
   - Add: `ANTHROPIC_API_KEY=sk_test_...` (your actual key)

4. **Plan**
   - Free (limited resources, sleeps after 15min inactivity)
   - Paid ($7/month) for production

#### 4. Deploy

Click "Create Web Service" → Render builds and deploys automatically

**Your app is live at:** `https://rag-chat-assistant.onrender.com`

---

## 🚂 Option 2: Deploy to Railway

### Why Railway?
✓ $5 free credits/month
✓ Simple deployment
✓ GitHub integration
✓ Fast startup

### Steps

#### 1. Create Railway Account

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Create new project

#### 2. Add Service

1. Click "Add Service"
2. Select "GitHub Repo"
3. Select your repo

#### 3. Configure

1. Environment variables:
   - `ANTHROPIC_API_KEY=sk_test_...`

2. Build settings:
   - Railway auto-detects Python
   - Add `requirements.txt` (already done)

3. Start command (optional, usually auto-detected):
   ```
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

#### 4. Deploy

Click "Deploy" → Railway automatically builds and deploys

**Your app is live at:** `https://rag-chat-assistant-production.up.railway.app`

---

## ☁️ Option 3: Deploy to AWS (EC2)

### Why AWS?
✓ Full control
✓ Scalable
✓ Production-grade
✓ Free tier available (limited)

### Steps

#### 1. Create EC2 Instance

1. Go to AWS Console
2. EC2 → Instances → Launch Instance
3. Select "Ubuntu 22.04 LTS" (free tier eligible)
4. Instance type: t2.micro (free)
5. Configure security group:
   - Allow HTTP (80)
   - Allow HTTPS (443)
   - Allow SSH (22)

#### 2. Connect & Setup

```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3.10 python3-pip python3-venv git -y

# Clone repo
git clone https://github.com/yourusername/rag-chat-assistant.git
cd rag-chat-assistant

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "ANTHROPIC_API_KEY=sk_test_..." > .env
```

#### 3. Run with Gunicorn

```bash
# Install gunicorn
pip install gunicorn

# Run
gunicorn -w 4 -b 0.0.0.0:8000 main:app
```

#### 4. Setup Systemd Service (Recommended)

Create `/etc/systemd/system/rag-assistant.service`:

```ini
[Unit]
Description=RAG Chat Assistant
After=network.target

[Service]
Type=notify
User=ubuntu
WorkingDirectory=/home/ubuntu/rag-chat-assistant
Environment="PATH=/home/ubuntu/rag-chat-assistant/venv/bin"
ExecStart=/home/ubuntu/rag-chat-assistant/venv/bin/gunicorn \
    -w 4 -b 0.0.0.0:8000 main:app

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable rag-assistant
sudo systemctl start rag-assistant
```

#### 5. Setup Nginx Reverse Proxy

```bash
# Install nginx
sudo apt install nginx -y

# Create config: /etc/nginx/sites-available/rag-assistant
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/rag-assistant /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**Your app is live at:** `https://your-domain.com`

---

## 🍃 Option 4: Deploy to Google Cloud Run

### Why Cloud Run?
✓ Serverless
✓ Auto-scaling
✓ Free tier available
✓ Pay per invocation

### Steps

#### 1. Create Dockerfile

Create `Dockerfile` in project root:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 2. Push to Google Cloud

```bash
# Install gcloud CLI
# https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID

# Build and deploy
gcloud run deploy rag-chat-assistant \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars ANTHROPIC_API_KEY=sk_test_...
```

**Your app is live at:** `https://rag-chat-assistant-xxxxx.a.run.app`

---

## 💻 Option 5: Local Development

Run locally on your machine:

```bash
# Setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env
echo "ANTHROPIC_API_KEY=sk_test_..." > .env

# Run
python -m main

# Access at: http://localhost:8000
```

---

## ✅ Deployment Checklist

Before submitting, verify:

- [ ] Code pushed to GitHub (public repo)
- [ ] Deployment working (live URL accessible)
- [ ] Environment variables configured (ANTHROPIC_API_KEY set)
- [ ] Chat working end-to-end
- [ ] Error handling working
- [ ] README complete with architecture
- [ ] docs.json has 5-10 documents
- [ ] Frontend loads without errors
- [ ] API endpoints responding correctly

### Test Endpoints

```bash
# Health check
curl https://your-deployed-app.com/health

# Sample chat
curl -X POST https://your-deployed-app.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{"sessionId":"test","message":"How do I reset my password?"}'
```

---

## 🚨 Troubleshooting

### Issue: App crashes on deployment

**Render:** Check deploy logs → Settings → Logs
**Railway:** Check railway.app dashboard → Logs
**AWS/GCP:** Check CloudWatch / Cloud Logging

### Issue: "Module not found" error

**Solution:** 
```bash
pip install -r requirements.txt
```

Ensure `requirements.txt` is in root directory.

### Issue: "ANTHROPIC_API_KEY not found"

**Solution:** Set environment variable in your platform's settings:
- Render: Advanced → Environment
- Railway: Variables
- AWS: EC2 instance .env file
- GCP: Cloud Run → set-env-vars

### Issue: Slow responses

- First request is slow (model loading) - normal
- Check Claude API status
- Verify internet connection

### Issue: 502 Bad Gateway

- Service crashed, check logs
- Memory insufficient, try larger instance
- Port not accessible, check firewall rules

---

## 📦 Production Recommendations

For production deployment:

1. **Use paid tier** - Free tiers sleep/have limits
2. **Enable HTTPS** - Use Let's Encrypt
3. **Monitor errors** - Setup logging/alerts
4. **Cache responses** - Redis (optional)
5. **Rate limiting** - Prevent abuse
6. **Database** - Move to PostgreSQL/MongoDB
7. **CDN** - CloudFront for static files

---

## 🎯 Quick Deployment Cheat Sheet

### Render (Fastest)
```
1. GitHub → Push code
2. Render.com → New Web Service
3. Connect GitHub repo
4. Add ANTHROPIC_API_KEY
5. Deploy! ✓
```

### Railway (Fast)
```
1. GitHub → Push code
2. Railway.app → New Project
3. Add service → Select repo
4. Set environment variable
5. Deploy! ✓
```

### Local (Development)
```
pip install -r requirements.txt
echo "ANTHROPIC_API_KEY=sk_..." > .env
python -m main
# Access http://localhost:8000
```

---

**Choose Render for simplest deployment!** 🎉

Questions? Check the README.md for more info.
