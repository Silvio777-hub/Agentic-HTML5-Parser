"""
Configuration module for the Agentic AI HTML5 Parser pipeline.
Manages environment variables, API keys, and system parameters.
"""

import os
from pathlib import Path
try:
    from dotenv import load_dotenv
except ImportError:
    # dotenv is optional; proceed without it in lightweight environments
    def load_dotenv(*args, **kwargs) -> None:  # type: ignore
        pass

# Load environment variables from .env file if available on disk
load_dotenv()

class Config:
    """Configuration class for the agentic pipeline."""
    
    # --- Anthropic Claude API Configuration ---
    # API key read securely from local environment or .env file (never hardcoded in repo)
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    # Default foundation model for agent reasoning, code synthesis, and critique
    CLAUDE_MODEL = "claude-3-5-sonnet-20241022"
    # Maximum token generation ceiling per agent inference request
    MAX_TOKENS = 4096
    # Generation temperature: 0.7 balances deterministic syntax with creative edge-case discovery
    TEMPERATURE = 0.7
    
    # --- Project File System Paths ---
    # Absolute root directory of the workspace
    PROJECT_ROOT = Path(__file__).parent
    # Path to core Python implementation packages
    SRC_DIR = PROJECT_ROOT / "src"
    # Path to automated test suites (pytest)
    TESTS_DIR = PROJECT_ROOT / "tests"
    # Path to agent prompt templates and configurations
    AGENTS_DIR = PROJECT_ROOT / "agents"
    # Path to YAML grammar and parser subset specifications
    SPECS_DIR = PROJECT_ROOT / "specs"
    # Destination directory for timestamped pipeline run artifacts (runs/<run_id>/)
    RUNS_DIR = PROJECT_ROOT / "runs"
    # Prompts repository
    PROMPTS_DIR = PROJECT_ROOT / "prompts"
    # Documentation and technical reports
    DOCS_DIR = PROJECT_ROOT / "docs"
    
    # --- Parser Safety Limits & Guards ---
    # Hard timeout ceiling in seconds to prevent infinite loops during regex/tokenizer evaluation
    MAX_PARSING_TIME = 5.0
    # Guard against stack overflow during deeply recursive DOM tree traversal
    MAX_TREE_DEPTH = 1000
    # Maximum token count allowed per document to prevent memory exhaustion attacks
    MAX_TOKEN_COUNT = 100000
    
    # --- Test & Adversarial Runner Configuration ---
    # Maximum execution duration before timing out an individual test case
    TEST_TIMEOUT = 10.0
    # Iteration count for red-team adversarial fuzzing rounds
    STRESS_TEST_ITERATIONS = 100
    
    # --- Patch & Automated Program Repair Configuration ---
    # Number of surrounding context lines to include in generated unified diffs (.patch)
    PATCH_CONTEXT_LINES = 3
    
    @classmethod
    def ensure_directories_exist(cls):
        """Create all required directories if they don't exist."""
        # Iterate over all defined filesystem locations and create missing parent dirs
        for directory in [cls.SRC_DIR, cls.TESTS_DIR, cls.AGENTS_DIR, 
                          cls.SPECS_DIR, cls.RUNS_DIR, cls.PROMPTS_DIR, cls.DOCS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    Config.ensure_directories_exist()
    print(f"Project root: {Config.PROJECT_ROOT}")
    print(f"All directories initialized successfully")
