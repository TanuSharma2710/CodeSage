"""
AI Service for code analysis and debugging using Groq LLM.
Uses Groq API for real AI-powered code analysis.
"""
from typing import Dict, List
import httpx
import json
import re
from config import settings


GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


async def analyze_code(code: str, error_message: str, language: str = "python", expected_output: str = None) -> Dict:
    """
    Analyze code using Groq LLM and return diagnosis, fixes, and study topics.
    Works for any programming language.
    """
    
    if not settings.groq_api_key:
        return get_fallback_response(code, error_message, language)
    
    try:
        result = await call_groq_api(code, error_message, language, expected_output)
        return result
    except Exception as e:
        print(f"Groq API error: {e}")
        return get_fallback_response(code, error_message, language)


async def call_groq_api(code: str, error_message: str, language: str, expected_output: str = None) -> Dict:
    """
    Call Groq API to analyze code and get fixes.
    """
    # Build expected output section if provided
    expected_output_section = ""
    if expected_output and expected_output.strip():
        expected_output_section = f"""

## EXPECTED VS ACTUAL OUTPUT (LOGICAL ERROR DETECTION):
The user expected different output than what they received. This indicates a LOGICAL error.
```
{expected_output}
```
IMPORTANT: When comparing expected vs actual output, classify the root cause as "logical" error type.
"""

    prompt = f"""You are an expert {language} debugger. Analyze this code that has errors and fix ALL problems.

## CODE WITH ERRORS:
```{language}
{code}
```

## ERROR MESSAGE FROM COMPILER/INTERPRETER:
```
{error_message}
```
{expected_output_section}
## YOUR TASK:
1. Find ALL errors in the code (not just the one mentioned in error message)
2. Fix EVERY error you find
3. Classify EACH error by its type (syntax, type, runtime, import, logical, other)
4. Return the COMPLETE corrected code

## RESPOND WITH THIS EXACT JSON FORMAT (no markdown, no extra text):
{{
    "diagnosis": "Clear explanation of what was wrong with the code in simple terms",
    "mistakes": [
        "First mistake: describe what was wrong",
        "Second mistake: describe what was wrong (if any)"
    ],
    "fixes": [
        {{
            "line_number": 3,
            "original": "the exact original wrong line of code",
            "fixed": "the corrected line of code",
            "explanation": "what was fixed",
            "error_type": "syntax or type or runtime or import or logical or other"
        }}
    ],
    "fixed_code": "PASTE THE COMPLETE FIXED CODE HERE - THE ENTIRE WORKING PROGRAM",
    "changed_lines": [3, 5, 7],
    "study_topics": ["Topic 1 to learn", "Topic 2 to learn"],
    "error_type": "the MOST COMMON error type among all fixes (syntax/type/runtime/import/logical/other)",
    "error_name": "Short 5-10 word summary like 'Multiple syntax and type errors'"
}}

## CRITICAL INSTRUCTIONS:
- "fixes" MUST contain each line that was changed, with the EXACT original code and fixed code
- EACH FIX MUST have its own "error_type" field classifying that specific error:
  * "syntax" = missing semicolons, colons, brackets, incorrect syntax structure
  * "type" = type mismatches like assigning string to int, wrong parameter types
  * "runtime" = NameError, IndexError, KeyError, ValueError, AttributeError, ZeroDivisionError
  * "import" = ImportError, ModuleNotFoundError
  * "logical" = logic bugs, wrong conditions, infinite loops, wrong output results
  * "other" = anything else
- If EXPECTED OUTPUT was provided and the code produces wrong results, the issue is LOGICAL
- "fixed_code" MUST contain the COMPLETE working program, not just changed parts
- "changed_lines" MUST list ONLY the line numbers you actually modified (as integers)
- The top-level "error_type" should be the most common type among all your fixes
- Fix ALL errors, even ones not mentioned in the error message
- Make sure the fixed code will actually compile and run correctly"""

    headers = {
        "Authorization": f"Bearer {settings.groq_api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.3-70b-versatile",  # Correct Groq model
        "messages": [
            {
                "role": "system", 
                "content": f"You are an expert {language} debugger. Always respond with valid JSON only. Find and fix ALL errors in the code, not just the first one. Return complete working code."
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 4096
    }
    
    async with httpx.AsyncClient(timeout=90.0) as client:
        response = await client.post(GROQ_API_URL, headers=headers, json=payload)
        
        if response.status_code != 200:
            print(f"Groq API Error: {response.status_code} - {response.text}")
            raise Exception(f"Groq API returned {response.status_code}")
        
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        
        print(f"Groq response received: {len(content)} chars")
        
        result = parse_ai_response(content, code, error_message, language)
        return result


def parse_ai_response(content: str, original_code: str, error_message: str, language: str) -> Dict:
    """Parse the AI response and extract structured data."""
    
    try:
        # Clean up content - remove markdown code blocks if present
        content = content.strip()
        
        # Remove ```json and ``` wrappers
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        # Try to parse JSON
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            # Try to find JSON object in the response
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                data = json.loads(json_match.group())
            else:
                raise ValueError("No valid JSON found in response")
        
        # Extract fields
        fixed_code = data.get("fixed_code", "")
        changed_lines = data.get("changed_lines", [])
        fixes = data.get("fixes", [])
        
        # Ensure changed_lines is a list of integers
        if isinstance(changed_lines, list):
            changed_lines = [int(x) for x in changed_lines if str(x).isdigit()]
        else:
            changed_lines = []
        
        # Ensure fixes is a list
        if not isinstance(fixes, list):
            fixes = []
        
        # Validate fixed_code - it should be different from original if there were errors
        if not fixed_code or len(fixed_code.strip()) < 10:
            fixed_code = original_code  # Fallback to original
        
        # Clean up fixed_code if it has markdown code blocks
        if fixed_code.startswith("```"):
            lines = fixed_code.split('\n')
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            fixed_code = '\n'.join(lines)
        
        # If AI didn't return fixes but we have changed_lines, generate fixes by comparing code
        if len(fixes) == 0 and len(changed_lines) > 0:
            original_lines = original_code.split('\n')
            fixed_lines = fixed_code.split('\n')
            
            for line_num in changed_lines:
                idx = line_num - 1  # Convert to 0-indexed
                original_line = original_lines[idx] if idx < len(original_lines) else ""
                fixed_line = fixed_lines[idx] if idx < len(fixed_lines) else ""
                
                fixes.append({
                    "line_number": line_num,
                    "original": original_line,
                    "fixed": fixed_line,
                    "explanation": f"Line {line_num} was corrected"
                })
        
        return {
            "diagnosis": data.get("diagnosis", "Errors found and fixed."),
            "mistakes": data.get("mistakes", ["Error corrected"]),
            "fixes": fixes,
            "fixed_code": fixed_code,
            "changed_lines": changed_lines,
            "study_topics": data.get("study_topics", ["Debugging", "Error Handling", "Code Review"]),
            "error_type": data.get("error_type", "unknown"),
            "error_name": data.get("error_name", data.get("error_type", "Unknown Error"))
        }
        
    except Exception as e:
        print(f"Parse error: {e}")
        print(f"Content was: {content[:500]}...")
        return get_fallback_response(original_code, error_message, language)


def get_fallback_response(code: str, error_message: str, language: str) -> Dict:
    """Fallback when API fails - return original code with helpful message."""
    
    error_type = extract_error_type(error_message)
    
    # Don't attempt to "fix" code if we can't use AI - just return original
    # with a message explaining the issue
    diagnosis = f"""⚠️ **AI Analysis Unavailable**

The AI service could not analyze your {language} code at this time.

**Error detected:** {error_type}
**Error message:** {error_message[:300]}

**Possible reasons:**
- API key not configured or invalid
- Service temporarily unavailable  
- Rate limit exceeded

Please try again or check your GROQ_API_KEY in the .env file."""
    
    return {
        "diagnosis": diagnosis,
        "mistakes": [f"Unable to auto-fix - {error_type} in your {language} code"],
        "fixes": [],
        "fixed_code": code,  # Return original code, not garbage
        "changed_lines": [],  # No lines changed
        "study_topics": [f"{language} Debugging", f"Understanding {error_type}", "Reading Error Messages"],
        "error_type": error_type.lower().replace("error", "") or "unknown",
        "error_name": f"{error_type} - See error message for details"
    }


def extract_error_type(error_message: str) -> str:
    """Extract error type from message."""
    common_errors = [
        "SyntaxError", "IndentationError", "NameError", "TypeError",
        "ValueError", "IndexError", "KeyError", "AttributeError",
        "ImportError", "ModuleNotFoundError", "ZeroDivisionError",
        "NullPointerException", "ArrayIndexOutOfBoundsException",
        "ClassNotFoundException", "NoSuchMethodError"
    ]
    
    for err in common_errors:
        if err.lower() in error_message.lower():
            return err
    
    # Check for generic error patterns
    if "error:" in error_message.lower():
        return "CompilationError"
    if "exception" in error_message.lower():
        return "RuntimeException"
        
    return "Error"


def attempt_basic_fix(code: str, error_message: str, language: str) -> tuple:
    """Attempt basic fix and return (fixed_code, changed_lines)."""
    
    lines = code.split('\n')
    fixed_lines = lines.copy()
    changed = []
    
    # Extract all line numbers mentioned in error
    line_matches = re.findall(r':(\d+):', error_message)
    error_lines = [int(m) - 1 for m in line_matches]
    
    # Also try other patterns
    line_matches2 = re.findall(r'line\s+(\d+)', error_message.lower())
    error_lines.extend([int(m) - 1 for m in line_matches2])
    
    # Remove duplicates
    error_lines = list(set(error_lines))
    
    # Fix missing semicolons in C-family languages
    if language.lower() in ['java', 'c', 'cpp', 'c++', 'csharp', 'c#', 'javascript', 'typescript']:
        if "';'" in error_message or "semicolon" in error_message.lower():
            for error_line in error_lines:
                if 0 <= error_line < len(fixed_lines):
                    line = fixed_lines[error_line].rstrip()
                    if not line.endswith((';', '{', '}', ':')):
                        fixed_lines[error_line] = line + ';'
                        changed.append(error_line + 1)
    
    # Fix missing colon in Python
    if language.lower() == 'python':
        if "':'" in error_message or "colon" in error_message.lower():
            for error_line in error_lines:
                if 0 <= error_line < len(fixed_lines):
                    line = fixed_lines[error_line].rstrip()
                    keywords = ['def ', 'class ', 'if ', 'else', 'elif ', 'for ', 'while ', 'try', 'except', 'finally', 'with ']
                    if any(kw in line for kw in keywords) and not line.endswith(':'):
                        fixed_lines[error_line] = line + ':'
                        changed.append(error_line + 1)
    
    return '\n'.join(fixed_lines), changed


async def generate_summary(transcript: str) -> Dict:
    """Generate a summary from a video transcript using Groq."""
    if not settings.groq_api_key:
        return {
            "title": "Video Summary",
            "topics": ["Core Concepts"],
            "summary": "Configure GROQ_API_KEY for AI summaries.",
            "key_points": ["Please configure API key"]
        }
    
    prompt = f"""Summarize this programming tutorial:

{transcript[:2000]}

Reply with ONLY JSON: {{"title": "...", "topics": ["..."], "summary": "...", "key_points": ["..."]}}"""

    headers = {
        "Authorization": f"Bearer {settings.groq_api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 1024
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(GROQ_API_URL, headers=headers, json=payload)
            content = response.json()["choices"][0]["message"]["content"]
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                return json.loads(json_match.group())
    except:
        pass
    
    return {"title": "Summary", "topics": [], "summary": "Error", "key_points": []}
