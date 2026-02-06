"""FastAPI main application for regulatory reporting assistant."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import os

from backend.rag_engine import get_rag_engine
from backend.llm_client import get_llm_client
from backend.validator import get_validator
from backend.corep_templates import list_templates, format_template_output


# Initialize FastAPI app
app = FastAPI(
    title="Regulatory Reporting Assistant",
    description="LLM-assisted COREP regulatory reporting for UK banks",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount frontend static files
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path, html=True), name="static")


# Request/Response models
class QueryRequest(BaseModel):
    """Request model for regulatory query."""
    question: str
    scenario: str
    template_code: str = "C_01.00"


class QueryResponse(BaseModel):
    """Response model for regulatory query."""
    template: str
    fields: list
    validation_flags: list
    audit_log: list
    formatted_output: Optional[str] = None
    retrieved_context: Optional[list] = None


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Regulatory Reporting Assistant API",
        "version": "1.0.0",
        "endpoints": {
            "query": "/api/query",
            "templates": "/api/templates",
            "health": "/api/health"
        }
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    try:
        rag_engine = get_rag_engine()
        doc_count = rag_engine.collection.count()
        return {
            "status": "healthy",
            "documents_loaded": doc_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@app.get("/api/templates")
async def get_templates():
    """Get list of available COREP templates."""
    return {"templates": list_templates()}


@app.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process a regulatory reporting query.
    
    This is the main endpoint that:
    1. Retrieves relevant regulatory context (RAG)
    2. Generates structured output using LLM
    3. Validates the output
    4. Returns formatted results with audit trail
    """
    try:
        # Step 1: Retrieve regulatory context
        rag_engine = get_rag_engine()
        context = rag_engine.retrieve_context(
            f"{request.question} {request.scenario}"
        )
        
        if not context:
            raise HTTPException(
                status_code=404,
                detail="No relevant regulatory context found. Please ensure documents are ingested."
            )
        
        # Step 2: Generate LLM response
        llm_client = get_llm_client()
        llm_output = llm_client.generate_regulatory_response(
            user_question=request.question,
            scenario=request.scenario,
            template_code=request.template_code,
            retrieved_context=context
        )
        
        # Check for LLM errors
        if "error" in llm_output:
            raise HTTPException(
                status_code=500,
                detail=f"LLM processing error: {llm_output['error']}"
            )
        
        # Step 3: Validate output
        validator = get_validator()
        validated_output = validator.validate_output(llm_output)
        
        # Add consistency checks
        consistency_issues = validator.check_consistency(validated_output)
        if consistency_issues:
            validated_output["validation_flags"].extend(consistency_issues)
        
        # Generate comprehensive audit trail
        audit_trail = validator.generate_audit_trail(validated_output)
        validated_output["audit_log"] = audit_trail
        
        # Step 4: Format output
        formatted = format_template_output(
            request.template_code,
            validated_output.get("fields", [])
        )
        
        # Return response
        return QueryResponse(
            template=validated_output.get("template", request.template_code),
            fields=validated_output.get("fields", []),
            validation_flags=validated_output.get("validation_flags", []),
            audit_log=audit_trail,
            formatted_output=formatted,
            retrieved_context=[
                {
                    "content": ctx["content"][:200] + "...",  # Truncate for response
                    "source": ctx["metadata"].get("document_type", "Unknown")
                }
                for ctx in context[:3]  # Return top 3 context items
            ]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query processing error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
