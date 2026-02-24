"""
Demo: Running the Agentic AI Pipeline

This script demonstrates the full agentic pipeline in action.
It uses the AI agents to generate, test, and refine an HTML5 parser implementation.

REQUIRES: Valid GROQ_API_KEY in .env file
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import Config


def check_api_key():
    """Check if GROQ_API_KEY is configured"""
    api_key = Config.GROQ_API_KEY
    
    if not api_key or api_key == "your_groq_api_key_here":
        print("\n❌ GROQ_API_KEY not configured!")
        print("\nPlease follow these steps:")
        print("  1. Get your free API key from: https://console.groq.com")
        print("  2. Edit .env file")
        print("  3. Set: GROQ_API_KEY=gsk_... (your actual key)")
        print("  4. Run this script again")
        return False
    
    return True


def run_pipeline():
    """Run the agentic pipeline"""
    try:
        from orchestrator import PipelineOrchestrator
        from src.parser import tokenize, parse
        
        # Define a simple HTML subset to parse
        html_subset = """
        HTML5 Subset:
        - Basic tags: <html>, <head>, <body>, <div>, <p>, <span>
        - Formatting: <b>, <i>, <strong>, <em>
        - Lists: <ul>, <ol>, <li>
        - Links: <a href="...">
        - Images: <img src="...">
        """
        
        # Define the parser interface/specification
        parser_interface = {
            "name": "HTML5Parser",
            "methods": [
                {"name": "tokenize", "input": "html_string", "output": "List[Token]"},
                {"name": "parse", "input": "html_string", "output": "TreeNode"},
            ],
            "features": [
                "Tokenization with state machine",
                "DOM tree construction",
                "Implicit tag closure",
                "Execution tracing",
                "Error recovery"
            ]
        }
        
        print("\n" + "=" * 70)
        print("AGENTIC AI HTML5 PARSER PIPELINE")
        print("=" * 70)
        print("\n📋 Pipeline Configuration:")
        print(f"  HTML Subset: {len(html_subset)} characters")
        print(f"  Parser: {parser_interface['name']}")
        print(f"  Features: {len(parser_interface['features'])}")
        
        print("\n🚀 Starting Pipeline Execution...")
        print("  This will run all 7 agents in sequence:")
        print("    1. Spec Agent - Generate specification")
        print("    2. Codegen Agent - Generate implementation")
        print("    3. Critique Agent - Review code")
        print("    4. Test Agent - Create tests")
        print("    5. Red-Team Agent - Security testing")
        print("    6. Monitor Agent - Analyze execution")
        print("    7. Repair Agent - Fix issues (if needed)")
        
        # Create orchestrator
        orchestrator = PipelineOrchestrator()
        
        # Run the pipeline
        print("\n⏳ Running pipeline... (this may take a few minutes)\n")
        results = orchestrator.run(html_subset, parser_interface)
        
        # Display results
        print("\n" + "=" * 70)
        print("PIPELINE EXECUTION COMPLETE")
        print("=" * 70)
        
        if results:
            print(f"\n✓ Pipeline completed successfully!")
            print(f"\n📁 Output Location:")
            print(f"   {results.get('run_dir', 'N/A')}")
            
            print(f"\n📊 Results Summary:")
            print(f"   Spec Generated: {results.get('spec_generated', False)}")
            print(f"   Code Generated: {results.get('code_generated', False)}")
            print(f"   Tests Created: {results.get('tests_created', False)}")
            print(f"   Artifacts Saved: {results.get('artifact_count', 0)}")
            
            print(f"\n📂 Generated Files:")
            run_dir = results.get('run_dir')
            if run_dir and Path(run_dir).exists():
                for item in Path(run_dir).glob("*"):
                    print(f"   - {item.name}")
            
            print(f"\n✨ The pipeline generated:")
            print(f"   • spec.yml - Complete HTML5 parser specification")
            print(f"   • code.patch - Implementation as unified diff")
            print(f"   • critique.json - Code review and feedback")
            print(f"   • tests.py - Comprehensive test suite")
            print(f"   • report.json - Final execution report")
        else:
            print("\n⚠️  Pipeline completed but no results returned")
        
        print("\n" + "=" * 70)
        print("Next Steps:")
        print("  1. Review the generated specification in spec.yml")
        print("  2. Check the implementation patch in code.patch")
        print("  3. Run the generated tests: pytest tests/")
        print("  4. View the detailed report in report.json")
        print("=" * 70 + "\n")
        
        return True
        
    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        print("Make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"\n❌ Pipeline Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point"""
    print("\n╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "AGENTIC AI PIPELINE DEMO" + " " * 29 + "║")
    print("╚" + "=" * 68 + "╝")
    
    # Check if API key is configured
    if not check_api_key():
        return 1
    
    # Run the pipeline
    success = run_pipeline()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
