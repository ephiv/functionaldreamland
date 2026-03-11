import os
import re
import math
from pathlib import Path
from typing import Dict, Tuple

from textual import work
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import (
    Static, RichLog, Input, Label, Markdown, MarkdownViewer,
    TextArea, TabbedContent, TabPane, ListView, ListItem,
)
from textual.containers import Horizontal, Vertical
from textual.binding import Binding
from game import Game, CommandError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_id(s: str) -> str:
    """Sanitise a string for use as a Textual/CSS widget id."""
    return re.sub(r"[^a-zA-Z0-9_-]", "_", s)

DIFF_COLOR = {"Easy": "green", "Medium": "yellow", "Hard": "red"}


# ---------------------------------------------------------------------------
# Animated menu background
# ---------------------------------------------------------------------------

class ClojureBackground(Static):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.a = 0.0

    def on_mount(self) -> None:
        self.set_interval(0.1, self._tick)

    def _tick(self) -> None:
        self.a += 0.1
        self.update(self._render_bg())

    def _render_bg(self) -> str:
        w = max(40, self.size.width)
        h = max(18, self.size.height)
        chars = "( ) { } [ ]"
        out = [" "] * (w * h)
        for x in range(w):
            y1 = int((h / 2) + math.sin(x * 0.1 + self.a) * (h / 4))
            y2 = int((h / 2) + math.cos(x * 0.15 + self.a * 0.8) * (h / 3))
            if 0 <= y1 < h:
                out[y1 * w + x] = chars[x % len(chars)]
            if 0 <= y2 < h:
                out[y2 * w + x] = chars[(x + 2) % len(chars)]
        frame = "".join(out[k] if (k + 1) % w else out[k] + "\n" for k in range(w * h))
        return f"[#2a3948]{frame}[/]"


# ---------------------------------------------------------------------------
# Menu screen
# ---------------------------------------------------------------------------

class MenuScreen(Screen):
    CSS = """
    Screen { layers: bg fg; }
    #menu-bg  { layer: bg; width: 100%; height: 100%; }
    #menu-center {
        layer: fg;
        width: 100%; height: 100%;
        align: center middle;
    }
    #menu-box {
        width: 100; height: 28;
        border: round #6e7f91;
        padding: 1 2;
        background: #0d1116 55%;
    }
    #menu-text { height: 1fr; }
    #menu-cmd  { height: 3; margin-top: 1; }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._awaiting_reset_confirm = False

    def compose(self) -> ComposeResult:
        yield ClojureBackground(id="menu-bg")
        with Vertical(id="menu-center"):
            with Vertical(id="menu-box"):
                yield Static(id="menu-text")
                yield Input(
                    placeholder="Type command: start | continue | tutorial | reset | quit",
                    id="menu-cmd",
                )

    def on_mount(self) -> None:
        self.update_menu()
        self.query_one("#menu-cmd").focus()

    def update_menu(self) -> None:
        game      = self.app.game
        completed = len(game.solved)
        total     = len(game.levels)
        pct       = completed / total if total > 0 else 0
        bar_len   = 30
        bar_str   = "=" * int(pct * bar_len) + "-" * (bar_len - int(pct * bar_len))

        packs     = game.loader.packs_info()
        pack_list = "\n".join(
            f"  • [{p['pack_id']}]  {p['pack_name']}  ({len(p['levels'])} levels)"
            for p in packs
        )

        text = (
            "=========================================================================================\n"
            "                                  FUNCTIONAL DREAMLAND                                 \n"
            "=========================================================================================\n\n"
            "Welcome to the Clojure programming realm. Solve problems,\n"
            "evaluate expressions, and ascend the functional ladder.\n\n"
            f"Progress: [{bar_str}] {pct*100:.0f}%  ({completed}/{total} solved)\n\n"
            "Loaded Packs:\n"
            f"{pack_list}\n\n"
            "-----------------------------------------------------------------------------------------\n"
            "Commands:\n"
            "  [#88c0d0]start[/]    – Start campaign from Level 1\n"
            "  [#88c0d0]continue[/] – Resume from last position\n"
            "  [#88c0d0]tutorial[/] – Open the Clojure docs\n"
            "  [#88c0d0]reset[/]    – Erase all progress and start fresh\n"
            "  [#88c0d0]quit[/]     – Exit\n"
            "-----------------------------------------------------------------------------------------\n"
            "DLC: drop .json / .json.gz pack files into [bold]packs/dlc/[/bold] to add more levels."
        )
        self.query_one("#menu-text", Static).update(text)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        cmd = event.value.strip().lower()
        inp = self.query_one("#menu-cmd", Input)
        inp.value = ""

        # ── Two-step reset confirmation ───────────────────────────────────
        if self._awaiting_reset_confirm:
            self._awaiting_reset_confirm = False
            inp.placeholder = "Type command: start | continue | tutorial | reset | quit"
            if cmd == "yes":
                game = self.app.game
                game.solved.clear()
                game.idx = 0
                game._update_current_file()
                if not game.current_file.exists():
                    game._reset_workspace()
                game._save()
                # Also refresh the game screen if it's already mounted
                try:
                    self.app.get_screen("game").sync_to_game()
                except Exception:
                    pass
                self.update_menu()
                self.query_one("#menu-text", Static).update(
                    self.query_one("#menu-text", Static).renderable  # keep current text
                )
                # Append a confirmation notice by re-rendering the menu with a flash
                self._show_reset_done()
            else:
                self._show_notice("[yellow]Reset cancelled.[/yellow]")
            return

        # ── Normal commands ───────────────────────────────────────────────
        if cmd == "start":
            self.app.game.select(1)
            try:
                self.app.get_screen("game").sync_to_game()
            except Exception:
                pass
            self.app.switch_screen("game")

        elif cmd == "continue":
            self.app.switch_screen("game")

        elif cmd == "tutorial":
            self.app.push_screen("tutorial")

        elif cmd == "reset":
            self._awaiting_reset_confirm = True
            inp.placeholder = "Type  yes  to confirm, or anything else to cancel"
            self._show_notice(
                "[bold red]⚠  This will erase ALL solved progress.[/bold red]\n"
                "Type [bold]yes[/bold] to confirm, or anything else to cancel."
            )

        elif cmd in {"quit", "exit"}:
            self.app.exit()

    def _show_notice(self, markup: str) -> None:
        """Temporarily append a notice line below the normal menu text."""
        game      = self.app.game
        completed = len(game.solved)
        total     = len(game.levels)
        pct       = completed / total if total > 0 else 0
        bar_len   = 30
        bar_str   = "=" * int(pct * bar_len) + "-" * (bar_len - int(pct * bar_len))
        packs     = game.loader.packs_info()
        pack_list = "\n".join(
            f"  • [{p['pack_id']}]  {p['pack_name']}  ({len(p['levels'])} levels)"
            for p in packs
        )
        base = (
            "=========================================================================================\n"
            "                                  FUNCTIONAL DREAMLAND                                 \n"
            "=========================================================================================\n\n"
            "Welcome to the Clojure programming realm. Solve problems,\n"
            "evaluate expressions, and ascend the functional ladder.\n\n"
            f"Progress: [{bar_str}] {pct*100:.0f}%  ({completed}/{total} solved)\n\n"
            "Loaded Packs:\n"
            f"{pack_list}\n\n"
            "-----------------------------------------------------------------------------------------\n"
            "Commands:\n"
            "  [#88c0d0]start[/]    – Start campaign from Level 1\n"
            "  [#88c0d0]continue[/] – Resume from last position\n"
            "  [#88c0d0]tutorial[/] – Open the Clojure docs\n"
            "  [#88c0d0]reset[/]    – Erase all progress and start fresh\n"
            "  [#88c0d0]quit[/]     – Exit\n"
            "-----------------------------------------------------------------------------------------\n"
            "DLC: drop .json / .json.gz pack files into [bold]packs/dlc/[/bold] to add more levels."
        )
        self.query_one("#menu-text", Static).update(f"{base}\n\n{markup}")

    def _show_reset_done(self) -> None:
        self._show_notice("[bold green]✓  Progress reset. All levels marked unsolved.[/bold green]")


# ---------------------------------------------------------------------------
# Tutorial screen
# ---------------------------------------------------------------------------

class TutorialScreen(Screen):
    CSS = """
    #tut-content { height: 1fr; background: $surface; }
    .tut-label {
        dock: bottom; width: 100%;
        text-align: center;
        background: $primary; color: $text;
        padding: 1; text-style: bold;
    }
    """
    BINDINGS = [Binding("escape", "back", "Back")]

    def compose(self) -> ComposeResult:
        md_text = "Tutorial not found. Add `tutorial.md` to the game directory."
        tut_path = Path("tutorial.md")
        if tut_path.exists():
            md_text = tut_path.read_text(encoding="utf-8")
        yield MarkdownViewer(md_text, id="tut-content", show_table_of_contents=True)
        yield Label("ESC — return to Main Menu", classes="tut-label")

    def action_back(self) -> None:
        self.app.pop_screen()


# ---------------------------------------------------------------------------
# Game screen
# ---------------------------------------------------------------------------

class GameScreen(Screen):
    CSS = """
    /* ── Overall layout ─────────────────────────────────────── */
    #game-root {
        width: 100%; height: 100%;
    }

    /* ── Left pane (40 %) ───────────────────────────────────── */
    #left-pane {
        width: 40%;
        height: 100%;
    }

    /* Problem List panel — top 50 % of left pane */
    #problem-list-panel {
        height: 50%;
        border: solid $primary;
        border-title-align: left;
        border-title-color: $accent;
        border-title-style: bold;
        padding: 0;
    }

    /* TabbedContent + ListViews fill the panel */
    #pack-tabs {
        height: 1fr;
        background: transparent;
    }
    #pack-tabs TabPane {
        padding: 0;
    }
    ListView {
        height: 1fr;
        background: transparent;
    }
    ListItem {
        padding: 0 1;
        background: transparent;
    }
    ListItem:hover {
        background: $primary 30%;
    }
    ListItem.-highlight {
        background: $primary 50%;
    }

    /* Problem Description panel — bottom 50 % of left pane */
    #description-panel {
        height: 1fr;
        border: solid $primary;
        border-title-align: left;
        border-title-color: $accent;
        border-title-style: bold;
    }
    #description {
        height: 1fr;
        overflow-y: auto;
        padding: 0 1;
    }

    /* ── Right pane (60 %) ──────────────────────────────────── */
    #right-pane {
        width: 60%;
        height: 100%;
        padding: 0 0 0 1;
    }

    /* Editor panel — 2/3 of right pane */
    #editor-panel {
        height: 2fr;
        border: solid $primary;
        border-title-align: left;
        border-title-color: $accent;
        border-title-style: bold;
    }
    #editor {
        height: 1fr;
    }

    /* Hotkey bar */
    .hotkey-bar {
        height: 1;
        background: $surface-darken-1;
        color: $text-muted;
        padding: 0 1;
    }

    /* Output / log panel — 1/3 of right pane */
    #log-panel {
        height: 1fr;
        border: solid $secondary;
        border-title-align: left;
        border-title-color: $accent;
        border-title-style: bold;
    }
    #log {
        height: 1fr;
        padding: 0 1;
    }
    """

    BINDINGS = [
        Binding("escape", "menu",   "Menu",   show=False),
        Binding("ctrl+r", "run",    "Run",    show=False),
        Binding("ctrl+s", "submit", "Submit", show=False),
        Binding("ctrl+n", "next",   "Next",   show=False),
    ]

    # ── lifecycle ────────────────────────────────────────────────────────

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        # Maps list-item widget id → (pack_id, level_id) for click navigation
        self._item_to_level: Dict[str, Tuple[str, int]] = {}
        # Guard flag to suppress list events during programmatic rebuilds
        self._rebuilding = False

    def compose(self) -> ComposeResult:
        packs = self.app.game.loader.packs_info()

        with Horizontal(id="game-root"):
            # ── Left pane ──────────────────────────────────────────────
            with Vertical(id="left-pane"):

                # Problem List (top half)
                with Vertical(id="problem-list-panel"):
                    with TabbedContent(id="pack-tabs"):
                        for pi, pack in enumerate(packs):
                            tab_label = self._tab_label(pack["pack_name"])
                            with TabPane(tab_label, id=f"tab-p{pi}"):
                                yield ListView(id=f"list-p{pi}")

                # Problem Description (bottom half)
                with Vertical(id="description-panel"):
                    yield Markdown("", id="description")

            # ── Right pane ─────────────────────────────────────────────
            with Vertical(id="right-pane"):

                # Editor
                with Vertical(id="editor-panel"):
                    yield TextArea(id="editor")

                yield Label(
                    " ^R Run Examples   ^S Submit   ^N Next Level   ESC Menu",
                    classes="hotkey-bar",
                )

                # Output log
                with Vertical(id="log-panel"):
                    yield RichLog(id="log", wrap=True, highlight=True, markup=True)

    def on_mount(self) -> None:
        # Titled borders — compact, left-aligned, rendered on the border line
        self.query_one("#problem-list-panel").border_title = "Problem List"
        self.query_one("#description-panel").border_title  = "Problem Description"
        self.query_one("#editor-panel").border_title       = "Editor · Clojure"
        self.query_one("#log-panel").border_title          = "Output"

        # Populate lists, description, editor
        self._rebuild_lists()
        self._update_description()
        self._load_editor()

        log = self.query_one("#log", RichLog)
        log.write("[bold]Functional Dreamland[/bold] — write your Clojure solution above.")
        log.write("^R to run examples · ^S to submit · ^N for next level")

        self.query_one("#editor", TextArea).focus()

    # ── Public sync helper (called from MenuScreen) ──────────────────────

    def sync_to_game(self) -> None:
        """Called externally (e.g. after 'start') to refresh all panels."""
        self._rebuild_lists()
        self._update_description()
        self._load_editor()

    # ── Problem List ─────────────────────────────────────────────────────

    @staticmethod
    def _tab_label(pack_name: str, max_len: int = 22) -> str:
        # Use the part after the last em-dash for long base pack names
        short = pack_name.split("—")[-1].strip()
        if len(short) > max_len:
            short = short[:max_len - 1] + "…"
        return short

    def _rebuild_lists(self) -> None:
        """
        Sync every pack's ListView with the current solved/selected state.

        Strategy: mount ListItems exactly once (on_mount), then on every
        subsequent call only update the Label text inside each existing item.
        This avoids Textual's DuplicateIds error that occurs when clear() is
        called synchronously but the DOM removal is deferred.
        """
        self._rebuilding = True
        try:
            game        = self.app.game
            current_lid = game.level.id
            packs       = game.loader.packs_info()
            self._item_to_level.clear()

            for pi, pack in enumerate(packs):
                pack_id = pack["pack_id"]
                try:
                    lv_list = self.query_one(f"#list-p{pi}", ListView)
                except Exception:
                    continue

                existing = list(lv_list.query(ListItem))
                first_mount = len(existing) == 0
                scroll_to   = 0

                for li, raw in enumerate(pack["levels"]):
                    lid        = int(raw["id"])
                    diff       = raw.get("difficulty", "")
                    color      = DIFF_COLOR.get(diff, "white")
                    is_solved  = lid in game.solved
                    is_current = lid == current_lid
                    if is_current:
                        scroll_to = li
                    prefix = "▶" if is_current else " "
                    cb     = "☑" if is_solved else "☐"
                    item_id    = f"li-p{pi}-l{lid}"
                    self._item_to_level[item_id] = (pack_id, lid)
                    label_text = (
                        f"{prefix} {cb} {lid:03d}. "
                        f"[{color}]{raw['title']}[/{color}]"
                        f"  [dim]{diff}[/dim]"
                    )

                    if first_mount:
                        # First time: create and mount the item
                        lv_list.append(
                            ListItem(Label(label_text, markup=True), id=item_id)
                        )
                    else:
                        # Subsequent calls: update the label text in-place
                        # (no DOM add/remove → no DuplicateIds crash)
                        if li < len(existing):
                            try:
                                existing[li].query_one(Label).update(label_text)
                            except Exception:
                                pass

                lv_list.index = scroll_to

        finally:
            self._rebuilding = False

    def _switch_tab_to_current(self) -> None:
        """Activate the tab that contains the currently selected level."""
        game  = self.app.game
        packs = game.loader.packs_info()
        for pi, pack in enumerate(packs):
            for raw in pack["levels"]:
                if int(raw["id"]) == game.level.id:
                    try:
                        tabs = self.query_one("#pack-tabs", TabbedContent)
                        tabs.active = f"tab-p{pi}"
                    except Exception:
                        pass
                    return

    # ── Description ──────────────────────────────────────────────────────

    def _update_description(self) -> None:
        lv      = self.app.game.level
        meta    = self.app.game.loader.all_meta()[self.app.game.idx]
        pid     = meta.get("_pack_id", "")
        diff    = lv.difficulty
        diff_badge = {"Easy": "🟢 Easy", "Medium": "🟡 Medium", "Hard": "🔴 Hard"}.get(diff, diff)
        content = (
            f"# {lv.id}. {lv.title}\n"
            f"**Pack:** `{pid}`  ·  "
            f"**Difficulty:** {diff_badge}\n\n"
            f"{lv.description}\n\n---\n\n### Examples\n"
        )
        for i, ex in enumerate(lv.examples, 1):
            content += (
                f"**Example {i}:**\n"
                f"```clojure\nInput:  {ex.args}\nOutput: {ex.expected}\n```\n\n"
            )
        self.query_one("#description", Markdown).update(content)

    # ── Editor ───────────────────────────────────────────────────────────

    def _load_editor(self) -> None:
        editor = self.query_one("#editor", TextArea)
        editor.text = self.app.game.current_file.read_text(encoding="utf-8")

    def _save_code(self) -> None:
        editor = self.query_one("#editor", TextArea)
        self.app.game.current_file.write_text(editor.text, encoding="utf-8")
        self.app.game._save()

    # ── Log ──────────────────────────────────────────────────────────────

    def _write_log(self, text: str) -> None:
        self.query_one("#log", RichLog).write(text)

    # ── Events ───────────────────────────────────────────────────────────

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle a player clicking / pressing Enter on a problem in the list."""
        if self._rebuilding or event.item is None:
            return
        item_id = event.item.id
        if item_id not in self._item_to_level:
            return

        pack_id, level_id = self._item_to_level[item_id]
        if level_id == self.app.game.level.id:
            return  # already on this level — nothing to do

        try:
            self._save_code()
            msg = self.app.game.select_by_pack(pack_id, level_id)
            self._load_editor()
            self._update_description()
            self._rebuild_lists()
            self._write_log(f"[bold cyan]{msg}[/bold cyan]")
        except CommandError as e:
            self._write_log(f"[red]{e}[/red]")

    # ── Bindings ─────────────────────────────────────────────────────────

    def action_menu(self) -> None:
        self._save_code()
        try:
            self.app.get_screen("menu").update_menu()
        except Exception:
            pass
        self.app.switch_screen("menu")

    def action_run(self) -> None:
        self._save_code()
        self._write_log("[dim]▶ Running examples…[/dim]")
        self._run_task("examples")

    def action_submit(self) -> None:
        self._save_code()
        self._write_log("[dim]▶ Running all hidden tests…[/dim]")
        self._run_task("submit")

    def action_next(self) -> None:
        total      = len(self.app.game.loader)
        next_order = self.app.game.idx + 2   # idx is 0-based; select() is 1-based
        try:
            self._save_code()
            msg = self.app.game.select(min(total, next_order))
            self._load_editor()
            self._update_description()
            self._rebuild_lists()
            self._switch_tab_to_current()
            self._write_log(f"[bold cyan]{msg}[/bold cyan]")
        except CommandError as e:
            self._write_log(f"[red]{e}[/red]")

    @work(thread=True)
    def _run_task(self, mode: str) -> None:
        try:
            result = self.app.game.run_tests(mode)
            self.app.call_from_thread(self._write_log, result)
            # Rebuild lists so solved checkmark appears immediately on submit
            self.app.call_from_thread(self._rebuild_lists)
        except Exception as e:
            self.app.call_from_thread(self._write_log, f"[red]Error: {e}[/red]")


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

class DreamlandTUI(App[None]):
    CSS = """
    Screen { background: $surface; }
    """

    def __init__(self) -> None:
        super().__init__()
        self.game = Game()

    def on_mount(self) -> None:
        self.install_screen(MenuScreen(),  name="menu")
        self.install_screen(TutorialScreen(), name="tutorial")
        self.install_screen(GameScreen(),  name="game")
        self.push_screen("menu")


if __name__ == "__main__":
    DreamlandTUI().run()