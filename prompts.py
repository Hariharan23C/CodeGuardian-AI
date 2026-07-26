"""
prompts.py
Builds the prompt sent to Gemini. The whole "teach me at my level" feature
lives here: each level gets a different instruction for HOW to explain,
not just what to explain.
"""

LEVEL_INSTRUCTIONS = {
    "child": (
        "Explain like the reader has never coded before. Use a simple real-world "
        "analogy for every concept (e.g. compare a loop to washing each plate in a stack "
        "one at a time). Avoid jargon; if you must use a technical term, define it in "
        "plain words right after. Use short sentences."
    ),
    "beginner": (
        "Explain like the reader knows basic syntax (variables, loops, if/else) but is "
        "new to this specific pattern or concept. Define any non-obvious term the first "
        "time it appears. Include one small example for anything non-trivial."
    ),
    "intermediate": (
        "Explain like the reader is a CS student comfortable with data structures and "
        "basic algorithms. Focus on the *why* behind design choices, not basic syntax."
    ),
    "advanced": (
        "Explain like the reader is preparing for technical interviews. Be concise, "
        "focus on trade-offs, edge cases, and what a senior engineer would flag in review."
    ),
}

SYSTEM_INSTRUCTIONS = """You are CodeGuardian AI, a code-teaching assistant. You will be given a
block of code and a target explanation level. You must respond with ONLY a valid JSON object
(no markdown fences, no prose outside the JSON) matching exactly this shape:

{
  "language_detected": "string",
  "overall_summary": "1-3 sentence plain-language summary of what the code does",
  "line_by_line": [
    {"lines": "e.g. 1-2 or 5", "code": "the actual code snippet", "explanation": "what it does and why"}
  ],
  "complexity": {
    "time": "e.g. O(n log n)",
    "space": "e.g. O(n)",
    "explanation": "why, in plain terms"
  },
  "bugs": [
    {"issue": "description", "line": "line number or range", "severity": "low|medium|high", "fix": "how to fix it"}
  ],
  "suggestions": [
    "improvement suggestion as a string"
  ],
  "interview_questions": [
    {"question": "string", "hint": "a short hint, not the full answer"}
  ],
  "flowchart_mermaid": "a valid Mermaid.js flowchart definition (flowchart TD ...) representing the code's control flow"
}

Rules:
- "bugs" and "suggestions" can be empty arrays if the code is clean -- do not invent problems.
- Keep "flowchart_mermaid" syntactically valid Mermaid flowchart syntax, using short node labels.
- If the input is not recognizable code, set overall_summary to explain that and return empty arrays elsewhere.
- Never include text outside the single JSON object.
"""


def build_prompt(code, level):
    level = level if level in LEVEL_INSTRUCTIONS else "beginner"
    tone_instruction = LEVEL_INSTRUCTIONS[level]

    return f"""{SYSTEM_INSTRUCTIONS}

Target explanation level: {level}
Tone/depth instruction for this level: {tone_instruction}

Code to analyze:
```
{code}
```

Respond with the JSON object only."""
