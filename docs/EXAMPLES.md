# Examples & Tutorials

Step-by-step tutorials for using mozhi-pkg.

---

## Tutorial 1: Create a Pure Mozhi Library

### Step 1: Initialize

```bash
mozhi init --lib greet
cd greet
```

### Step 2: Edit `src/greet.mz`

```mozhi
# Greet library

public func hello(name):
    echo "Hello, ", name, "!"
end

public func goodbye(name):
    echo "Goodbye, ", name, "!"
end
```

### Step 3: Build

```bash
mozhi build --native
```

Output:
```
[info]  Building greet v0.1.0...
  → PACK greet.silib
[ok]    Built native library: dist/greet.silib
```

### Step 4: Test

Edit `tests/test_greet.mz`:

```mozhi
import greet

func test_hello():
    hello("World")  # Should print: Hello, World!
    echo "PASS: test_hello"
    return 0
end

test_hello()
```

Run:

```bash
mozhi test
```

### Step 5: Document

```bash
mozhi doc
```

View `docs/API.md`:

```markdown
# greet API

## greet.mz

### `hello(name)`

### `goodbye(name)`
```

---

## Tutorial 2: Create a Library with C FFI

### Step 1: Initialize

```bash
mozhi init --lib fastmath
cd fastmath
```

### Step 2: Edit `native/fastmath.c`

```c
/* Fast math in C */

int fast_add(int a, int b) {
    return a + b;
}

int fast_mul(int a, int b) {
    return a * b;
}

/* Compute sum of array */
int fast_sum(int* arr, int n) {
    int s = 0;
    for (int i = 0; i < n; i++) {
        s += arr[i];
    }
    return s;
}
```

### Step 3: Edit `src/fastmath.mz`

```mozhi
# Fastmath library — Mozhi wrappers for C functions

public func add(a, b):
    return c_add(a, b)
end

public func multiply(a, b):
    return c_mul(a, b)
end
```

### Step 4: Build

```bash
mozhi build --static
```

Output:
```
[info]  Building fastmath v0.1.0...
  → CC  fastmath.c
  → AR  libfastmath.a
[ok]    Built static library: dist/libfastmath.a
  → PACK fastmath.silib
[ok]    Also built native package: dist/fastmath.silib
```

### Step 5: Build as Shared Library

```bash
mozhi build --shared
```

Output:
```
[info]  Building fastmath v0.1.0...
  → CC  fastmath.c
  → LINK libfastmath.so
[ok]    Built shared library: dist/libfastmath.so
```

---

## Tutorial 3: Use a GitHub Dependency

### Step 1: Create a Library and Push to GitHub

```bash
mozhi init --lib myutils
cd myutils
echo 'public func double(x):
    return x * 2
end' > src/myutils.mz

git init
git add -A
git commit -m "Initial commit"
git tag v1.0.0
git remote add origin https://github.com/yourname/myutils.git
git push -u origin main
git push origin v1.0.0
```

### Step 2: Create Another Project That Depends On It

```bash
cd ..
mozhi init --bin myapp
cd myapp
```

### Step 3: Add the Dependency

```bash
mozhi add github:yourname/myutils@1.0.0
```

This adds to `mozhi.toml`:

```toml
[dependencies]
"github:yourname/myutils" = "1.0.0"
```

### Step 4: Install

```bash
mozhi install
```

Output:
```
[info]  Installing 1 dependencies...
  → Resolving github:yourname/myutils (1.0.0)...
[ok]    github:yourname/myutils -> v1.0.0
[ok]    Installed 1 dependencies. Lock file: mozhi.lock
```

### Step 5: Use It

Edit `src/main.mz`:

```mozhi
import myutils

func main():
    echo double(21)  # 42
end

main()
```

Run:

```bash
mozhi run
```

---

## Tutorial 4: Multi-Language Library

Mix C, C++, Assembly, and Rust in one library.

### Step 1: Initialize

```bash
mozhi init --lib polyglot
cd polyglot
```

### Step 2: Write C Code

`native/core.c`:

```c
int c_add(int a, int b) { return a + b; }
```

### Step 3: Write C++ Code

`native/algo.cpp`:

```cpp
#include <algorithm>
#include <vector>

extern "C" void cpp_sort(int* arr, int n) {
    std::vector<int> v(arr, arr + n);
    std::sort(v.begin(), v.end());
    for (int i = 0; i < n; i++) arr[i] = v[i];
}
```

### Step 4: Write Assembly (x86_64)

`native/simd.S`:

```asm
.global asm_square
asm_square:
    mov %rdi, %rax
    imul %rdi, %rax
    ret
```

### Step 5: Write Rust Code

`native/safe.rs`:

```rust
#[no_mangle]
pub extern "C" fn rs_factorial(n: u64) -> u64 {
    (1..=n).product()
}
```

### Step 6: Configure `mozhi.toml`

```toml
name = "polyglot"
version = "0.1.0"

[build]
c = true
cpp = true
assembly = true
rust = true

[build.output]
type = "static"
```

### Step 7: Build

```bash
mozhi build
```

Output:
```
[info]  Building polyglot v0.1.0...
  → CC  core.c
  → C++ algo.cpp
  → ASM simd.S
  → RUST safe.rs
  → AR  libpolyglot.a
[ok]    Built static library: dist/libpolyglot.a
```

The resulting `libpolyglot.a` contains all four languages' object files.

---

## Tutorial 5: Local Path Dependency

For development, link to a local library without publishing.

### Step 1: Create Two Libraries

```bash
mkdir myworkspace && cd myworkspace
mozhi init --lib utils
mozhi init --lib app
```

### Step 2: Add Local Dependency

```bash
cd app
mozhi add local:../utils
mozhi install
```

### Step 3: Edit and Iterate

Edit `../utils/src/utils.mz` — changes are immediately visible to `app/` because `mozhi_modules/utils` is a symlink.

---

## Tutorial 6: Testing

### Step 1: Write Tests

`tests/test_math.mz`:

```mozhi
# Unit tests for math library

import math

func assert_eq(actual, expected, name):
    if actual != expected:
        echo "FAIL: ", name, " — expected ", expected, ", got ", actual
        return 1
    end
    echo "PASS: ", name
    return 0
end

var failures = 0
failures = failures + assert_eq(add(2, 3), 5, "add(2,3)")
failures = failures + assert_eq(multiply(4, 5), 20, "multiply(4,5)")

if failures == 0:
    echo "All tests passed!"
end
```

### Step 2: Run

```bash
mozhi test
```

---

## Common Patterns

### Conditional Compilation

Mozhi doesn't have built-in conditional compilation, but you can use environment variables or separate files:

```
src/
├── math.mz          # main module
├── math_linux.mz    # Linux-specific
└── math_macos.mz    # macOS-specific
```

And in `math.mz`:

```mozhi
# Re-export platform-specific code
# (Future: mozhi will support conditional imports)
```

### Module Organization

```
src/
├── mylib.mz          # Main module (import mylib)
├── vector.mz         # Sub-module (import mylib.vector)
├── matrix.mz         # Sub-module (import mylib.matrix)
└── utils/
    └── string.mz     # Nested (import mylib.utils.string)
```

### Versioning

Follow [SemVer](https://semver.org/):

- **MAJOR**: breaking changes (e.g., `1.0.0` → `2.0.0`)
- **MINOR**: new features, backwards compatible (e.g., `1.0.0` → `1.1.0`)
- **PATCH**: bug fixes (e.g., `1.0.0` → `1.0.1`)

Tag releases in git:

```bash
git tag v1.2.3
git push origin v1.2.3
```
