"""
Core orchestrator for the policy-enforced AI agent framework.

This script serves as the primary controller for a custom, policy-governed
agentic system. It:
1. Reads local Markdown policy files as context guidelines
2. Routes user requests to the appropriate guardrails and language guidelines
3. Constructs an engineered prompt payload
4. Sends it to the Gemini API with deterministic parameters
5. Captures and writes generated code output to the file system
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict
from google import genai
from google.genai import types

# ============================================================================
# Configuration Constants
# ============================================================================

# Base directories for policy and configuration files
CONFIG_DIR = Path("config_engine")
POLICY_DIR = Path("policy_guardrails")
BLUEPRINTS_DIR = Path("platform_blueprints")
PATTERNS_DIR = Path("solution_patterns")
OUTPUT_DIR = Path("generated_artifacts")

# Core policy and guardrail files
CORE_ORCHESTRATOR = CONFIG_DIR / "core_orchestrator.md"
ASSET_NOMENCLATURE = POLICY_DIR / "asset_nomenclature.md"

# Language-specific guidelines (Fixed paths to policy_guardrails)
GUIDELINES_MAP = {
    "python": POLICY_DIR / "programming_python.md",
    "pyspark": POLICY_DIR / "programming_python.md",
    "sql": POLICY_DIR / "programming_sql.md",
}

# Platform blueprint maps
PLATFORM_MAP = {
    "python": BLUEPRINTS_DIR / "catalog_topology.md",
    "pyspark": BLUEPRINTS_DIR / "catalog_topology.md",
    "sql": PATTERNS_DIR / "schema_ddl.md",
    "adf": BLUEPRINTS_DIR / "data_factory.md"
}

# Gemini model configuration
GEMINI_MODEL = "gemini-2.5-flash"

# ============================================================================
# Helper Functions
# ============================================================================

def load_context(file_path: Path) -> str:
    """Safely load and return the contents of a Markdown policy or guideline file."""
    try:
        if not file_path.exists():
            print(f"[WARNING] Policy file not found: {file_path}")
            return ""
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except IOError as e:
        print(f"[ERROR] Failed to read file {file_path}: {e}")
        raise

def build_system_instruction(
    orchestrator_context: str,
    nomenclature_context: str,
    language_guidelines: str,
    platform_blueprints: str
) -> str:
    """Construct the system instruction payload by combining all policy contexts."""
    system_instruction = f"""You are a strict, policy-enforced AI agent for data engineering code generation.

## ORCHESTRATION RULES
{orchestrator_context}

## ASSET NAMING & NOMENCLATURE STANDARDS
{nomenclature_context}

## PLATFORM BLUEPRINTS & TOPOLOGY
{platform_blueprints}

## LANGUAGE-SPECIFIC GUIDELINES
{language_guidelines}

Your task is to generate compliant, production-ready code that adheres to all above policies and guidelines.
Ensure all generated code is deterministic, follows naming conventions, and complies with organizational standards."""
    
    return system_instruction

def extract_code_block(response_text: str, language: str = "python") -> str:
    """Extract code block from Gemini API response."""
    fenced_start = f"```{language}"
    fenced_end = "```"
    
    start_idx = response_text.find(fenced_start)
    if start_idx != -1:
        start_idx += len(fenced_start)
        end_idx = response_text.find(fenced_end, start_idx)
        if end_idx != -1:
            return response_text[start_idx:end_idx].strip()
    
    start_idx = response_text.find("```")
    if start_idx != -1:
        start_idx += 3
        newline_idx = response_text.find("\n", start_idx)
        if newline_idx != -1:
            start_idx = newline_idx + 1
        
        end_idx = response_text.find("```", start_idx)
        if end_idx != -1:
            return response_text[start_idx:end_idx].strip()
    
    return response_text.strip()

def write_output_artifact(code_content: str, target_type: str, artifact_name: str) -> Path:
    """Write generated code to the output directory with appropriate file extension."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    extension_map = {
        "python": ".py",
        "pyspark": ".py",
        "sql": ".sql",
    }
    extension = extension_map.get(target_type.lower(), ".txt")
    output_file = OUTPUT_DIR / f"{artifact_name}{extension}"
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(code_content)
    
    print(f"[SUCCESS] Generated artifact written to: {output_file}")
    return output_file

# ============================================================================
# Main Orchestrator Function
# ============================================================================

def execute_agent_run(
    user_query: str,
    target_type: str = "python",
    artifact_name: Optional[str] = None
) -> Dict[str, str]:
    """
    Execute a complete agent run: load policies, construct prompt, call Gemini, 
    extract and save output.
    """
    try:
        # Initialize Gemini Client (picks up GEMINI_API_KEY environment variable)
        client = genai.Client()
        
        # Determine paths
        target_key = target_type.lower()
        guideline_path = GUIDELINES_MAP.get(target_key, POLICY_DIR / "programming_python.md")
        blueprint_path = PLATFORM_MAP.get(target_key, BLUEPRINTS_DIR / "catalog_topology.md")
        
        # 1. Load Contexts
        orchestrator_ctx = load_context(CORE_ORCHESTRATOR)
        nomenclature_ctx = load_context(ASSET_NOMENCLATURE)
        language_ctx = load_context(guideline_path)
        blueprint_ctx = load_context(blueprint_path)
        
        # 2. Build System Prompt Guardrails
        system_instruction = build_system_instruction(
            orchestrator_ctx, nomenclature_ctx, language_ctx, blueprint_ctx
        )
        
        # Default name if none provided
        if not artifact_name:
            artifact_name = f"generated_code_{target_key}"
            
        print(f"🤖 Activating framework engine for target: {target_type}...")
        
        # 3. Request generation from Gemini 2.5 Flash
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=user_query,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2, # Low temperature ensures strict compliance over creativity
            ),
        )
        
        # 4. Extract and Save clean code
        clean_code = extract_code_block(response.text, language=target_key)
        final_path = write_output_artifact(clean_code, target_type, artifact_name)
        
        return {
            "status": "success",
            "artifact_path": str(final_path),
            "raw_response": response.text
        }
        
    except Exception as e:
        print(f"[CRITICAL ERROR] Agent pipeline failed: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

# --- Quick Test Execution ---
if __name__ == "__main__":
    # Make sure you set your environment variable in terminal first:
    # export GEMINI_API_KEY="your-api-key"
    
    test_query = "Write a PySpark script to optimize table ingestion from orders dataset into the silver layer."
    result = execute_agent_run(user_query=test_query, target_type="pyspark", artifact_name="ingest_orders_silver")
    print(result)
