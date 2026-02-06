# Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Add Your OpenAI API Key

Edit the `.env` file:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### Step 2: Run Setup Commands

```powershell
# Install dependencies (if not already done)
pip install fastapi uvicorn openai chromadb sentence-transformers pydantic pydantic-settings python-dotenv python-multipart

# Ingest regulatory documents
python backend\ingest_documents.py

# Start the server
python -m uvicorn backend.main:app --reload
```

### Step 3: Open the App

Navigate to: **http://localhost:8000/static/index.html**

---

## 📝 Try These Sample Scenarios

Click the sample scenario buttons in the interface:

1. **CET1 Capital** - Common Equity Tier 1 classification
2. **AT1 Instrument** - Additional Tier 1 reporting  
3. **Deductions** - Regulatory deductions from capital

---

## 📚 Full Documentation

- **[README.md](file:///d:/Akoin_company_assignment/README.md)** - Complete project overview
- **[SETUP.md](file:///d:/Akoin_company_assignment/SETUP.md)** - Detailed setup and troubleshooting
- **[ARCHITECTURE.md](file:///d:/Akoin_company_assignment/ARCHITECTURE.md)** - Technical architecture

---

## ✨ What You'll See

The system will:
- ✅ Retrieve relevant PRA Rulebook sections
- ✅ Generate structured COREP field values
- ✅ Provide regulatory justifications
- ✅ Create complete audit trail
- ✅ Flag validation issues

---

**Ready for AKOIN evaluation!** 🎯
