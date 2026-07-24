"""
Core orchestrator for the policy-enforced AI agent framework.

This script serves as the primary controller for a custom, policy-governed
agentic system. It:
1. Reads local Markdown policy files as context guidelines
2. Routes user requests to the appropriate guardrails and language guidelines
3. Constructs an engineered prompt payload
4. Sends it to the Gemini API with deterministic parameters
5. Saves artifacts directly into an isolated downstream production repository
6. Programmatically automates Git branching, staging, committing, and pushing
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict
from google import genai
from google.genai import types
from git import Repo  # FIX 1: Required for Git automation loop

# ============================================================================
# Multi-Repository Configuration Constants
# ============================================================================

# Target this to the absolute local folder path of your SECOND repository
# Example: Path("/Users/yourname/projects/data-ops-generated-artifacts")
TARGET_REPO_PATH = Path("../data-ops-generated-artifacts")

# Relative folders inside your framework repository
CONFIG_DIR = Path("config_engine")
POLICY_DIR = Path("policy_guardrails")
BLUEPRINTS_DIR = Path("platform_blueprints")
PATTERNS_DIR = Path("solution_patterns")

# Core policy and guardrail files
CORE_ORCHESTRATOR = CONFIG_DIR / "core_orchestrator.md"
ASSET_NOMENCLATURE = POLICY_DIR / "asset_nomenclature.md"

# ============================================================================
# Dynamic Multi-Template & Blueprint Mapping Matrix
# ============================================================================
TEMPLATE_DIR = Path("prompt_templates")

# New Map linking your target code language to its custom .txt template file
PROMPT_TEMPLATE_MAP = {
    "python": TEMPLATE_DIR / "template_pyspark_notebook.txt",
    "pyspark": TEMPLATE_DIR / "template_pyspark_notebook.txt",
    "sql": TEMPLATE_DIR / "template_sql_ddl.txt",
    "adf": TEMPLATE_DIR / "template_data_factory.txt"
}

# Language-specific guidelines
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
            return f.read()
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
    return f"""You are a strict, policy-enforced AI agent for data engineering code generation.

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

def extract_code_block(response_text: str, language: str = "python") -> str:
    """Extract clean code block from Gemini API response, stripping fences."""
    fenced_start = f"```{language}"
    start_idx = response_text.find(fenced_start)
    if start_idx != -1:
        start_idx += len(fenced_start)
        end_idx = response_text.find("```", start_idx)
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
    """Write generated code into the target_repo subdirectories based on asset logic."""
    target_key = target_type.lower()
    
    # Map code type to its correct Database-As-Code folder inside TARGET_REPO_PATH
    if target_key == "sql":
        sub_folder = TARGET_REPO_PATH / "database_deployment" / "tables"
        extension = ".sql"
    elif target_key == "adf":
        sub_folder = TARGET_REPO_PATH / "database_deployment" / "pipelines"
        extension = ".json"
    else:
        sub_folder = TARGET_REPO_PATH / "database_deployment" / "notebooks"
        extension = ".py"
        
    sub_folder.mkdir(parents=True, exist_ok=True)
    output_file = sub_folder / f"{artifact_name}{extension}"
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(code_content)
    
    print(f"[SUCCESS] Artifact deployed locally to target repository: {output_file}")
    return output_file

# ============================================================================
# Git Automation Engine Block
# ============================================================================

def automate_git_push(file_path: Path, artifact_name: str):
    """Programmatically runs the version control lifecycle inside the downstream repo."""
    try:
        print("🐙 Connecting to Downstream Delivery Repository...")
        repo = Repo(TARGET_REPO_PATH)
        assert not repo.bare, "Target repository could not be initialized."
        
        # Pull latest master tracking to avoid alignment drift
        print("[GIT] Fetching and aligning remote state...")
        repo.remotes.origin.fetch()
        
        # Build isolated semantic branch context
        branch_name = f"feature/ai-gen-{artifact_name.lower().replace('_', '-')}"
        
        # Create and checkout branch safely
        if branch_name in repo.heads:
            repo.git.branch('-D', branch_name)  # Clear local stale variants
            
        new_branch = repo.create_head(branch_name)
        new_branch.checkout()
        print(f"[GIT] Switched to isolated context branch: {branch_name}")
        
        # Stage the newly created file using its relative path to the second repository
        relative_path = file_path.relative_to(TARGET_REPO_PATH)
        repo.index.add([str(relative_path)])
        
        # Commit signature tracing
        repo.index.commit(f"feat(ai-agent): automated deployment of compliant asset '{artifact_name}'")
        print("[GIT] Changes staged and committed to delivery repo.")
        
        # Push upstream
        origin = repo.remote(name='origin')
        origin.push(branch_name)
        print(f"[GIT SUCCESS] Feature branch successfully pushed to downstream origin: {branch_name}")
        
        # Switch back to master safely to leave repo clean
        repo.heads.main.checkout()
        
    except Exception as git_err:
        print(f"[GIT ERROR] Failed to push to downstream repo: {str(git_err)}")

# ============================================================================
# Main Orchestrator Execution Flow
# ============================================================================

def execute_agent_run(
    user_query: str,
    target_type: str = "python",
    artifact_name: Optional[str] = None
) -> Dict[str, str]:
    try:
        # Initialize Gemini Client (Requires GEMINI_API_KEY env variable)
        client = genai.Client()
                # Determine specific prompt template and governance paths
        target_key = target_type.lower()
        template_path = PROMPT_TEMPLATE_MAP.get(target_key, TEMPLATE_DIR / "template_pyspark_notebook.txt")
        guideline_path = GUIDELINES_MAP.get(target_key, POLICY_DIR / "programming_python.md")
        blueprint_path = PLATFORM_MAP.get(target_key, BLUEPRINTS_DIR / "catalog_topology.md")
        
        # Ingest the clean contexts
        orchestrator_ctx = load_context(CORE_ORCHESTRATOR)
        nomenclature_ctx = load_context(ASSET_NOMENCLATURE)
        language_ctx = load_context(guideline_path)
        blueprint_ctx = load_context(blueprint_path)
        
        # Load the newly specialized prompt template file
        raw_prompt_template = load_context(template_path)
        
        # Inject the active policy variables directly into the template slots
        system_instruction = raw_prompt_template.replace("{{orchestrator_context}}", orchestrator_ctx) \
                                               .replace("{{nomenclature_context}}", nomenclature_ctx) \
                                               .replace("{{language_guidelines}}", language_ctx) \
                                               .replace("{{platform_blueprints}}", blueprint_ctx) \
                                               .replace("{{target_type}}", target_type) \
                                               .replace("{{artifact_name}}", artifact_name if artifact_name else "generated_code") \
                                               .replace("{{user_query}}", user_query)

        
        if not artifact_name:
            artifact_name = f"generated_code_{target_key}"
            
        print(f"🤖 Invoking Gemini 2.5 Flash execution layer for asset: {artifact_name}...")
        
        # 3. Call Gemini
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=user_query,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2, # Deterministic guardrails enforcement
            ),
        )
        
        # 4. Strip fences and write to target repo
        clean_code = extract_code_block(response.text, language=target_key)
        final_path = write_output_artifact(clean_code, target_type, artifact_name)
        
        # FIX 2: Connect the Git lifecycle to execution workflow
        automate_git_push(final_path, artifact_name)
        
        return {
            "status": "success",
            "artifact_path": str(final_path),
            "response_summary": "Code successfully written and pushed upstream."
        }
        
    except Exception as e:
        print(f"[CRITICAL ERROR] Core execution loop failed: {str(e)}")
        return {"status": "error", "message": str(e)}

# --- Operational Local Verification ---
if __name__ == "__main__":
    # Test Run Configuration
    prompt = "Create a PySpark script to update the silver customer table using a merge operation on customer_id."
    execute_agent_run(user_query=prompt, target_type="pyspark", artifact_name="nb_upsert_slv_customers")