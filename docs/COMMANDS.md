# Command Reference

Complete reference for all `sino` commands.

---

## `sino init`

Initialize a new Sino project.

### Usage

```
sino init [--lib|--bin] [name]
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
sino init --lib mymath

# Create a binary using the current directory name
sino init --bin

# Create a library in the current directory
cd mylib && sino init --lib
```

### Library Project Layout

```
mylib/
├── sino.toml
├── src/
│   ├── mylib.si
│   └── vector.si
├── native/
│   ├── mylib.c
│   ├── mylib.cpp
│   └── simd.S
├── include/
│   └── mylib.h
├── tests/
│   └── test_lib.si
├── examples/
│   └── demo.si
├── README.md
└── LICENSE
```

### Binary Project Layout

```
myapp/
├── sino.toml
├── src/
│   └── main.si
└── README.md
```

---

## `sino build`

Build the project according to its `sino.toml`.

### Usage

```
sino build [--static|--shared|--native]
```

### Options

| Option | Description |
|--------|-------------|
| `--static` | Build a static library (`lib<name>.a`) |
| `--shared` | Build a shared library (`lib<name>.so`/`.dylib`/`.dll`) |
| `--native` | Build a native Sino library (`<name>.silib`) |

If no option is given, uses the `[build.output] type` from `sino.toml`.

### Build Process

1. **Clean** stale object files in `build/`
2. **Compile C** files (`native/*.c`) with `cc -c -O2 -fPIC`
3. **Compile C++** files (`native/*.cpp`) with `c++ -c -O2 -fPIC`
4. **Compile Assembly** files (`native/*.S`) with `cc -c`
5. **Compile Rust** files (`native/*.rs`) with `rustc --crate-type staticlib`
6. **Link** all object files into the output:
   - Static: `ar rcs lib<name>.a *.o`
   - Shared: `cc -shared -o lib<name>.so *.o`
   - Native: `zip` of `.si` files + manifest
7. For static/shared, also build a `.silib` package

### Output Location

All build artifacts go to `dist/`:

```
dist/
├── libmylib.a         # static library
├── libmylib.so        # shared library (Linux)
├── libmylib.dylib     # shared library (macOS)
├── mylib.dll          # shared library (Windows)
└── mylib.silib        # native Sino library (zip)
```

---

## `sino install`

Install all dependencies listed in `sino.toml`.

### Usage

```
sino install
```

### Process

1. Read `[dependencies]` from `sino.toml`
2. For each dependency:
   - Resolve the version (GitHub clone, local path, or registry)
   - Cache the resolved package in `~/.sino/cache/`
   - Create a symlink in `sino_modules/`
3. Write the resolved versions to `sino.lock`

### Example

```bash
$ sino install
[info]  Installing 2 dependencies...
  → Resolving github:crossberry-in/sino-math (^1.0.0)...
[ok]    github:crossberry-in/sino-math -> v1.0.0
  → Resolving local:../mylib (*)...
[ok]    local:../mylib -> v0.2.0
[ok]    Installed 2 dependencies. Lock file: sino.lock
```

---

## `sino add`

Add a dependency to `sino.toml`.

### Usage

```
sino add <source> [version]
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
sino add github:crossberry-in/sino-math

# GitHub, specific version
sino add github:crossberry-in/sino-math 1.0.0
sino add github:crossberry-in/sino-math ^1.0.0

# GitHub, pinned via @ syntax
sino add github:crossberry-in/sino-math@1.2.0

# Local path
sino add local:../mylib
```

---

## `sino remove`

Remove a dependency from `sino.toml`.

### Usage

```
sino remove <name>
```

### Examples

```bash
sino remove github:crossberry-in/sino-math
sino remove local:../mylib
sino remove serde
```

---

## `sino update`

Update dependencies.

### Usage

```
sino update [name...]
```

### Examples

```bash
# Update all dependencies
sino update

# Update specific packages
sino update github:crossberry-in/sino-math
```

---

## `sino test`

Run all test files in `tests/`.

### Usage

```
sino test
```

### Process

1. Find all `*.si` files in `tests/`
2. Run each with the `sino` interpreter
3. Report pass/fail count

### Example

```bash
$ sino test
[info]  Running 2 test files...
  → Running test_lib.si...
PASS: test_add
PASS: test_multiply
All tests passed!
[ok]    All 2 test files passed.
```

---

## `sino doc`

Generate documentation from source files.

### Usage

```
sino doc
```

### Output

- `docs/API.md` — API reference extracted from `public func` declarations
- `.vscode/sino-lsp.json` — VS Code / LSP metadata for IDE integration

### Example

```markdown
# mylib API

## mylib.si

### `add(a, b)`

Adds two numbers.

---

### `multiply(a, b)`

Multiplies two numbers.
```

---

## `sino publish`

Publish to the registry (currently a stub).

### Usage

```
sino publish
```

### Current Behavior

Prints instructions for distributing via GitHub releases:

```
[warn]  'sino publish' is not yet implemented for the public registry.
[info]  To distribute mylib v1.0.0:
  1. Push to GitHub
  2. Tag a release: git tag v1.0.0
  3. Others can install with: sino add github:you/mylib
```

---

## `sino clean`

Remove all build artifacts.

### Usage

```
sino clean
```

Removes:
- `build/` directory
- `dist/` directory
- `sino_modules/` directory
- `sino.lock` file

---

## `sino run`

Run the project's main script (`src/main.si`).

### Usage

```
sino run [args...]
```

### Example

```bash
$ sino run
Hello from myapp!
Sum:  30
```

---

## `sino version`

Show version and detected compilers.

### Usage

```
sino version
sino --version
sino -v
```

### Example

```
sino-pkg 1.0.0
Sino Package Manager
Compilers: c=cc, cpp=c++, asm=cc, ar=ar, git=git
Platform:  linux/x86_64
```

---

## `sino help`

Show help.

### Usage

```
sino help
sino --help
sino -h
sino
```
