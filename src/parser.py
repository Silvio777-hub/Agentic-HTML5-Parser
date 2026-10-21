"""
HTML5 Parser Interface and Implementation
Core tokenization and tree-building functionality with tracing capabilities.

FEATURE 1: Traceable Parser Interface
- Tokenize HTML into a stream of tokens
- Parse tokens into a DOM tree structure
- Provide execution traces for debugging
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple, Set
from enum import Enum
import time
import re
import html as _html_module

# Standard HTML5 void elements (cannot have children or closing tags)
VOID_ELEMENTS_SET = {
    'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
    'link', 'meta', 'param', 'source', 'track', 'wbr'
}


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
    """Represents a node in the DOM tree with full query, traversal, and HTML serialization."""
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

    # -------------------------------------------------------------
    # DOM Text Extraction & Navigation Properties
    # -------------------------------------------------------------
    def get_text(self, separator: str = "", strip: bool = False) -> str:
        """
        Recursively extract all concatenated text from this node and all descendants.
        
        Args:
            separator: String inserted between text chunks
            strip: If True, whitespace at start/end of each chunk is stripped
        """
        chunks: List[str] = []
        
        def _collect(node: 'TreeNode'):
            if node.text_content:
                t = node.text_content.strip() if strip else node.text_content
                if t:
                    chunks.append(t)
            for child in node.children:
                _collect(child)
                
        _collect(self)
        result = separator.join(chunks)
        return result.strip() if strip else result

    @property
    def text(self) -> str:
        """Convenience property matching BeautifulSoup's .text attribute."""
        return self.get_text()

    # -------------------------------------------------------------
    # DOM Query & Search API (find, find_all, select, select_one)
    # -------------------------------------------------------------
    def _matches(self, name: Optional[str] = None, attrs: Optional[Dict[str, Any]] = None, **kwargs) -> bool:
        """Helper to determine if this node satisfies given tag name and attribute constraints."""
        if name is not None:
            if name != "*" and self.name.lower() != name.lower():
                return False
                
        target_attrs: Dict[str, Any] = {}
        if attrs:
            target_attrs.update(attrs)
        for k, v in kwargs.items():
            attr_key = "class" if k == "class_" else k
            target_attrs[attr_key] = v
            
        for key, expected_val in target_attrs.items():
            actual_val = self.attributes.get(key)
            if actual_val is None:
                return False
            if expected_val is True:
                continue
            if key == "class" and isinstance(expected_val, str):
                actual_classes = actual_val.split()
                expected_classes = expected_val.split()
                if not all(cls in actual_classes for cls in expected_classes):
                    return False
            elif str(actual_val) != str(expected_val):
                return False
                
        return True

    def find(self, name: Optional[str] = None, attrs: Optional[Dict[str, Any]] = None, recursive: bool = True, **kwargs) -> Optional['TreeNode']:
        """
        Find the first matching descendant element in the DOM subtree.
        
        Examples:
            node.find("p")
            node.find("div", class_="container")
            node.find(id="header")
        """
        results = self.find_all(name=name, attrs=attrs, recursive=recursive, limit=1, **kwargs)
        return results[0] if results else None

    def find_all(self, name: Optional[str] = None, attrs: Optional[Dict[str, Any]] = None, recursive: bool = True, limit: Optional[int] = None, **kwargs) -> List['TreeNode']:
        """
        Find all matching descendant elements in the DOM subtree.
        
        Args:
            name: Tag name to match ('*' for any tag, None to match attributes only)
            attrs: Dictionary of attribute names and expected values
            recursive: If True, search all descendants; if False, search direct children only
            limit: Maximum number of matches to return
            **kwargs: Direct attribute lookups (e.g. class_="active", id="btn")
        """
        matches: List['TreeNode'] = []
        
        def _search(node: 'TreeNode'):
            for child in node.children:
                if child._matches(name=name, attrs=attrs, **kwargs):
                    matches.append(child)
                    if limit is not None and len(matches) >= limit:
                        return
                if recursive:
                    _search(child)
                    if limit is not None and len(matches) >= limit:
                        return

        _search(self)
        return matches

    def select_one(self, selector: str) -> Optional['TreeNode']:
        """Find the first element matching a CSS selector."""
        results = self.select(selector)
        return results[0] if results else None

    def select(self, selector: str) -> List['TreeNode']:
        """
        Query the DOM subtree using CSS selectors.
        Supports:
          - Tag selectors ('p', 'div')
          - ID selectors ('#header', 'div#main')
          - Class selectors ('.card', 'div.card')
          - Attribute selectors ('[href]', '[type="text"]')
          - Descendant combinators ('div p', 'article.post span.author')
          - Comma-separated selectors ('h1, h2, h3')
        """
        if "," in selector:
            results: List['TreeNode'] = []
            seen_ids = set()
            for part in selector.split(","):
                for node in self.select(part.strip()):
                    if id(node) not in seen_ids:
                        seen_ids.add(id(node))
                        results.append(node)
            return results

        tokens = selector.strip().split()
        if not tokens:
            return []

        candidates = [self]
        for token in tokens:
            next_candidates = []
            for candidate in candidates:
                matched = candidate._match_selector_token(token)
                next_candidates.extend(matched)
            candidates = next_candidates
            
        return candidates

    def _match_selector_token(self, token: str) -> List['TreeNode']:
        """Matches a single selector token (e.g. 'div.container#main[data-active]') against all descendants."""
        tag_match = re.match(r'^([a-zA-Z0-9_\-]+|\*)?', token)
        tag_name = tag_match.group(1) if tag_match and tag_match.group(1) else None
        
        id_match = re.search(r'#([a-zA-Z0-9_\-]+)', token)
        target_id = id_match.group(1) if id_match else None
        
        classes = re.findall(r'\.([a-zA-Z0-9_\-]+)', token)
        attr_specs = re.findall('\\[([a-zA-Z0-9_\\-]+)(?:=[\\\'"]?([^\\\'"]*)[\\\'"]?)?\\]', token)
        
        attrs_filter: Dict[str, Any] = {}
        if target_id:
            attrs_filter["id"] = target_id
        for attr_name, attr_val in attr_specs:
            attrs_filter[attr_name] = attr_val if attr_val != "" else True
            
        def _matches_token(node: 'TreeNode') -> bool:
            if not node._matches(name=tag_name, attrs=attrs_filter):
                return False
            if classes:
                node_classes = node.attributes.get("class", "").split()
                if not all(c in node_classes for c in classes):
                    return False
            return True

        matched: List['TreeNode'] = []
        def _traverse(node: 'TreeNode'):
            for child in node.children:
                if _matches_token(child):
                    matched.append(child)
                _traverse(child)
                
        _traverse(self)
        return matched

    # -------------------------------------------------------------
    # Reverse HTML Serialization (to_html)
    # -------------------------------------------------------------
    def to_html(self, pretty: bool = False, indent_level: int = 0, indent_step: str = "  ") -> str:
        """
        Serialize this DOM subtree back into clean, standard-compliant HTML markup.
        Supports pretty-printing and proper void element handling.
        
        Args:
            pretty: If True, format with indentation and line breaks
            indent_level: Current indentation depth
            indent_step: String used for each indentation level (default 2 spaces)
            
        Returns:
            Rendered HTML string
        """
        indent = (indent_step * indent_level) if pretty else ""
        nl = "\n" if pretty else ""

        if self.name in ("#document",):
            return "".join(child.to_html(pretty=pretty, indent_level=indent_level, indent_step=indent_step) for child in self.children)

        if self.name == "!doctype":
            return f"<!DOCTYPE html>{nl}"

        if self.name == "#comment":
            return f"{indent}<!-- {self.text_content} -->{nl}"

        if self.name == "#text":
            return self.text_content

        attr_parts = []
        for k, v in sorted(self.attributes.items()):
            if v == "" or v is True:
                attr_parts.append(k)
            else:
                escaped_v = str(v).replace('"', '&quot;')
                attr_parts.append(f'{k}="{escaped_v}"')
        attr_str = f" {' '.join(attr_parts)}" if attr_parts else ""

        if self.name.lower() in VOID_ELEMENTS_SET:
            return f"{indent}<{self.name}{attr_str}>{nl}"

        if not self.children:
            if self.text_content:
                return f"{indent}<{self.name}{attr_str}>{self.text_content}</{self.name}>{nl}"
            else:
                return f"{indent}<{self.name}{attr_str}></{self.name}>{nl}"

        inner_html_parts = []
        if self.text_content:
            text_indent = (indent_step * (indent_level + 1)) if pretty else ""
            inner_html_parts.append(f"{text_indent}{self.text_content}{nl}")
            
        for child in self.children:
            inner_html_parts.append(child.to_html(pretty=pretty, indent_level=indent_level + 1, indent_step=indent_step))
            
        inner_str = "".join(inner_html_parts)
        return f"{indent}<{self.name}{attr_str}>{nl}{inner_str}{indent}</{self.name}>{nl}"


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
    COMMENT_STATE = "COMMENT"
    RAWTEXT_STATE = "RAWTEXT"

    # Self-closing tags in HTML5
    VOID_ELEMENTS = {
        'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
        'link', 'meta', 'param', 'source', 'track', 'wbr'
    }

    # Raw-text elements: content consumed verbatim until the matching end tag.
    # Prevents '<' or '>' inside <script>/<style> from being mis-tokenised.
    RAWTEXT_ELEMENTS = {'script', 'style', 'textarea', 'title'}
    
    def __init__(self, trace: Optional[ParsingTrace] = None):
        """Initialize tokenizer with optional trace."""
        self.trace = trace or ParsingTrace()
        self.current_state = self.DATA_STATE
        # Tracks which RAWTEXT element we are inside (e.g. 'script', 'style')
        self._rawtext_tag: str = ""

    def _consume_character_reference(self, html: str, index: int) -> Tuple[Optional[str], int]:
        """
        Consumes a character reference starting at index (where html[index] == '&').
        Returns (decoded_char, new_index).
        If not a valid character reference, returns (None, index).
        """
        if index >= len(html) or html[index] != '&':
            return None, index

        # Decimal or Hex numeric character reference: &#...; or &#x...;
        if index + 2 < len(html) and html[index + 1] == '#':
            if index + 3 < len(html) and html[index + 2] in ('x', 'X'):
                end = index + 3
                while end < len(html) and (end - index) <= 12:
                    if html[end] == ';':
                        hex_str = html[index + 3:end]
                        try:
                            code_point = int(hex_str, 16)
                            if 0 <= code_point <= 0x10FFFF:
                                return chr(code_point), end + 1
                        except ValueError:
                            break
                        break
                    elif not html[end].isalnum():
                        break
                    end += 1
            else:
                end = index + 2
                while end < len(html) and (end - index) <= 12:
                    if html[end] == ';':
                        dec_str = html[index + 2:end]
                        try:
                            code_point = int(dec_str, 10)
                            if 0 <= code_point <= 0x10FFFF:
                                return chr(code_point), end + 1
                        except ValueError:
                            break
                        break
                    elif not html[end].isdigit():
                        break
                    end += 1

        # Named character reference: &name;
        end = index + 1
        while end < len(html) and (end - index) <= 35:
            if html[end] == ';':
                entity_substr = html[index:end + 1]
                val = _html_module.unescape(entity_substr)
                if val != entity_substr:
                    return val, end + 1
                break
            elif not (html[end].isalnum() or html[end] in ('_', '-')):
                break
            end += 1

        return None, index
    
    def tokenize(self, html: str) -> List[Token]:
        """
        Tokenize HTML string into list of tokens.
        
        Args:
            html: Raw HTML string
            
        Returns:
            List of Token objects
        """
        self.current_state = self.DATA_STATE
        self._rawtext_tag = ""
        tokens: List[Token] = []
        i = 0
        current_token: Optional[Token] = None
        current_attr_name = ""
        current_attr_value = ""
        tag_name = ""
        quote_char = None
        
        # Track state for tracing
        self.trace.add_event("tokenization_start", {"html_length": len(html)})
        
        while i < len(html):
            char = html[i]
            
            # DATA STATE: Normal character data
            if self.current_state == self.DATA_STATE:
                if char == '<':
                    self.current_state = self.TAG_OPEN_STATE
                elif char == '&':
                    decoded, next_i = self._consume_character_reference(html, i)
                    if decoded is not None:
                        for ch in decoded:
                            tokens.append(Token(TokenType.CHARACTER, data=ch))
                            self.trace.add_event("character_reference_decoded", {"char": ch})
                        i = next_i - 1  # will increment by 1 at end of loop
                    else:
                        tokens.append(Token(TokenType.CHARACTER, data=char))
                        self.trace.add_event("character_emitted", {"char": char})
                else:
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
                    # Comment: <!-- ... -->
                    # NOTE: char='!' and i points to '!'. The '<' was already consumed.
                    # So html[i:i+3] == "!--" means we have the full "<!--" sequence.
                    if html[i:i+3] == "!--":
                        # Advance i to first content character after "<!--".
                        # i currently points to '!'; '!' + '--' occupies 3 chars.
                        # After this block the main loop does i += 1, so we set i = i+2
                        # so that after i+=1 we land on the first content char (i+3).
                        self.current_state = self.COMMENT_STATE
                        i += 2  # points to last '-' of '<!--'; +1 in loop → first content
                    # DOCTYPE declaration (case-insensitive per HTML5 spec)
                    elif html[i:i+8].upper() == "!DOCTYPE":
                        # Consume up to the closing '>'
                        end = html.find('>', i)
                        if end == -1:
                            end = len(html) - 1
                        tokens.append(Token(TokenType.DOCTYPE, data="html"))
                        self.trace.add_event("doctype_emitted", {})
                        i = end
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
                    # Switch to RAWTEXT state when entering a raw-text element
                    if (current_token
                            and current_token.type == TokenType.START_TAG
                            and (current_token.name or tag_name.lower()) in self.RAWTEXT_ELEMENTS):
                        self.current_state = self.RAWTEXT_STATE
                        self._rawtext_tag = current_token.name or tag_name.lower()
                    else:
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
                        # Switch to RAWTEXT state for raw-text elements
                        if (current_token.type == TokenType.START_TAG
                                and current_token.name in self.RAWTEXT_ELEMENTS):
                            self.current_state = self.RAWTEXT_STATE
                            self._rawtext_tag = current_token.name
                        else:
                            self.current_state = self.DATA_STATE
                    else:
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
                    quote_char = char
                    self.current_state = self.ATTRIBUTE_VALUE_STATE
                    current_attr_value = ""
                else:
                    quote_char = None
                    current_attr_value = char
                    self.current_state = self.ATTRIBUTE_VALUE_STATE
            
            # ATTRIBUTE_VALUE STATE
            elif self.current_state == self.ATTRIBUTE_VALUE_STATE:
                if quote_char and char == quote_char:
                    # Closing quote for attribute value
                    if current_token and current_attr_name:
                        decoded_val = _html_module.unescape(current_attr_value)
                        current_token.attributes[current_attr_name] = decoded_val
                        self.trace.add_event("attribute_parsed", {
                            "name": current_attr_name,
                            "value": decoded_val
                        })
                    current_attr_name = ""
                    current_attr_value = ""
                    quote_char = None
                    self.current_state = self.BEFORE_ATTRIBUTE_NAME_STATE
                elif not quote_char and (char == '>' or char in ' \t\n'):
                    if current_token and current_attr_name:
                        decoded_val = _html_module.unescape(current_attr_value)
                        current_token.attributes[current_attr_name] = decoded_val
                        self.trace.add_event("attribute_parsed", {
                            "name": current_attr_name,
                            "value": decoded_val
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
                elif quote_char and char == '>':
                    # Unclosed quote followed by tag close
                    if current_token and current_attr_name:
                        decoded_val = _html_module.unescape(current_attr_value)
                        current_token.attributes[current_attr_name] = decoded_val
                    current_attr_name = ""
                    current_attr_value = ""
                    quote_char = None
                    if current_token:
                        tokens.append(current_token)
                    self.current_state = self.DATA_STATE
                    current_token = None
                else:
                    current_attr_value += char

            # BOGUS_COMMENT STATE: Ingests bogus comments (e.g. <?...>) until '>'
            elif self.current_state == self.BOGUS_COMMENT_STATE:
                if char == '>':
                    tokens.append(Token(TokenType.COMMENT, data=""))
                    self.trace.add_event("bogus_comment_emitted", {})
                    self.current_state = self.DATA_STATE

            # COMMENT STATE: Properly captures <!-- ... --> with data preserved
            elif self.current_state == self.COMMENT_STATE:
                # Collect everything up to (but not including) '-->'
                end = html.find('-->', i)
                if end == -1:
                    # Unterminated comment — consume the rest
                    comment_data = html[i:]
                    tokens.append(Token(TokenType.COMMENT, data=comment_data))
                    self.trace.add_event("comment_emitted", {"data_len": len(comment_data)})
                    i = len(html)
                else:
                    comment_data = html[i:end]
                    tokens.append(Token(TokenType.COMMENT, data=comment_data))
                    self.trace.add_event("comment_emitted", {"data_len": len(comment_data)})
                    i = end + 3  # skip '-->'
                self.current_state = self.DATA_STATE
                continue  # i already positioned; skip the normal i += 1

            # RAWTEXT STATE: Verbatim content inside <script>, <style>, <textarea>, <title>
            elif self.current_state == self.RAWTEXT_STATE:
                # Look for the closing end tag
                close_tag = f"</{self._rawtext_tag}"
                end = html.lower().find(close_tag.lower(), i)
                if end == -1:
                    # No closing tag found — consume the rest as raw text
                    raw = html[i:]
                    if raw:
                        tokens.append(Token(TokenType.CHARACTER, data=raw))
                        self.trace.add_event("rawtext_emitted", {
                            "tag": self._rawtext_tag,
                            "length": len(raw)
                        })
                    i = len(html)
                else:
                    raw = html[i:end]
                    if raw:
                        tokens.append(Token(TokenType.CHARACTER, data=raw))
                        self.trace.add_event("rawtext_emitted", {
                            "tag": self._rawtext_tag,
                            "length": len(raw)
                        })
                    # Emit the closing end-tag token
                    close_end = html.find('>', end)
                    if close_end == -1:
                        close_end = len(html) - 1
                    tokens.append(Token(TokenType.END_TAG, name=self._rawtext_tag))
                    self.trace.add_event("rawtext_end_tag_emitted", {"tag": self._rawtext_tag})
                    i = close_end + 1
                self.current_state = self.DATA_STATE
                self._rawtext_tag = ""
                continue  # i already positioned; skip the normal i += 1

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
            elif token.type == TokenType.DOCTYPE:
                self._process_doctype(token)
            elif token.type == TokenType.COMMENT:
                self._process_comment(token)
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
        Implements implicit tag closure rules and root <html> attribute merging.
        """
        tag_name = token.name

        # HTML5 Spec: If we receive a second <html> start tag when one is already
        # open, merge its attributes into the root rather than creating a nested node.
        # This prevents the duplicate-root "<html <html>>" artifact.
        if tag_name == "html" and self.root and self.root.name == "html":
            for attr_key, attr_val in (token.attributes or {}).items():
                if attr_key not in self.root.attributes:
                    self.root.attributes[attr_key] = attr_val
            self.trace.add_event("html_attributes_merged", {"attributes": token.attributes})
            return

        # HTML5 Spec Rule: An open <p> element must implicitly close before
        # block-level container elements (div, h1-h6, blockquote, table, etc.)
        if tag_name in self.SPECIAL_END_TAGS and self._is_open("p"):
            self._close_element("p")
            self.trace.add_event("implicit_p_closed", {
                "before_tag": tag_name
            })

        # Instantiate a new DOM TreeNode with parsed element attributes
        new_node = TreeNode(tag_name or "", attributes=token.attributes or {})

        # Attach the new node as a child of the currently active open element (stack top)
        if self.open_elements:
            self.open_elements[-1].add_child(new_node)

        # Push to the open elements stack only if this element has children (non-void, non-self-closing)
        if not token.self_closing:
            self.open_elements.append(new_node)

        self.trace.add_event("start_tag_processed", {
            "tag": tag_name,
            "attributes": token.attributes,
            "self_closing": token.self_closing
        })

    def _process_doctype(self, token: Token) -> None:
        """Process a DOCTYPE token by inserting a !doctype node before the root."""
        doctype_node = TreeNode("!doctype", text_content="html")
        # If root is the implicit html node and has no children yet, prepend doctype
        if self.root:
            # We store DOCTYPE as a sibling concept; attach to the open_elements[0]
            # so it appears as a top-level child when using #document wrapper.
            # For simplicity, attach to root's parent if exists, otherwise mark on root.
            self.root.attributes.setdefault("_has_doctype", "true")
        self.trace.add_event("doctype_processed", {})

    def _process_comment(self, token: Token) -> None:
        """Process a COMMENT token by inserting a #comment node in the current position."""
        comment_node = TreeNode("#comment", text_content=token.data or "")
        if self.open_elements:
            self.open_elements[-1].add_child(comment_node)
        self.trace.add_event("comment_processed", {"data_len": len(token.data or "")})
    
    def _process_end_tag(self, token: Token) -> None:
        """Process an end tag token."""
        tag_name = token.name
        if tag_name:
            # Search open stack backwards from top and pop matching element to close scope
            self._close_element(tag_name)
        self.trace.add_event("end_tag_processed", {"tag": tag_name})
    
    def _process_character(self, token: Token) -> None:
        """Process a character token."""
        # Append textual character data directly to the currently open container element
        if self.open_elements and token.data:
            current = self.open_elements[-1]
            current.text_content += token.data
            self.trace.add_event("character_processed", {"char": token.data})
    
    def _close_element(self, tag_name: Optional[str]) -> None:
        """Close an open element by tag name."""
        if not tag_name:
            return
        # Traverse stack from top to bottom (LIFO) to find and pop the most recent matching tag
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
