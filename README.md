# 🏛️ Regulatory Reporting Assistant

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.128+-green.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-demo-orange.svg)

**LLM-Assisted COREP Automation for UK Banks**

An AI-powered prototype demonstrating how Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG) can transform regulatory reporting for UK banks preparing PRA COREP returns.

> **Demo Mode Enabled:** This system works without OpenAI API credits using intelligent scenario analysis. For production use with real LLM, add OpenAI credits and set `demo_mode=False` in `backend/config.py`.

---

## Project Overview

This prototype solves a critical challenge in banking regulation: converting complex regulatory requirements into structured, auditable COREP reports. The system:

 **Converts natural language questions** into structured COREP-aligned outputs  
 **Provides full regulatory traceability** with audit trails  
 **Prevents hallucination** through retrieval-augmented generation  
 **Validates outputs** against regulatory rules  

---

##  Architecture

### End-to-End Flow

```
User Query → RAG Retrieval → LLM Reasoning → Validation → Structured Output
```

### Components

1. **RAG Engine** (`rag_engine.py`)
   - Document chunking and embedding
   - Vector similarity search with ChromaDB
   - Retrieves relevant PRA Rulebook & COREP instructions

2. **LLM Client** (`llm_client.py`)
   - OpenAI GPT-4 integration
   - System/user prompt engineering
   - JSON schema enforcement

3. **COREP Templates** (`corep_templates.py`)
   - Template definitions (Own Funds C 01.00)
   - Field schemas with validation rules
   - Human-readable formatting

4. **Validator** (`validator.py`)
   - Field-level validation
   - Consistency checks
   - Audit trail generation

5. **FastAPI Backend** (`main.py`)
   - REST API endpoints
   - Request/response handling
   - CORS configuration

6. **Frontend** (`frontend/`)
   - Premium dark mode UI
   - Sample scenarios
   - Interactive results display

---

## Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key
- pip package manager

### Installation

1. **Clone/Navigate to project directory**
   ```bash
   cd d:\Akoin_company_assignment
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   # Copy example env file
   copy .env.example .env
   
   # Edit .env and add your OpenAI API key
   # OPENAI_API_KEY=sk-your-key-here
   ```

4. **Ingest regulatory documents**
   ```bash
   python backend/ingest_documents.py
   ```
   
   This loads sample PRA Rulebook and COREP instructions into the vector database.

5. **Start the backend server**
   ```bash
   python -m uvicorn backend.main:app --reload
   ```
   
   Server will start at `http://localhost:8000`

6. **Open the frontend**
   
   Open `frontend/index.html` in your browser, or visit:
   ```
   http://localhost:8000/static/index.html
   ```

---

##  Usage

### Sample Scenarios

The interface includes 3 pre-configured scenarios:

1. **CET1 Capital** - Common Equity Tier 1 classification
2. **AT1 Instrument** - Additional Tier 1 reporting
3. **Deductions** - Regulatory deductions from capital

### Custom Queries

1. Enter your question (e.g., "How should this be reported in COREP?")
2. Describe the scenario in detail
3. Select the COREP template
4. Click "Generate Report"

### Output

The system provides:
- **Populated COREP fields** with values
- **Justifications** for each field
- **Regulatory references** (source rules)
- **Audit trail** showing reasoning
- **Validation flags** for issues/missing data
- **Retrieved context** from regulatory documents

---

## Success Criteria Mapping

| Requirement | Implementation |
|------------|----------------|
| **End-to-end behavior** | User → RAG → LLM → Validation → Output |
| **Regulatory accuracy** | RAG prevents hallucination, retrieves actual rules |
| **Structured output** | JSON schema with Pydantic validation |
| **Human-readable** | Formatted COREP template display |
| **Auditability** | Field-level regulatory references + reasoning |
| **Scoped complexity** | 1 COREP template (Own Funds C 01.00) |

---

## Technical Details

### RAG Pipeline

1. **Document Ingestion**
   - Chunks regulatory texts by sections/paragraphs
   - Generates embeddings using `sentence-transformers`
   - Stores in ChromaDB vector database

2. **Retrieval**
   - Query embedding generation
   - Semantic similarity search
   - Returns top-k relevant chunks

3. **Context Injection**
   - Retrieved chunks added to LLM prompt
   - Prevents hallucination
   - Grounds responses in actual regulations

### LLM Prompting

**System Prompt:**
- Defines role as regulatory assistant
- Sets constraints (no hallucination, conservative)
- Specifies output format (JSON schema)

**User Prompt:**
- Includes user question + scenario
- Adds retrieved regulatory context
- Provides JSON schema template
- Requests justifications and sources

### Validation

- **Field validation**: Non-negative values, required fields
- **Consistency checks**: CET1 ≤ Tier 1 ≤ Total Capital
- **Audit trail**: Maps each field to regulatory source

---

##  Project Structure

```
Akoin_company_assignment/
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── rag_engine.py        # RAG implementation
│   ├── llm_client.py        # OpenAI integration
│   ├── corep_templates.py   # Template definitions
│   ├── validator.py         # Validation logic
│   ├── config.py            # Configuration
│   └── ingest_documents.py  # Document ingestion script
├── frontend/
│   ├── index.html           # Web interface
│   ├── styles.css           # Premium styling
│   └── app.js               # Frontend logic
├── data/
│   └── regulatory_docs/
│       ├── pra_rulebook_sample.txt
│       └── corep_instructions_sample.txt
├── requirements.txt
├── .env.example
└── README.md
```

---

## For AKOIN Evaluation

### What This Demonstrates

1. **AI Architecture Design**
   - Production-ready RAG pipeline
   - LLM integration with structured outputs
   - Multi-component system design

2. **Regulation Understanding**
   - PRA Rulebook interpretation
   - COREP template knowledge
   - Capital requirements domain expertise

3. **Prompt Engineering**
   - System prompt for role definition
   - Context injection strategies
   - JSON schema enforcement

4. **Policy-to-Data Mapping**
   - Regulatory text → Template fields
   - Justification generation
   - Audit trail creation

5. **Safety-First AI**
   - RAG prevents hallucination
   - Conservative approach (N/A over guessing)
   - Validation and consistency checks

### Key Differentiators

 **Audit Trail** - Every field maps to specific regulatory paragraph  
 **RAG-Based** - No hallucinated rules, only retrieved context  
 **Validation** - Automated consistency checks  
 **Production-Ready** - Proper error handling, logging, API design  

---

##  API Endpoints

### `GET /api/health`
Health check and document count

### `GET /api/templates`
List available COREP templates

### `POST /api/query`
Process regulatory query

**Request:**
```json
{
  "question": "How should this be reported?",
  "scenario": "Detailed scenario description...",
  "template_code": "C_01.00"
}
```

**Response:**
```json
{
  "template": "C_01.00",
  "fields": [...],
  "validation_flags": [...],
  "audit_log": [...],
  "formatted_output": "...",
  "retrieved_context": [...]
}
```

---

##  Notes

### Scope Limitations

- **1 COREP template** (Own Funds C 01.00) for demonstration
- **Sample regulatory texts** (not full licensed documents)
- **Simplified validation** (production would be more comprehensive)

### Production Considerations

For a real deployment, you would need:
- Licensed access to full PRA Rulebook and EBA documentation
- All COREP templates (100+ templates)
- Integration with bank's data systems
- Enhanced validation and business rules
- User authentication and authorization
- Audit logging and compliance tracking

---

##  Contributing

This is a prototype for assignment evaluation. For questions or improvements, contact the developer.

---

##  License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with  for AKOIN Assignment**

*Demonstrating the future of regulatory compliance through AI*
