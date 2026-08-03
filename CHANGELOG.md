# Changelog

All notable changes to mozhi-pkg will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v1.2.0] — 2026-08-01

### Added — Unified `mozhi` Command Dispatcher (Go-style)

Following the Go/Cargo model, `mozhi` is now a **unified dispatcher** that routes
all Mozhi-related commands through a single entry point. This resolves the
naming conflict between the Mozhi interpreter and the mozhi-pkg package manager.

- **Unified dispatcher** — `mozhi` now handles both interpreter and package
  manager commands:
  - `mozhi` (no args) → start REPL (via interpreter)
  - `mozhi file.mz` → run file (via interpreter)
  - `mozhi <subcommand>` → mozhi-pkg subcommand (build, test, add, etc.)
  - `mozhi -v / --version` → mozhi-pkg version
  - `mozhi -h / --help` → mozhi-pkg help
  - `mozhi <unknown-word>` → try as filename via interpreter (backwards compatible)

- **Interpreter renamed to `mozhi-interpreter`** — The Mozhi interpreter binary
  is now installed as `mozhi-interpreter` (not `mozhi`) to avoid conflict with
  the dispatcher. The `mozhi` command is now the Python dispatcher script.

- **Migration logic** — The mozhi-pkg installer automatically detects if an old
  interpreter binary is installed as `mozhi` and renames it to `mozhi-interpreter`
  before installing the dispatcher. This provides a seamless upgrade path for
  existing users.

- **Cross-platform interpreter discovery** — `find_mozhi_interpreter()` now
  handles Windows (`.exe` suffix) and checks multiple locations:
  1. `$MOZHI_INTERPRETER` env var
  2. `~/.mozhi/bin/mozhi-interpreter` (or `.exe` on Windows)
  3. `mozhi-interpreter` on PATH
  4. `mozhi` on PATH (skipping the mozhi-pkg script itself)

### Fixed

- **Critical: `mozhi version` / `mozhi help` / `mozhi search` returned "Cannot open file"** —
  This happened because the Mozhi interpreter was installed as `mozhi`, so running
  `mozhi version` made the interpreter try to open `version` as a script file.
  The unified dispatcher now intercepts known subcommands before they reach the
  interpreter.

### Changed

- mozhi-doc installer now installs the interpreter as `mozhi-interpreter`
- mozhi-pkg installer now installs the dispatcher as `mozhi`
- mozhi-pkg installer now warns if the interpreter is not installed
- Version bumped from 1.1.0 → 1.2.0

---

## [v1.1.0] — 2026-08-01

### Added — Modern CLI UI/UX

Complete redesign of the command-line interface with a polished developer
experience comparable to Rust Cargo, Clang, and Go tooling.

- **`mozhi_ui.py` module** — A comprehensive UI library with:
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
  - `mozhi new <project>` — Create a new binary project (alias for `init --bin`)
  - `mozhi repl` — Start the interactive Mozhi REPL
  - `mozhi bench` — Run benchmarks (Lexer, Parser, Compiler, Runtime, Memory)
  - `mozhi fmt` — Format source files (normalize indentation, strip trailing whitespace)
  - `mozhi lint` — Lint source files (unused variable detection with `SN2001` warning)
  - `mozhi search <query>` — Search packages
  - `mozhi uninstall <name>` — Uninstall a package
  - `mozhi login` — Log in to the registry (stub with credential storage)
  - `mozhi logout` — Log out of the registry
  - `mozhi doctor` — Check the Mozhi environment (compiler, package manager, runtime, libraries, network)

- **Diagnostic UI** — All errors, warnings, notes, and help now render with:
  - Error codes (`SN1001` for unknown variable, `SN2001` for unused variable, etc.)
  - Source file context with line numbers and carets pointing to the error
  - Hints and suggestions
  - Documentation URLs
  - Severity-specific colors (red for errors, yellow for warnings, blue for notes/help)

- **Startup banner** — Unicode box-drawn banner shown by `mozhi version`, `mozhi help`, `mozhi doctor`, and `mozhi build --banner`:
  ```
  ┌────────────────────────┐
  │     Mozhi Compiler      │
  │     Version 1.1.0      │
  │  Fast • Safe • Modern  │
  └────────────────────────┘
  ```

- **Build progress** — `mozhi build` now shows a step list:
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

- **Interpreter discovery** — `find_mozhi_interpreter()` looks for the Mozhi
  interpreter binary at:
  1. `$MOZHI_INTERPRETER` env var
  2. `~/.mozhi/bin/mozhi-interpreter`
  3. `mozhi-interpreter` on PATH
  4. `mozhi` on PATH (skipping the mozhi-pkg script itself)

### Changed

- `mozhi version` now shows the banner + toolchain info + detected compilers
- `mozhi help` now shows the banner + formatted command list + examples + options
- `mozhi build` now shows a step list with timing and output path
- `mozhi test` now uses the polished UI for pass/fail messages
- `mozhi install` now uses the polished UI for resolve/success messages
- `mozhi clean` now shows a single success message with removed artifacts
- `mozhi run` now uses `find_mozhi_interpreter()` instead of `shutil.which("mozhi")`
- All `info`, `ok`, `warn`, `error` helpers now delegate to the `mozhi_ui` module
- Version bumped from 1.0.0 → 1.1.0

### Fixed

- Fixed `mozhi test` and `mozhi run` failing when `mozhi` on PATH resolves to the mozhi-pkg script itself (now skips Python scripts when looking for the interpreter binary)

---

## [v1.0.0] — 2026-08-01

### Added

- **Initial release** of the Mozhi Package Manager.
- **Commands**:
  - `mozhi init --lib [name]` — Initialize a library project
  - `mozhi init --bin [name]` — Initialize a binary project
  - `mozhi build [--static|--shared|--native]` — Build the project
  - `mozhi install` — Install dependencies from `mozhi.toml`
  - `mozhi add <source> [version]` — Add a dependency
  - `mozhi remove <name>` — Remove a dependency
  - `mozhi update [name...]` — Update dependencies
  - `mozhi test` — Run tests in `tests/`
  - `mozhi doc` — Generate API documentation + VS Code/LSP metadata
  - `mozhi publish` — Publish stub (instructs to use GitHub releases)
  - `mozhi clean` — Remove build artifacts
  - `mozhi run [args...]` — Run `src/main.mz`
  - `mozhi version` / `mozhi --version` — Show version and detected compilers
  - `mozhi help` / `mozhi --help` — Show help
- **Manifest format** (`mozhi.toml`):
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
  - Native Mozhi library output (ZIP → `<name>.silib`)
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
  - Dependency caching in `~/.mozhi/cache/github/`
  - Lock file (`mozhi.lock`) with resolved versions
  - Symlinked dependencies in `mozhi_modules/`
- **Documentation generation**:
  - `docs/API.md` from `public func` declarations in `.mz` files
  - `.vscode/mozhi-lsp.json` for IDE integration
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
- `docs/MANIFEST.md` — `mozhi.toml` format reference
- `docs/FFI.md` — Foreign Function Interface guide (C, C++, Assembly, Rust)
- `docs/EXAMPLES.md` — Step-by-step tutorials

### Known Limitations

- **Registry** is not yet launched. Use GitHub dependencies for distribution.
- **`mozhi publish`** is a stub — instructs users to use GitHub releases.
- **Incremental builds** not yet implemented — all files recompile on each build.
- **Parallel compilation** not yet implemented — files compile sequentially.
- **LSP server** not included — only metadata is generated for future LSP integration.
- **Benchmarks** not yet supported in `mozhi test`.
- **Dependency resolution** does not yet resolve transitive dependencies automatically.

---

## Version History

| Version | Release Date | Notes |
|---------|--------------|-------|
| v1.0.0  | 2026-08-01   | Initial public release |
