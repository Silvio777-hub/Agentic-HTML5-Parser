"""
HTML5 Parser Interface and Implementation
Core tokenization and tree-building functionality with tracing capabilities.

FEATURE 1: Traceable Parser Interface
- Tokenize HTML into a stream of tokens
- Parse tokens into a DOM tree structure
- Provide execution traces for debugging
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import time


class TokenType(Enum):
    """Enumeration of HTML5 token types."""
    DOCTYPE = "DOCTYPE"
    START_TAG = "StartTag"
    END_TAG = "EndTag"
    COMMENT = "Comment"
    CHARACTER = "Character"
    EOF = "EOF"
    PARSE_ERROR = "ParseError"


@dataclass
class Token:
    """Represents a single HTML5 token."""
    type: TokenType
    name: Optional[str] = None
    attributes: Dict[str, str] = field(default_factory=dict)
    self_closing: bool = False
    data: Optional[str] = None
    force_quirks: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert token to dictionary representation."""
        return {
            "type": self.type.value,
            "name": self.name,
            "attributes": self.attributes,
            "self_closing": self.self_closing,
            "data": self.data,
            "force_quirks": self.force_quirks
        }
    
    def __str__(self) -> str:
        """String representation of token."""
        if self.type == TokenType.CHARACTER:
            return f"Char('{self.data}')"
        elif self.type == TokenType.START_TAG:
            return f"<{self.name}>"
        elif self.type == TokenType.END_TAG:
            return f"</{self.name}>"
        return f"{self.type.value}({self.name})"


@dataclass
class TreeNode:
    """Represents a node in the DOM tree."""
    name: str
    attributes: Dict[str, str] = field(default_factory=dict)
    children: List['TreeNode'] = field(default_factory=list)
    text_content: str = ""
    parent: Optional['TreeNode'] = field(default=None, repr=False)
    
    def add_child(self, child: 'TreeNode') -> None:
        """Add a child node."""
        child.parent = self
        self.children.append(child)
    
    def serialize(self) -> Dict[str, Any]:
        """Serialize node to dictionary."""
        return {
            "name": self.name,
            "attributes": self.attributes,
            "text_content": self.text_content,
            "children": [child.serialize() for child in self.children]
        }
    
    def __str__(self) -> str:
        """String representation."""
        return self.name


@dataclass
class ParsingTrace:
    """Records execution trace during parsing for debugging."""
    events: List[Dict[str, Any]] = field(default_factory=list)
    tokenizer_states: List[str] = field(default_factory=list)
    parse_errors: List[str] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    
    def add_event(self, event_type: str, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Add an event to the trace.
        
        Args:
            event_type: Type of event (e.g., 'token_emitted', 'tag_closed')
            details: Event-specific details
        """
        if details is None:
            details = {}
        self.events.append({
            "timestamp": time.time() - self.start_time,
            "type": event_type,
            "details": details or {}
        })
    
    def add_error(self, error_msg: str) -> None:
        """Record a parse error."""
        self.parse_errors.append(error_msg)
        self.add_event("parse_error", {"message": error_msg})
    
    def finalize(self) -> None:
        """Mark trace as complete."""
        self.end_time = time.time()
    
    def duration(self) -> float:
        """Get total parsing duration."""
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time


class HTMLTokenizer:
    """
    HTML5 tokenizer implementing an 11+ state machine.
    Supports double quotes, single quotes, unquoted attributes, and boolean flags.
    """
    
    # 11+ Core States
    DATA = "DATA"
    TAG_OPEN = "TAG_OPEN"
    END_TAG_OPEN = "END_TAG_OPEN"
    TAG_NAME = "TAG_NAME"
    BEFORE_ATTR_NAME = "BEFORE_ATTR_NAME"
    ATTR_NAME = "ATTR_NAME"
    AFTER_ATTR_NAME = "AFTER_ATTR_NAME"
    BEFORE_ATTR_VALUE = "BEFORE_ATTR_VALUE"
    ATTR_VALUE_DQ = "ATTR_VALUE_DQ"
    ATTR_VALUE_SQ = "ATTR_VALUE_SQ"
    ATTR_VALUE_UQ = "ATTR_VALUE_UQ"
    SELF_CLOSING = "SELF_CLOSING"
    BOGUS_COMMENT = "BOGUS_COMMENT"
    
    VOID_ELEMENTS = {
        'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
        'link', 'meta', 'param', 'source', 'track', 'wbr'
    }
    
    def __init__(self, trace: Optional[ParsingTrace] = None):
        self.trace = trace or ParsingTrace()
        self.state = self.DATA
        self.current_token: Optional[Token] = None
        self.current_attr_name = ""
        self.current_attr_value = ""
        self.reconsume = False
        self.pos = 0

    def tokenize(self, html: str) -> List[Token]:
        tokens: List[Token] = []
        self.pos = 0
        self.trace.add_event("tokenization_start", {"html_length": len(html)})
        
        while self.pos < len(html) or self.reconsume:
            char = html[self.pos] if self.pos < len(html) else None
            
            if self.state == self.DATA:
                if char == '<':
                    self.state = self.TAG_OPEN
                elif char is None:
                    break
                else:
                    tokens.append(Token(TokenType.CHARACTER, data=char))
            
            elif self.state == self.TAG_OPEN:
                if char == '/':
                    self.state = self.END_TAG_OPEN
                elif char is not None and char.isalpha():
                    self.current_token = Token(TokenType.START_TAG, name=char.lower())
                    self.state = self.TAG_NAME
                else:
                    self.state = self.DATA
                    self.reconsume = True
            
            elif self.state == self.END_TAG_OPEN:
                if char is not None and char.isalpha():
                    self.current_token = Token(TokenType.END_TAG, name=char.lower())
                    self.state = self.TAG_NAME
                else:
                    self.state = self.DATA
            
            elif self.state == self.TAG_NAME:
                if char is None or char == '>':
                    self._emit_token(tokens)
                    self.state = self.DATA
                elif char.isspace():
                    self.state = self.BEFORE_ATTR_NAME
                elif char == '/':
                    self.state = self.SELF_CLOSING
                else:
                    if self.current_token:
                        self.current_token.name += char.lower()
            
            elif self.state == self.BEFORE_ATTR_NAME:
                if char is None or char == '>':
                    self._emit_token(tokens)
                    self.state = self.DATA
                elif char == '/':
                    self.state = self.SELF_CLOSING
                elif not char.isspace():
                    self.current_attr_name = char.lower()
                    self.state = self.ATTR_NAME
            
            elif self.state == self.ATTR_NAME:
                if char is None or char == '>' or char == '/' or char.isspace():
                    if self.current_token and self.current_attr_name:
                        self.current_token.attributes[self.current_attr_name] = "" # Boolean
                    self.state = self.BEFORE_ATTR_NAME if char.isspace() else self.state
                    self.reconsume = True
                    if char in ">/": self.state = self.BEFORE_ATTR_NAME
                elif char == '=':
                    self.state = self.BEFORE_ATTR_VALUE
                else:
                    self.current_attr_name += char.lower()
            
            elif self.state == self.BEFORE_ATTR_VALUE:
                if char == '"':
                    self.state = self.ATTR_VALUE_DQ
                    self.current_attr_value = ""
                elif char == "'":
                    self.state = self.ATTR_VALUE_SQ
                    self.current_attr_value = ""
                elif char is None or char == '>':
                    self._emit_token(tokens)
                    self.state = self.DATA
                elif not char.isspace():
                    self.state = self.ATTR_VALUE_UQ
                    self.current_attr_value = char
                # skip space
            
            elif self.state == self.ATTR_VALUE_DQ:
                if char == '"':
                    self._finalize_attr()
                    self.state = self.BEFORE_ATTR_NAME
                elif char is None:
                    self._finalize_attr()
                    self.state = self.DATA
                else:
                    self.current_attr_value += char
            
            elif self.state == self.ATTR_VALUE_SQ:
                if char == "'":
                    self._finalize_attr()
                    self.state = self.BEFORE_ATTR_NAME
                elif char is None:
                    self._finalize_attr()
                    self.state = self.DATA
                else:
                    self.current_attr_value += char
                    
            elif self.state == self.ATTR_VALUE_UQ:
                if char is None or char.isspace() or char == '>':
                    self._finalize_attr()
                    self.state = self.BEFORE_ATTR_NAME
                    self.reconsume = True
                else:
                    self.current_attr_value += char

            elif self.state == self.SELF_CLOSING:
                if char == '>':
                    if self.current_token:
                        self.current_token.self_closing = True
                    self._emit_token(tokens)
                    self.state = self.DATA
                else:
                    self.state = self.BEFORE_ATTR_NAME
                    self.reconsume = True

            if self.reconsume:
                self.reconsume = False
            else:
                self.pos += 1
                
        tokens.append(Token(TokenType.EOF))
        return tokens

    def _finalize_attr(self):
        if self.current_token and self.current_attr_name:
            self.current_token.attributes[self.current_attr_name] = self.current_attr_value
            self.trace.add_event("attr_parsed", {"name": self.current_attr_name, "value": self.current_attr_value})
        self.current_attr_name = ""
        self.current_attr_value = ""

    def _emit_token(self, tokens):
        if self.current_token:
            if self.current_token.name in self.VOID_ELEMENTS:
                self.current_token.self_closing = True
            tokens.append(self.current_token)
            self.trace.add_event("tag_emitted", {"name": self.current_token.name})
            self.current_token = None


class HTMLParser:
    """
    HTML5 parser implementing simplified tree construction algorithm.
    Converts token stream into a DOM tree.
    """
    
    # Auto-closing tags that implicitly close <p>
    SPECIAL_END_TAGS = {
        'div', 'blockquote', 'section', 'article', 'nav', 'aside',
        'header', 'footer', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'
    }
    
    def __init__(self, trace: Optional[ParsingTrace] = None):
        """Initialize parser with optional trace."""
        self.trace = trace or ParsingTrace()
        self.open_elements: List[TreeNode] = []
        self.root: Optional[TreeNode] = None
    
    def parse(self, html: str) -> TreeNode:
        """
        Parse HTML string into DOM tree.
        
        Args:
            html: Raw HTML string
            
        Returns:
            Root TreeNode of the DOM tree
        """
        # Tokenize
        tokenizer = HTMLTokenizer(self.trace)
        tokens = tokenizer.tokenize(html)
        
        self.trace.add_event("parsing_start", {"token_count": len(tokens)})
        
        # Create root element
        self.root = TreeNode("html")
        self.open_elements = [self.root]
        
        # Process tokens
        for token in tokens:
            if token.type == TokenType.EOF:
                break
            elif token.type == TokenType.START_TAG:
                self._process_start_tag(token)
            elif token.type == TokenType.END_TAG:
                self._process_end_tag(token)
            elif token.type == TokenType.CHARACTER:
                self._process_character(token)
        
        self.trace.add_event("parsing_complete", {
            "tree_depth": self._calculate_depth(),
            "node_count": self._count_nodes()
        })
        
        return self.root
    
    def _process_start_tag(self, token: Token) -> None:
        """
        Process a start tag token.
        Implements implicit tag closure rules.
        """
        tag_name = token.name
        
        # Implicit <p> closure before block elements
        if tag_name in self.SPECIAL_END_TAGS and self._is_open("p"):
            self._close_element("p")
            self.trace.add_event("implicit_p_closed", {
                "before_tag": tag_name
            })
        
        # Create new node
        new_node = TreeNode(tag_name or "", attributes=token.attributes or {})
        
        # Add to current open element
        if self.open_elements:
            self.open_elements[-1].add_child(new_node)
        
        # Add to open elements stack (unless self-closing)
        if not token.self_closing:
            self.open_elements.append(new_node)
        
        self.trace.add_event("start_tag_processed", {
            "tag": tag_name,
            "attributes": token.attributes,
            "self_closing": token.self_closing
        })
    
    def _process_end_tag(self, token: Token) -> None:
        """Process an end tag token."""
        tag_name = token.name
        if tag_name:
            self._close_element(tag_name)
        self.trace.add_event("end_tag_processed", {"tag": tag_name})
    
    def _process_character(self, token: Token) -> None:
        """Process a character token."""
        if self.open_elements and token.data:
            current = self.open_elements[-1]
            current.text_content += token.data
            self.trace.add_event("character_processed", {"char": token.data})
    
    def _close_element(self, tag_name: Optional[str]) -> None:
        """Close an open element by tag name."""
        if not tag_name:
            return
        for i in range(len(self.open_elements) - 1, -1, -1):
            if self.open_elements[i].name == tag_name:
                self.open_elements.pop(i)
                return
    
    def _is_open(self, tag_name: str) -> bool:
        """Check if a tag is currently open."""
        return any(node.name == tag_name for node in self.open_elements)
    
    def _calculate_depth(self) -> int:
        """Calculate maximum depth of the tree."""
        def depth(node: TreeNode) -> int:
            if not node.children:
                return 1
            return 1 + max(depth(child) for child in node.children)
        
        return depth(self.root) if self.root else 0
    
    def _count_nodes(self) -> int:
        """Count total nodes in tree."""
        def count(node: TreeNode) -> int:
            return 1 + sum(count(child) for child in node.children)
        
        return count(self.root) if self.root else 0


def tokenize(html: str) -> List[Token]:
    """
    FEATURE 1 FUNCTION 1: Tokenize HTML string.
    
    Args:
        html: Raw HTML string
        
    Returns:
        List of Token objects
    """
    tokenizer = HTMLTokenizer()
    return tokenizer.tokenize(html)


def parse(html: str) -> TreeNode:
    """
    FEATURE 1 FUNCTION 2: Parse HTML string to DOM tree.
    
    Args:
        html: Raw HTML string
        
    Returns:
        Root TreeNode of DOM tree
    """
    parser = HTMLParser()
    return parser.parse(html)


def parse_with_trace(html: str) -> Dict[str, Any]:
    """
    FEATURE 1 FUNCTION 3: Parse HTML with execution trace.
    
    Args:
        html: Raw HTML string
        
    Returns:
        Dictionary containing tokens, tree, and trace
    """
    trace = ParsingTrace()
    
    # Tokenize
    tokenizer = HTMLTokenizer(trace)
    tokens = tokenizer.tokenize(html)
    
    # Parse
    parser = HTMLParser(trace)
    tree = parser.parse(html)
    
    # Finalize trace
    trace.finalize()
    
    return {
        "tokens": [t.to_dict() for t in tokens],
        "tree": tree.serialize(),
        "trace": {
            "events": trace.events,
            "errors": trace.parse_errors,
            "duration": trace.duration()
        }
    }


if __name__ == "__main__":
    # Example usage
    html = "<html><body><p>Hello</p><div>World</div></body></html>"
    
    print("=== TOKENIZATION ===")
    tokens = tokenize(html)
    for token in tokens:
        print(f"  {token}")
    
    print("\n=== PARSING ===")
    tree = parse(html)
    print(tree.serialize())
    
    print("\n=== PARSING WITH TRACE ===")
    result = parse_with_trace(html)
    print(f"Trace events: {len(result['trace']['events'])}")
    print(f"Parsing duration: {result['trace']['duration']:.4f}s")
