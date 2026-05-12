#!/usr/bin/env python3
import argparse
import sys
import os
import re
import glob

# ANSI color codes for terminal reporting
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

# Hardcoded AI Slop Signatures (hallucinations and lazy patterns)
SLOP_SIGNATURES = {
    r"from langchain.*import.*DiscontinuedTool": "Hallucinated LangChain tool reference",
    r"import.*openai\.tools": "Hallucinated OpenAI tools module (often confused with openai.types)",
    r"\[INSERT CODE HERE\]": "Lazy AI placeholder detected",
    r"\[Rest of the code remains the same\]": "Lazy AI omission signature",
    r"#.*?As an AI language model": "AI conversational boilerplate in comments",
    r"I can help with that": "AI conversational filler detected in source",
    r"openai\.ChatCompletion\.create\(.*model=[\"']gpt-5[\"']": "Hallucinated model version (GPT-5)",
    r"import.*google\.generativeai\.NonExistentModule": "Hallucinated Google AI module",
    r"import.*torch\.magic": "Hallucinated PyTorch module",
    r"def.*\(.*\):\s*\.\.\.": "Empty implementation with ellipsis (AI lazy block)",
    r"pass\s+#\s+TODO:.*AI": "AI-generated placeholder comment",
    r"hallucinate": "Self-referential hallucination keyword",
    r"Sure! Here is": "AI conversational prefix in comments",
}

def calculate_slop_score(matches):
    """Calculates a slop score from 1 to 10 based on findings."""
    if not matches:
        return 1
    # Weight findings: more matches = higher score
    score = min(1 + len(matches) * 2, 10)
    return score

def lint_content(content):
    """Checks content against slop signatures."""
    results = []
    lines = content.splitlines()
    for i, line in enumerate(lines):
        for pattern, reason in SLOP_SIGNATURES.items():
            if re.search(pattern, line, re.IGNORECASE):
                results.append({
                    "line": i + 1,
                    "reason": reason,
                    "content": line.strip()
                })
    return results

def perform_deep_pass(content):
    """Optional deeper pass using OpenAI if key is available."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a code auditor. Identify if the following code contains hallucinations or AI slop. Reply only with 'SLOP' or 'CLEAN' and a 1-sentence reason."},
                {"role": "user", "content": content[:2000]} # Limit context
            ]
        )
        return response.choices[0].message.content
    except ImportError:
        return "OpenAI library not installed for deep pass."
    except Exception as e:
        return f"Deep pass failed: {str(e)}"

def print_report(filename, results, deep_result=None):
    score = calculate_slop_score(results)
    print(f"\n{BLUE}Target:{RESET} {filename}")
    
    if not results:
        print(f"{GREEN}✔ No obvious slop detected.{RESET}")
    else:
        for r in results:
            print(f"  {RED}Line {r['line']}:{RESET} {r['reason']}")
            print(f"    {YELLOW}↳ {r['content']}{RESET}")
    
    if deep_result:
        print(f"  {BLUE}Deep Pass Analysis:{RESET} {deep_result}")

    color = GREEN if score < 4 else (YELLOW if score < 7 else RED)
    print(f"{color}Slop Score: {score}/10{RESET}")
    return score

def main():
    parser = argparse.ArgumentParser(description="garbage-fantasy: The AI slop linter.")
    parser.add_argument("path", nargs="?", help="File path or glob pattern")
    parser.add_argument("--diff", action="store_true", help="Lint from git diff stdin")
    args = parser.parse_args()

    max_score = 0

    if args.diff or not sys.stdin.isatty():
        # Process from stdin
        content = sys.stdin.read()
        results = lint_content(content)
        deep = perform_deep_pass(content)
        max_score = print_report("stdin/diff", results, deep)
    elif args.path:
        files = glob.glob(args.path, recursive=True)
        if not files:
            print(f"{RED}No files found matching path/pattern.{RESET}")
            sys.exit(0)
            
        for f in files:
            if os.path.isfile(f):
                with open(f, "r", encoding="utf-8", errors="ignore") as file:
                    content = file.read()
                    results = lint_content(content)
                    deep = perform_deep_pass(content)
                    max_score = max(max_score, print_report(f, results, deep))
    else:
        parser.print_help()
        sys.exit(0)

    if max_score >= 8:
        print(f"\n{RED}CRITICAL SLOP DETECTED. Blocking execution/merge.{RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()
