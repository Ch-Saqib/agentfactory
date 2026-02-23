---
sidebar_position: 5
title: "Pyright -- Your Type Safety Net"
description: "Run pyright to catch type errors before your code runs, compare typed vs untyped Python functions, and understand why strict mode requires complete type annotations"
keywords: ["pyright", "static type checker", "type annotations", "strict mode", "type error", "type safety", "Python types", "uv run pyright", "str | None", "type checking"]
chapter: 14.1
lesson: 5
duration_minutes: 22

# HIDDEN SKILLS METADATA
skills:
  - name: "Type Error Interpretation"
    proficiency_level: "A2"
    category: "Technical"
    bloom_level: "Apply"
    digcomp_area: "Problem Solving"
    measurable_at_this_level: "Student can run uv run pyright, read the error output, identify which line and parameter caused the error, and explain what type mismatch pyright detected"

  - name: "Type Annotation Reading"
    proficiency_level: "A1"
    category: "Conceptual"
    bloom_level: "Understand"
    digcomp_area: "Computational Thinking"
    measurable_at_this_level: "Student can read a typed function signature like def greet(name: str) -> str and explain what each annotation means, including union types like str | None"

learning_objectives:
  - objective: "Run pyright and interpret type error messages to identify the source of a type mismatch"
    proficiency_level: "A2"
    bloom_level: "Apply"
    assessment_method: "Student runs uv run pyright on a file with deliberate type errors, reads the output, and identifies which line, parameter, and type mismatch caused each error"

  - objective: "Compare typed and untyped function signatures and explain what type annotations add"
    proficiency_level: "A2"
    bloom_level: "Understand"
    assessment_method: "Given before/after code examples, student explains which version pyright can check and why the typed version catches bugs that the untyped version misses"

  - objective: "Explain why strict mode catches more errors than basic mode and why this course uses strict"
    proficiency_level: "A1"
    bloom_level: "Understand"
    assessment_method: "Student describes at least two categories of errors that strict mode catches but standard mode ignores, and explains why requiring complete annotations leads to safer code"

cognitive_load:
  new_concepts: 5
  assessment: "5 concepts (static type checker, type annotation, str | None union type, strict mode, type error message reading) within A2 limit of 7"

differentiation:
  extension_for_advanced: "Explore pyright's diagnostic rule list at github.com/microsoft/pyright and identify which of the 28 strict-mode rules apply to common Python patterns like decorators, generics, and match statements"
  remedial_for_struggling: "Focus on the single before/after example (greet function). Run pyright on just that one file until the error message format becomes familiar before examining strict vs standard differences"
---

# Pyright -- Your Type Safety Net

In Lesson 4, James ran ruff on his first Python function and discovered the difference between code that runs and code that is correct. Ruff caught style problems and potential bugs. But there is an entire category of errors that ruff cannot see -- errors where the code uses the wrong kind of data. A function expects a name, and someone passes it a number. A function returns a string, and someone tries to do math with the result. Python does not complain about any of this until the program is already running. By then, it might be 2 AM and 50,000 users are affected.

Emma gives James two files. Both contain the same function -- `greet` -- that takes a name and returns a greeting. The first file has no type information:

```python
def greet(name):
    return f"Hello, {name}"

result = greet(42)
print(result)
```

**Output:**

```
Hello, 42
```

Python runs it without complaint. The function received a number where a name should go, produced nonsense output, and nobody was notified. James shrugs. "It ran fine."

Emma opens the second file. Same function, but with type annotations:

```python
def greet(name: str) -> str:
    return f"Hello, {name}"

result = greet(42)
print(result)
```

She runs a single command: `uv run pyright`. The terminal shows:

**Output:**

```
/home/james/smartnotes/main.py
  /home/james/smartnotes/main.py:4:16 - error: Argument of type "int" is not
    assignable to parameter "name" of type "str"
    "int" is not assignable to "str" (reportArgumentType)
1 error, 0 warnings, 0 informations
```

The bug was caught without executing a single line of code. James reads the message: line 4, the argument `42` is an `int`, but the parameter `name` expects a `str`. The error name in parentheses -- `reportArgumentType` -- tells him exactly which rule flagged it.

"That," Emma says, "is why every function in this course has types."

---

## The Problem Without Type Checking

Python is a dynamically typed language. When you write `def greet(name):`, Python does not know or care what kind of data `name` will hold. It could be a string. It could be a number. It could be a list of dictionaries. Python figures it out at runtime -- when the code is already executing.

This flexibility is convenient for small scripts. It becomes dangerous in real projects:

| Scenario | What Happens Without Type Checking |
|----------|----------------------------------|
| Function receives wrong data type | Code runs, produces wrong output silently |
| Function returns unexpected type | Caller crashes later, far from the actual bug |
| Optional parameter is None | `AttributeError: 'NoneType' has no attribute 'lower'` at runtime |
| Refactoring changes a return type | Every caller breaks, but you only discover the breakage one caller at a time |

The common thread: bugs hide. They do not surface at the point where the mistake was made. They surface later, in a different file, during a different operation, often in production. James experienced this pattern with the deployment script in Chapter 14 -- a failure in one part of the system cascaded because nothing checked assumptions early.

A **static type checker** solves this by analyzing code *without running it*. It reads type annotations, traces data flow through functions, and reports every place where the declared types do not match the actual usage. Errors appear in your terminal seconds after you save the file -- not hours later in a crash report.

---

## Pyright Defined

> **Pyright** is a static type checker for Python, built by Microsoft. It reads type annotations in your code and verifies that every function call, variable assignment, and return value uses the correct data type -- all without running your program.

| Aspect | Detail |
|--------|--------|
| **Creator** | Microsoft |
| **Version** | 1.1.408 |
| **Speed** | Analyzes most projects in under a second |
| **Modes** | off, basic, standard (default), strict |
| **Configuration** | `[tool.pyright]` section in `pyproject.toml` |
| **Run command** | `uv run pyright` |

Pyright has four type checking modes, each progressively stricter:

| Mode | What It Checks | When to Use |
|------|---------------|-------------|
| `"off"` | Nothing (syntax errors only) | Never in this course |
| `"basic"` | Minimal rules | Legacy projects being gradually typed |
| `"standard"` | Moderate coverage (CLI default) | General-purpose development |
| `"strict"` | All rules enabled; requires complete type annotations | This course, new projects, AI-generated code |

You switch modes by changing one word in `pyproject.toml` — the command to run pyright is always the same (`uv run pyright`):

```toml
# off — pyright does almost nothing
typeCheckingMode = "off"

# basic — catches obvious mismatches only
typeCheckingMode = "basic"

# standard — the default if you don't set anything
typeCheckingMode = "standard"

# strict — checks everything, requires type labels on all code
typeCheckingMode = "strict"
```

Your SmartNotes `pyproject.toml` already has pyright configured in strict mode from Lesson 3:

```toml
[tool.pyright]
typeCheckingMode = "strict"
pythonVersion = "3.12"
```

Strict mode enables 28 additional rules beyond standard. The most important ones fall into three categories:

| Category | What Strict Mode Catches | Example |
|----------|------------------------|---------|
| **Missing annotations** | Functions without type hints on parameters or return values | `def greet(name):` -- parameter type unknown |
| **Unknown types** | Variables or expressions that resolve to an unknown type | `result = some_function()` where return type is not declared |
| **Unused code** | Imports, variables, functions, and classes that are never referenced | `import os` when `os` is never used in the file |

---

## From Axiom to Practice

In Axiom V from Chapter 14, you learned that types are guardrails -- not bureaucracy. They prevent your code from driving off a cliff by making the rules explicit. Pyright is the guardrail inspector. It walks along every function signature, every variable assignment, and every return value before your code runs and tells you which guardrails are missing.

This matters more in the AI era than it ever did before. When AI generates code, it generates fast. Dozens of functions in seconds. Without types, you have to read every function and mentally trace every data flow to verify correctness. With types, pyright does that verification for you. The type annotations serve double duty: they document what data each function expects (for humans and AI), and they enable automated verification (for pyright). One annotation, two benefits.

Consider the difference:

```python
# Without types: what does this function accept? What does it return?
# You have to read the implementation to find out.
def process(data):
    return data.strip().lower()
```

```python
# With types: the signature IS the documentation.
# Pyright verifies every caller passes a str and handles the str return.
def process(data: str) -> str:
    return data.strip().lower()
```

The typed version communicates intent at a glance: `process` takes a `str` and returns a `str`. Anyone reading this -- human or AI -- knows immediately what data to pass and what to expect back. And pyright will flag any caller that passes an `int`, a `list`, or `None` instead.

---

## Practical Application

### Step 1: Create a File with Type Errors

Open the SmartNotes `main.py` and replace its contents with the following code. This version has deliberate type problems that Python will run without complaint but pyright will catch:

```python
def greet(name: str) -> str:
    return f"Hello, {name}"


def add_numbers(a: int, b: int) -> int:
    return a + b


def format_title(title: str, prefix: str | None = None) -> str:
    if prefix:
        return f"{prefix}: {title}"
    return title


# Bug 1: passing an int where str is expected
greeting = greet(42)

# Bug 2: passing a str where int is expected
total = add_numbers("five", 10)

# Bug 3: using the result as wrong type
length: int = format_title("My Note")
```

The function definitions at the top are correct -- they have proper type annotations. The bugs are in the *calls* at the bottom, where the wrong types are passed or assigned.

Note the `str | None` annotation on the `prefix` parameter in `format_title`. This is a **union type** -- it means the parameter accepts either a `str` or `None`. The `| None` part makes the parameter explicitly optional. Without it, passing `None` would be a type error.

### Step 2: Run Pyright

Run pyright on the project:

```bash
uv run pyright
```

**Output:**

```
/home/james/smartnotes/main.py
  /home/james/smartnotes/main.py:16:21 - error: Argument of type "int" is not
    assignable to parameter "name" of type "str"
    "int" is not assignable to "str" (reportArgumentType)
  /home/james/smartnotes/main.py:19:26 - error: Argument of type "str" is not
    assignable to parameter "a" of type "int"
    "str" is not assignable to "int" (reportArgumentType)
  /home/james/smartnotes/main.py:22:15 - error: Type "str" is not assignable
    to declared type "int" (reportAssignmentType)
3 errors, 0 warnings, 0 informations
```

### Step 3: Read the Error Output

Every pyright error follows the same format:

```
[file path]:[line]:[column] - error: [description] ([rule name])
```

Break down the three errors:

| Error | Line | What Pyright Found | Rule |
|-------|------|-------------------|------|
| 1 | 16 | `42` (int) passed to `name` (str) | `reportArgumentType` |
| 2 | 19 | `"five"` (str) passed to `a` (int) | `reportArgumentType` |
| 3 | 22 | `format_title` returns str, assigned to `length: int` | `reportAssignmentType` |

Each error points to the exact line, the exact mismatch, and the exact rule that caught it. No guessing. No digging through stack traces. The errors appear before the code runs.

### Step 4: Fix the Type Errors

Replace the buggy calls with corrected versions:

```python
def greet(name: str) -> str:
    return f"Hello, {name}"


def add_numbers(a: int, b: int) -> int:
    return a + b


def format_title(title: str, prefix: str | None = None) -> str:
    if prefix:
        return f"{prefix}: {title}"
    return title


# Fixed: passing str where str is expected
greeting = greet("James")

# Fixed: passing int where int is expected
total = add_numbers(5, 10)

# Fixed: result is str, so variable should be str
title: str = format_title("My Note")
```

Run pyright again:

```bash
uv run pyright
```

**Output:**

```
0 errors, 0 warnings, 0 informations
```

Clean. Every type annotation matches. Every function call passes the right data. Every assignment stores the right type. Pyright verified all of this in under a second, without executing the code.

### Strict Mode vs Standard Mode

Your SmartNotes project uses `typeCheckingMode = "strict"`. What would happen with standard mode instead?

In standard mode, pyright would still catch the three explicit type errors above (passing `int` to `str`, etc.) -- those are basic mismatches. But standard mode would NOT catch functions that are missing annotations entirely.

Consider this code:

```python
# Standard mode: no error (annotations not required)
# Strict mode: error -- reportUnknownParameterType
def process(data):
    return data.strip()
```

In standard mode, pyright ignores this function because it has no type annotations to check. In strict mode, pyright reports an error: the parameter `data` has an unknown type. Strict mode requires you to declare your intent for every function. This is why the course uses strict -- it ensures complete coverage, leaving no function unchecked.

---

## Anti-Patterns

James now understands what pyright catches and why the course runs in strict mode. Here are the patterns Emma warned him to avoid:

| Anti-Pattern | What Happens | The Fix |
|-------------|-------------|---------|
| **Ignoring type errors** | You run pyright, see 12 errors, and skip them because "the code works." The errors accumulate. Eventually a type mismatch causes a production crash. | Fix every error before committing. Pyright errors are not suggestions -- they are guardrails reporting missing protection. |
| **Using `Any` everywhere** | You annotate parameters as `Any` to silence pyright. Every function accepts everything, which means pyright checks nothing. | Use the most specific type possible. `str`, `int`, `list[str]`. Reserve `Any` for genuinely dynamic cases (rare in application code). |
| **Disabling strict mode** | You switch to basic or standard mode because strict "has too many errors." Those errors represent real coverage gaps. | Start with strict mode on a new project (like SmartNotes). Fix errors as you write. Strict mode is harder to retrofit than to start with. |
| **Types as afterthought** | You write all functions without types, then add annotations later as a chore. The annotations become inaccurate because they describe what you intended, not what the code does. | Add types as you write each function. The annotation is part of the function's design, not a comment added later. |

---

## Try With AI

### Prompt 1: Explain a Pyright Error Message

```
I ran uv run pyright on my Python file and got this error:

/home/james/smartnotes/main.py:19:26 - error: Argument of type "str" is not
  assignable to parameter "a" of type "int"
  "str" is not assignable to "int" (reportArgumentType)

Explain this error to me step by step:
1. What file and line is the error on?
2. What did I write that caused the error?
3. What type did pyright expect?
4. What type did I actually pass?
5. What is "reportArgumentType" -- what category of error is this?
6. How would I fix this error?
```

**What you're learning:** How to read pyright error messages systematically. Every pyright error follows the same format -- file, line, column, description, rule name. By asking AI to break down a real error, you are building the pattern recognition to read these messages independently. This is the most practical type-checking skill: not writing types, but reading what pyright tells you when types are wrong.

### Prompt 2: Add Type Annotations to Untyped Code

```
Here is a Python function without type annotations:

def calculate_total(items, tax_rate, discount):
    subtotal = sum(item["price"] * item["quantity"] for item in items)
    tax = subtotal * tax_rate
    discounted = subtotal - discount
    return discounted + tax

The function is called like this:
items = [{"price": 9.99, "quantity": 2}, {"price": 4.50, "quantity": 1}]
result = calculate_total(items, 0.08, 5.00)

Add complete type annotations to this function so it would pass
pyright in strict mode. Explain each annotation you add and why
you chose that type.
```

**What you're learning:** How type annotations describe data flow through a function. By seeing AI add annotations to real code, you learn to read what each annotation means: `items: list[dict[str, float]]` tells you the function expects a list of dictionaries with string keys and float values. You are not writing these annotations yourself yet -- you are learning to read and understand them, which is the foundation for every typed Python chapter ahead.

### Prompt 3: Compare Strict Mode vs Standard Mode

```
I am configuring pyright for a new Python project. My pyproject.toml has:

[tool.pyright]
typeCheckingMode = "strict"
pythonVersion = "3.12"

My teammate wants to change it to "standard" because strict mode
shows too many errors. Explain:

1. What specific categories of errors does strict mode catch that
   standard mode ignores?
2. Give me 3 concrete code examples where strict catches a real bug
   but standard lets it pass silently.
3. Why is strict mode easier to start with on a new project than to
   add later to an existing one?
4. Is there ever a good reason to use standard instead of strict?
```

**What you're learning:** The engineering trade-off between strictness and convenience. Strict mode requires more annotations but catches more bugs. Standard mode is easier in the short term but leaves gaps. By asking AI to show concrete examples of what strict catches, you build an informed opinion about why this course requires strict mode -- not because it is a rule, but because you understand what you would miss without it.

---

## Key Takeaways

1. **A static type checker analyzes code without running it.** Pyright reads type annotations, traces data flow, and reports every type mismatch before your program executes.

2. **Type annotations serve double duty.** They document what data each function expects (for humans and AI to read) and they enable automated verification (for pyright to check). One annotation, two benefits.

3. **Every pyright error follows the same format:** file path, line number, column, description, and rule name in parentheses. Learning to read this format is the key skill.

4. **Strict mode requires complete type annotations.** It enables 28 additional rules beyond standard mode, catching missing annotations, unknown types, and unused code. New projects should start in strict mode.

5. **`str | None` is a union type.** It means a parameter or variable can hold either a `str` or `None`. This pattern appears throughout typed Python to make optional values explicit.

---

## Looking Ahead

Your SmartNotes project now has two verification tools running clean: ruff checks code quality and pyright checks type safety. But there is a third question neither tool can answer: does the code do what it is supposed to do? Code can be perfectly formatted, fully typed, and still produce the wrong result.

In Lesson 6, James writes his first test, initializes Git, and runs the complete verification pipeline -- ruff, pyright, pytest -- in one command chain. The workbench will be complete.
