# Changelog

All notable changes to sino-pkg will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
