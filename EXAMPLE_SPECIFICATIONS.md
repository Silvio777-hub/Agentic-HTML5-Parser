# Example HTML5 Subset Specification

This file provides example specifications that can be used with the Agentic AI HTML5 Parser.

## Example 1: Basic Semantic HTML

```markdown
# HTML5 Subset: Basic Semantic Elements

## Specification

Implement a parser for the following HTML5 elements:

### Structure Elements
- `<html>` - Root element
- `<head>` - Document metadata
- `<body>` - Document content
- `<header>` - Header/navigation
- `<nav>` - Navigation section
- `<main>` - Main content
- `<article>` - Self-contained composition
- `<section>` - Thematic grouping
- `<aside>` - Sidebar content
- `<footer>` - Footer section

### Text Elements
- `<h1>` through `<h6>` - Headings
- `<p>` - Paragraph
- `<strong>` - Strong emphasis
- `<em>` - Emphasis
- `<span>` - Inline container

### Link and Image
- `<a href="">` - Hyperlink with href attribute
- `<img src="" alt="">` - Image with src and alt attributes

## Parsing Rules

1. **Implicit Closure Rules:**
   - `<p>` closes before: `<h1>`, `<h2>`, `<h3>`, `<h4>`, `<h5>`, `<h6>`, 
     `<div>`, `<section>`, `<article>`, `<nav>`, `<aside>`, `<header>`, `<footer>`
   - `<li>` closes before another `<li>`

2. **Attribute Handling:**
   - Parse attributes in key="value" format
   - Handle both double and single quotes
   - Support unquoted attributes
   - Handle attributes with no value (boolean)

3. **Text Content:**
   - Preserve text nodes as-is
   - Collapse whitespace where appropriate
   - Handle special HTML entities

## Test Cases

### Case 1: Simple Document
```html
<html>
  <head>
    <title>Page Title</title>
  </head>
  <body>
    <h1>Welcome</h1>
    <p>This is a paragraph.</p>
  </body>
</html>
```

Expected behavior:
- Parse structure correctly
- Preserve text content
- Handle nesting

### Case 2: Implicit P Closure
```html
<p>Paragraph text<h1>Heading</h1>
```

Expected behavior:
- `<p>` closes before `<h1>`
- Result: `<p>Paragraph text</p><h1>Heading</h1>`

### Case 3: Attributes
```html
<a href="https://example.com" title="Example">Link</a>
```

Expected behavior:
- Parse href attribute
- Parse title attribute
- Preserve both in tree

### Case 4: Mixed Content
```html
<article>
  <h2>Article Title</h2>
  <p>First paragraph</p>
  <section>
    <h3>Section Title</h3>
    <p>Section content</p>
  </section>
</article>
```

Expected behavior:
- Maintain correct nesting
- Preserve all elements
- Handle semantic structure
```

## Example 2: Inline vs Block Elements

```markdown
# HTML5 Subset: Inline and Block Elements

## Specification

Implement a parser distinguishing inline and block elements:

### Block Elements
- `<div>` - Division/container
- `<blockquote>` - Block quotation
- `<pre>` - Preformatted text
- `<hr>` - Horizontal rule
- `<p>` - Paragraph
- `<section>` - Thematic section
- `<article>` - Article content
- `<nav>` - Navigation
- `<header>` - Header
- `<footer>` - Footer

### Inline Elements
- `<span>` - Inline container
- `<a>` - Anchor/link
- `<strong>` - Strong emphasis
- `<em>` - Emphasis
- `<code>` - Code snippet
- `<img>` - Image
- `<br>` - Line break

### Self-Closing (Void) Elements
- `<br>` - Line break
- `<hr>` - Horizontal rule
- `<img src="">` - Image
- `<input type="">` - Input field
- `<link rel="">` - Link resource

## Parsing Rules

1. **Block-level Implicit Closure:**
   Block elements close open `<p>` tags automatically
   ```html
   <p>Text<div>Block content</div>
   <!-- Result: <p>Text</p><div>Block content</div> -->
   ```

2. **Void Elements:**
   Self-closing tags don't have end tags
   ```html
   <br>
   <hr>
   <img src="pic.jpg">
   ```

3. **Nested Blocks:**
   Block elements can contain block and inline elements
   Inline elements should not contain block elements

## Test Cases

### Case 1: Block Nesting
```html
<div>
  <p>Content</p>
  <blockquote>Quote</blockquote>
</div>
```

Expected: Correct nesting with proper closure

### Case 2: Void Elements
```html
<p>Line 1<br>Line 2</p>
Content<hr>More content
```

Expected: BR and HR treated as self-closing

### Case 3: Inline in Block
```html
<p>This is <strong>important</strong> text</p>
```

Expected: Inline element preserved within block

### Case 4: Block Before Inline Closure
```html
<p><span>Text<div>Block</div></span></p>
```

Expected: Correct handling of improper nesting
```

## Example 3: Complex Document Structure

```markdown
# HTML5 Subset: Complex Document Structure

## Specification

Implement a parser for complex real-world HTML documents:

### Elements
All previously mentioned elements plus:
- `<table>` - Table element
- `<tr>` - Table row
- `<td>` - Table cell
- `<th>` - Table header cell
- `<form>` - Form container
- `<input>` - Form input
- `<button>` - Button element
- `<label>` - Form label
- `<ul>` - Unordered list
- `<ol>` - Ordered list
- `<li>` - List item

## Parsing Rules

1. **List Item Closure:**
   `<li>` closes before another `<li>` or closing `</ul>` `</ol>`

2. **Table Structure:**
   Maintain correct `<table>` > `<tr>` > `<td>` hierarchy

3. **Form Elements:**
   Handle form nesting and inline input elements

4. **Attribute Requirements:**
   - `<img>` requires `src` and `alt`
   - `<a>` requires `href`
   - `<input>` requires `type`
   - `<form>` requires `action`

## Test Cases

### Case 1: Nested Lists
```html
<ul>
  <li>Item 1</li>
  <li>Item 2
    <ul>
      <li>Nested item</li>
    </ul>
  </li>
</ul>
```

Expected: Maintain list hierarchy

### Case 2: Form Structure
```html
<form action="/submit">
  <label for="name">Name:</label>
  <input type="text" id="name">
  <button type="submit">Submit</button>
</form>
```

Expected: All form elements correctly parsed

### Case 3: Table Structure
```html
<table>
  <tr>
    <th>Header 1</th>
    <th>Header 2</th>
  </tr>
  <tr>
    <td>Data 1</td>
    <td>Data 2</td>
  </tr>
</table>
```

Expected: Correct table hierarchy
```

## Example 4: Minimal Viable Parser

```markdown
# HTML5 Subset: Minimal Viable Parser

## Specification

Implement a minimal parser for the absolute essentials:

### Elements
- `<html>` - Root
- `<body>` - Body
- `<p>` - Paragraph
- `<div>` - Division
- `<br>` - Line break (void)
- `<a href="">` - Link

## Parsing Rules

1. Implicit `<p>` closure before `<div>`
2. Self-closing `<br>` handling
3. Basic attribute parsing (href)
4. Simple error recovery

## Test Cases

### Case 1: Minimal Document
```html
<html><body><p>Hello</p></body></html>
```

### Case 2: P Closure
```html
<p>Text<div>Block</div>
```

Result:
```html
<p>Text</p><div>Block</div>
```

### Case 3: Self-Closing
```html
<p>Line1<br>Line2</p>
```

### Case 4: Links
```html
<p><a href="test.html">Link</a></p>
```
```

## Using These Specifications

### With the Agentic Pipeline

```python
from orchestrator import PipelineOrchestrator

orchestrator = PipelineOrchestrator()

# Use one of the above specifications
html_subset = """[Paste specification here]"""

parser_interface = """
The parser must provide:
- tokenize(html) -> List[Token]
- parse(html) -> TreeNode
- parse_with_trace(html) -> {tokens, tree, trace}
"""

report = orchestrator.run(html_subset, parser_interface)
```

### Expected Output

The pipeline will generate:

1. **spec.yml** - Structured YAML specification
2. **code.patch** - Implementation patch
3. **test_parser.py** - Conformance tests
4. **test_red_team.py** - Adversarial tests
5. **test_report.json** - Test results
6. **execution traces** - For debugging

## Customization Tips

1. **Start Simple**
   - Begin with Example 4 (Minimal)
   - Gradually add complexity

2. **Focus on Edge Cases**
   - Implicit closures
   - Self-closing tags
   - Attribute parsing

3. **Test Thoroughly**
   - Generate diverse test cases
   - Include edge cases
   - Test error handling

4. **Document Assumptions**
   - What should happen with invalid HTML?
   - How to handle malformed tags?
   - Error recovery strategy?

## Common Patterns

### Pattern 1: Implicit Element Closure
Some elements automatically close before others:
```html
<p>Text<div>Block</div>
<!-- p automatically closes before div -->
```

### Pattern 2: Self-Closing Elements
Some elements don't have closing tags:
```html
<br>
<hr>
<img src="">
```

### Pattern 3: Attribute Variations
Attributes can be quoted or unquoted:
```html
<div class="foo">           <!-- Quoted -->
<div class='foo'>           <!-- Single quoted -->
<div class=foo>             <!-- Unquoted (if no spaces) -->
<div disabled>              <!-- Boolean (no value) -->
```

### Pattern 4: Nesting Rules
Some elements can only contain specific types:
```html
<ul><li>Item</li></ul>      <!-- Valid -->
<p><p>Nested</p></p>        <!-- Invalid - auto-closes -->
<a><div>Block</div></a>     <!-- Questionable -->
```

---

**These examples provide starting points for your HTML5 parser implementation.**

Choose a complexity level appropriate for your project timeline and expertise!
