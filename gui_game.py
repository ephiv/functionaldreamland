import re
import threading
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Dict, List, Tuple

from game import Game, CommandError


BG = "#0f131a"
PANEL = "#151b24"
PANEL_DARK = "#11161d"
TEXT = "#e6edf3"
TEXT_DIM = "#9aa4b2"
ACCENT = "#5cc8ff"
ACCENT_2 = "#7dd3a7"
WARN = "#f6b26b"
ERROR = "#ff6b6b"



INLINE_RE = re.compile(r"(`[^`]+`|\*\*[^*]+\*\*|__[^_]+__|\*[^*]+\*|_[^_]+_)")


class MarkdownRenderer:
    def __init__(self, text: tk.Text) -> None:
        self.text = text
        self._setup_tags()

    def _setup_tags(self) -> None:
        base = tkfont.Font(font=self.text.cget("font"))
        code = tkfont.Font(family="Consolas", size=base.cget("size"))
        bold = tkfont.Font(font=base)
        bold.configure(weight="bold")
        italic = tkfont.Font(font=base)
        italic.configure(slant="italic")

        h1 = tkfont.Font(font=base)
        h1.configure(size=base.cget("size") + 6, weight="bold")
        h2 = tkfont.Font(font=base)
        h2.configure(size=base.cget("size") + 4, weight="bold")
        h3 = tkfont.Font(font=base)
        h3.configure(size=base.cget("size") + 2, weight="bold")

        self.text.tag_configure("bold", font=bold)
        self.text.tag_configure("italic", font=italic)
        self.text.tag_configure("code", font=code, background=PANEL_DARK, foreground=ACCENT_2)
        self.text.tag_configure("codeblock", font=code, background=PANEL_DARK, foreground=TEXT)
        self.text.tag_configure("quote", foreground=TEXT_DIM, lmargin1=18, lmargin2=30)
        self.text.tag_configure("list", lmargin1=18, lmargin2=36)
        self.text.tag_configure("hr", foreground=TEXT_DIM)
        self.text.tag_configure("h1", font=h1, foreground=TEXT)
        self.text.tag_configure("h2", font=h2, foreground=TEXT)
        self.text.tag_configure("h3", font=h3, foreground=TEXT)
        self.text.tag_configure("h4", font=bold, foreground=TEXT)
        self.text.tag_configure("h5", font=bold, foreground=TEXT_DIM)
        self.text.tag_configure("h6", font=bold, foreground=TEXT_DIM)

    def render(self, markdown: str) -> List[Tuple[int, str, str]]:
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")

        headings: List[Tuple[int, str, str]] = []
        in_code = False

        for line in markdown.splitlines():
            if line.strip().startswith("```"):
                in_code = not in_code
                if not in_code:
                    self.text.insert("end", "\n")
                continue

            if in_code:
                self.text.insert("end", line + "\n", ("codeblock",))
                continue

            if re.match(r"^\s*([-*_])\1\1+\s*$", line):
                self.text.insert("end", "-" * 48 + "\n", ("hr",))
                continue

            heading = re.match(r"^(#{1,6})\s+(.*)$", line)
            if heading:
                level = len(heading.group(1))
                title = heading.group(2).strip()
                index = self.text.index("end-1c")
                self.text.insert("end", title + "\n", (f"h{level}",))
                headings.append((level, title, index))
                continue

            quote = re.match(r"^>\s+(.*)$", line)
            if quote:
                self._insert_inline(quote.group(1), base_tag="quote")
                self.text.insert("end", "\n")
                continue

            list_item = re.match(r"^\s*([-*]|\d+\.)\s+(.*)$", line)
            if list_item:
                self._insert_inline("- " + list_item.group(2), base_tag="list")
                self.text.insert("end", "\n")
                continue

            if line.strip() == "":
                self.text.insert("end", "\n")
                continue

            self._insert_inline(line)
            self.text.insert("end", "\n")

        self.text.configure(state="disabled")
        return headings

    def _insert_inline(self, line: str, base_tag: str | None = None) -> None:
        pos = 0
        for match in INLINE_RE.finditer(line):
            if match.start() > pos:
                self._insert_text(line[pos:match.start()], base_tag)
            token = match.group(0)
            if token.startswith("`"):
                self._insert_text(token[1:-1], self._merge_tags(base_tag, "code"))
            elif token.startswith("**") or token.startswith("__"):
                self._insert_text(token[2:-2], self._merge_tags(base_tag, "bold"))
            else:
                self._insert_text(token[1:-1], self._merge_tags(base_tag, "italic"))
            pos = match.end()

        if pos < len(line):
            self._insert_text(line[pos:], base_tag)

    def _merge_tags(self, base: str | None, extra: str) -> Tuple[str, ...]:
        if base:
            return (base, extra)
        return (extra,)

    def _insert_text(self, text: str, tags: str | Tuple[str, ...] | None) -> None:
        if tags:
            self.text.insert("end", text, tags)
        else:
            self.text.insert("end", text)

class CodeEditor(ttk.Frame):
    def __init__(self, master: tk.Widget, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self._on_modified = None

        self._build_ui()
        self._bind_events()

        def _build_ui(self) -> None:
        self.canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.content = tk.Frame(self.canvas, bg=BG)
        self.content_id = self.canvas.create_window(0, 0, window=self.content, anchor="center")

        left_card = tk.Frame(self.content, bg=PANEL, highlightthickness=1, highlightbackground="#273040")
        right_card = tk.Frame(self.content, bg=PANEL, highlightthickness=1, highlightbackground="#273040")

        left_card.grid(row=0, column=0, padx=16, pady=12, sticky="nsew")
        right_card.grid(row=0, column=1, padx=16, pady=12, sticky="nsew")

        self.content.columnconfigure(0, weight=3)
        self.content.columnconfigure(1, weight=2)
        self.content.rowconfigure(0, weight=1)

        title = tk.Label(
            left_card,
            text="FUNCTIONAL DREAMLAND",
            font=("Segoe UI Semibold", 22),
            fg=TEXT,
            bg=PANEL,
        )
        subtitle = tk.Label(
            left_card,
            text="Solve Clojure puzzles, unlock packs, and beat hidden tests.",
            font=("Segoe UI", 11),
            fg=TEXT_DIM,
            bg=PANEL,
        )
        badge = tk.Label(
            left_card,
            text="Version: GUI Edition",
            font=("Segoe UI", 9),
            fg=ACCENT,
            bg=PANEL_DARK,
            padx=8,
            pady=2,
        )

        title.grid(row=0, column=0, columnspan=2, sticky="w", padx=18, pady=(18, 4))
        subtitle.grid(row=1, column=0, columnspan=2, sticky="w", padx=18, pady=(0, 12))
        badge.grid(row=2, column=0, sticky="w", padx=18, pady=(0, 18))

        btn_frame = tk.Frame(left_card, bg=PANEL)
        btn_frame.grid(row=3, column=0, columnspan=2, sticky="w", padx=18)

        self.start_btn = ttk.Button(btn_frame, text="Start Campaign", command=self._start, style="Hero.TButton")
        self.continue_btn = ttk.Button(btn_frame, text="Continue", command=self._continue, style="Hero.TButton")
        self.tutorial_btn = ttk.Button(btn_frame, text="Tutorial", command=self.app.open_tutorial)
        self.reset_btn = ttk.Button(btn_frame, text="Reset Progress", command=self._reset)
        self.quit_btn = ttk.Button(btn_frame, text="Quit", command=self.app.quit)

        self.start_btn.grid(row=0, column=0, padx=(0, 10), pady=4, sticky="w")
        self.continue_btn.grid(row=0, column=1, padx=(0, 10), pady=4, sticky="w")
        self.tutorial_btn.grid(row=1, column=0, padx=(0, 10), pady=6, sticky="w")
        self.reset_btn.grid(row=1, column=1, padx=(0, 10), pady=6, sticky="w")
        self.quit_btn.grid(row=2, column=0, padx=(0, 10), pady=6, sticky="w")

        right_title = tk.Label(
            right_card,
            text="Campaign Status",
            font=("Segoe UI Semibold", 12),
            fg=TEXT,
            bg=PANEL,
        )
        right_title.grid(row=0, column=0, sticky="w", padx=16, pady=(16, 6))

        self.progress = ttk.Progressbar(right_card, orient="horizontal", length=320, mode="determinate")
        self.progress.grid(row=1, column=0, padx=16, sticky="ew")

        self.progress_label = tk.Label(
            right_card,
            text="Progress: 0%",
            font=("Segoe UI", 10),
            fg=TEXT_DIM,
            bg=PANEL,
        )
        self.progress_label.grid(row=2, column=0, padx=16, pady=(6, 12), sticky="w")

        pack_label = tk.Label(
            right_card,
            text="Loaded Packs",
            font=("Segoe UI Semibold", 10),
            fg=TEXT,
            bg=PANEL,
        )
        pack_label.grid(row=3, column=0, padx=16, sticky="w")

        self.pack_list = tk.Text(
            right_card,
            height=10,
            width=42,
            font=("Consolas", 10),
            bg=PANEL_DARK,
            fg=TEXT,
            relief="flat",
            padx=8,
            pady=8,
        )
        self.pack_list.configure(state="disabled")
        self.pack_list.grid(row=4, column=0, padx=16, pady=(6, 12), sticky="nsew")

        tip = tk.Label(
            right_card,
            text="Tip: Drop DLC packs into packs/dlc/ then restart.",
            font=("Segoe UI", 9),
            fg=TEXT_DIM,
            bg=PANEL,
        )
        tip.grid(row=5, column=0, padx=16, pady=(0, 14), sticky="w")

        right_card.columnconfigure(0, weight=1)

        self.canvas.bind("<Configure>", self._on_canvas_resize)\n\n    def _on_canvas_resize(self, event: tk.Event) -> None:
        self.canvas.coords(self.content_id, event.width // 2, event.height // 2)
        self._draw_gradient(event.width, event.height)

        def _draw_gradient(self, width: int, height: int) -> None:
        self.canvas.delete("gradient")
        steps = 50
        for i in range(steps):
            ratio = i / steps
            r = int(15 + (24 - 15) * ratio)
            g = int(19 + (28 - 19) * ratio)
            b = int(26 + (36 - 26) * ratio)
            color = f"#{r:02x}{g:02x}{b:02x}"
            y0 = int(height * i / steps)
            y1 = int(height * (i + 1) / steps)
            self.canvas.create_rectangle(0, y0, width, y1, fill=color, outline="", tags="gradient")

        self.canvas.create_oval(width * 0.72, height * 0.1, width * 1.1, height * 0.55, fill="#1b2430", outline="", tags="gradient")
        self.canvas.create_oval(width * -0.1, height * 0.55, width * 0.35, height * 1.1, fill="#18202b", outline="", tags="gradient")\n\n    def _start_background_animation(self) -> None:
        for _ in range(28):
            x = self.canvas.winfo_reqwidth() // 2
            y = self.canvas.winfo_reqheight() // 2
            item = self.canvas.create_text(x, y, text="()", fill="#2e3a4a", font=("Consolas", 12))
            self._float_items.append(item)
            self._float_dx.append(0.5)
            self._float_dy.append(0.3)
        self._animate_floats()

    def _animate_floats(self) -> None:
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        for i, item in enumerate(self._float_items):
            x, y = self.canvas.coords(item)
            nx = x + self._float_dx[i]
            ny = y + self._float_dy[i]
            if nx < 10 or nx > w - 10:
                self._float_dx[i] *= -1
            if ny < 10 or ny > h - 10:
                self._float_dy[i] *= -1
            self.canvas.coords(item, nx, ny)
        self.after(60, self._animate_floats)

    def update_menu(self) -> None:
        game = self.app.game
        completed = len(game.solved)
        total = len(game.levels)
        pct = int((completed / total) * 100) if total else 0
        self.progress.configure(maximum=total, value=completed)
        self.progress_label.configure(text=f"Progress: {pct}% ({completed}/{total})")

        packs = game.loader.packs_info()
        lines = ["Loaded Packs:"]
        for pack in packs:
            lines.append(f"  [{pack['pack_id']}] {pack['pack_name']} ({len(pack['levels'])} levels)")
        lines.append("")
        lines.append("DLC: drop .json / .json.gz into packs/dlc/ to add more levels.")

        self.pack_list.configure(state="normal")
        self.pack_list.delete("1.0", "end")
        self.pack_list.insert("1.0", "\n".join(lines))
        self.pack_list.configure(state="disabled")

    def _start(self) -> None:
        self.app.game.select(1)
        self.app.show_game()

    def _continue(self) -> None:
        self.app.show_game()

    def _reset(self) -> None:
        confirm = messagebox.askyesno("Reset Progress", "Erase all solved progress?")
        if not confirm:
            return
        game = self.app.game
        game.solved.clear()
        game.idx = 0
        game._update_current_file()
        if not game.current_file.exists():
            game._reset_workspace()
        game._save()
        self.update_menu()
        self.app.game_frame.sync_to_game()


class GameFrame(ttk.Frame):
    def __init__(self, master: tk.Widget, app: "DreamlandGUI") -> None:
        super().__init__(master)
        self.app = app
        self._listboxes: Dict[str, tk.Listbox] = {}
        self._list_map: Dict[str, List[int]] = {}
        self._rebuilding = False
        self._busy = False

        self._build_ui()
        self._bind_shortcuts()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        root = ttk.Panedwindow(self, orient="horizontal")
        root.grid(row=0, column=0, sticky="nsew")

        left = ttk.Frame(root)
        right = ttk.Frame(root)

        root.add(left, weight=3)
        root.add(right, weight=5)

        left.columnconfigure(0, weight=1)
        left.rowconfigure(1, weight=1)
        left.rowconfigure(3, weight=1)

        ttk.Label(left, text="Problem List", style="Title.TLabel").grid(row=0, column=0, sticky="w", padx=8, pady=(6, 0))
        self.tabs = ttk.Notebook(left)
        self.tabs.grid(row=1, column=0, sticky="nsew", padx=8, pady=(4, 12))

        ttk.Label(left, text="Problem Description", style="Title.TLabel").grid(row=2, column=0, sticky="w", padx=8)
        desc_frame = ttk.Frame(left)
        desc_frame.grid(row=3, column=0, sticky="nsew", padx=8, pady=(4, 8))
        desc_frame.columnconfigure(0, weight=1)
        desc_frame.rowconfigure(0, weight=1)

                self.desc_text = tk.Text(
            desc_frame,
            wrap="word",
            bg=PANEL,
            fg=TEXT,
            font=("Segoe UI", 10),
            relief="flat",
            padx=8,
            pady=8,
        )
        self.desc_text.configure(state="disabled")
        desc_scroll = ttk.Scrollbar(desc_frame, orient="vertical", command=self.desc_text.yview)
        self.desc_text.configure(yscrollcommand=desc_scroll.set)
        self.desc_text.grid(row=0, column=0, sticky="nsew")
        desc_scroll.grid(row=0, column=1, sticky="ns")

        self.desc_renderer = MarkdownRenderer(self.desc_text)

        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)
        right.rowconfigure(4, weight=1)

        ttk.Label(right, text="Editor (Clojure)", style="Title.TLabel").grid(row=0, column=0, sticky="w", padx=8, pady=(6, 0))
        self.editor = CodeEditor(right)
        self.editor.grid(row=1, column=0, sticky="nsew", padx=8, pady=(4, 6))

        button_row = ttk.Frame(right)
        button_row.grid(row=2, column=0, sticky="ew", padx=8)
        button_row.columnconfigure(5, weight=1)
        self.run_btn = ttk.Button(button_row, text="Run Examples (Ctrl+R)", command=self.run_examples)
        self.submit_btn = ttk.Button(button_row, text="Submit (Ctrl+Shift+S)", command=self.submit_all)
        self.next_btn = ttk.Button(button_row, text="Next Level (Ctrl+N)", command=self.next_level)
        self.menu_btn = ttk.Button(button_row, text="Menu (Esc)", command=self.back_to_menu)
        self.save_btn = ttk.Button(button_row, text="Save (Ctrl+S)", command=self.save_code)
        self.run_btn.grid(row=0, column=0, padx=4, pady=4)
        self.submit_btn.grid(row=0, column=1, padx=4, pady=4)
        self.next_btn.grid(row=0, column=2, padx=4, pady=4)
        self.save_btn.grid(row=0, column=3, padx=4, pady=4)
        self.menu_btn.grid(row=0, column=4, padx=4, pady=4)

        ttk.Label(right, text="Output", style="Title.TLabel").grid(row=3, column=0, sticky="w", padx=8, pady=(8, 0))
        output_frame = ttk.Frame(right)
        output_frame.grid(row=4, column=0, sticky="nsew", padx=8, pady=(4, 8))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)

        self.output = tk.Text(
            output_frame,
            wrap="word",
            bg=PANEL,
            fg=TEXT,
            font=("Consolas", 10),
            relief="flat",
            padx=8,
            pady=8,
        )
        self.output.configure(state="disabled")
        out_scroll = ttk.Scrollbar(output_frame, orient="vertical", command=self.output.yview)
        self.output.configure(yscrollcommand=out_scroll.set)
        self.output.grid(row=0, column=0, sticky="nsew")
        out_scroll.grid(row=0, column=1, sticky="ns")

        self.status = ttk.Label(self, text="", style="Status.TLabel")
        self.status.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 6))

        self.output.tag_configure("info", foreground=TEXT)
        self.output.tag_configure("success", foreground=ACCENT_2)
        self.output.tag_configure("error", foreground=ERROR)

        self.editor.set_modified_callback(self._mark_dirty)

    def _bind_shortcuts(self) -> None:
        self.bind_all("<Control-r>", lambda _e: self.run_examples())
        self.bind_all("<Control-n>", lambda _e: self.next_level())
        self.bind_all("<Control-s>", lambda _e: self.save_code())
        self.bind_all("<Control-Shift-S>", lambda _e: self.submit_all())
        self.bind_all("<Escape>", lambda _e: self.back_to_menu())

    def sync_to_game(self) -> None:
        self._rebuild_lists()
        self._update_description()
        self._load_editor()
        self._switch_tab_to_current()
        self._set_status(f"Ready - {self.app.game.current_file}")

    def _rebuild_lists(self) -> None:
        self._rebuilding = True
        try:
            self._listboxes.clear()
            self._list_map.clear()
            for tab in self.tabs.tabs():
                self.tabs.forget(tab)

            game = self.app.game
            packs = game.loader.packs_info()
            for pack in packs:
                frame = ttk.Frame(self.tabs)
                frame.columnconfigure(0, weight=1)
                frame.rowconfigure(0, weight=1)

                listbox = tk.Listbox(
                    frame,
                    bg=PANEL,
                    fg=TEXT,
                    selectbackground=ACCENT,
                    selectforeground=BG,
                    font=("Segoe UI", 10),
                    relief="flat",
                    activestyle="none",
                )
                scroll = ttk.Scrollbar(frame, orient="vertical", command=listbox.yview)
                listbox.configure(yscrollcommand=scroll.set)
                listbox.grid(row=0, column=0, sticky="nsew")
                scroll.grid(row=0, column=1, sticky="ns")

                pack_id = pack["pack_id"]
                levels = []
                for raw in pack["levels"]:
                    lid = int(raw["id"])
                    levels.append(lid)
                    is_current = lid == game.level.id
                    is_solved = lid in game.solved
                    label = self._format_level_label(lid, raw["title"], raw.get("difficulty", ""), is_current, is_solved)
                    listbox.insert("end", label)
                    if is_current:
                        listbox.selection_clear(0, "end")
                        listbox.selection_set("end")
                        listbox.see("end")

                listbox.bind("<<ListboxSelect>>", lambda e, pid=pack_id: self._on_select(pid))

                tab_label = self._tab_label(pack.get("pack_name", pack_id))
                self.tabs.add(frame, text=tab_label)
                self._listboxes[pack_id] = listbox
                self._list_map[pack_id] = levels
        finally:
            self._rebuilding = False

    @staticmethod
    def _tab_label(name: str, max_len: int = 22) -> str:
        short = name.split("-")[-1].strip()
        return short if len(short) <= max_len else short[: max_len - 1] + "..."

    @staticmethod
    def _format_level_label(level_id: int, title: str, diff: str, current: bool, solved: bool) -> str:
        prefix = ">" if current else " "
        cb = "x" if solved else " "
        diff = diff or "?"
        return f"{prefix} [{cb}] {level_id:03d}  {title} ({diff})"

    def _switch_tab_to_current(self) -> None:
        game = self.app.game
        packs = game.loader.packs_info()
        for index, pack in enumerate(packs):
            for raw in pack["levels"]:
                if int(raw["id"]) == game.level.id:
                    self.tabs.select(index)
                    return

    def _on_select(self, pack_id: str) -> None:
        if self._rebuilding:
            return
        listbox = self._listboxes.get(pack_id)
        if not listbox:
            return
        selection = listbox.curselection()
        if not selection:
            return
        idx = selection[0]
        level_id = self._list_map.get(pack_id, [])[idx]
        if level_id == self.app.game.level.id:
            return
        try:
            self.save_code()
            msg = self.app.game.select_by_pack(pack_id, level_id)
            self._load_editor()
            self._update_description()
            self._rebuild_lists()
            self._switch_tab_to_current()
            self._write_output(msg, style="info")
        except CommandError as exc:
            self._write_output(str(exc), style="error")

        def _update_description(self) -> None:
        lv = self.app.game.level
        meta = self.app.game.loader.all_meta()[self.app.game.idx]
        pack_id = meta.get("_pack_id", "")

        md = f"# {lv.id}. {lv.title}\n\n"
        md += f"**Pack:** `{pack_id}`  **Difficulty:** `{lv.difficulty}`\n\n"
        md += lv.description.strip() + "\n\n"
        md += "---\n\n## Examples\n"
        for i, ex in enumerate(lv.examples, 1):
            md += f"### Example {i}\n```\nInput:  {ex.args}\nOutput: {ex.expected}\n```\n\n"

        self.desc_renderer.render(md)\n    def _load_editor(self) -> None:
        code = self.app.game.current_file.read_text(encoding="utf-8")
        self.editor.set_text(code)
        self.editor.focus_editor()

    def save_code(self) -> None:
        self.app.game.current_file.write_text(self.editor.get_text(), encoding="utf-8")
        self.app.game._save()
        self._set_status(f"Saved - {self.app.game.current_file}")

    def _mark_dirty(self) -> None:
        self._set_status("Editing...")

    def back_to_menu(self) -> None:
        self.save_code()
        self.app.show_menu()

    def run_examples(self) -> None:
        self._run_tests("examples", "Running example tests...")

    def submit_all(self) -> None:
        self._run_tests("submit", "Running all tests (including hidden)...")

    def next_level(self) -> None:
        total = len(self.app.game.loader)
        next_order = self.app.game.idx + 2
        try:
            self.save_code()
            msg = self.app.game.select(min(total, next_order))
            self._load_editor()
            self._update_description()
            self._rebuild_lists()
            self._switch_tab_to_current()
            self._write_output(msg, style="info")
        except CommandError as exc:
            self._write_output(str(exc), style="error")

    def _run_tests(self, mode: str, banner: str) -> None:
        if self._busy:
            return
        self.save_code()
        self._set_busy(True)
        self._write_output(banner, style="info")

        def task() -> None:
            try:
                result = self.app.game.run_tests(mode)
            except Exception as exc:
                result = f"Error: {exc}"
            self.after(0, lambda: self._finish_run(result))

        threading.Thread(target=task, daemon=True).start()

    def _finish_run(self, result: str) -> None:
        style = "success" if "All tests passed" in result else "info"
        if "Error:" in result or "Compilation Error" in result or "Runtime Error" in result:
            style = "error"
        self._write_output(result, style=style)
        self._rebuild_lists()
        self._set_busy(False)

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        state = "disabled" if busy else "normal"
        for btn in (self.run_btn, self.submit_btn, self.next_btn, self.save_btn, self.menu_btn):
            btn.configure(state=state)
        if busy:
            self._set_status("Working...")

    def _write_output(self, text: str, style: str = "info") -> None:
        self.output.configure(state="normal")
        tag = {"info": "info", "success": "success", "error": "error"}.get(style, "info")
        self.output.insert("end", text.strip() + "\n\n", tag)
        self.output.see("end")
        self.output.configure(state="disabled")

    def _set_status(self, text: str) -> None:
        self.status.configure(text=text)


class DreamlandGUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Functional Dreamland - GUI")
        self.geometry("1280x820")
        self.minsize(1024, 700)
        self.configure(bg=BG)

        self._configure_styles()
        self.game = Game()

        self.menu_frame = MenuFrame(self, self)
        self.game_frame = GameFrame(self, self)

        self.show_menu()

    def _configure_styles(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=TEXT)
        style.configure("Title.TLabel", font=("Segoe UI Semibold", 11), background=BG, foreground=TEXT)
        style.configure("Status.TLabel", font=("Segoe UI", 9), background=BG, foreground=TEXT_DIM)
        style.configure("TButton", font=("Segoe UI", 10))
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", padding=(12, 6), font=("Segoe UI", 10))

    def show_menu(self) -> None:
        self.game_frame.pack_forget()
        self.menu_frame.pack(fill="both", expand=True)
        self.menu_frame.update_menu()

    def show_game(self) -> None:
        self.menu_frame.pack_forget()
        self.game_frame.pack(fill="both", expand=True)
        self.game_frame.sync_to_game()

    def open_tutorial(self) -> None:
        tut_path = Path("tutorial.md")
        content = "Tutorial not found. Add tutorial.md to the game directory."
        if tut_path.exists():
            content = tut_path.read_text(encoding="utf-8")

        window = tk.Toplevel(self)
        window.title("Clojure Tutorial")
        window.geometry("860x700")
        window.configure(bg=BG)

        frame = ttk.Frame(window)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        text = tk.Text(
            frame,
            wrap="word",
            bg=PANEL,
            fg=TEXT,
            font=("Segoe UI", 10),
            relief="flat",
            padx=8,
            pady=8,
        )
        scroll = ttk.Scrollbar(frame, orient="vertical", command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        text.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")

        text.insert("1.0", content)
        text.configure(state="disabled")


if __name__ == "__main__":
    DreamlandGUI().mainloop()




