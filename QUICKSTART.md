🚀 QUICK START GUIDE - RAG Chat Assistant
==========================================

📋 What You Got:
===============
A complete, production-ready GenAI Chat Assistant with RAG that uses Claude API.

⏱️ DEADLINE: Tuesday, May 26th, 2026 @ 10:00 AM (34 hours)

🎯 Next 10 Minutes:
===================

1️⃣ GET YOUR CLAUDE API KEY
   → Go to: https://console.anthropic.com/account/keys
   → Click "Create Key"
   → Copy the key (starts with sk_test_)

2️⃣ EXTRACT THE PROJECT
   → Download all files from the outputs folder
   → Unzip to your desired location
   → cd into the project folder

3️⃣ SETUP THE PROJECT (Choose your OS)

   🐧 Linux/Mac:
   ```
   bash setup.sh
   ```

   🪟 Windows:
   ```
   setup.bat
   ```

   📝 Manual (All OS):
   ```
   python -m venv venv
   source venv/bin/activate  (Windows: venv\Scripts\activate)
   pip install -r requirements.txt
   ```

4️⃣ CREATE .env FILE
   ```
   Copy .env.example → .env
   Edit .env and paste your API key:
   ANTHROPIC_API_KEY=sk_test_xxxxxxxxxxxxx
   ```

5️⃣ RUN THE APP
   ```
   python -m main
   ```
   
   Open browser: http://localhost:8000
   ✓ Chat with the assistant!

✅ VERIFY IT WORKS (5 minutes)
============================

Test these questions:
- "How do I reset my password?"
- "What are your subscription plans?"
- "How is my data protected?"

All should get answers from the knowledge base.

📦 READY TO DEPLOY (Before Deadline)
====================================

Choose ONE platform:

🌐 EASIEST - Render.com (Recommended)
   1. Create Render account (free, no credit card)
   2. Push code to GitHub (public repo)
   3. Connect GitHub repo to Render
   4. Add ANTHROPIC_API_KEY environment variable
   5. Deploy! (Takes 2-3 minutes)
   
   Your live app: https://rag-chat-assistant.onrender.com

🚂 ALTERNATIVE - Railway.app
   Similar to Render, just connect GitHub repo

☁️ PRODUCTION - AWS/Google Cloud
   See DEPLOYMENT.md for detailed instructions

📝 SUBMISSION REQUIREMENTS
=========================

Before submitting, you need:

✓ GitHub Repository (public)
  - All source code
  - README.md (already complete!)
  - DEPLOYMENT.md (included)
  - requirements.txt
  - docs.json
  - /frontend folder

✓ Live Deployed Application
  - Working URL
  - Accessible from browser
  - Chat working end-to-end

✓ Submit Form
  - GitHub URL: https://github.com/yourusername/rag-chat-assistant
  - Live App URL: https://your-deployed-app.com
  - Submit at: https://forms.ccbp.in/form/interview-process-status?round=assignment&job_id=db0ba480-3444-4891-a3af-e07f69990bc4

🗂️ PROJECT STRUCTURE
====================

rag-chat-assistant/
├── main.py                    # FastAPI server
├── rag.py                     # RAG pipeline
├── embeddings.py              # Embedding generation
├── retrieval.py               # Vector search
├── llm.py                     # Claude integration
├── storage.py                 # Data storage
├── docs.json                  # Knowledge base (8 documents)
├── requirements.txt           # Dependencies
├── .env.example               # Environment template
├── .gitignore                 # Git configuration
├── README.md                  # Full documentation (17KB)
├── DEPLOYMENT.md              # Deployment guide
├── setup.sh                   # Linux/Mac setup
├── setup.bat                  # Windows setup
└── frontend/
    ├── index.html             # Chat interface
    ├── style.css              # Styling
    └── app.js                 # Frontend logic

💡 KEY IMPLEMENTATION DETAILS
=============================

✓ RAG Pipeline (30% weight)
  - Document chunking by sentences
  - 8 documents with meaningful content
  - Embedding generation using sentence-transformers
  - Vector storage with cosine similarity search

✓ Embedding & Similarity (25% weight)
  - Uses all-MiniLM-L6-v2 (local, fast)
  - Cosine similarity: ranges 0-1
  - Threshold filtering (≥0.75)
  - Top-3 retrieval

✓ LLM Integration (20% weight)
  - Claude 3.5 Sonnet API
  - Temperature: 0.2 (factual)
  - Token usage tracking
  - Error handling for timeouts/rate limits

✓ Prompt Design (10% weight)
  - System instructions
  - Retrieved context (grounded)
  - Conversation history
  - User question

✓ Frontend (5% weight)
  - Beautiful chat UI
  - Session management
  - Loading indicators
  - Retrieval metrics

✓ Code Quality (10% weight)
  - Error handling throughout
  - Logging statements
  - Type hints
  - Modular design

🐛 TROUBLESHOOTING
==================

Issue: "ModuleNotFoundError: No module named 'anthropic'"
→ Run: pip install -r requirements.txt

Issue: "ANTHROPIC_API_KEY not found"
→ Create .env file with your API key

Issue: "Address already in use: 0.0.0.0:8000"
→ Change port: uvicorn main:app --port 8001

Issue: "SSL: CERTIFICATE_VERIFY_FAILED"
→ Check internet connection, Claude API status

Issue: No response from assistant
→ Check .env file has valid API key
→ Test: curl http://localhost:8000/health

💬 SAMPLE QUESTIONS FOR TESTING
===============================

The knowledge base includes:
1. Account Creation and Registration
2. Password Reset and Security
3. Profile Management
4. Billing and Subscriptions
5. Data Privacy and Protection
6. Customer Support
7. Data Export and Account Deletion
8. Two-Factor Authentication

Try asking:
✓ "How do I create an account?"
✓ "What's your free plan?"
✓ "How do I enable two-factor authentication?"
✓ "Is my data secure?"
✓ "Can I delete my account?"

If Claude can't answer → It's working! (RAG threshold filtering)

📞 SUPPORT
==========

If stuck:
1. Check README.md (comprehensive guide)
2. Check DEPLOYMENT.md (for deployment help)
3. Look at error messages in terminal
4. Verify API key in .env file
5. Check Claude API status/quota

⏰ TIME MANAGEMENT (34 hours)
=============================

Suggested timeline:
- 0-1 hour: Setup and run locally ✓
- 1-4 hours: Test and verify everything works
- 4-6 hours: Deploy to Render/Railway
- 6-8 hours: Create GitHub repo and push code
- 8 hours: Buffer time for fixes
- Before deadline: Submit!

🎉 YOU'RE READY!
================

This is a production-grade implementation that meets all requirements:
✓ Python FastAPI backend
✓ Claude LLM integration
✓ Real RAG pipeline with embeddings
✓ Vector similarity search
✓ HTML/CSS/JS frontend
✓ Session management
✓ Error handling
✓ Complete documentation
✓ Easy deployment

Good luck with your assignment! 🚀

Questions? Check:
- README.md (architecture & setup)
- DEPLOYMENT.md (for deployment help)
- Code comments (inline documentation)

Deadline: Tuesday, May 26th, 2026 @ 10:00 AM

Submit here: https://forms.ccbp.in/form/interview-process-status?round=assignment&job_id=db0ba480-3444-4891-a3af-e07f69990bc4
