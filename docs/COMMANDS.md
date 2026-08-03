# Command Reference

Complete reference for all `mozhi` commands.

---

## `mozhi init`

Initialize a new Mozhi project.

### Usage

```
mozhi init [--lib|--bin] [name]
```

### Options

| Option | Description |
|--------|-------------|
| `--lib` | Create a library project (default) |
| `--bin` | Create a binary (executable) project |
| `--binary` | Alias for `--bin` |
| `--app` | Alias for `--bin` |
| `--library` | Alias for `--lib` |

### Examples

```bash
# Create a library in a new directory
mozhi init --lib mymath

# Create a binary using the current directory name
mozhi init --bin

# Create a library in the current directory
cd mylib && mozhi init --lib
```

### Library Project Layout

```
mylib/
├── mozhi.toml
├── src/
│   ├── mylib.mz
│   └── vector.mz
├── native/
│   ├── mylib.c
│   ├── mylib.cpp
│   └── simd.S
├── include/
│   └── mylib.h
├── tests/
│   └── test_lib.mz
├── examples/
│   └── demo.mz
├── README.md
└── LICENSE
```

### Binary Project Layout

```
myapp/
├── mozhi.toml
├── src/
│   └── main.mz
└── README.md
```

---

## `mozhi build`

Build the project according to its `mozhi.toml`.

### Usage

```
mozhi build [--static|--shared|--native]
```

### Options

| Option | Description |
|--------|-------------|
| `--static` | Build a static library (`lib<name>.a`) |
| `--shared` | Build a shared library (`lib<name>.so`/`.dylib`/`.dll`) |
| `--native` | Build a native Mozhi library (`<name>.silib`) |

If no option is given, uses the `[build.output] type` from `mozhi.toml`.

### Build Process

1. **Clean** stale object files in `build/`
2. **Compile C** files (`native/*.c`) with `cc -c -O2 -fPIC`
3. **Compile C++** files (`native/*.cpp`) with `c++ -c -O2 -fPIC`
4. **Compile Assembly** files (`native/*.S`) with `cc -c`
5. **Compile Rust** files (`native/*.rs`) with `rustc --crate-type staticlib`
6. **Link** all object files into the output:
   - Static: `ar rcs lib<name>.a *.o`
   - Shared: `cc -shared -o lib<name>.so *.o`
   - Native: `zip` of `.mz` files + manifest
7. For static/shared, also build a `.silib` package

### Output Location

All build artifacts go to `dist/`:

```
dist/
├── libmylib.a         # static library
├── libmylib.so        # shared library (Linux)
├── libmylib.dylib     # shared library (macOS)
├── mylib.dll          # shared library (Windows)
└── mylib.silib        # native Mozhi library (zip)
```

---

## `mozhi install`

Install all dependencies listed in `mozhi.toml`.

### Usage

```
mozhi install
```

### Process

1. Read `[dependencies]` from `mozhi.toml`
2. For each dependency:
   - Resolve the version (GitHub clone, local path, or registry)
   - Cache the resolved package in `~/.mozhi/cache/`
   - Create a symlink in `mozhi_modules/`
3. Write the resolved versions to `mozhi.lock`

### Example

```bash
$ mozhi install
[info]  Installing 2 dependencies...
  → Resolving github:crossberry-in/mozhi-math (^1.0.0)...
[ok]    github:crossberry-in/mozhi-math -> v1.0.0
  → Resolving local:../mylib (*)...
[ok]    local:../mylib -> v0.2.0
[ok]    Installed 2 dependencies. Lock file: mozhi.lock
```

---

## `mozhi add`

Add a dependency to `mozhi.toml`.

### Usage

```
mozhi add <source> [version]
```

### Sources

| Source Format | Description |
|---------------|-------------|
| `github:owner/repo` | GitHub repository (latest) |
| `github:owner/repo@tag` | GitHub repository at specific tag |
| `github:owner/repo@1.2.0` | GitHub repository at version tag |
| `local:../path` | Local path dependency |
| `name` | Registry package (future) |

### Examples

```bash
# GitHub, latest version
mozhi add github:crossberry-in/mozhi-math

# GitHub, specific version
mozhi add github:crossberry-in/mozhi-math 1.0.0
mozhi add github:crossberry-in/mozhi-math ^1.0.0

# GitHub, pinned via @ syntax
mozhi add github:crossberry-in/mozhi-math@1.2.0

# Local path
mozhi add local:../mylib
```

---

## `mozhi remove`

Remove a dependency from `mozhi.toml`.

### Usage

```
mozhi remove <name>
```

### Examples

```bash
mozhi remove github:crossberry-in/mozhi-math
mozhi remove local:../mylib
mozhi remove serde
```

---

## `mozhi update`

Update dependencies.

### Usage

```
mozhi update [name...]
```

### Examples

```bash
# Update all dependencies
mozhi update

# Update specific packages
mozhi update github:crossberry-in/mozhi-math
```

---

## `mozhi test`

Run all test files in `tests/`.

### Usage

```
mozhi test
```

### Process

1. Find all `*.mz` files in `tests/`
2. Run each with the `mozhi` interpreter
3. Report pass/fail count

### Example

```bash
$ mozhi test
[info]  Running 2 test files...
  → Running test_lib.mz...
PASS: test_add
PASS: test_multiply
All tests passed!
[ok]    All 2 test files passed.
```

---

## `mozhi doc`

Generate documentation from source files.

### Usage

```
mozhi doc
```

### Output

- `docs/API.md` — API reference extracted from `public func` declarations
- `.vscode/mozhi-lsp.json` — VS Code / LSP metadata for IDE integration

### Example

```markdown
# mylib API

## mylib.mz

### `add(a, b)`

Adds two numbers.

---

### `multiply(a, b)`

Multiplies two numbers.
```

---

## `mozhi publish`

Publish to the registry (currently a stub).

### Usage

```
mozhi publish
```

### Current Behavior

Prints instructions for distributing via GitHub releases:

```
[warn]  'mozhi publish' is not yet implemented for the public registry.
[info]  To distribute mylib v1.0.0:
  1. Push to GitHub
  2. Tag a release: git tag v1.0.0
  3. Others can install with: mozhi add github:you/mylib
```

---

## `mozhi clean`

Remove all build artifacts.

### Usage

```
mozhi clean
```

Removes:
- `build/` directory
- `dist/` directory
- `mozhi_modules/` directory
- `mozhi.lock` file

---

## `mozhi run`

Run the project's main script (`src/main.mz`).

### Usage

```
mozhi run [args...]
```

### Example

```bash
$ mozhi run
Hello from myapp!
Sum:  30
```

---

## `mozhi version`

Show version and detected compilers.

### Usage

```
mozhi version
mozhi --version
mozhi -v
```

### Example

```
mozhi-pkg 1.0.0
Mozhi Package Manager
Compilers: c=cc, cpp=c++, asm=cc, ar=ar, git=git
Platform:  linux/x86_64
```

---

## `mozhi help`

Show help.

### Usage

```
mozhi help
mozhi --help
mozhi -h
mozhi
```
