# Changelog

All notable changes to sino-pkg will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v1.2.0] — 2026-08-01

### Added — Unified `sino` Command Dispatcher (Go-style)

Following the Go/Cargo model, `sino` is now a **unified dispatcher** that routes
all Sino-related commands through a single entry point. This resolves the
naming conflict between the Sino interpreter and the sino-pkg package manager.

- **Unified dispatcher** — `sino` now handles both interpreter and package
  manager commands:
  - `sino` (no args) → start REPL (via interpreter)
  - `sino file.si` → run file (via interpreter)
  - `sino <subcommand>` → sino-pkg subcommand (build, test, add, etc.)
  - `sino -v / --version` → sino-pkg version
  - `sino -h / --help` → sino-pkg help
  - `sino <unknown-word>` → try as filename via interpreter (backwards compatible)

- **Interpreter renamed to `sino-interpreter`** — The Sino interpreter binary
  is now installed as `sino-interpreter` (not `sino`) to avoid conflict with
  the dispatcher. The `sino` command is now the Python dispatcher script.

- **Migration logic** — The sino-pkg installer automatically detects if an old
  interpreter binary is installed as `sino` and renames it to `sino-interpreter`
  before installing the dispatcher. This provides a seamless upgrade path for
  existing users.

- **Cross-platform interpreter discovery** — `find_sino_interpreter()` now
  handles Windows (`.exe` suffix) and checks multiple locations:
  1. `$SINO_INTERPRETER` env var
  2. `~/.sino/bin/sino-interpreter` (or `.exe` on Windows)
  3. `sino-interpreter` on PATH
  4. `sino` on PATH (skipping the sino-pkg script itself)

### Fixed

- **Critical: `sino version` / `sino help` / `sino search` returned "Cannot open file"** —
  This happened because the Sino interpreter was installed as `sino`, so running
  `sino version` made the interpreter try to open `version` as a script file.
  The unified dispatcher now intercepts known subcommands before they reach the
  interpreter.

### Changed

- sino-lang-docs installer now installs the interpreter as `sino-interpreter`
- sino-pkg installer now installs the dispatcher as `sino`
- sino-pkg installer now warns if the interpreter is not installed
- Version bumped from 1.1.0 → 1.2.0

---

## [v1.1.0] — 2026-08-01

### Added — Modern CLI UI/UX

Complete redesign of the command-line interface with a polished developer
experience comparable to Rust Cargo, Clang, and Go tooling.

- **`sino_ui.py` module** — A comprehensive UI library with:
  - Terminal capability auto-detection (TTY, NO_COLOR, FORCE_COLOR, encoding)
  - Consistent color palette calibrated for light and dark terminals
  - Unicode box drawing with ASCII fallback (for `dumb` terminals)
  - Spinner & progress bar
  - Step list (build progress with checkmarks)
  - Diagnostic renderer with source context, carets, hints, suggestions, doc URLs
  - Banner component
  - REPL framework (banner + prompt)
  - Table renderer
  - Panic UI with stack traces
  - Fatal compiler error UI

- **New commands**:
  - `sino new <project>` — Create a new binary project (alias for `init --bin`)
  - `sino repl` — Start the interactive Sino REPL
  - `sino bench` — Run benchmarks (Lexer, Parser, Compiler, Runtime, Memory)
  - `sino fmt` — Format source files (normalize indentation, strip trailing whitespace)
  - `sino lint` — Lint source files (unused variable detection with `SN2001` warning)
  - `sino search <query>` — Search packages
  - `sino uninstall <name>` — Uninstall a package
  - `sino login` — Log in to the registry (stub with credential storage)
  - `sino logout` — Log out of the registry
  - `sino doctor` — Check the Sino environment (compiler, package manager, runtime, libraries, network)

- **Diagnostic UI** — All errors, warnings, notes, and help now render with:
  - Error codes (`SN1001` for unknown variable, `SN2001` for unused variable, etc.)
  - Source file context with line numbers and carets pointing to the error
  - Hints and suggestions
  - Documentation URLs
  - Severity-specific colors (red for errors, yellow for warnings, blue for notes/help)

- **Startup banner** — Unicode box-drawn banner shown by `sino version`, `sino help`, `sino doctor`, and `sino build --banner`:
  ```
  ┌────────────────────────┐
  │     Sino Compiler      │
  │     Version 1.1.0      │
  │  Fast • Safe • Modern  │
  └────────────────────────┘
  ```

- **Build progress** — `sino build` now shows a step list:
  ```
  ✔ Loading configuration
  ✔ Resolving packages
  ✔ Parsing
  ✔ Semantic analysis
  ✔ Type checking
  ✔ Optimizing
  ✔ Generating code
  ✔ Linking
  ```

- **Color control**:
  - `--no-color` flag disables colored output
  - `--force-color` flag forces colored output (even when piped)
  - `NO_COLOR` environment variable respected
  - `FORCE_COLOR` environment variable respected
  - Auto-detection of TTY and terminal encoding

- **Interpreter discovery** — `find_sino_interpreter()` looks for the Sino
  interpreter binary at:
  1. `$SINO_INTERPRETER` env var
  2. `~/.sino/bin/sino-interpreter`
  3. `sino-interpreter` on PATH
  4. `sino` on PATH (skipping the sino-pkg script itself)

### Changed

- `sino version` now shows the banner + toolchain info + detected compilers
- `sino help` now shows the banner + formatted command list + examples + options
- `sino build` now shows a step list with timing and output path
- `sino test` now uses the polished UI for pass/fail messages
- `sino install` now uses the polished UI for resolve/success messages
- `sino clean` now shows a single success message with removed artifacts
- `sino run` now uses `find_sino_interpreter()` instead of `shutil.which("sino")`
- All `info`, `ok`, `warn`, `error` helpers now delegate to the `sino_ui` module
- Version bumped from 1.0.0 → 1.1.0

### Fixed

- Fixed `sino test` and `sino run` failing when `sino` on PATH resolves to the sino-pkg script itself (now skips Python scripts when looking for the interpreter binary)

---

## [v1.0.0] — 2026-08-01

### Added

- **Initial release** of the Sino Package Manager.
- **Commands**:
  - `sino init --lib [name]` — Initialize a library project
  - `sino init --bin [name]` — Initialize a binary project
  - `sino build [--static|--shared|--native]` — Build the project
  - `sino install` — Install dependencies from `sino.toml`
  - `sino add <source> [version]` — Add a dependency
  - `sino remove <name>` — Remove a dependency
  - `sino update [name...]` — Update dependencies
  - `sino test` — Run tests in `tests/`
  - `sino doc` — Generate API documentation + VS Code/LSP metadata
  - `sino publish` — Publish stub (instructs to use GitHub releases)
  - `sino clean` — Remove build artifacts
  - `sino run [args...]` — Run `src/main.si`
  - `sino version` / `sino --version` — Show version and detected compilers
  - `sino help` / `sino --help` — Show help
- **Manifest format** (`sino.toml`):
  - Package metadata: `name`, `version`, `authors`, `license`, `description`
  - `[dependencies]` table with GitHub, local, and registry sources
  - `[build]` section: `c`, `cpp`, `assembly`, `rust` flags
  - `[build.output]` section: `type` (static/shared/native)
  - Minimal TOML parser included (no external dependencies)
- **Build system**:
  - C compilation (`cc`/`gcc`/`clang` with `-c -O2 -fPIC`)
  - C++ compilation (`c++`/`g++`/`clang++`)
  - Assembly compilation (`cc` for `.S` files)
  - Rust compilation (`rustc --crate-type staticlib`)
  - Static library output (`ar rcs` → `lib<name>.a`)
  - Shared library output (`cc -shared` → `.so`/`.dylib`/`.dll`)
  - Native Sino library output (ZIP → `<name>.silib`)
  - Automatic compiler detection
  - Include path support (`include/` and `native/`)
  - Stale object file cleanup between builds
  - Unique object file names per language (prevents collisions)
- **Dependency management**:
  - Semantic versioning with `^`, `~`, `>=`, `>`, `<=`, `<`, `=`, `*` operators
  - GitHub dependencies (`github:owner/repo@version`)
  - Local path dependencies (`local:../path`)
  - Registry dependencies (future — `name = "1.0"`)
  - Shallow git clone for GitHub dependencies
  - Dependency caching in `~/.sino/cache/github/`
  - Lock file (`sino.lock`) with resolved versions
  - Symlinked dependencies in `sino_modules/`
- **Documentation generation**:
  - `docs/API.md` from `public func` declarations in `.si` files
  - `.vscode/sino-lsp.json` for IDE integration
- **Cross-platform support**:
  - Linux (x86_64, ARM64)
  - macOS (Intel, Apple Silicon)
  - Windows (x86_64)
  - Termux (Android)
- **Installers**:
  - `install.sh` for Linux/macOS/WSL/Termux
  - `install.ps1` for native Windows

### Documentation

- `README.md` — Project overview and quick start
- `docs/COMMANDS.md` — Full command reference
- `docs/MANIFEST.md` — `sino.toml` format reference
- `docs/FFI.md` — Foreign Function Interface guide (C, C++, Assembly, Rust)
- `docs/EXAMPLES.md` — Step-by-step tutorials

### Known Limitations

- **Registry** is not yet launched. Use GitHub dependencies for distribution.
- **`sino publish`** is a stub — instructs users to use GitHub releases.
- **Incremental builds** not yet implemented — all files recompile on each build.
- **Parallel compilation** not yet implemented — files compile sequentially.
- **LSP server** not included — only metadata is generated for future LSP integration.
- **Benchmarks** not yet supported in `sino test`.
- **Dependency resolution** does not yet resolve transitive dependencies automatically.

---

## Version History

| Version | Release Date | Notes |
|---------|--------------|-------|
| v1.0.0  | 2026-08-01   | Initial public release |
