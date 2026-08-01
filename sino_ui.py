#!/usr/bin/env python3
"""
sino_ui — Modern CLI UI/UX module for the Sino programming language.

Provides:
  - Terminal capability detection (TTY, NO_COLOR, FORCE_COLOR, --no-color)
  - Consistent color palette (works in light & dark terminals)
  - Unicode box drawing with ASCII fallback
  - Spinner & progress bar
  - Step list (build progress)
  - Diagnostic renderer (error/warning/note/help with source snippets)
  - Banner
  - REPL framework
  - Tables

Usage:
    from sino_ui import UI

    ui = ui_or_no_color(args)
    ui.banner()
    ui.success("Build completed")
    ui.error("SN1001", "Unknown variable", file="src/main.si", line=12, col=8,
             source_line='print(total)', col_span=5,
             message="Variable 'total' does not exist.",
             hint="Did you mean: totalPrice",
             doc_url="https://crossberry-in.github.io/sino-lang-docs/errors/SN1001")
"""

import os
import sys
import shutil
import platform
import re
from typing import Optional, List, Tuple

# ============================================================================
# Terminal Capability Detection
# ============================================================================

class Colors:
    """ANSI color codes — chosen to be readable in both light and dark terminals."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"

    # Foreground colors — calibrated for light/dark readability
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    GRAY = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_CYAN = "\033[96m"

    # Semantic aliases
    ERROR = BRIGHT_RED
    WARNING = BRIGHT_YELLOW
    SUCCESS = BRIGHT_GREEN
    INFO = BRIGHT_CYAN
    ACCENT = BRIGHT_BLUE
    MUTED = GRAY

# Box drawing characters
BOX_LIGHT = {
    "tl": "┌", "tr": "┐", "bl": "└", "br": "┘",
    "h": "─", "v": "│",
    "t-down": "├", "t-up": "┤", "t-right": "├", "t-left": "┤",
}

BOX_ASCII = {
    "tl": "+", "tr": "+", "bl": "+", "br": "+",
    "h": "-", "v": "|",
    "t-down": "+", "t-up": "+", "t-right": "+", "t-left": "+",
}

# Spinner frames (Braille)
SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
SPINNER_FRAMES_ASCII = ["|", "/", "-", "\\"]

# Checkmarks and symbols
SYMBOLS = {
    "ok": "✔",
    "fail": "✖",
    "warn": "⚠",
    "info": "ℹ",
    "arrow_down": "↓",
    "arrow_up": "↑",
    "arrow_right": "→",
    "bullet": "•",
    "ellipsis": "…",
    "star": "★",
}

SYMBOLS_ASCII = {
    "ok": "v",
    "fail": "x",
    "warn": "!",
    "info": "i",
    "arrow_down": "v",
    "arrow_up": "^",
    "arrow_right": "->",
    "bullet": "*",
    "ellipsis": "...",
    "star": "*",
}


def detect_capabilities():
    """Detect terminal capabilities. Returns dict with:
       color (bool), unicode (bool), tty (bool), width (int)."""
    tty = sys.stderr.isatty() and sys.stdout.isatty()
    no_color = os.environ.get("NO_COLOR") is not None
    force_color = os.environ.get("FORCE_COLOR") is not None
    term = os.environ.get("TERM", "")
    is_dumb = term in ("dumb", "")

    color = force_color or (tty and not no_color and not is_dumb)

    # Unicode support: assume yes if color is on and TERM is not latin1
    codec = sys.stdout.encoding.lower() if sys.stdout.encoding else "utf-8"
    unicode = color and "utf" in codec
    if force_color and "utf" in codec:
        unicode = True

    # Terminal width
    try:
        import shutil as _sh
        cols = _sh.get_terminal_size((80, 24)).columns
    except Exception:
        cols = 80

    return {
        "color": color,
        "unicode": unicode,
        "tty": tty,
        "width": cols,
    }


# ============================================================================
# UI Class
# ============================================================================

class UI:
    """Main UI renderer. Detects terminal capabilities on construction."""

    def __init__(self, color: Optional[bool] = None, unicode: Optional[bool] = None):
        caps = detect_capabilities()
        self.color = caps["color"] if color is None else color
        self.unicode = caps["unicode"] if unicode is None else unicode
        self.width = caps["width"]
        self._box = BOX_LIGHT if self.unicode else BOX_ASCII
        self._symbols = SYMBOLS if self.unicode else SYMBOLS_ASCII
        self._spinner = SPINNER_FRAMES if self.unicode else SPINNER_FRAMES_ASCII
        self._spinner_idx = 0

    # --- Color helpers ---------------------------------------------------

    def c(self, text: str, color: str) -> str:
        """Wrap text in color codes if color is enabled."""
        if not self.color:
            return text
        return f"{color}{text}{Colors.RESET}"

    def bold(self, text: str) -> str:
        return self.c(text, Colors.BOLD) if self.color else text

    def dim(self, text: str) -> str:
        return self.c(text, Colors.DIM) if self.color else text

    # --- Symbol helpers --------------------------------------------------

    def symbol(self, name: str) -> str:
        return self._symbols.get(name, name)

    # --- Output primitives ----------------------------------------------

    def write(self, text: str = "", end: str = "\n", file=None):
        """Write text to stdout (or specified file)."""
        f = file or sys.stdout
        print(text, end=end, file=f)

    def write_err(self, text: str = "", end: str = "\n"):
        """Write text to stderr."""
        print(text, end=end, file=sys.stderr)

    def hr(self, char: str = "─", color: str = Colors.MUTED):
        """Horizontal rule across terminal width."""
        line = char * self.width
        self.write(self.c(line, color) if self.color else line)

    # --- Banner ----------------------------------------------------------

    def banner(self, title: str = "Sino Compiler", subtitle: str = "Version 1.0",
               tagline: str = "Fast • Safe • Modern"):
        """Draw the startup banner."""
        # Choose width based on title length
        inner_width = max(len(title), len(subtitle), len(tagline)) + 4
        h = self._box["h"]
        v = self._box["v"]
        tl, tr, bl, br = self._box["tl"], self._box["tr"], self._box["bl"], self._box["br"]

        accent = Colors.ACCENT if self.color else ""

        def center(s, w):
            pad = (w - len(s)) // 2
            return " " * pad + s + " " * (w - len(s) - pad)

        self.write()
        self.write(self.c(f"{tl}{h * inner_width}{tr}", accent))
        self.write(self.c(f"{v}", accent) + self.c(center(title, inner_width), Colors.BOLD) + self.c(f"{v}", accent))
        self.write(self.c(f"{v}", accent) + self.c(center(subtitle, inner_width), Colors.MUTED) + self.c(f"{v}", accent))
        self.write(self.c(f"{v}", accent) + self.c(center(tagline, inner_width), Colors.INFO) + self.c(f"{v}", accent))
        self.write(self.c(f"{bl}{h * inner_width}{br}", accent))
        self.write()

    # --- Status messages -------------------------------------------------

    def success(self, msg: str, detail: str = ""):
        """Print a success message."""
        sym = self.c(self.symbol("ok"), Colors.SUCCESS)
        text = self.bold(msg)
        if detail:
            text += "\n" + self.dim(detail)
        self.write(f"{sym} {text}")

    def fail(self, msg: str, detail: str = ""):
        """Print a failure message."""
        sym = self.c(self.symbol("fail"), Colors.ERROR)
        text = self.bold(msg)
        if detail:
            text += "\n" + self.dim(detail)
        self.write_err(f"{sym} {text}")

    def warning(self, msg: str, detail: str = ""):
        """Print a warning message."""
        sym = self.c(self.symbol("warn"), Colors.WARNING)
        text = self.bold(msg)
        if detail:
            text += "\n" + self.dim(detail)
        self.write(f"{sym} {text}")

    def info(self, msg: str):
        """Print an info message (no symbol, just dim prefix)."""
        self.write(self.dim("→") + " " + msg)

    # --- Step list (build progress) -------------------------------------

    def step_start(self, label: str):
        """Print a step that's about to run (with spinner)."""
        spinner = self.c(self._spinner[0], Colors.INFO)
        self.write(f"{spinner} {self.dim(label)}")

    def step_done(self, label: str):
        """Print a completed step."""
        sym = self.c(self.symbol("ok"), Colors.SUCCESS)
        self.write(f"{sym} {self.dim(label)}")

    def step_fail(self, label: str):
        """Print a failed step."""
        sym = self.c(self.symbol("fail"), Colors.ERROR)
        self.write(f"{sym} {self.dim(label)}")

    def step_skip(self, label: str):
        """Print a skipped step."""
        sym = self.c(self.symbol("bullet"), Colors.MUTED)
        self.write(f"{sym} {self.dim(label)}")

    def step_list(self, steps: List[Tuple[str, str]]):
        """Render a list of (status, label) where status is 'ok'|'fail'|'skip'|'start'.
        Example: ui.step_list([('ok','Loading config'), ('ok','Parsing'), ('fail','Linking')])"""
        for status, label in steps:
            if status == "ok":
                self.step_done(label)
            elif status == "fail":
                self.step_fail(label)
            elif status == "skip":
                self.step_skip(label)
            else:
                self.step_start(label)

    # --- Progress bar ----------------------------------------------------

    def progress_bar(self, percent: float, width: int = 24, label: str = "") -> str:
        """Return a progress bar string."""
        filled = int(width * percent / 100)
        empty = width - filled
        if self.unicode:
            bar = "█" * filled + "░" * empty
        else:
            bar = "#" * filled + "-" * empty
        pct = f"{int(percent):3d}%"
        line = f"{bar} {pct}"
        if self.color:
            line = self.c(filled_bar := "█" * filled if self.unicode else "#" * filled,
                          Colors.SUCCESS) + self.c(empty_bar := "░" * empty if self.unicode else "-" * empty,
                                                   Colors.MUTED) + " " + self.bold(pct)
        if label:
            line = f"{label} {line}"
        return line

    # --- Diagnostics (errors, warnings, notes, help) --------------------

    def diagnostic(self,
                   severity: str,           # "error" | "warning" | "note" | "help"
                   code: Optional[str],     # "SN1001" or None
                   title: str,              # "Unknown variable"
                   message: Optional[str] = None,
                   file: Optional[str] = None,
                   line: Optional[int] = None,
                   col: Optional[int] = None,
                   source_line: Optional[str] = None,
                   col_span: Optional[int] = None,
                   hint: Optional[str] = None,
                   suggestion: Optional[str] = None,
                   suggestion_code: Optional[str] = None,
                   doc_url: Optional[str] = None):
        """Render a diagnostic message in the Sino style.

        severity: error | warning | note | help
        """
        sev = severity.lower()
        color_map = {
            "error": Colors.ERROR,
            "warning": Colors.WARNING,
            "note": Colors.INFO,
            "help": Colors.ACCENT,
        }
        color = color_map.get(sev, Colors.INFO)

        self.write()
        self.hr("─", Colors.MUTED)
        self.write()

        # Header: error[SN1001]: Unknown variable
        header = self.c(sev, color) + self.bold(sev)
        # Re-do: color the word, then add code and title
        header = self.c(sev, color)
        if code:
            header += self.c(f"[{code}]", color)
        header += f": {self.bold(title)}"
        self.write(header)
        self.write()

        # Source context
        if file and line is not None and source_line:
            self._render_source_context(file, line, col, source_line, col_span, color)
            self.write()

        # Message
        if message:
            self.write(message)
            self.write()

        # Hint
        if hint:
            self.write(self.c("Hint:", Colors.ACCENT))
            self.write(self.dim(hint))
            self.write()

        # Suggestion
        if suggestion or suggestion_code:
            self.write(self.c("Suggestion:", Colors.ACCENT))
            if suggestion:
                self.write(suggestion)
            if suggestion_code:
                self.write()
                self.write(self.dim("    " + suggestion_code))
            self.write()

        # Doc URL
        if doc_url:
            self.write(self.c("Documentation:", Colors.MUTED))
            self.write(self.c(doc_url, Colors.UNDERLINE) if self.color else doc_url)
            self.write()

        self.hr("─", Colors.MUTED)
        self.write()

    def _render_source_context(self, file, line, col, source, col_span, color):
        """Render the source file snippet with caret."""
        # Header: ┌─ src/main.si:12:8
        h = self._box["h"]
        v = self._box["v"]
        tl = self._box["tl"]
        loc = f"{file}:{line}"
        if col is not None:
            loc += f":{col}"
        self.write(f"  {self.c(tl + '─ ' + loc, color)}")
        self.write(f"  {self.c(v, color)}")

        # Line number gutter
        line_str = str(line)
        gutter_width = max(len(line_str), 2)

        # The source line
        gutter = self.c(line_str.rjust(gutter_width) + " " + v + " ", Colors.MUTED)
        self.write(f"  {gutter}{source}")

        # Caret line
        if col is not None:
            caret_col = max(col - 1, 0)
            span = col_span or 1
            indent = " " * (gutter_width + 3 + caret_col)  # +3 for " | "
            carets = "^" * span
            self.write(f"  {' ' * gutter_width} {self.c(v, Colors.MUTED)} {indent}{self.c(carets, color)}")

        # Closing border
        self.write(f"  {self.c(v, color)}")

    # --- Tables ----------------------------------------------------------

    def table(self, headers: List[str], rows: List[List[str]]):
        """Render a simple table."""
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(cell))

        def fmt_row(cells):
            return "  ".join(cell.ljust(col_widths[i]) for i, cell in enumerate(cells))

        # Header
        self.write(self.bold(fmt_row(headers)))
        self.write(self.c("  ".join("-" * w for w in col_widths), Colors.MUTED))
        # Rows
        for row in rows:
            self.write(fmt_row(row))
        self.write()

    # --- REPL ------------------------------------------------------------

    def repl_banner(self, version: str = "1.0"):
        """Print the REPL banner."""
        self.write(self.c("Sino REPL", Colors.ACCENT))
        self.write(self.c(f"Version {version}", Colors.MUTED))
        self.write()

    def repl_prompt(self) -> str:
        """Return the REPL prompt string."""
        return self.c("> ", Colors.ACCENT) if self.color else "> "

    def repl_continuation_prompt(self) -> str:
        """Return the continuation prompt for multi-line input."""
        return self.c("... ", Colors.MUTED) if self.color else "... "

    # --- Misc ------------------------------------------------------------

    def version(self, version: str, target: str = None):
        """Print version info."""
        self.write(self.bold(f"sino-pkg {version}"))
        self.write(self.dim("Sino Programming Language Toolchain"))
        if target:
            self.write(self.dim(f"Target: {target}"))
        self.write()

    def panic(self, title: str, location: str, stack_trace: List[str], suggestion: str = None):
        """Render a runtime panic."""
        self.write()
        self.hr("─", Colors.ERROR)
        self.write()
        self.write(self.c(self.bold("Runtime Panic"), Colors.ERROR))
        self.write(self.bold(title))
        self.write()
        self.write(self.c("Location:", Colors.MUTED))
        self.write(f"  {location}")
        self.write()
        self.write(self.c("Stack Trace:", Colors.MUTED))
        for i, frame in enumerate(stack_trace):
            if i == 0:
                self.write(f"  {self.bold(frame)}")
            else:
                self.write(f"  {self.c(self.symbol('arrow_down'), Colors.MUTED)}")
                self.write(f"  {self.dim(frame)}")
        if suggestion:
            self.write()
            self.write(self.c("Suggestion:", Colors.ACCENT))
            self.write(suggestion)
        self.write()
        self.hr("─", Colors.ERROR)
        self.write()

    def fatal_compiler_error(self, code: str, message: str, version: str, target: str,
                             report_url: str = "https://github.com/crossberry-in/sino-pkg/issues"):
        """Render an internal compiler error."""
        self.write()
        self.write(self.c(self.bold(f"fatal[{code}]"), Colors.ERROR))
        self.write(self.bold(message))
        self.write()
        self.write(self.c("Please report:", Colors.MUTED))
        self.write(self.c(report_url, Colors.UNDERLINE) if self.color else report_url)
        self.write()
        self.write(self.c("Compiler:", Colors.MUTED) + f" {version}")
        self.write(self.c("Target:", Colors.MUTED) + f" {target}")
        self.write()


# ============================================================================
# Convenience factory
# ============================================================================

def create_ui(no_color: bool = False, force_color: bool = False) -> UI:
    """Create a UI instance, respecting --no-color and --force-color flags."""
    if force_color:
        return UI(color=True, unicode=True)
    if no_color:
        return UI(color=False, unicode=False)
    return UI()


def ui_from_args(args: List[str]) -> UI:
    """Inspect args for --no-color or --force-color and return a UI instance."""
    no_color = "--no-color" in args or os.environ.get("NO_COLOR") is not None
    force_color = "--force-color" in args or os.environ.get("FORCE_COLOR") is not None
    return create_ui(no_color=no_color, force_color=force_color)
