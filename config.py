"""
Configuration module for the Agentic AI HTML5 Parser pipeline.
Manages environment variables, API keys, and system parameters.
Uses Groq as the AI provider.
"""

import os
from pathlib import Path
try:
    from dotenv import load_dotenv
except ImportError:
    # dotenv is optional; proceed without it
    def load_dotenv(*args, **kwargs) -> None:  # type: ignore
        pass

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the agentic pipeline."""
    
    # API Configuration for Groq
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")  # Groq's flagship model
    MAX_TOKENS = 4096
    TEMPERATURE = 0.7  # Balance between creativity and consistency
    
    # Project Paths
    PROJECT_ROOT = Path(__file__).parent
    SRC_DIR = PROJECT_ROOT / "src"
    TESTS_DIR = PROJECT_ROOT / "tests"
    AGENTS_DIR = PROJECT_ROOT / "agents"
    SPECS_DIR = PROJECT_ROOT / "specs"
    RUNS_DIR = PROJECT_ROOT / "runs"
    PROMPTS_DIR = PROJECT_ROOT / "prompts"
    DOCS_DIR = PROJECT_ROOT / "docs"
    
    # Parser Configuration
    MAX_PARSING_TIME = 5.0  # Maximum seconds for parsing
    MAX_TREE_DEPTH = 1000  # Maximum DOM tree depth
    MAX_TOKEN_COUNT = 100000  # Maximum tokens allowed
    
    # Test Configuration
    TEST_TIMEOUT = 10.0  # Timeout for individual tests
    STRESS_TEST_ITERATIONS = 100  # Red-team iterations
    
    # Patch Configuration
    PATCH_CONTEXT_LINES = 3  # Lines of context in diffs
    
    @classmethod
    def ensure_directories_exist(cls):
        """Create all required directories if they don't exist."""
        for directory in [cls.SRC_DIR, cls.TESTS_DIR, cls.AGENTS_DIR, 
                          cls.SPECS_DIR, cls.RUNS_DIR, cls.PROMPTS_DIR, cls.DOCS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    Config.ensure_directories_exist()
    print(f"Project root: {Config.PROJECT_ROOT}")
    print(f"All directories initialized successfully")
