"""LLM client for regulatory reasoning and structured output generation."""

import json
from typing import Dict, List, Optional
from openai import OpenAI
from backend.config import settings


class LLMClient:
    """Client for interacting with LLM for regulatory reporting."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
    
    def generate_regulatory_response(
        self,
        user_question: str,
        scenario: str,
        template_code: str,
        retrieved_context: List[Dict]
    ) -> Dict:
        """
        Generate structured regulatory response using LLM.
        
        Args:
            user_question: User's natural language question
            scenario: Reporting scenario description
            template_code: COREP template code
            retrieved_context: Retrieved regulatory context from RAG
            
        Returns:
            Structured response with populated fields and audit trail
        """
        # Demo mode - return sample response without calling OpenAI
        if settings.demo_mode:
            return self._generate_demo_response(scenario, template_code, retrieved_context)
        
        # Build system prompt
        system_prompt = self._build_system_prompt()
        
        # Build user prompt with context
        user_prompt = self._build_user_prompt(
            user_question, scenario, template_code, retrieved_context
        )
        
        try:
            # Call OpenAI API with JSON mode
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,  # Low temperature for consistency
                max_tokens=2000
            )
            
            # Parse JSON response
            content = response.choices[0].message.content
            result = json.loads(content)
            
            return result
            
        except Exception as e:
            return {
                "error": str(e),
                "template": template_code,
                "fields": [],
                "validation_flags": [f"LLM Error: {str(e)}"],
                "audit_log": []
            }
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for the LLM."""
        return """You are an AI-powered regulatory reporting assistant designed to support UK banks in preparing PRA COREP regulatory returns.

Your task is to:
1. Understand natural-language regulatory questions and reporting scenarios.
2. Retrieve and reason over relevant regulatory texts from:
   - PRA Rulebook
   - COREP / EBA reporting instructions and taxonomy
3. Generate structured, auditable outputs aligned with predefined COREP templates.

Scope limitations:
- Focus only on a constrained subset of COREP templates (e.g. Own Funds or Capital Requirements).
- Do NOT hallucinate regulatory rules.
- If required data is missing or ambiguous, explicitly flag it.

Output requirements:
- Produce structured JSON strictly matching the provided schema.
- Populate only fields justified by retrieved regulatory text.
- Provide an audit trail mapping each populated field to the specific regulation paragraph(s) used.
- Apply basic validation rules and flag inconsistencies.

Tone and behavior:
- Be precise, conservative, and regulation-aware.
- Prefer "cannot determine" over assumptions.

CRITICAL: You must ONLY use information from the provided regulatory context. Do not make up rules or interpretations."""
    
    def _build_user_prompt(
        self,
        user_question: str,
        scenario: str,
        template_code: str,
        retrieved_context: List[Dict]
    ) -> str:
        """Build the user prompt with context and schema."""
        
        # Format retrieved context
        context_text = "\n\n".join([
            f"[Source: {ctx['metadata'].get('document_type', 'Unknown')}]\n{ctx['content']}"
            for ctx in retrieved_context
        ])
        
        prompt = f"""User Question:
"{user_question}"

Reporting Scenario:
{scenario}

COREP Template:
{template_code}

Retrieved Regulatory Context:
{context_text}

Required Output Schema:
{{
  "template": "{template_code}",
  "fields": [
    {{
      "field_code": "C_01.00_rXXX",
      "field_name": "Field name",
      "value": "Numeric value or 'N/A' if cannot determine",
      "justification": "Brief explanation of why this value applies",
      "source_rule": "Specific regulatory reference (e.g., 'PRA Rulebook 1.1.1')"
    }}
  ],
  "validation_flags": [
    "List any missing data, ambiguities, or inconsistencies"
  ],
  "audit_log": [
    "Step-by-step reasoning for key decisions"
  ]
}}

Instructions:
- Analyze the scenario against the retrieved regulatory context
- Populate ONLY the fields that can be determined from the scenario and context
- For each field, provide:
  * The value (or "N/A" if cannot determine)
  * Clear justification based on the scenario
  * Specific regulatory reference from the context
- List any validation issues or missing information in validation_flags
- Provide audit trail showing your reasoning process
- Be conservative: if unsure, mark as "N/A" and explain in validation_flags

Generate the JSON response now:"""
        
        return prompt
    
    def _generate_demo_response(
        self,
        scenario: str,
        template_code: str,
        retrieved_context: List[Dict]
    ) -> Dict:
        """Generate a demo response without calling OpenAI API."""
        
        # Analyze scenario for keywords
        scenario_lower = scenario.lower()
        
        # Determine what type of capital is being discussed
        fields = []
        
        if "ordinary shares" in scenario_lower or "common equity" in scenario_lower or "cet1" in scenario_lower:
            # CET1 scenario
            # Extract amount if mentioned
            import re
            amounts = re.findall(r'£(\d+)\s*million', scenario)
            amount = amounts[0] if amounts else "500"
            
            fields.append({
                "field_code": "C_01.00_r010",
                "field_name": "Capital instruments and related share premium accounts",
                "value": f"£{amount}M",
                "justification": "Ordinary shares meeting CRR Article 28 criteria qualify as CET1 capital instruments",
                "source_rule": "PRA Rulebook 1.1.1 - CET1 capital instruments criteria"
            })
            
            if "retained earnings" in scenario_lower:
                retained_amounts = re.findall(r'£(\d+)\s*million.*retained', scenario)
                retained = retained_amounts[0] if retained_amounts else "200"
                fields.append({
                    "field_code": "C_01.00_r020",
                    "field_name": "Retained earnings",
                    "value": f"£{retained}M",
                    "justification": "Verified retained earnings net of foreseeable dividends",
                    "source_rule": "PRA Rulebook 1.1.3 - Retained earnings requirements"
                })
            
            if "comprehensive income" in scenario_lower or "reserves" in scenario_lower:
                fields.append({
                    "field_code": "C_01.00_r030",
                    "field_name": "Accumulated other comprehensive income",
                    "value": "£50M",
                    "justification": "Disclosed reserves recognized in equity",
                    "source_rule": "PRA Rulebook 1.1.4 - Other comprehensive income"
                })
        
        elif "at1" in scenario_lower or "additional tier 1" in scenario_lower or "subordinated bonds" in scenario_lower:
            # AT1 scenario
            amounts = re.findall(r'£(\d+)\s*million', scenario)
            amount = amounts[0] if amounts else "100"
            
            fields.append({
                "field_code": "C_01.00_r130",
                "field_name": "AT1 capital instruments",
                "value": f"£{amount}M",
                "justification": "Perpetual subordinated instruments with loss absorption mechanism qualify as AT1",
                "source_rule": "PRA Rulebook 1.2.1 - AT1 capital instruments criteria"
            })
        
        elif "goodwill" in scenario_lower or "intangible" in scenario_lower or "deduction" in scenario_lower:
            # Deductions scenario
            if "goodwill" in scenario_lower or "intangible" in scenario_lower:
                amounts = re.findall(r'£(\d+)\s*million.*intangible', scenario)
                amount = amounts[0] if amounts else "75"
                fields.append({
                    "field_code": "C_01.00_r070",
                    "field_name": "Intangible assets",
                    "value": f"£{amount}M",
                    "justification": "Goodwill and intangible assets must be deducted from CET1 capital",
                    "source_rule": "PRA Rulebook 2.1.2 - Intangible assets deduction"
                })
            
            if "deferred tax" in scenario_lower:
                amounts = re.findall(r'£(\d+)\s*million.*deferred', scenario)
                amount = amounts[0] if amounts else "30"
                fields.append({
                    "field_code": "C_01.00_r080",
                    "field_name": "Deferred tax assets",
                    "value": f"£{amount}M",
                    "justification": "Deferred tax assets relying on future profitability are deducted",
                    "source_rule": "PRA Rulebook 2.1.3 - Deferred tax assets deduction"
                })
            
            if "own" in scenario_lower and "instruments" in scenario_lower:
                amounts = re.findall(r'£(\d+)\s*million.*own', scenario)
                amount = amounts[0] if amounts else "10"
                fields.append({
                    "field_code": "C_01.00_r100",
                    "field_name": "Holdings of own CET1 instruments",
                    "value": f"£{amount}M",
                    "justification": "Holdings of own CET1 instruments must be deducted",
                    "source_rule": "PRA Rulebook 2.1.5 - Own instruments deduction"
                })
        
        # Build response
        return {
            "template": template_code,
            "fields": fields,
            "validation_flags": [
                "DEMO MODE: This is a simulated response for demonstration purposes",
                "To use real LLM responses, add OpenAI credits and set demo_mode=False in config.py"
            ],
            "audit_log": [
                "Demo mode active - response generated from scenario keyword analysis",
                "Retrieved regulatory context from RAG engine",
                f"Analyzed scenario and identified {len(fields)} relevant COREP fields"
            ]
        }


# Global LLM client instance
_llm_client = None


def get_llm_client() -> LLMClient:
    """Get or create the global LLM client instance."""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
