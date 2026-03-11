# Functional Dreamland

Functional Dreamland (or Programmer's Dreamland) is a terminal-based coding game where you solve algorithmic challenges (similar to LeetCode) using the functional programming language **Clojure**.

You code in your favorite modal editor (like nano), which is embedded directly into the game loop. When ready, the game's test runner evaluates your solution against examples and hundreds of hidden test cases.

## Requirements

- Python 3.10+
- The `textual` Python library
- `clojure` CLI tools installed on your system (the `clj` or `clojure` command must be available in your PATH)

## Installation

```bash
pip install -r requirements.txt
```

## How to Play

### TUI Mode (Recommended)

Start the Textual User Interface:

```bash
python tui_game.py
```

- **Code:** Write your Clojure solution directly in the built-in non-modal editor on the right pane.
- **Run:** Press `Ctrl+R` to test your code against the provided examples.
- **Submit:** Press `Ctrl+S` to run your solution against all hidden test cases (usually ~200 cases).
- **Next Level:** Press `Ctrl+N` to advance after solving.
- **Menu:** Press `Esc` to return to the Main Menu.

### CLI Mode

Alternatively, you can play in the raw command line:

```bash
python game.py
```

- Type `edit` to open your editor.
- Type `run` to test against examples.
- Type `submit` to test against all cases.
- Type `status` to read the current level description and see where your code file is located.
- Type `help` for a full list of commands.

## How it works

The game generates a dynamic Clojure runner script that loads your `solution.clj` code and uses `(apply f args)` to run the test cases. Test inputs and expected outputs are dynamically generated for each level to ensure variety and prevent hardcoding.
