# Mozhi Package Manager (mozhi-pkg)

<div align="center">

**A production-ready package manager for the Mozhi programming language.**

Build, dependency, and release tooling comparable to Cargo, Go Modules, or Swift Package Manager — with full C/C++/Assembly/Rust FFI support.

[![Version: v1.0.0](https://img.shields.io/badge/Version-v1.0.0-green.svg)](https://github.com/crossberry-in/mozhi-pkg/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform: Cross-platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows%20%7C%20Termux-blue.svg)](#platform-support)

</div>

---

## Overview

**mozhi-pkg** is the official package manager for the [Mozhi programming language](https://github.com/crossberry-in/mozhi-doc). It provides:

- **Native Mozhi libraries** (`.silib` packages)
- **Foreign Function Interface** to C, C++, Assembly, and Rust
- **Static libraries** (`lib<name>.a`)
- **Shared libraries** (`lib<name>.so` / `lib<name>.dylib` / `<name>.dll`)
- **GitHub-hosted dependencies** (`mozhi add github:owner/repo`)
- **Local path dependencies** (`mozhi add local:../mylib`)
- **Semantic versioning** with `^`, `~`, `>=`, `<`, `*` operators
- **Lock files** (`mozhi.lock`) for reproducible builds
- **Offline cache** (`~/.mozhi/cache/`)
- **Test runner** (`mozhi test`)
- **Documentation generator** (`mozhi doc`)
- **VS Code / LSP metadata generation**

---

## Quick Start

### Install

**Linux / macOS / WSL / Termux:**

```bash
curl -fsSL https://github.com/crossberry-in/mozhi-pkg/raw/main/install.sh | bash
```

**Windows (PowerShell):**

```powershell
irm https://github.com/crossberry-in/mozhi-pkg/raw/main/install.ps1 | iex
```

### Create a Library

```bash
mozhi init --lib mymath
cd mymath
mozhi build          # builds libmymath.a + mymath.silib
mozhi test           # runs tests in tests/
mozhi doc            # generates docs/API.md
```

### Create a Binary

```bash
mozhi init --bin myapp
cd myapp
mozhi run            # runs src/main.mz
```

### Add Dependencies

```bash
# From GitHub (clones, caches, resolves version)
mozhi add github:crossberry-in/mozhi-math@1.0.0
mozhi install

# From local path
mozhi add local:../mylib
mozhi install

# Remove
mozhi remove github:crossberry-in/mozhi-math
```

---

## Commands

| Command | Description |
|---------|-------------|
| `mozhi init --lib [name]` | Initialize a new library project |
| `mozhi init --bin [name]` | Initialize a new binary project |
| `mozhi build [--static\|--shared\|--native]` | Build the project |
| `mozhi install` | Install dependencies from `mozhi.toml` |
| `mozhi add <source> [version]` | Add a dependency |
| `mozhi remove <name>` | Remove a dependency |
| `mozhi update [name...]` | Update dependencies |
| `mozhi test` | Run tests in `tests/` |
| `mozhi doc` | Generate documentation |
| `mozhi publish` | Publish (stub — see [Publishing](#publishing)) |
| `mozhi clean` | Remove build artifacts |
| `mozhi run [args...]` | Run `src/main.mz` |
| `mozhi version` | Show version and detected compilers |
| `mozhi help` | Show help |

See [COMMANDS.md](docs/COMMANDS.md) for full details.

---

## Project Structure

A Mozhi library project created by `mozhi init --lib`:

```
mylib/
├── mozhi.toml          # Package manifest
├── src/               # Mozhi source files (.mz)
│   ├── mylib.mz       # Main module
│   └── vector.mz      # Sub-module (import mylib.vector)
├── native/            # Foreign function implementations
│   ├── mylib.c        # C functions
│   ├── mylib.cpp      # C++ functions (extern "C")
│   └── simd.S         # Assembly functions
├── include/           # C/C++ headers
│   └── mylib.h
├── tests/             # Test files (.mz)
│   └── test_lib.mz
├── examples/          # Example programs
│   └── demo.mz
├── README.md
└── LICENSE
```

---

## Manifest (`mozhi.toml`)

```toml
name = "math"
version = "1.0.0"
authors = ["Author <author@example.com>"]
license = "MIT"
description = "Math Library"

[dependencies]
"github:owner/repo" = "1.2.0"
"local:../mylib" = "*"
serde = "1.0"

[build]
c = true
cpp = true
assembly = true
rust = false

[build.output]
type = "static"   # static | shared | native
```

See [MANIFEST.md](docs/MANIFEST.md) for full reference.

---

## Foreign Function Interface (FFI)

Mozhi libraries can call C, C++, Assembly, and Rust functions through the FFI.

### C

```c
// native/math.c
int c_add(int a, int b) {
    return a + b;
}
```

### C++

```cpp
// native/math.cpp
#include <cmath>
extern "C" {
    double cpp_sqrt(double x) { return std::sqrt(x); }
}
```

### Assembly

```asm
# native/simd.S
.global asm_square
asm_square:
    mov %rdi, %rax
    imul %rdi, %rax
    ret
```

### Rust

```rust
// native/math.rs
#[no_mangle]
pub extern "C" fn rs_factorial(n: u64) -> u64 {
    (1..=n).product()
}
```

See [FFI.md](docs/FFI.md) for full details.

---

## Dependency Sources

### GitHub

```bash
mozhi add github:owner/repo           # latest
mozhi add github:owner/repo@1.2.0     # specific tag
mozhi add github:owner/repo@v2.0.0    # tag with v prefix
```

The package manager:
1. Clones the repository (shallow clone)
2. Reads its `mozhi.toml`
3. Caches it in `~/.mozhi/cache/github/`
4. Creates a symlink in `mozhi_modules/`
5. Records the resolved version in `mozhi.lock`

### Local Path

```bash
mozhi add local:../mylib
```

Useful during development — changes to the local library are immediately visible.

### Registry (Future)

```bash
mozhi add serde 1.0
```

The public registry is not yet launched. For now, use GitHub dependencies.

---

## Semantic Versioning

mozhi-pkg supports the following version requirement operators:

| Operator | Example | Matches |
|----------|---------|---------|
| `^` (caret) | `^1.2.3` | `>=1.2.3, <2.0.0` (compatible) |
| `~` (tilde) | `~1.2.3` | `>=1.2.3, <1.3.0` (patch only) |
| `>=` | `>=1.0.0` | `>=1.0.0` |
| `>` | `>1.0.0` | `>1.0.0` |
| `<=` | `<=1.5.0` | `<=1.5.0` |
| `<` | `<2.0.0` | `<2.0.0` |
| `=` | `=1.2.3` | exactly `1.2.3` |
| `*` or `""` | `*` | any version |
| (none) | `1.2.3` | exactly `1.2.3` |

---

## Lock File (`mozhi.lock`)

After `mozhi install`, a lock file is generated:

```json
{
  "version": 1,
  "updated": "2026-08-01T12:00:00+00:00",
  "packages": {
    "github:owner/repo": {
      "version": "1.2.0",
      "source": "/home/user/.mozhi/cache/github/owner_repo@1.2.0",
      "resolved_at": "2026-08-01T12:00:00+00:00"
    }
  }
}
```

Commit `mozhi.lock` to your repository for reproducible builds.

---

## Platform Support

| Platform | Architecture | Status |
|----------|--------------|--------|
| Linux | x86_64 | ✅ Supported |
| Linux | ARM64 (aarch64) | ✅ Supported |
| macOS | Intel | ✅ Supported |
| macOS | Apple Silicon | ✅ Supported |
| Windows | x86_64 | ✅ Supported (via Python) |
| Termux (Android) | ARM64 | ✅ Supported |

**Requirements:**
- Python 3.8+ (preinstalled on most systems)
- For C/C++/ASM builds: `gcc`/`clang` and `ar`
- For Rust FFI: `rustc`
- For GitHub dependencies: `git`

---

## Publishing

`mozhi publish` is currently a stub. To distribute your library:

1. Push your project to GitHub
2. Tag a release: `git tag v1.0.0 && git push origin v1.0.0`
3. Others can install it with: `mozhi add github:yourname/yourlib@1.0.0`

A public registry is planned for a future release.

---

## Documentation

- [Command Reference](docs/COMMANDS.md)
- [Manifest Format](docs/MANIFEST.md)
- [FFI Guide](docs/FFI.md)
- [Examples & Tutorials](docs/EXAMPLES.md)

---

## License

MIT — see [LICENSE](LICENSE).

---

## Related

- [Mozhi Language](https://github.com/crossberry-in/mozhi-doc) — The Mozhi interpreter and language documentation
- [Mozhi Language (Source)](https://github.com/crossberry-in/mozhi-lang) — Closed-source interpreter source (private)
