# Manifest Format (`sino.toml`)

The `sino.toml` file is the manifest for a Sino package. It describes the package's metadata, dependencies, and build configuration.

---

## Example

```toml
name = "math"
version = "1.0.0"
authors = ["Alice <alice@example.com>", "Bob"]
license = "MIT"
description = "A math library for Sino"

[dependencies]
"github:alice/vector" = "^1.0.0"
"github:bob/matrix" = "~2.1.0"
"local:../utils" = "*"

[build]
c = true
cpp = true
assembly = true
rust = false

[build.output]
type = "static"
```

---

## Fields

### Package Metadata

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | ✅ Yes | Package name (lowercase, no spaces) |
| `version` | string | ✅ Yes | Semantic version (e.g., `1.0.0`) |
| `authors` | array of strings | No | List of authors |
| `license` | string | No | SPDX license identifier (e.g., `MIT`, `Apache-2.0`) |
| `description` | string | No | Short description |

### `[dependencies]`

A table of dependencies. Keys are source identifiers, values are version requirements.

| Source Format | Example |
|---------------|---------|
| `github:owner/repo` | `"github:alice/vector" = "^1.0.0"` |
| `local:path` | `"local:../utils" = "*"` |
| `name` (registry, future) | `serde = "1.0"` |

### `[build]`

Build configuration for foreign code.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `c` | boolean | `false` | Compile `native/*.c` files |
| `cpp` | boolean | `false` | Compile `native/*.cpp` files |
| `assembly` | boolean | `false` | Compile `native/*.S` files |
| `rust` | boolean | `false` | Compile `native/*.rs` files |

### `[build.output]`

Output type for `sino build`.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `type` | string | `"static"` | One of: `static`, `shared`, `native` |

---

## Output Types

### `static`

Produces a static library archive:

| Platform | Output |
|----------|--------|
| Linux | `lib<name>.a` |
| macOS | `lib<name>.a` |
| Windows | `lib<name>.a` (MinGW) or `<name>.lib` (MSVC) |

Also produces `<name>.silib` (native Sino package).

### `shared`

Produces a shared/dynamic library:

| Platform | Output |
|----------|--------|
| Linux | `lib<name>.so` |
| macOS | `lib<name>.dylib` |
| Windows | `<name>.dll` |

Also produces `<name>.silib`.

### `native`

Produces only the native Sino library: `<name>.silib` (a ZIP archive of `.si` files + `sino.toml`). No C/C++/ASM/Rust compilation occurs, even if `[build]` flags are set.

---

## Version Requirements

See [Semantic Versioning](../README.md#semantic-versioning) in the README.

| Operator | Example | Matches |
|----------|---------|---------|
| `^` | `^1.2.3` | `>=1.2.3, <2.0.0` |
| `~` | `~1.2.3` | `>=1.2.3, <1.3.0` |
| `>=` | `>=1.0.0` | `>=1.0.0` |
| `>` | `>1.0.0` | `>1.0.0` |
| `<=` | `<=1.5.0` | `<=1.5.0` |
| `<` | `<2.0.0` | `<2.0.0` |
| `=` | `=1.2.3` | exactly `1.2.3` |
| `*` | `*` | any version |
| (none) | `1.2.3` | exactly `1.2.3` |

---

## Minimal Manifest

The smallest valid `sino.toml`:

```toml
name = "mylib"
version = "0.1.0"
```

All other fields have sensible defaults.

---

## Binary Project Manifest

For an executable (`sino init --bin`):

```toml
name = "myapp"
version = "0.1.0"
description = "My application"

[build]
c = false
cpp = false
assembly = false
rust = false

[build.output]
type = "native"
```

Binary projects typically use `type = "native"` (just Sino source, no foreign code).

---

## Validation Rules

- `name` must be lowercase, alphanumeric, and may contain hyphens. No spaces.
- `version` must be a valid semantic version (e.g., `1.0.0`, `0.1.0-beta`).
- `type` must be one of: `static`, `shared`, `native`.
- Dependency sources must start with `github:`, `local:`, or be a registry name.
