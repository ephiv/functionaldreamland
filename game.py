import sys
import json
import gzip
import subprocess
import os
import textwrap
import tempfile
import random
from collections import OrderedDict
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Any, Callable, Tuple

class CommandError(ValueError):
    pass

@dataclass
class TestCase:
    args: str
    expected: str

@dataclass
class Level:
    id: int
    title: str
    difficulty: str
    description: str
    starter_code: str
    examples: List[TestCase]
    generator_spec: Dict[str, Any]

# ---------------------------------------------------------------------------
# Built-in hidden-test generators
# ---------------------------------------------------------------------------

_BUILTIN_GENERATORS: Dict[str, Callable[..., List[TestCase]]] = {}

def _register(name: str):
    def deco(fn):
        _BUILTIN_GENERATORS[name] = fn
        return fn
    return deco

@_register("two_sum")
def _gen_two_sum(count: int = 200, **_) -> List[TestCase]:
    cases = []
    for _ in range(count):
        length = random.randint(5, 20)
        nums = [random.randint(-100, 100) for _ in range(length)]
        i, j = random.sample(range(length), 2)
        if i > j:
            i, j = j, i
        target = nums[i] + nums[j]
        cases.append(TestCase(
            f"[[{' '.join(map(str, nums))}] {target}]",
            f"[{i} {j}]"
        ))
    return cases

@_register("valid_parens")
def _gen_valid_parens(count: int = 200, **_) -> List[TestCase]:
    def is_valid(s: str) -> bool:
        stack = []
        mapping = {")": "(", "}": "{", "]": "["}
        for ch in s:
            if ch in mapping:
                top = stack.pop() if stack else "#"
                if mapping[ch] != top:
                    return False
            else:
                stack.append(ch)
        return not stack

    def gen_parens(valid: bool) -> str:
        pairs = ["()", "[]", "{}"]
        if valid:
            res = ""
            for _ in range(random.randint(1, 10)):
                p = random.choice(pairs)
                pos = random.randint(0, len(res))
                res = res[:pos] + p + res[pos:]
            return res
        return "".join(random.choices("()[]{}", k=random.randint(2, 20)))

    cases = []
    for _ in range(count):
        s = gen_parens(random.choice([True, False]))
        cases.append(TestCase(f'["{s}"]', "true" if is_valid(s) else "false"))
    return cases

@_register("longest_substr")
def _gen_longest_substr(count: int = 200, **_) -> List[TestCase]:
    def ref(s: str) -> int:
        chars: Dict[str, int] = {}
        left = max_len = 0
        for right, ch in enumerate(s):
            if ch in chars:
                left = max(left, chars[ch] + 1)
            chars[ch] = right
            max_len = max(max_len, right - left + 1)
        return max_len

    cases = []
    for _ in range(count):
        s = "".join(random.choices("abcdefghijklmnopqrstuvwxyz",
                                   k=random.randint(0, 50)))
        cases.append(TestCase(f'["{s}"]', str(ref(s))))
    return cases

# ---------------------------------------------------------------------------
# Script / static generators
# ---------------------------------------------------------------------------

def _run_script_generator(code: str, count: int) -> List[TestCase]:
    ns: Dict[str, Any] = {}
    exec(compile(code, "<generator>", "exec"), ns)  # noqa: S102
    gen_fn = ns.get("generate_case")
    if not callable(gen_fn):
        raise ValueError("Script generator must define a generate_case() function.")
    return [TestCase(**gen_fn()) for _ in range(count)]

def _run_static_generator(cases_data: List[Dict[str, str]]) -> List[TestCase]:
    return [TestCase(c["args"], c["expected"]) for c in cases_data]

def generate_hidden(spec: Dict[str, Any]) -> List[TestCase]:
    gen_type = spec.get("type", "static")
    count    = int(spec.get("count", 200))
    if gen_type == "builtin":
        name = spec["name"]
        if name not in _BUILTIN_GENERATORS:
            raise ValueError(f"Unknown builtin generator: {name!r}. "
                             f"Available: {sorted(_BUILTIN_GENERATORS)}")
        return _BUILTIN_GENERATORS[name](count=count, **{
            k: v for k, v in spec.items() if k not in ("type", "name", "count")
        })
    if gen_type == "script":
        return _run_script_generator(spec["code"], count)
    if gen_type == "static":
        return _run_static_generator(spec.get("cases", []))
    raise ValueError(f"Unknown generator type: {gen_type!r}.")

# ---------------------------------------------------------------------------
# LevelLoader
# ---------------------------------------------------------------------------

class LevelLoader:
    """
    Scans packs/ and packs/dlc/ for *.json / *.json.gz files.
    Each raw level dict is annotated with _pack_id and _pack_name so the
    UI can group problems by their source pack (base vs. DLC tabs).
    """

    PACKS_DIR = Path("packs")
    DLC_DIR   = Path("packs") / "dlc"

    def __init__(self) -> None:
        self._index: List[Dict[str, Any]] = []
        self._id_to_pos: Dict[int, int]   = {}
        self._cache: Dict[int, Level]     = {}
        self._scan()

    # ------------------------------------------------------------------
    # Pack discovery
    # ------------------------------------------------------------------

    def _scan(self) -> None:
        pack_files: List[Path] = []
        for directory in (self.PACKS_DIR, self.DLC_DIR):
            if directory.exists():
                pack_files += sorted(directory.glob("*.json"))
                pack_files += sorted(directory.glob("*.json.gz"))

        seen: Dict[int, int] = {}
        for pf in pack_files:
            try:
                data = self._read_pack(pf)
            except Exception as exc:
                print(f"[warning] Could not load pack {pf.name}: {exc}")
                continue

            pack_id   = data.get("pack_id",  pf.stem.replace(".json", ""))
            pack_name = data.get("name",     pack_id)

            for raw in data.get("levels", []):
                raw = dict(raw)
                raw["_pack_id"]   = pack_id
                raw["_pack_name"] = pack_name
                lid = int(raw["id"])
                if lid in seen:
                    # DLC override: replace existing entry, bust cache
                    self._index[seen[lid]] = raw
                    self._cache.pop(lid, None)
                else:
                    seen[lid] = len(self._index)
                    self._index.append(raw)

        self._index.sort(key=lambda r: int(r["id"]))
        self._id_to_pos = {int(r["id"]): i for i, r in enumerate(self._index)}

    @staticmethod
    def _read_pack(path: Path) -> Dict[str, Any]:
        if path.suffix == ".gz":
            with gzip.open(path, "rt", encoding="utf-8") as fh:
                return json.load(fh)
        return json.loads(path.read_text(encoding="utf-8"))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self._index)

    def all_meta(self) -> List[Dict[str, Any]]:
        return list(self._index)

    def get_by_index(self, idx: int) -> Level:
        return self._hydrate(self._index[idx])

    def get_by_id(self, level_id: int) -> Level:
        pos = self._id_to_pos.get(level_id)
        if pos is None:
            raise KeyError(f"Level {level_id} not found in any pack.")
        return self._hydrate(self._index[pos])

    def get_hidden(self, level_id: int) -> List[TestCase]:
        pos = self._id_to_pos.get(level_id)
        if pos is None:
            raise KeyError(f"Level {level_id} not found.")
        spec = self._index[pos].get("generator", {"type": "static", "cases": []})
        return generate_hidden(spec)

    def packs_info(self) -> List[Dict[str, Any]]:
        """
        Return [{pack_id, pack_name, levels}] in campaign order.
        Levels within each pack are sorted by ascending id.
        """
        groups: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        for raw in self._index:          # already sorted by id
            pid = raw.get("_pack_id", "unknown")
            if pid not in groups:
                groups[pid] = {
                    "pack_id":   pid,
                    "pack_name": raw.get("_pack_name", pid),
                    "levels":    [],
                }
            groups[pid]["levels"].append(raw)
        return list(groups.values())

    def reload(self) -> None:
        self._index.clear()
        self._id_to_pos.clear()
        self._cache.clear()
        self._scan()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _hydrate(self, raw: Dict[str, Any]) -> Level:
        lid = int(raw["id"])
        if lid in self._cache:
            return self._cache[lid]
        level = Level(
            id=lid,
            title=raw["title"],
            difficulty=raw["difficulty"],
            description=raw["description"],
            starter_code=raw["starter_code"],
            examples=[TestCase(c["args"], c["expected"]) for c in raw.get("examples", [])],
            generator_spec=raw.get("generator", {"type": "static", "cases": []}),
        )
        self._cache[lid] = level
        return level


# ---------------------------------------------------------------------------
# Game
# ---------------------------------------------------------------------------

class Game:
    def __init__(self, save_file: str = ".dreamland_save.json") -> None:
        self.loader = LevelLoader()
        if len(self.loader) == 0:
            raise RuntimeError("No level packs found. Make sure packs/base.json.gz exists.")

        self.save_path    = Path(save_file)
        self.solved: set[int] = set()
        self.idx          = 0

        self.workspace_dir = Path("workspace")
        self.workspace_dir.mkdir(exist_ok=True)

        self._load()
        self._update_current_file()

        if not self.current_file.exists():
            self._reset_workspace()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def levels(self):
        """Compatibility shim â€” lets callers use len(game.levels)."""
        return _LevelCountProxy(len(self.loader))

    @property
    def level(self) -> Level:
        return self.loader.get_by_index(self.idx)

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _update_current_file(self) -> None:
        self.current_file = self.workspace_dir / f"solution_{self.level.id}.clj"

    def _load(self) -> None:
        if not self.save_path.exists():
            return
        try:
            data       = json.loads(self.save_path.read_text(encoding="utf-8"))
            self.solved = set(data.get("solved", []))
            saved_id   = int(data.get("selected", 1))
            saved_pack = data.get("selected_pack", "")

            # Prefer exact pack+id match; fall back to global id
            if saved_pack:
                for i, raw in enumerate(self.loader.all_meta()):
                    if raw.get("_pack_id", "") == saved_pack and int(raw["id"]) == saved_id:
                        self.idx = i
                        return
            try:
                self.idx = self.loader._id_to_pos[saved_id]
            except KeyError:
                self.idx = 0
        except Exception:
            pass

    def _save(self) -> None:
        current_meta = self.loader.all_meta()[self.idx]
        self.save_path.write_text(json.dumps({
            "solved":        list(self.solved),
            "selected":      self.level.id,
            "selected_pack": current_meta.get("_pack_id", ""),
        }, indent=2), encoding="utf-8")

    def _reset_workspace(self) -> None:
        self.current_file.write_text(self.level.starter_code, encoding="utf-8")

    # ------------------------------------------------------------------
    # Level selection â€” all levels freely accessible, no locking
    # ------------------------------------------------------------------

    def select(self, n: int) -> str:
        """Select the n-th level in campaign order (1-based). No locking."""
        total = len(self.loader)
        if not 1 <= n <= total:
            raise CommandError(f"Level out of range 1..{total}.")
        target_id = int(self.loader.all_meta()[n - 1]["id"])
        self.idx  = self.loader._id_to_pos[target_id]
        self._update_current_file()
        if not self.current_file.exists():
            self._reset_workspace()
        self._save()
        return f"Selected Level {n}: {self.level.title}"

    def select_by_pack(self, pack_id: str, level_id: int) -> str:
        """
        Select a level by its pack_id and numeric level id.
        Called by the TUI when a player clicks a problem in the Problem List.
        """
        for i, raw in enumerate(self.loader.all_meta()):
            if raw.get("_pack_id", "") == pack_id and int(raw["id"]) == level_id:
                self.idx = i
                self._update_current_file()
                if not self.current_file.exists():
                    self._reset_workspace()
                self._save()
                return f"â†’ [{pack_id}] {self.level.title}"
        raise CommandError(f"Level {level_id} not found in pack '{pack_id}'.")

    # ------------------------------------------------------------------
    # Test runner
    # ------------------------------------------------------------------

    def run_tests(self, mode: str = "examples") -> str:
        code  = self.current_file.read_text(encoding="utf-8")
        level = self.level

        cases = (level.examples if mode == "examples"
                 else level.examples + self.loader.get_hidden(level.id))
        validator_spec = {}
        if isinstance(level.generator_spec, dict):
            validator_spec = level.generator_spec.get("validator", {}) or {}
        validator_code = ""
        if isinstance(validator_spec, dict):
            validator_code = validator_spec.get("code", "") or ""

        cases_clj = "[\n"
        for c in cases:
            cases_clj += f"  {{:args {c.args} :expected {c.expected}}}\n"
        cases_clj += "]\n"

        validator_block = ""
        if validator_code:
            validator_block = f"""
(defn validate-case [args expected actual]
  (try
    (let [res (validate args expected actual)]
      (cond
        (map? res) res
        (boolean? res) {{:pass res}}
        :else {{:pass false :error "Validator must return boolean or map"}}))
    (catch Exception e
      {{:pass false :error (.getMessage e)}})))
"""

        runner_code = f"""
(try
  (load-file "solution.clj")
  (catch Exception e
    (println "COMPILE_ERROR")
    (println (.getMessage e))
    (System/exit 1)))

(require '[solution])

(def test-cases {cases_clj})

(defn default-eval [f test-case]
  (let [res (apply f (:args test-case))
        expected (:expected test-case)]
    {{:actual-res res :expected expected}}))

(def validator-enabled? {str(bool(validator_code)).lower()})

{validator_code}
{validator_block}

(defn run-case [f test-case]
  (try
    (let [start (System/nanoTime)
          eval-result (default-eval f test-case)
          res   (:actual-res eval-result)
          expected (:expected eval-result)
          end   (System/nanoTime)
          time-ms (/ (- end start) 1000000.0)
          args-str (pr-str (:args test-case))
          base-expected (pr-str expected)
          base-actual   (pr-str res)
          vres (when validator-enabled?
                 (validate-case (:args test-case) expected res))
          pass (if validator-enabled?
                 (:pass vres)
                 (= res expected))
          v-expected (when validator-enabled?
                       (:expected vres))
          v-actual   (when validator-enabled?
                       (:actual vres))
          out-expected (if (and validator-enabled? (nil? v-expected)) "" (or v-expected base-expected))
          out-actual   (or v-actual base-actual)]
      {{:pass pass
       :expected (str out-expected)
       :args     args-str
       :actual   (str out-actual)
       :time-ms  time-ms}})
    (catch Exception e
      {{:pass false
       :args     (pr-str (:args test-case))
       :expected (pr-str (:expected test-case))
       :error    (.getMessage e)}})))

(defn run-all []
  (let [results (mapv #(run-case solution/solve %) test-cases)
        passed  (count (filter :pass results))
        total   (count results)]
    (println "---RESULTS---")
    (println (str "PASSED:" passed))
    (println (str "TOTAL:"  total))
    (doseq [r results]
      (if (:pass r)
        (println (str "PASS|" (:time-ms r)))
        (if (:error r)
          (println (str "ERR|"  (:error r) "|" (:expected r) "|" (:args r)))
          (println (str "FAIL|" (:expected r) "|" (:actual r) "|" (:args r))))))))

(run-all)
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "solution.clj"), "w", encoding="utf-8") as fh:
                fh.write(code)
            with open(os.path.join(tmpdir, "runner.clj"), "w", encoding="utf-8") as fh:
                fh.write(runner_code)
            try:
                try:
                    proc = subprocess.run(
                        ["clojure", "-M", "runner.clj"],
                        cwd=tmpdir, capture_output=True, text=True, timeout=10
                    )
                except FileNotFoundError:
                    proc = subprocess.run(
                        ["clj", "-M", "runner.clj"],
                        cwd=tmpdir, capture_output=True, text=True, timeout=10
                    )
                stdout, stderr = proc.stdout, proc.stderr

                if "COMPILE_ERROR" in stdout:
                    return "Compilation Error:\n" + stdout.split("COMPILE_ERROR")[1].strip()

                if "---RESULTS---" in stdout:
                    lines  = stdout.split("---RESULTS---")[1].strip().split("\n")
                    passed = int(lines[0].split(":")[1])
                    total  = int(lines[1].split(":")[1])
                    out    = [f"Result: {passed}/{total} passed."]
                    for i, line in enumerate(lines[2:]):
                        if line.startswith("PASS|"):
                            continue
                        elif line.startswith("ERR|"):
                            _, err, expected, args = (line.split("|", 3) + ["", "", ""])[:4]
                            parts = [
                                f"Case {i+1} Error:",
                                f"  Input:    {args}",
                            ]
                            if expected:
                                parts.append(f"  Expected: {expected}")
                            parts.append(f"  Error:    {err}")
                            out.append("\n".join(parts))
                        elif line.startswith("FAIL|"):
                            _, expected, actual, args = (line.split("|", 3) + ["", "", ""])[:4]
                            parts = [
                                f"Case {i+1} Failed:",
                                f"  Input:    {args}",
                            ]
                            if expected:
                                parts.append(f"  Expected: {expected}")
                            parts.append(f"  Actual:   {actual}")
                            out.append("\n".join(parts))
                    if passed == total:
                        out.append("All tests passed! đŸ‰")
                        if mode == "submit":
                            self.solved.add(level.id)
                            self._save()
                    return "\n".join(out)

                return "Runtime Error:\n" + stderr + "\n" + stdout

            except subprocess.TimeoutExpired:
                return "Time Limit Exceeded (10s)"
            except FileNotFoundError:
                return "Error: Clojure CLI ('clojure') not found. Please install it."

    # ------------------------------------------------------------------
    # CLI command interpreter
    # ------------------------------------------------------------------

    def execute(self, raw: str) -> List[str]:
        t     = raw.strip()
        if not t:
            return []
        k     = t.lower()
        parts = t.split()   # preserve original case for pack_id

        if k == "help":
            return [(
                "Commands:\n"
                "  help | levels | status | edit | run | submit | reset | next | reload | quit\n"
                "  select <n>                  â€” nth level in campaign order (1-based)\n"
                "  select <pack_id> <level_id> â€” jump directly to a level in a specific pack"
            )]

        if k == "levels":
            out = [f"  {'':1}  {'':3}  {'ID':>4}  {'DIFF':<8}  TITLE  [pack]"]
            for i, meta in enumerate(self.loader.all_meta()):
                lid    = int(meta["id"])
                marker = "â–¶" if lid == self.level.id else " "
                solved = "x" if lid in self.solved else " "
                pid    = meta.get("_pack_id", "?")
                out.append(
                    f"  {marker} [{solved}]  {lid:04d}  {meta['difficulty']:<8}  {meta['title']}  [{pid}]"
                )
            return out

        if parts[0].lower() == "select":
            if len(parts) == 2:
                try:
                    return [self.select(int(parts[1]))]
                except ValueError:
                    raise CommandError("Usage: select <n>  or  select <pack_id> <level_id>")
            elif len(parts) == 3:
                try:
                    return [self.select_by_pack(parts[1], int(parts[2]))]
                except ValueError:
                    raise CommandError("level_id must be an integer")
            else:
                raise CommandError("Usage: select <n>  or  select <pack_id> <level_id>")

        if k == "status":
            lv   = self.level
            meta = self.loader.all_meta()[self.idx]
            pid  = meta.get("_pack_id", "?")
            out  = [
                "FUNCTIONAL DREAMLAND",
                f"[{pid}] #{lv.id} â€” Level {self.idx+1}/{len(self.loader)} | {lv.difficulty}",
                f"Title: {lv.title}",
                f"Description:\n{textwrap.indent(lv.description, '  ')}",
                f"File: {self.current_file.absolute()}",
                "edit | run | submit",
            ]
            return ["\n".join(out)]

        if k == "edit":
            editor = os.environ.get("EDITOR", "vim")
            subprocess.run([editor, str(self.current_file)])
            return ["Editor closed."]

        if k == "run":
            return [self.run_tests("examples")]

        if k == "submit":
            return [self.run_tests("submit")]

        if k == "reset":
            self._reset_workspace()
            return ["Workspace reset to starter code."]

        if k == "next":
            return [self.select(min(len(self.loader), self.idx + 2))]

        if k == "reload":
            self.loader.reload()
            return [f"Packs reloaded â€” {len(self.loader)} levels available."]

        if k in {"quit", "exit"}:
            return ["QUIT"]

        raise CommandError("Unknown command. Type `help`.")

    def run(self) -> None:
        print("FUNCTIONAL DREAMLAND â€” Clojure Problem Solving")
        print(self.execute("help")[0])
        while True:
            try:
                out = self.execute(input("dreamland> "))
                for line in out:
                    if line == "QUIT":
                        return
                    print(line)
            except (EOFError, KeyboardInterrupt):
                print("\nExiting.")
                return
            except Exception as exc:
                print(f"[error] {exc}")


# ---------------------------------------------------------------------------
# Shim
# ---------------------------------------------------------------------------

class _LevelCountProxy:
    def __init__(self, n: int) -> None:
        self._n = n
    def __len__(self) -> int:
        return self._n


if __name__ == "__main__":
    Game().run()






