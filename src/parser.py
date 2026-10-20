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
    HTML5 tokenizer implementing a simplified state machine.
    Converts raw HTML into a stream of tokens.
    """
    
    # HTML5 tokenizer states
    DATA_STATE = "DATA"
    TAG_OPEN_STATE = "TAG_OPEN"
    TAG_NAME_STATE = "TAG_NAME"
    BEFORE_ATTRIBUTE_NAME_STATE = "BEFORE_ATTRIBUTE_NAME"
    ATTRIBUTE_NAME_STATE = "ATTRIBUTE_NAME"
    AFTER_ATTRIBUTE_NAME_STATE = "AFTER_ATTRIBUTE_NAME"
    BEFORE_ATTRIBUTE_VALUE_STATE = "BEFORE_ATTRIBUTE_VALUE"
    ATTRIBUTE_VALUE_STATE = "ATTRIBUTE_VALUE"
    SELF_CLOSING_STATE = "SELF_CLOSING"
    BOGUS_COMMENT_STATE = "BOGUS_COMMENT"
    
    # Self-closing tags in HTML5
    VOID_ELEMENTS = {
        'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
        'link', 'meta', 'param', 'source', 'track', 'wbr'
    }
    
    def __init__(self, trace: Optional[ParsingTrace] = None):
        """Initialize tokenizer with optional trace."""
        self.trace = trace or ParsingTrace()
        self.current_state = self.DATA_STATE
    
    def tokenize(self, html: str) -> List[Token]:
        """
        Tokenize HTML string into list of tokens.
        
        Args:
            html: Raw HTML string
            
        Returns:
            List of Token objects
        """
        tokens: List[Token] = []
        i = 0
        current_token: Optional[Token] = None
        current_attr_name = ""
        current_attr_value = ""
        tag_name = ""
        
        # Track state for tracing
        self.trace.add_event("tokenization_start", {"html_length": len(html)})
        
        while i < len(html):
            char = html[i]
            
            # DATA STATE: Normal character data
            if self.current_state == self.DATA_STATE:
                if char == '<':
                    self.current_state = self.TAG_OPEN_STATE
                else:
                    # Emit character token
                    tokens.append(Token(TokenType.CHARACTER, data=char))
                    self.trace.add_event("character_emitted", {"char": char})
            
            # TAG_OPEN STATE: After '<'
            elif self.current_state == self.TAG_OPEN_STATE:
                if char == '/':
                    # End tag
                    self.current_state = self.TAG_NAME_STATE
                    current_token = Token(TokenType.END_TAG)
                    tag_name = ""
                elif char == '!':
                    # Comment or DOCTYPE
                    if html[i:i+7] == "<!DOCTYPE":
                        tokens.append(Token(TokenType.DOCTYPE))
                        i += 6
                        self.current_state = self.DATA_STATE
                    else:
                        self.current_state = self.BOGUS_COMMENT_STATE
                else:
                    # Start tag
                    self.current_state = self.TAG_NAME_STATE
                    current_token = Token(TokenType.START_TAG)
                    tag_name = char
                    i += 1
                    continue
            
            # TAG_NAME STATE: Reading tag name
            elif self.current_state == self.TAG_NAME_STATE:
                if char == '>':
                    if current_token:
                        current_token.name = tag_name.lower()
                        if current_token.type == TokenType.START_TAG and tag_name.lower() in self.VOID_ELEMENTS:
                            current_token.self_closing = True
                        tokens.append(current_token)
                        self.trace.add_event("tag_emitted", {
                            "tag_name": tag_name.lower(),
                            "tag_type": current_token.type.value
                        })
                    self.current_state = self.DATA_STATE
                    current_token = None
                    tag_name = ""
                elif char == ' ' or char == '\t' or char == '\n':
                    if current_token:
                        current_token.name = tag_name.lower()
                    self.current_state = self.BEFORE_ATTRIBUTE_NAME_STATE
                    tag_name = ""
                    current_attr_name = ""
                else:
                    tag_name += char
            
            # BEFORE_ATTRIBUTE_NAME STATE
            elif self.current_state == self.BEFORE_ATTRIBUTE_NAME_STATE:
                if char == '>':
                    if current_token:
                        tokens.append(current_token)
                        self.trace.add_event("tag_with_attributes_emitted", {
                            "tag_name": current_token.name,
                            "attributes_count": len(current_token.attributes)
                        })
                    self.current_state = self.DATA_STATE
                    current_token = None
                elif char == '/' and i + 1 < len(html) and html[i + 1] == '>':
                    # Self-closing tag
                    if current_token:
                        current_token.self_closing = True
                    i += 1  # Skip next '>'
                    if current_token:
                        tokens.append(current_token)
                        self.trace.add_event("self_closing_tag_emitted", {
                            "tag_name": current_token.name
                        })
                    self.current_state = self.DATA_STATE
                    current_token = None
                elif char not in ' \t\n/>':
                    current_attr_name = char
                    self.current_state = self.ATTRIBUTE_NAME_STATE
            
            # ATTRIBUTE_NAME STATE
            elif self.current_state == self.ATTRIBUTE_NAME_STATE:
                if char == '=':
                    self.current_state = self.BEFORE_ATTRIBUTE_VALUE_STATE
                    current_attr_value = ""
                elif char == '>':
                    if current_token and current_attr_name:
                        current_token.attributes[current_attr_name] = ""
                    if current_token:
                        tokens.append(current_token)
                    self.current_state = self.DATA_STATE
                    current_token = None
                    current_attr_name = ""
                elif char in ' \t\n':
                    self.current_state = self.AFTER_ATTRIBUTE_NAME_STATE
                else:
                    current_attr_name += char
            
            # BEFORE_ATTRIBUTE_VALUE STATE
            elif self.current_state == self.BEFORE_ATTRIBUTE_VALUE_STATE:
                if char in '"\'':
                    self.current_state = self.ATTRIBUTE_VALUE_STATE
                    current_attr_value = ""
                else:
                    current_attr_value = char
                    self.current_state = self.ATTRIBUTE_VALUE_STATE
            
            # ATTRIBUTE_VALUE STATE
            elif self.current_state == self.ATTRIBUTE_VALUE_STATE:
                if char == '>' or char in ' \t\n':
                    if current_token and current_attr_name:
                        current_token.attributes[current_attr_name] = current_attr_value
                        self.trace.add_event("attribute_parsed", {
                            "name": current_attr_name,
                            "value": current_attr_value
                        })
                    current_attr_name = ""
                    current_attr_value = ""
                    if char == '>':
                        if current_token:
                            tokens.append(current_token)
                        self.current_state = self.DATA_STATE
                        current_token = None
                    else:
                        self.current_state = self.BEFORE_ATTRIBUTE_NAME_STATE
                else:
                    current_attr_value += char
            
            i += 1
        
        # Emit EOF token
        tokens.append(Token(TokenType.EOF))
        self.trace.add_event("tokenization_complete", {"token_count": len(tokens)})
        
        return tokens


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


def tokenize_stream(chunks):
    """
    FEATURE 1 EXTENSION: Stream tokenizer that accepts an iterable of HTML chunks
    and yields tokens incrementally as characters become available.
    
    Args:
        chunks: Iterable of str chunks (e.g. from network or generator)
        
    Yields:
        Token instances as they are constructed
    """
    buffer = ""
    tokenizer = HTMLTokenizer()
    for chunk in chunks:
        buffer += chunk
        # Tokenize currently available text
        tokens = tokenizer.tokenize(buffer)
        for token in tokens:
            if token.type != TokenType.EOF:
                yield token


def parse_stream(chunks):
    """
    FEATURE 1 EXTENSION: Streaming parser API.
    Processes incoming HTML chunks incrementally, maintaining DOM state
    and yielding tree snapshot updates.
    
    Args:
        chunks: Iterable of str chunks
        
    Yields:
        Dictionary with current tree serialization and newly emitted tokens
    """
    parser = HTMLParser()
    accumulated_html = ""
    
    for chunk in chunks:
        accumulated_html += chunk
        tree = parser.parse(accumulated_html)
        yield {
            "chunk_size": len(chunk),
            "accumulated_bytes": len(accumulated_html),
            "tree": tree.serialize(),
            "root_children_count": len(tree.children)
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
    
    print("\n=== STREAMING PARSE ===")
    chunks = ["<html><body>", "<p>Streamed Chunk 1</p>", "<div>Streamed Chunk 2</div>", "</body></html>"]
    for step, update in enumerate(parse_stream(chunks), 1):
        print(f"Step {step}: {update['accumulated_bytes']} bytes parsed, {update['root_children_count']} children")
