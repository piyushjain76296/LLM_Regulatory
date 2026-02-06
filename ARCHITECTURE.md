# Architecture Documentation

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                     (Frontend - HTML/CSS/JS)                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP/JSON
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FASTAPI BACKEND                            │
│                         (main.py)                               │
└─────┬──────────────┬──────────────┬──────────────┬─────────────┘
      │              │              │              │
      ▼              ▼              ▼              ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│   RAG    │  │   LLM    │  │  COREP   │  │Validator │
│  Engine  │  │  Client  │  │Templates │  │          │
└────┬─────┘  └────┬─────┘  └──────────┘  └──────────┘
     │             │
     ▼             ▼
┌──────────┐  ┌──────────┐
│ ChromaDB │  │  OpenAI  │
│ Vector   │  │   API    │
│   DB     │  │          │
└──────────┘  └──────────┘
```

---

## Component Details

### 1. RAG Engine (`rag_engine.py`)

**Purpose:** Retrieval-Augmented Generation for regulatory documents

**Key Features:**
- Document chunking by sections/paragraphs
- Embedding generation using `sentence-transformers`
- Vector storage in ChromaDB
- Semantic similarity search

**Flow:**
1. **Ingestion Phase:**
   - Load regulatory documents (PRA Rulebook, COREP instructions)
   - Split into meaningful chunks (by section headers, paragraphs)
   - Generate embeddings for each chunk
   - Store in ChromaDB with metadata

2. **Retrieval Phase:**
   - Receive user query
   - Generate query embedding
   - Perform vector similarity search
   - Return top-k relevant chunks with metadata

**Why RAG?**
- Prevents LLM hallucination
- Grounds responses in actual regulatory text
- Provides source attribution
- Enables updates without retraining

---

### 2. LLM Client (`llm_client.py`)

**Purpose:** Interface with OpenAI GPT-4 for regulatory reasoning

**Prompt Engineering:**

**System Prompt:**
```
Role: AI regulatory reporting assistant for UK banks
Task: Understand queries, reason over regulations, generate structured outputs
Constraints: No hallucination, conservative, regulation-aware
Output: Structured JSON with audit trail
```

**User Prompt Structure:**
```
1. User Question
2. Reporting Scenario
3. COREP Template Code
4. Retrieved Regulatory Context (from RAG)
5. Required JSON Schema
6. Instructions
```

**JSON Schema Enforcement:**
- Uses OpenAI's `response_format={"type": "json_object"}`
- Pydantic validation on response
- Ensures consistent structure

**Temperature:** 0.1 (low for consistency)

---

### 3. COREP Templates (`corep_templates.py`)

**Purpose:** Define COREP template schemas and validation rules

**Template Structure:**
```python
COREPTemplate:
  - template_code: "C_01.00"
  - template_name: "Own Funds"
  - fields: List[TemplateField]

TemplateField:
  - field_code: "C_01.00_r010"
  - field_name: "Capital instruments..."
  - description: "..."
  - is_deduction: bool
  - calculation: Optional[str]
  - validation_rules: List[str]
```

**Own Funds Template (C 01.00):**
- CET1 Capital (rows 010-120)
- AT1 Capital (rows 130-170)
- Tier 2 Capital (rows 180-230)
- Regulatory adjustments (deductions)

---

### 4. Validator (`validator.py`)

**Purpose:** Validate outputs and generate audit trails

**Validation Types:**

1. **Field-Level Validation:**
   - Non-negative values where required
   - Required fields populated
   - Justification provided
   - Source rule referenced

2. **Consistency Checks:**
   - CET1 must be positive
   - Tier 1 ≥ CET1
   - Total Capital ≥ Tier 1

3. **Audit Trail Generation:**
   - Maps each field to regulatory source
   - Documents reasoning
   - Creates compliance record

**Output:**
- Updated validation_flags list
- Comprehensive audit_log
- Consistency issue warnings

---

### 5. FastAPI Backend (`main.py`)

**Purpose:** REST API server

**Endpoints:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | API info |
| `/api/health` | GET | Health check + doc count |
| `/api/templates` | GET | List COREP templates |
| `/api/query` | POST | Process regulatory query |

**Query Processing Flow:**
1. Receive request (question, scenario, template)
2. Retrieve context via RAG
3. Generate LLM response
4. Validate output
5. Check consistency
6. Generate audit trail
7. Format results
8. Return response

**Error Handling:**
- HTTPException for API errors
- Validation error messages
- LLM error handling

---

## Data Flow

### Complete Request Flow

```
1. User submits query via frontend
   ↓
2. Frontend sends POST /api/query
   ↓
3. Backend receives request
   ↓
4. RAG Engine retrieves relevant regulatory chunks
   ↓
5. LLM Client builds prompt with context
   ↓
6. OpenAI generates structured JSON response
   ↓
7. Validator checks fields and consistency
   ↓
8. Audit trail generated
   ↓
9. Response formatted
   ↓
10. Frontend displays results
```

---

## Key Design Decisions

### Why ChromaDB?
- Lightweight, embeddable vector database
- No separate server required
- Persistent storage
- Good for prototypes and small-scale deployments

### Why Sentence Transformers?
- Open-source embedding model
- No API costs for embeddings
- Good quality for semantic search
- Fast inference

### Why OpenAI GPT-4?
- Strong reasoning capabilities
- JSON mode for structured outputs
- Reliable for regulatory interpretation
- Production-ready API

### Why FastAPI?
- Modern Python web framework
- Automatic API documentation
- Type hints and validation
- Async support
- Easy CORS configuration

---

## Scalability Considerations

### Current Prototype Limitations
- Single COREP template
- Sample regulatory documents
- In-memory processing
- No caching

### Production Enhancements
1. **Database:**
   - PostgreSQL for structured data
   - Pinecone/Weaviate for vector storage at scale

2. **Caching:**
   - Redis for query caching
   - Reduce API calls

3. **Processing:**
   - Async processing for long queries
   - Queue system (Celery/RabbitMQ)

4. **Monitoring:**
   - Logging (structured logs)
   - Metrics (Prometheus)
   - Tracing (OpenTelemetry)

5. **Security:**
   - Authentication (OAuth2)
   - Rate limiting
   - Input sanitization
   - Audit logging

---

## Testing Strategy

### Unit Tests
- RAG chunking logic
- Template validation rules
- Consistency checks

### Integration Tests
- End-to-end query processing
- API endpoint responses
- Error handling

### Manual Testing
- Sample scenarios
- Edge cases
- Validation flag triggering

---

## Deployment

### Local Development
```bash
python -m uvicorn backend.main:app --reload
```

### Production Deployment
```bash
# Using Gunicorn with Uvicorn workers
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Docker (Optional)
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Future Enhancements

1. **More Templates:** Expand to all COREP templates
2. **Real Data Integration:** Connect to bank's data systems
3. **Workflow:** Multi-step approval process
4. **Version Control:** Track template changes over time
5. **Comparison:** Compare across reporting periods
6. **Export:** Generate submission-ready files
7. **Collaboration:** Multi-user support with roles

---

**Architecture designed for:**
- ✅ Clarity and maintainability
- ✅ Regulatory compliance
- ✅ Auditability
- ✅ Scalability
- ✅ Production readiness
