# Setup Guide

## Quick Setup Steps

### 1. Install Dependencies

Open PowerShell in the project directory and run:

```powershell
cd d:\Akoin_company_assignment
pip install fastapi uvicorn openai chromadb sentence-transformers pydantic pydantic-settings python-dotenv python-multipart
```

### 2. Configure OpenAI API Key

Edit the `.env` file and add your OpenAI API key:

```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 3. Ingest Regulatory Documents

Run the document ingestion script:

```powershell
python backend\ingest_documents.py
```

You should see output like:
```
Initializing RAG engine...
Clearing existing documents...
Collection cleared

Ingesting PRA_Rulebook...
Ingested X chunks from ...pra_rulebook_sample.txt

Ingesting COREP_Instructions...
Ingested Y chunks from ...corep_instructions_sample.txt

✓ Document ingestion complete!
Total documents in collection: Z
```

### 4. Start the Backend Server

```powershell
python -m uvicorn backend.main:app --reload
```

The server will start at `http://localhost:8000`

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 5. Open the Frontend

Open your web browser and navigate to:

```
http://localhost:8000/static/index.html
```

Or simply open `frontend\index.html` directly in your browser.

---

## Testing the System

### Using Sample Scenarios

The interface includes 3 pre-configured scenarios. Click any of these buttons:

1. **CET1 Capital** - Tests Common Equity Tier 1 classification
2. **AT1 Instrument** - Tests Additional Tier 1 reporting
3. **Deductions** - Tests regulatory deductions

### Custom Query

Try this example:

**Question:**
```
How should this capital instrument be reported in COREP Own Funds?
```

**Scenario:**
```
The bank has issued £300 million of ordinary shares that are:
- Perpetual with no maturity date
- Fully paid up
- Have full voting rights
- Meet all CRR Article 28 criteria for CET1 classification
- Approved by shareholders

The bank also has £150 million in retained earnings that have been verified by external auditors and are net of all foreseeable dividends.
```

**Template:** C 01.00 - Own Funds

Click "Generate Report" and you should see:
- Populated COREP fields with values
- Justifications for each field
- Regulatory references
- Audit trail
- Retrieved regulatory context

---

## Troubleshooting

### Issue: "Module not found" errors

**Solution:** Make sure you're using the correct Python environment. Try:
```powershell
python --version  # Should be Python 3.8+
pip list | Select-String "chromadb"  # Should show chromadb installed
```

### Issue: "OpenAI API key not configured"

**Solution:** Check that your `.env` file has the correct API key:
```
OPENAI_API_KEY=sk-...
```

### Issue: "No relevant regulatory context found"

**Solution:** Run the document ingestion script:
```powershell
python backend\ingest_documents.py
```

### Issue: Backend not responding

**Solution:** Make sure the backend server is running:
```powershell
python -m uvicorn backend.main:app --reload
```

---

## API Testing (Optional)

You can also test the API directly using curl or Postman:

### Health Check
```powershell
curl http://localhost:8000/api/health
```

### List Templates
```powershell
curl http://localhost:8000/api/templates
```

### Process Query
```powershell
curl -X POST http://localhost:8000/api/query `
  -H "Content-Type: application/json" `
  -d '{
    "question": "How should this be reported?",
    "scenario": "The bank has £500M in CET1 capital...",
    "template_code": "C_01.00"
  }'
```

---

## Next Steps

1. **Test all sample scenarios** to see different regulatory interpretations
2. **Try custom scenarios** based on your understanding of capital requirements
3. **Review the audit trails** to see how the system maps scenarios to regulations
4. **Check validation flags** to understand what data might be missing

---

## For AKOIN Evaluation

### Key Features to Demonstrate

1. **RAG in Action:**
   - Show how the system retrieves relevant PRA Rulebook sections
   - Demonstrate that responses are grounded in actual regulatory text

2. **Structured Output:**
   - Show the JSON schema enforcement
   - Display the formatted COREP template

3. **Audit Trail:**
   - Highlight how each field maps to specific regulatory paragraphs
   - Show the reasoning process

4. **Validation:**
   - Trigger validation flags by providing incomplete scenarios
   - Show consistency checks in action

5. **No Hallucination:**
   - Compare responses with and without retrieved context
   - Show conservative approach (N/A when uncertain)

---

**You're all set!** 🚀

The system is ready for demonstration and evaluation.
