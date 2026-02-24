"""
Groq AI Integration Module
Handles communication with Groq's API for all agent operations.
This module serves as the external AI tool bridge for the agentic pipeline.

FEATURE 2: External AI Tool Integration (Groq)
"""

from typing import Optional, Dict, Any
try:
    from groq import Groq
except ImportError:
    Groq = None  # type: ignore

# Import configuration
from config import Config


class GroqAgent:
    """
    Wrapper around Groq API for use by all specialized agents.
    Provides unified interface for calling Groq with different prompts.
    """

    def __init__(self):
        """Initialize Groq agent with API configuration."""
        if Groq is None:
            raise ImportError(
                "groq package is not installed. Run: pip install groq"
            )

        # Validate API key exists
        if not Config.GROQ_API_KEY or Config.GROQ_API_KEY == "":
            raise ValueError(
                "GROQ_API_KEY not set. Please set it in .env file or environment variable"
            )

        # Initialize Groq client
        self.client = Groq(api_key=Config.GROQ_API_KEY)
        self.model = Config.GROQ_MODEL
        self.max_tokens = Config.MAX_TOKENS
        self.conversation_history = []

    def call(self, user_message: str, system_prompt: Optional[str] = None,
             temperature: Optional[float] = None) -> str:
        """
        Call Groq API with a message.

        Args:
            user_message: The message to send to Groq
            system_prompt: Optional system prompt for context
            temperature: Optional temperature override (0-1)

        Returns:
            Groq's response text
        """
        try:
            # Build messages list
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": user_message})

            # Call Groq API (OpenAI-compatible chat completions)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=temperature if temperature is not None else Config.TEMPERATURE,
            )

            # Extract response text
            response_text = response.choices[0].message.content

            # Log for debugging
            print(f"[Groq] Response length: {len(response_text)} chars")

            return response_text

        except Exception as e:
            print(f"Error calling Groq API: {e}")
            raise

    def call_with_context(self, user_message: str,
                          system_prompt: Optional[str] = None) -> str:
        """
        Call Groq with conversation history for multi-turn interactions.

        Args:
            user_message: The message to send
            system_prompt: Optional system prompt

        Returns:
            Groq's response
        """
        # Build messages with optional system prompt
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # Add history + new user message
        messages.extend(self.conversation_history)
        messages.append({"role": "user", "content": user_message})

        # Call Groq API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=Config.TEMPERATURE,
        )

        # Extract response
        assistant_message = response.choices[0].message.content

        # Update history (without system prompt so we don't duplicate it)
        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": assistant_message})

        return assistant_message

    def clear_history(self) -> None:
        """Clear conversation history for a new conversation."""
        self.conversation_history = []


class SpecAgentAI:
    """AI component for Spec Agent - generates structured specifications."""

    def __init__(self):
        """Initialize Spec Agent AI."""
        self.groq = GroqAgent()

    def generate_specification(self, html_subset: str,
                               parser_interface: str) -> str:
        """
        Generate structured specification from HTML subset description.

        Args:
            html_subset: Human-written HTML subset to implement
            parser_interface: Description of parser interface

        Returns:
            YAML specification string
        """
        system_prompt = """You are an expert HTML5 specification interpreter.
Your task is to convert informal HTML5 subset descriptions into structured YAML specifications.
The specification should include:
1. Tokenizer states and rules
2. Parsing rules for tag handling
3. Implicit tag closure rules
4. Expected test cases
Provide only valid YAML without any markdown formatting."""

        user_message = f"""Create a detailed YAML specification for parsing this HTML5 subset:

HTML SUBSET:
{html_subset}

PARSER INTERFACE:
{parser_interface}

Requirements:
- Include tokenizer states
- Document parsing rules
- Specify implicit closure behaviors
- List expected test cases
- Be precise and unambiguous"""

        return self.groq.call(user_message, system_prompt)


class CodegenAgentAI:
    """AI component for Codegen Agent - generates implementation patches."""

    def __init__(self):
        """Initialize Codegen Agent AI."""
        self.groq = GroqAgent()

    def generate_code_patch(self, specification: str, current_implementation: str,
                            required_features: str) -> str:
        """
        Generate code patch from specification.

        Args:
            specification: YAML specification from Spec Agent
            current_implementation: Current parser code
            required_features: List of features to implement

        Returns:
            Unified diff patch string
        """
        system_prompt = """You are an expert Python developer specializing in HTML parsing.
Your task is to generate precise code patches that implement parsing specifications.
Always produce valid unified diff format patches.
Include inline comments explaining key decisions.
The patches must be directly applicable with 'git apply'."""

        user_message = f"""Generate a unified diff patch to implement these features:

SPECIFICATION:
{specification}

CURRENT IMPLEMENTATION:
{current_implementation}

REQUIRED FEATURES:
{required_features}

Instructions:
- Create patches that extend the parser incrementally
- Add inline comments explaining the implementation
- Ensure patches are valid unified diff format
- Handle edge cases gracefully
- Include error handling"""

        return self.groq.call(user_message, system_prompt)


class CritiqueAgentAI:
    """AI component for Critique Agent - validates generated code."""

    def __init__(self):
        """Initialize Critique Agent AI."""
        self.groq = GroqAgent()

    def critique_patch(self, patch_content: str, specification: str,
                       test_results: str) -> Dict[str, Any]:
        """
        Critique a generated patch for correctness and quality.

        Args:
            patch_content: The patch to critique
            specification: Original specification
            test_results: Test execution results

        Returns:
            Critique report with approval status and recommendations
        """
        system_prompt = """You are an expert code reviewer specializing in parser implementation.
Your task is to validate patches against specifications and test results.
Provide a structured JSON response with:
1. approval (true/false)
2. issues (list of problems found)
3. recommendations (list of improvements)
4. confidence_score (0-100)
Return only valid JSON."""

        user_message = f"""Review this patch against the specification:

PATCH:
{patch_content}

SPECIFICATION:
{specification}

TEST RESULTS:
{test_results}

Evaluate for:
- Correctness relative to specification
- Code quality and style
- Handling of edge cases
- Test pass rate
- Potential security issues

Respond as JSON only."""

        response = self.groq.call(user_message, system_prompt, temperature=0.3)

        # Parse JSON response
        try:
            import json
            return json.loads(response)
        except Exception:
            return {
                "approval": False,
                "issues": ["Failed to parse critique response"],
                "recommendations": ["Review agent output manually"],
                "confidence_score": 0
            }


class TestAgentAI:
    """AI component for Test Agent - generates test cases."""

    def __init__(self):
        """Initialize Test Agent AI."""
        self.groq = GroqAgent()

    def generate_tests(self, specification: str, parser_interface: str) -> str:
        """
        Generate test cases from specification.

        Args:
            specification: YAML specification
            parser_interface: Parser interface description

        Returns:
            Python test code as string
        """
        system_prompt = """You are an expert QA engineer specializing in parser testing.
Your task is to generate comprehensive test cases for HTML5 parsers.
Produce valid Python pytest code with:
1. Conformance tests (specification compliance)
2. Edge case tests
3. Error handling tests
Include inline comments explaining each test."""

        user_message = f"""Generate comprehensive test cases for this parser:

SPECIFICATION:
{specification}

PARSER INTERFACE:
{parser_interface}

Requirements:
- Use pytest framework
- Test tokenization correctness
- Test tree construction
- Test implicit tag closure
- Test error handling
- Include at least 10 test cases
- Add docstrings explaining test purpose"""

        return self.groq.call(user_message, system_prompt)


class RedTeamAgentAI:
    """AI component for Red-Team Agent - generates adversarial tests."""

    def __init__(self):
        """Initialize Red-Team Agent AI."""
        self.groq = GroqAgent()

    def generate_adversarial_tests(self, parser_interface: str,
                                   known_vulnerabilities: Optional[str] = None) -> str:
        """
        Generate stress and security tests.

        Args:
            parser_interface: Parser interface description
            known_vulnerabilities: Optional list of known issues

        Returns:
            Python test code for adversarial cases
        """
        system_prompt = """You are a security expert specializing in parser vulnerabilities.
Your task is to generate adversarial test cases that stress parser robustness.
Focus on:
1. Deeply nested structures
2. Malformed HTML
3. Resource exhaustion
4. Invalid attribute combinations
Produce valid pytest code with inline comments."""

        user_message = f"""Generate adversarial test cases for parser robustness:

PARSER INTERFACE:
{parser_interface}

{f'KNOWN VULNERABILITIES: {known_vulnerabilities}' if known_vulnerabilities else ''}

Create tests for:
- Deeply nested tags (>1000 levels)
- Malformed HTML with missing brackets
- Extremely long attributes
- Invalid character sequences
- Circular references
- Resource constraint violations
- Timeout scenarios

Ensure tests verify:
- Parser gracefully handles malformed input
- No resource exhaustion
- No infinite loops
- Predictable error messages"""

        return self.groq.call(user_message, system_prompt)


class MonitorAgentAI:
    """AI component for Monitor Agent - analyzes execution metrics."""

    def __init__(self):
        """Initialize Monitor Agent AI."""
        self.groq = GroqAgent()

    def analyze_execution(self, execution_trace: str,
                          performance_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze execution trace for anomalies.

        Args:
            execution_trace: Trace from parser execution
            performance_metrics: Performance measurements

        Returns:
            Analysis report with issues and recommendations
        """
        system_prompt = """You are a performance and reliability expert.
Your task is to analyze parser execution traces and identify issues.
Respond with JSON containing:
1. healthy (true/false)
2. issues (list of problems)
3. bottlenecks (list of performance issues)
4. recommendations (improvements)"""

        user_message = f"""Analyze this parser execution:

TRACE:
{execution_trace}

METRICS:
{str(performance_metrics)}

Check for:
- Excessive recursion
- Memory issues
- Timeout violations
- Inefficient algorithms
- State machine errors

Respond as JSON only."""

        response = self.groq.call(user_message, system_prompt, temperature=0.2)

        try:
            import json
            return json.loads(response)
        except Exception:
            return {
                "healthy": False,
                "issues": ["Failed to parse analysis"],
                "bottlenecks": [],
                "recommendations": ["Review execution manually"]
            }


class RepairAgentAI:
    """AI component for Repair Agent - generates fixes for failures."""

    def __init__(self):
        """Initialize Repair Agent AI."""
        self.groq = GroqAgent()

    def generate_repair_patch(self, failing_tests: str, execution_trace: str,
                              current_implementation: str) -> str:
        """
        Generate repair patch from failure evidence.

        Args:
            failing_tests: Description of failing tests
            execution_trace: Execution trace showing failures
            current_implementation: Current parser code

        Returns:
            Unified diff patch to fix issues
        """
        system_prompt = """You are an expert debugger specializing in parser repairs.
Your task is to analyze failures and generate targeted fixes.
Produce precise unified diff patches that:
1. Fix only the failing cases
2. Include inline comments
3. Don't introduce regressions
4. Are minimal and focused"""

        user_message = f"""Generate a repair patch for these failures:

FAILING TESTS:
{failing_tests}

EXECUTION TRACE:
{execution_trace}

CURRENT IMPLEMENTATION:
{current_implementation}

Requirements:
- Identify root cause of failures
- Fix only what's broken
- Add explanatory comments
- Ensure patch is minimal
- Output as unified diff"""

        return self.groq.call(user_message, system_prompt)


# Convenience factory function
def get_agent(agent_type: str) -> object:
    """
    Factory function to get specific AI agent.

    Args:
        agent_type: Type of agent ('spec', 'codegen', 'critique', 'test', 'red_team', 'monitor', 'repair')

    Returns:
        Initialized AI agent
    """
    agents = {
        "spec": SpecAgentAI,
        "codegen": CodegenAgentAI,
        "critique": CritiqueAgentAI,
        "test": TestAgentAI,
        "red_team": RedTeamAgentAI,
        "monitor": MonitorAgentAI,
        "repair": RepairAgentAI
    }

    agent_class = agents.get(agent_type)
    if not agent_class:
        raise ValueError(f"Unknown agent type: {agent_type}")

    return agent_class()


if __name__ == "__main__":
    # Test Groq integration
    print("Testing Groq AI Integration...")

    try:
        groq_agent = GroqAgent()
        response = groq_agent.call("Hello! What is an HTML5 parser?")
        print(f"Response: {response[:200]}...")
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure GROQ_API_KEY is set in .env file")
