"""
Offline integration tests for all 7 Claude agents, ResponseCache, and DOM export formats.

Verifies:
1. ClaudeAgent base class fallback to MockLLMProvider when offline / without API key
2. SpecAgentAI: generate_specification() and generate_spec()
3. CodegenAgentAI: generate_code_patch() and generate_patch()
4. CritiqueAgentAI: critique_patch()
5. TestAgentAI: generate_tests()
6. RedTeamAgentAI: generate_adversarial_tests()
7. MonitorAgentAI: analyze_execution()
8. RepairAgentAI: generate_repair_patch() and generate_repair()
9. get_agent() factory function across all 7 agent roles
10. TreeNode.to_dict() and TreeNode.to_json() DOM serialization methods
11. parse_to_dict() and parse_to_json() top-level convenience functions
"""

import pytest
import json
from src.parser import parse, tokenize, TreeNode, parse_to_dict, parse_to_json
from src.claude_integration import (
    ClaudeAgent,
    SpecAgentAI,
    CodegenAgentAI,
    CritiqueAgentAI,
    TestAgentAI as ClaudeTestAgentAI,
    RedTeamAgentAI,
    MonitorAgentAI,
    RepairAgentAI,
    get_agent
)

# Prevent pytest from mistaking ClaudeTestAgentAI for a test collection class
ClaudeTestAgentAI.__test__ = False


class TestDOMExportFormats:
    """Verifies TreeNode to_dict(), to_json(), parse_to_dict(), and parse_to_json()."""

    def test_tree_node_to_dict_basic(self):
        html = '<div id="main" class="container"><p>Hello <b>World</b></p></div>'
        root = parse(html)
        d = root.to_dict()

        assert isinstance(d, dict)
        assert d["name"] == "html"
        assert "attributes" in d
        assert "children" in d
        assert len(d["children"]) > 0

    def test_tree_node_to_json_valid_json(self):
        html = '<section><h1 class="title">Header</h1><p>Paragraph text</p></section>'
        root = parse(html)
        json_str = root.to_json(indent=2)

        assert isinstance(json_str, str)
        parsed_json = json.loads(json_str)
        assert parsed_json["name"] == "html"
        assert "children" in parsed_json

    def test_parse_to_dict_convenience_function(self):
        html = '<ul><li class="item">One</li><li class="item">Two</li></ul>'
        d = parse_to_dict(html)

        assert isinstance(d, dict)
        assert d["name"] == "html"
        # In our DOM representation, elements exist in children
        assert len(d["children"]) > 0
        ul = next((c for c in d["children"] if c["name"] == "ul"), None)
        assert ul is not None
        assert len(ul["children"]) == 2

    def test_parse_to_json_convenience_function(self):
        html = '<article><p>First paragraph</p><hr><p>Second paragraph</p></article>'
        json_output = parse_to_json(html, indent=4)

        assert isinstance(json_output, str)
        data = json.loads(json_output)
        assert data["name"] == "html"


class TestClaudeAgentBaseOffline:
    """Tests the ClaudeAgent base wrapper under offline Mock mode."""

    def test_claude_agent_initialization(self):
        agent = ClaudeAgent(use_cache=False)
        assert agent is not None
        assert agent.conversation_history == []

    def test_claude_agent_offline_call(self):
        agent = ClaudeAgent(use_cache=False)
        response = agent.call("Hello from test suite", system_prompt="You are a helpful assistant")
        assert isinstance(response, str)
        assert len(response) > 0

    def test_claude_agent_call_with_context_and_clear(self):
        agent = ClaudeAgent(use_cache=False)
        response = agent.call_with_context("Test message with context", system_prompt="Test system")
        assert isinstance(response, str)
        assert len(agent.conversation_history) == 2  # user + assistant

        agent.clear_history()
        assert len(agent.conversation_history) == 0


class TestSevenSpecializedAgentsOffline:
    """Verifies all 7 specialized agents execute correctly with mock fallback."""

    def test_spec_agent_ai(self):
        agent = SpecAgentAI()
        spec = agent.generate_specification(
            html_subset="<p>, <div>, <b>, <i>, implicit paragraph closure",
            parser_interface="tokenize(html), parse(html) -> TreeNode"
        )
        assert isinstance(spec, str)
        assert len(spec) > 0

        # Test alternative interface
        spec_short = agent.generate_spec(html_subset="<p>, <div>")
        assert isinstance(spec_short, (dict, str))

    def test_codegen_agent_ai(self):
        agent = CodegenAgentAI()
        patch = agent.generate_code_patch(
            specification="rules:\n  p:\n    closes_before: [div]",
            current_implementation="def parse(html): pass",
            required_features="Implicit paragraph closure"
        )
        assert isinstance(patch, str)
        assert len(patch) > 0

        # Test alternative interface
        patch_short = agent.generate_patch(specification="rules: test", current_implementation="def parse(): pass")
        assert isinstance(patch_short, str)

    def test_critique_agent_ai(self):
        agent = CritiqueAgentAI()
        critique = agent.critique_patch(
            patch_content="def parse(html): return TreeNode('html')",
            specification="Specification requirements...",
            test_results="All tests passed"
        )
        assert critique is not None

    def test_test_agent_ai(self):
        agent = ClaudeTestAgentAI()
        tests = agent.generate_tests(
            specification="Specification rules for HTML5 parsing",
            parser_interface="parse(html) -> TreeNode"
        )
        assert isinstance(tests, str)
        assert len(tests) > 0

    def test_red_team_agent_ai(self):
        agent = RedTeamAgentAI()
        attacks = agent.generate_adversarial_tests(
            parser_interface="parse(html) -> TreeNode",
            known_vulnerabilities="XSS, unclosed cascade, deep nesting"
        )
        assert isinstance(attacks, str)
        assert len(attacks) > 0

    def test_monitor_agent_ai(self):
        agent = MonitorAgentAI()
        analysis = agent.analyze_execution(
            execution_trace="event: tokenization_start; event: tag_emitted name=p",
            performance_metrics={"duration_ms": 1.5, "event_count": 10}
        )
        assert analysis is not None

    def test_repair_agent_ai(self):
        agent = RepairAgentAI()
        repair = agent.generate_repair_patch(
            failing_tests="FAILED test_implicit_closure - AssertionError: p not closed",
            execution_trace="events: [start, tag_p, tag_div]",
            current_implementation="class HTMLParser: pass"
        )
        assert isinstance(repair, str)
        assert len(repair) > 0

        # Test alternative interface
        repair_short = agent.generate_repair(failure_context="test failure context", current_implementation="class P: pass")
        assert isinstance(repair_short, str)


class TestAgentFactory:
    """Verifies get_agent() factory properly instantiates each agent role."""

    @pytest.mark.parametrize("role,expected_class", [
        ("spec", SpecAgentAI),
        ("codegen", CodegenAgentAI),
        ("critique", CritiqueAgentAI),
        ("test", ClaudeTestAgentAI),
        ("red_team", RedTeamAgentAI),
        ("monitor", MonitorAgentAI),
        ("repair", RepairAgentAI),
    ])
    def test_get_agent_valid_roles(self, role, expected_class):
        agent = get_agent(role)
        assert isinstance(agent, expected_class)

    def test_get_agent_invalid_role_raises(self):
        with pytest.raises(ValueError):
            get_agent("non_existent_role_xyz")
