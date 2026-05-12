# garbage-fantasy: The AI slop linter.

Don't let an 'almost-right' hallucination make it to production. Lint your AI's intentions.

![Demo](demo.gif)

> "Only 33% of developers trust AI accuracy." — StackOverflow 2025.

## Why?
We've linted syntax for years. It's time to lint for **intent**. `garbage-fantasy` is your cheap, offline, first line of defense against the 'it compiles, but it's nonsense' bug that eats 66% of our debugging time.

## Usage
```bash
# Lint a single file
python garbage-fantasy.py my_changed_file.py

# Lint a directory or glob pattern
python garbage-fantasy.py "src/**/*.py"

# Lint a git diff (ideal for pre-commit hooks)
git diff main | python garbage-fantasy.py --diff
```

## Features
- **Slop Signatures**: Catches common AI "signatures" (hallucinated libraries, lazy placeholders like `[INSERT CODE HERE]`, and boilerplate conversational fillers).
- **Slop Score**: A 1-10 rating of how likely the code is AI-generated "slop".
- **Deep Pass**: Optional secondary analysis using LLMs if `OPENAI_API_KEY` is provided.
- **CI Ready**: Exits with code 1 on high-confidence slop, perfect for GitHub Actions.

## License
MIT
