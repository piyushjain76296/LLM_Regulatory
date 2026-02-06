"""Validation and audit trail system for COREP reporting."""

from typing import Dict, List
from backend.corep_templates import get_template


class Validator:
    """Validator for COREP template outputs."""
    
    def validate_output(self, output: Dict) -> Dict:
        """
        Validate LLM output against template rules.
        
        Args:
            output: LLM-generated output with populated fields
            
        Returns:
            Validation result with additional flags if issues found
        """
        template_code = output.get("template")
        fields = output.get("fields", [])
        validation_flags = output.get("validation_flags", [])
        
        # Get template definition
        template = get_template(template_code)
        if not template:
            validation_flags.append(f"Unknown template: {template_code}")
            return output
        
        # Validate each field
        for field_data in fields:
            field_code = field_data.get("field_code")
            value = field_data.get("value")
            
            # Find field definition
            field_def = next(
                (f for f in template.fields if f.field_code == field_code),
                None
            )
            
            if not field_def:
                validation_flags.append(f"Unknown field code: {field_code}")
                continue
            
            # Check if value is provided
            if value == "N/A" or value is None or value == "":
                validation_flags.append(
                    f"Field {field_code} ({field_def.field_name}) has no value"
                )
            
            # Check if justification is provided
            if not field_data.get("justification"):
                validation_flags.append(
                    f"Field {field_code} missing justification"
                )
            
            # Check if source rule is provided
            if not field_data.get("source_rule"):
                validation_flags.append(
                    f"Field {field_code} missing regulatory source reference"
                )
            
            # Apply field-specific validation rules
            for rule in field_def.validation_rules:
                if "non-negative" in rule.lower() and value != "N/A":
                    try:
                        if float(value) < 0:
                            validation_flags.append(
                                f"Field {field_code} must be non-negative"
                            )
                    except (ValueError, TypeError):
                        pass
        
        # Update validation flags
        output["validation_flags"] = list(set(validation_flags))  # Remove duplicates
        
        return output
    
    def generate_audit_trail(self, output: Dict) -> List[str]:
        """
        Generate comprehensive audit trail.
        
        Args:
            output: Validated output
            
        Returns:
            List of audit trail entries
        """
        audit_trail = output.get("audit_log", [])
        
        # Add field-level audit entries
        for field_data in output.get("fields", []):
            field_code = field_data.get("field_code")
            field_name = field_data.get("field_name", "Unknown")
            value = field_data.get("value")
            source_rule = field_data.get("source_rule", "No source")
            justification = field_data.get("justification", "No justification")
            
            audit_entry = (
                f"[{field_code}] {field_name}: {value} | "
                f"Source: {source_rule} | "
                f"Reasoning: {justification}"
            )
            audit_trail.append(audit_entry)
        
        return audit_trail
    
    def check_consistency(self, output: Dict) -> List[str]:
        """
        Check for logical inconsistencies in the output.
        
        Args:
            output: Output to check
            
        Returns:
            List of consistency issues
        """
        issues = []
        fields = output.get("fields", [])
        
        # Build field value map
        field_values = {}
        for field_data in fields:
            field_code = field_data.get("field_code")
            value = field_data.get("value")
            try:
                field_values[field_code] = float(value) if value != "N/A" else None
            except (ValueError, TypeError):
                field_values[field_code] = None
        
        # Check CET1 calculation (r120 = sum of positive items - r110)
        # This is a simplified check
        if "C_01.00_r120" in field_values:
            cet1 = field_values.get("C_01.00_r120")
            if cet1 is not None and cet1 <= 0:
                issues.append("CET1 capital (r120) must be positive")
        
        # Check Tier 1 >= CET1
        if "C_01.00_r170" in field_values and "C_01.00_r120" in field_values:
            tier1 = field_values.get("C_01.00_r170")
            cet1 = field_values.get("C_01.00_r120")
            if tier1 is not None and cet1 is not None and tier1 < cet1:
                issues.append("Tier 1 capital must be >= CET1 capital")
        
        # Check Total Capital >= Tier 1
        if "C_01.00_r230" in field_values and "C_01.00_r170" in field_values:
            total = field_values.get("C_01.00_r230")
            tier1 = field_values.get("C_01.00_r170")
            if total is not None and tier1 is not None and total < tier1:
                issues.append("Total capital must be >= Tier 1 capital")
        
        return issues


# Global validator instance
_validator = None


def get_validator() -> Validator:
    """Get or create the global validator instance."""
    global _validator
    if _validator is None:
        _validator = Validator()
    return _validator
