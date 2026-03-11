# Functional Dreamland â€” Level Pack Format

Drop `.json` or `.json.gz` files into this directory (`packs/dlc/`) to add new levels.

Levels are sorted globally by their numeric `id`.  
**Use IDs â‰¥ 1000 for DLC to avoid conflicting with the base campaign.**  
A DLC pack with a duplicate ID will *override* the base-pack definition â€” useful for patches.

---

## Minimal Pack Structure

```json
{
  "pack_id":  "my_pack",
  "name":     "My Custom Level Pack",
  "version":  "1.0.0",
  "author":   "Your Name",
  "levels": [ ... ]
}
```

---

## Level Object

| Field           | Type   | Required | Description |
|-----------------|--------|----------|-------------|
| `id`            | int    | âœ…       | Unique level ID (â‰¥1000 for DLC) |
| `title`         | string | âœ…       | Display name |
| `difficulty`    | string | âœ…       | "Easy", "Medium", "Hard", etc. |
| `description`   | string | âœ…       | Problem statement (Markdown OK) |
| `starter_code`  | string | âœ…       | Initial Clojure code in the editor |
| `examples`      | array  | âœ…       | 2â€“4 visible test cases |
| `generator`     | object | âœ…       | How to produce hidden test cases |

---

## Generator Types

### 1. `builtin` â€” use a built-in procedural generator

Available names: `two_sum`, `valid_parens`, `longest_substr`

```json
"generator": {
  "type":  "builtin",
  "name":  "two_sum",
  "count": 200
}
```

### 2. `script` â€” embed a Python generator snippet

Define a `generate_case()` function that returns `{"args": "...", "expected": "..."}`.  
`args` must be a Clojure vector literal whose elements match your `solve` function's parameters.

```json
"generator": {
  "type":  "script",
  "count": 150,
  "code":  "import random\ndef generate_case():\n    n = random.randint(1, 100)\n    return {'args': f'[{n}]', 'expected': str(n * n)}\n"
}
```

### 3. `static` â€” hardcode all hidden cases in the file

Good for small or deterministic problem sets.

```json
"generator": {
  "type": "static",
  "cases": [
    {"args": "[1]", "expected": "1"},
    {"args": "[4]", "expected": "16"}
  ]
}
```

---

## Optional Validator (Per-Problem)

Some problems have multiple correct answers (e.g., Two Sum) or require custom
rules beyond a single expected value. You can provide a **per-problem validator**
that decides pass/fail using the input args, expected value, and the player's
actual output. This validator is **optional** and only affects the level it is
attached to.

Add a `validator` dictionary inside the level’s `generator`:

```json
"generator": {
  "type": "builtin",
  "name": "two_sum",
  "count": 200,
  "validator": {
    "code": "(defn validate [args expected actual]\n  (let [[nums target] args\n        idxs actual\n        ok? (and (vector? idxs)\n                 (= 2 (count idxs))\n                 (= target (+ (nth nums (first idxs)) (nth nums (second idxs)))))]\n    {:pass ok?}))"
  }
}
```

### Validator Contract

- Provide a Clojure function named `validate` with signature:
  `validate [args expected actual]`.
- Return **either**:
  - A boolean (`true` / `false`), or
  - A map: `{:pass true}` or `{:pass false :expected "..." :actual "..."}`.
- If `:expected` is omitted or `nil`, the failure output **will not display**
  an Expected line.

---
## Full Example (Square Number)

```json
{
  "pack_id": "extras",
  "name":    "Extra Practice",
  "version": "1.0.0",
  "author":  "A Modder",
  "levels": [
    {
      "id":          1001,
      "title":       "Square a Number",
      "difficulty":  "Easy",
      "description": "Given an integer `n`, return `n * n`.",
      "starter_code": "(ns solution)\n\n(defn solve [n]\n  ;; Your code here\n  )",
      "examples": [
        {"args": "[3]",  "expected": "9"},
        {"args": "[7]",  "expected": "49"},
        {"args": "[-2]", "expected": "4"}
      ],
      "generator": {
        "type":  "script",
        "count": 200,
        "code":  "import random\ndef generate_case():\n    n = random.randint(-1000, 1000)\n    return {'args': f'[{n}]', 'expected': str(n * n)}\n"
      }
    }
  ]
}
```

Save this as `packs/dlc/extras.json` (or gzip it as `extras.json.gz`).  
Then run `reload` in the game CLI, or restart the TUI, to pick it up.

---

## Compression (Optional but Recommended for Large Packs)

```python
import json, gzip
with gzip.open("packs/dlc/my_pack.json.gz", "wt", encoding="utf-8") as f:
    json.dump(pack_data, f, indent=2)
```

A 500-level JSON file (~200 KB) compresses to ~30 KB with gzip.

---

## Adding a New Built-in Generator (for contributors)

Register a function in `game.py`:

```python
@_register("my_generator")
def _gen_my_generator(count: int = 200, **kwargs) -> List[TestCase]:
    cases = []
    for _ in range(count):
        # build args and expected strings in Clojure literal syntax
        cases.append(TestCase(args="...", expected="..."))
    return cases
```

Then reference it as `"type": "builtin", "name": "my_generator"` in any pack.
