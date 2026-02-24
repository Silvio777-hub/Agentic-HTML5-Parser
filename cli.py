"""
CLI for the Agentic AI HTML5 Parser.
Converts input text files into HTML pages.
"""

import sys
import os
from src.preprocessor import Preprocessor
from src.generator import Generator

def main():
    if len(sys.argv) < 3:
        print("Usage: python cli.py <input_file> <output_file>")
        sys.exit(1)
        
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.")
        sys.exit(1)
        
    with open(input_path, "r") as f:
        text = f.read()
        
    preprocessor = Preprocessor()
    generator = Generator()
    
    print(f"[*] Processing {input_path}...")
    ir = preprocessor.process(text)
    
    print(f"[*] Generating {output_path}...")
    html = generator.generate(ir)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(html)
        
    print("[+] Done!")

if __name__ == "__main__":
    main()
