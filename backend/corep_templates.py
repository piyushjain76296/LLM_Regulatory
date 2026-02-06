"""COREP template definitions and schemas."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class TemplateField(BaseModel):
    """Definition of a single COREP template field."""
    
    field_code: str = Field(..., description="COREP field code (e.g., 'C_01.00_r010')")
    field_name: str = Field(..., description="Human-readable field name")
    description: str = Field(..., description="Field description and instructions")
    is_deduction: bool = Field(default=False, description="Whether this is a deduction field")
    calculation: Optional[str] = Field(None, description="Calculation formula if applicable")
    validation_rules: List[str] = Field(default_factory=list, description="Validation rules")


class COREPTemplate(BaseModel):
    """COREP template definition."""
    
    template_code: str = Field(..., description="Template code (e.g., 'C_01.00')")
    template_name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    fields: List[TemplateField] = Field(..., description="Template fields")


# Own Funds Template (C 01.00)
OWN_FUNDS_TEMPLATE = COREPTemplate(
    template_code="C_01.00",
    template_name="Own Funds",
    description="Composition of own funds including CET1, AT1, and Tier 2 capital",
    fields=[
        # CET1 Capital - Instruments and Reserves
        TemplateField(
            field_code="C_01.00_r010",
            field_name="Capital instruments and related share premium accounts",
            description="Capital instruments eligible as CET1 and their related share premium accounts",
            validation_rules=["Must be non-negative", "Requires verification of instrument eligibility"]
        ),
        TemplateField(
            field_code="C_01.00_r020",
            field_name="Retained earnings",
            description="Retained earnings including verified interim or year-end profits",
            validation_rules=["Must exclude foreseeable charges or dividends", "Requires auditor verification"]
        ),
        TemplateField(
            field_code="C_01.00_r030",
            field_name="Accumulated other comprehensive income",
            description="Accumulated other comprehensive income and other disclosed reserves",
            validation_rules=["Must be non-negative"]
        ),
        TemplateField(
            field_code="C_01.00_r040",
            field_name="Funds for general banking risk",
            description="Funds for general banking risk recognized in equity",
            validation_rules=["Must be recognized under applicable accounting standards"]
        ),
        
        # CET1 Capital - Regulatory Adjustments (Deductions)
        TemplateField(
            field_code="C_01.00_r070",
            field_name="Intangible assets",
            description="Intangible assets including goodwill, net of related tax liability",
            is_deduction=True,
            validation_rules=["Report as positive number", "Deducted from CET1"]
        ),
        TemplateField(
            field_code="C_01.00_r080",
            field_name="Deferred tax assets",
            description="Deferred tax assets that rely on future profitability",
            is_deduction=True,
            validation_rules=["Report as positive number", "Deducted from CET1"]
        ),
        TemplateField(
            field_code="C_01.00_r090",
            field_name="Negative amounts from expected loss",
            description="Negative amounts resulting from expected loss calculations",
            is_deduction=True,
            validation_rules=["Report as positive number", "Deducted from CET1"]
        ),
        TemplateField(
            field_code="C_01.00_r100",
            field_name="Holdings of own CET1 instruments",
            description="Direct, indirect, and synthetic holdings of own CET1 instruments",
            is_deduction=True,
            validation_rules=["Report as positive number", "Deducted from CET1"]
        ),
        TemplateField(
            field_code="C_01.00_r110",
            field_name="Total regulatory adjustments to CET1",
            description="Sum of all regulatory adjustments (deductions) from CET1",
            is_deduction=True,
            calculation="Sum of r070 to r100"
        ),
        TemplateField(
            field_code="C_01.00_r120",
            field_name="Common Equity Tier 1 (CET1) capital",
            description="Total CET1 capital after regulatory adjustments",
            calculation="(r010 + r020 + r030 + r040) - r110",
            validation_rules=["Must be positive"]
        ),
        
        # Additional Tier 1 Capital
        TemplateField(
            field_code="C_01.00_r130",
            field_name="AT1 capital instruments",
            description="AT1 capital instruments and related share premium accounts",
            validation_rules=["Must meet AT1 criteria", "Must be subordinated and perpetual"]
        ),
        TemplateField(
            field_code="C_01.00_r150",
            field_name="Total regulatory adjustments to AT1",
            description="Total deductions from AT1 capital",
            is_deduction=True
        ),
        TemplateField(
            field_code="C_01.00_r160",
            field_name="Additional Tier 1 (AT1) capital",
            description="Total AT1 capital after regulatory adjustments",
            calculation="r130 - r150"
        ),
        TemplateField(
            field_code="C_01.00_r170",
            field_name="Tier 1 capital (T1 = CET1 + AT1)",
            description="Total Tier 1 capital",
            calculation="r120 + r160",
            validation_rules=["Must be >= CET1 capital"]
        ),
        
        # Tier 2 Capital
        TemplateField(
            field_code="C_01.00_r180",
            field_name="Tier 2 capital instruments",
            description="Tier 2 capital instruments and subordinated loans",
            validation_rules=["Minimum 5-year maturity required"]
        ),
        TemplateField(
            field_code="C_01.00_r200",
            field_name="Credit risk adjustments",
            description="General credit risk adjustments (IRB approach)",
            validation_rules=["Limited to 1.25% of risk-weighted exposures"]
        ),
        TemplateField(
            field_code="C_01.00_r210",
            field_name="Total regulatory adjustments to T2",
            description="Total deductions from Tier 2 capital",
            is_deduction=True
        ),
        TemplateField(
            field_code="C_01.00_r220",
            field_name="Tier 2 (T2) capital",
            description="Total Tier 2 capital after regulatory adjustments",
            calculation="(r180 + r200) - r210"
        ),
        TemplateField(
            field_code="C_01.00_r230",
            field_name="Total capital (TC = T1 + T2)",
            description="Total own funds",
            calculation="r170 + r220",
            validation_rules=["Must be >= Tier 1 capital"]
        ),
    ]
)


# Template registry
TEMPLATE_REGISTRY: Dict[str, COREPTemplate] = {
    "C_01.00": OWN_FUNDS_TEMPLATE,
}


def get_template(template_code: str) -> Optional[COREPTemplate]:
    """Get a COREP template by code."""
    return TEMPLATE_REGISTRY.get(template_code)


def list_templates() -> List[Dict[str, str]]:
    """List all available templates."""
    return [
        {
            "code": template.template_code,
            "name": template.template_name,
            "description": template.description
        }
        for template in TEMPLATE_REGISTRY.values()
    ]


def format_template_output(template_code: str, populated_fields: List[Dict]) -> str:
    """Format populated template fields into human-readable output."""
    template = get_template(template_code)
    if not template:
        return "Template not found"
    
    output = [
        f"COREP Template: {template.template_name} ({template.template_code})",
        "=" * 80,
        ""
    ]
    
    for field_data in populated_fields:
        field_code = field_data.get("field_code")
        value = field_data.get("value", "N/A")
        justification = field_data.get("justification", "")
        
        # Find field definition
        field_def = next((f for f in template.fields if f.field_code == field_code), None)
        if field_def:
            output.append(f"[{field_code}] {field_def.field_name}")
            output.append(f"  Value: {value}")
            if justification:
                output.append(f"  Justification: {justification}")
            output.append("")
    
    return "\n".join(output)
