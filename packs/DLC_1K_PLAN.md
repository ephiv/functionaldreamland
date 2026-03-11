## The Professional Pack List

1. **DLC 1000: λ-Calculus & Functional Primitives**
2. **DLC 1100: Integer Sequence Cryptography**
3. **DLC 1200: Symbolic Rewrite Systems**
4. **DLC 1300: Binary Logic & Bitstream Operations**
5. **DLC 1400: Spatial Automata & Grid Dynamics**
6. **DLC 1500: Persistent Functional Data Structures**
7. **DLC 1600: Syntactic Analysis & Lexical Parsing**
8. **DLC 1700: Discrete Combinatorial Optimization**
9. **DLC 1800: Homoiconic Code Transformation**
10. **DLC 1900: Historical Cipher Engineering**

---

## Phase 1: Architectural Roadmap

### Stage 1: Problem Taxonomy (The "Sections")

Each pack is divided into **5 Sections**, with **10 Problems** per section. This provides a clear progression from "Convoluted" to "Nearly Impossible."

### Stage 2: Generator Synthesis

Developing the Python logic for the `generator` field in each `.json`. Since these tasks are esoteric, the generators will often require a "reference implementation" in Python to ensure the Clojure output is mathematically exact.

### Stage 3: Expansion & Completion

Drafting the Markdown descriptions for each problem. We will avoid "tutorial" language. The descriptions will read like technical requirements: *“Given State A and Rule B, produce Result C.”*

### Stage 4: Validation & Packaging

Compiling the JSON structures and gzip-compressing them for the `packs/dlc/` directory.

---

## Phase 2: Pack Content Breakdowns (The Gists)

### DLC 1000: λ-Calculus & Functional Primitives

* **S1: Church Encoding (10 levels):** Define $0$ through $9$ as functions. Successor logic.
* **S2: Boolean Combinators (10 levels):** Logic gates (AND, OR, NOT, XOR) using only functions.
* **S3: Arithmetic Primitives (10 levels):** Church Addition, Multiplication, and the "Cursed" Predecessor function.
* **S4: Fixed-Point Theory (10 levels):** Implementing the Y and Z combinators for recursion without named functions.
* **S5: SKI System (10 levels):** Reducing complex expressions into pure S, K, and I combinator strings.

### DLC 1100: Integer Sequence Cryptography

* **S1: Recurrence Constants (10 levels):** Calculating $n$-th terms of sequences defined by linear recurrence relations.
* **S2: Self-Referential Sets (10 levels):** The Kolakoski sequence (base-2/3) and Gijswijt's Sequence.
* **S3: Morphic Sequences (10 levels):** Thue-Morse and Paper-folding sequence generation.
* **S4: Prime Gaps & Constellations (10 levels):** Finding specific configurations of prime numbers within $N$ ranges.
* **S5: Permutation Cycles (10 levels):** Implementing the Josephus problem variations and Derangement counts.

### DLC 1200: Symbolic Rewrite Systems

* **S1: Markov Chains (10 levels):** String substitution systems with priority-based rules.
* **S2: L-Systems (10 levels):** Fractal plant and curve generation (Koch, Dragon, Hilbert) as string outputs.
* **S3: Semi-Thue Systems (10 levels):** Transforming specific alphabets into terminal forms.
* **S4: Tag Systems (10 levels):** Simulating 2-tag and 3-tag systems to reach halting states.
* **S5: Brainfuck Interpretation (10 levels):** Step-by-step execution of BF code using Clojure state-maps.

### DLC 1300: Binary Logic & Bitstream Operations

* **S1: Arithmetic-Free Math (10 levels):** Addition, Subtraction, and Multiplication using only `bit-and`, `bit-shift`, etc.
* **S2: Cyclic Redundancy (10 levels):** CRC-8, CRC-16, and CRC-32 implementations.
* **S3: Shift Registers (10 levels):** Linear Feedback Shift Registers (LFSR) for pseudo-random bitstreams.
* **S4: Huffman Encoding (10 levels):** Generating prefix-free codes from frequency maps.
* **S5: Bitplane Manipulation (10 levels):** Treating integers as 2D bit-grids and performing rotations/reflections.

### DLC 1400: Spatial Automata & Grid Dynamics

* **S1: Elementary Wolfram Rules (10 levels):** Simulating 1D rules (Rule 30, 90, 110) over $N$ generations.
* **S2: Totalistic 2D Rules (10 levels):** Life-like variations on Moore and von Neumann neighborhoods.
* **S3: Non-Standard Tesselations (10 levels):** Automata on hexagonal and triangular grids.
* **S4: Multi-State Machines (10 levels):** Wireworld (Electronics simulation) and Brian's Brain.
* **S5: Turing-Complete Patterns (10 levels):** Finding stable "oscillators" or "gliders" in specific rule-sets.

### DLC 1500: Persistent Functional Data Structures

* **S1: Immutable Lists (10 levels):** Manual implementation of linked lists without native Clojure collections.
* **S2: Difference Lists (10 levels):** Constant-time concatenation structures.
* **S3: Functional Trees (10 levels):** Red-Black trees and AVL trees with persistent updates.
* **S4: Tree Zippers (10 levels):** Implementing a "focus" for navigating and editing nested structures.
* **S5: Finger Trees (10 levels):** Implementing a general-purpose sequence representation.

### DLC 1600: Syntactic Analysis & Lexical Parsing

* **S1: Tokenization Engines (10 levels):** Splitting "Cursed" strings into typed tokens.
* **S2: RPN Evaluators (10 levels):** Handling Reverse Polish Notation with complex unary/binary operators.
* **S3: Recursive Descent (10 levels):** Parsing nested S-expressions with custom delimiters.
* **S4: Shunting-Yard Logic (10 levels):** Converting infix to postfix under varying precedence rules.
* **S5: Monadic Parser Combinators (10 levels):** Building a small JSON or CSV parser from scratch.

### DLC 1700: Discrete Combinatorial Optimization

* **S1: Integer Partitions (10 levels):** Counting and listing ways to sum to $N$ with specific subsets.
* **S2: Set Cover Problems (10 levels):** Finding minimal sub-collections to cover a universe of elements.
* **S3: Latin Square Generation (10 levels):** Constructing and validating orthogonal squares.
* **S4: Permutation Groups (10 levels):** Calculating group orbits and stabilizers.
* **S5: Constraint Satisfaction (10 levels):** Solving "N-Queens" and "Sudoku" variants functionally.

### DLC 1800: Homoiconic Code Transformation

* **S1: S-Expression Inversion (10 levels):** Recursively reversing code structures while maintaining validity.
* **S2: Macro-Expansion Emulation (10 levels):** Manually performing the steps of a macro expansion.
* **S3: Form Flattening (10 levels):** Taking nested `let` blocks and flattening them into a single scope.
* **S4: Symbolic Differentiation (10 levels):** Transforming Clojure math expressions into their derivatives.
* **S5: Code Obfuscators (10 levels):** Rewriting simple functions into "Golfed" or obfuscated S-expressions.

### DLC 1900: Historical Cipher Engineering

* **S1: Monoalphabetic Shifting (10 levels):** Advanced Caesar and Atbash variants.
* **S2: Polyalphabetic Systems (10 levels):** Vigenère and Beaufort ciphers with dynamic keys.
* **S3: Fractionating Ciphers (10 levels):** The Bifid and Trifid ciphers.
* **S4: Rotor Logic (10 levels):** Simulating a 3-rotor Enigma machine with reflector and plugboard.
* **S5: Public Key Primitives (10 levels):** Implementing RSA-style modular exponentiation and prime generation.