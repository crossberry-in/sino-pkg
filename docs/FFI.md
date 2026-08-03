# Foreign Function Interface (FFI)

Mozhi libraries can call functions written in C, C++, Assembly, and Rust. This allows you to write performance-critical code in a systems language while keeping the high-level logic in Mozhi.

---

## How It Works

1. You write foreign functions in `native/*.c`, `native/*.cpp`, `native/*.S`, or `native/*.rs`
2. You enable the corresponding flag in `[build]` in `mozhi.toml`
3. `mozhi build` compiles the foreign code into object files
4. Object files are linked into a static (`.a`) or shared (`.so`/`.dylib`/`.dll`) library
5. The Mozhi interpreter calls these functions through the C ABI

---

## Project Layout

```
mylib/
├── mozhi.toml
├── src/
│   └── mylib.mz          # Mozhi code (calls foreign functions)
├── native/
│   ├── mylib.c           # C implementation
│   ├── mylib.cpp         # C++ implementation
│   ├── simd.S            # Assembly implementation
│   └── fastmath.rs       # Rust implementation
└── include/
    └── mylib.h           # C/C++ headers (also used by Mozhi FFI)
```

---

## C

### `mozhi.toml`

```toml
[build]
c = true
```

### `native/mylib.c`

```c
/* C implementation */

int c_add(int a, int b) {
    return a + b;
}

int c_multiply(int a, int b) {
    return a * b;
}

double c_sqrt(double x) {
    /* Use the C standard library */
    extern double sqrt(double);
    return sqrt(x);
}
```

### `include/mylib.h`

```c
#ifndef MYLIB_H
#define MYLIB_H

int c_add(int a, int b);
int c_multiply(int a, int b);
double c_sqrt(double x);

#endif
```

### Compilation

`mozhi build` compiles `native/*.c` with:

```bash
cc -c -O2 -fPIC -Iinclude -Inative native/mylib.c -o build/mylib_c.o
```

---

## C++

### `mozhi.toml`

```toml
[build]
cpp = true
```

### `native/mylib.cpp`

```cpp
// C++ implementation
// Functions must be wrapped in extern "C" to expose the C ABI.

#include <cmath>
#include <vector>
#include <algorithm>

extern "C" {

double cpp_sqrt(double x) {
    return std::sqrt(x);
}

double cpp_pow(double base, double exp) {
    return std::pow(base, exp);
}

// C++ can use STL — great for complex algorithms
void cpp_sort_ints(int* arr, int n) {
    std::vector<int> v(arr, arr + n);
    std::sort(v.begin(), v.end());
    for (int i = 0; i < n; i++) {
        arr[i] = v[i];
    }
}

}  // extern "C"
```

### Compilation

`mozhi build` compiles `native/*.cpp` with:

```bash
c++ -c -O2 -fPIC -Iinclude -Inative native/mylib.cpp -o build/mylib_cpp.o
```

> **Important:** All functions callable from Mozhi must be wrapped in `extern "C" {}`. Otherwise, C++ name mangling will prevent the Mozhi FFI from finding them.

---

## Assembly

### `mozhi.toml`

```toml
[build]
assembly = true
```

### `native/simd.S` (x86_64 Linux/macOS)

```asm
/* Assembly implementation — platform-specific! */

.global asm_square
asm_square:
    /* Input: rdi = n (long), Output: rax = n*n */
    mov %rdi, %rax
    imul %rdi, %rax
    ret

.global asm_max
asm_max:
    /* Input: rdi = a, rsi = b, Output: rax = max(a, b) */
    cmp %rsi, %rdi
    cmovl %rsi, %rdi
    mov %rdi, %rax
    ret
```

### `native/simd.S` (ARM64 / aarch64)

```asm
.global asm_square
asm_square:
    /* Input: x0 = n, Output: x0 = n*n */
    mul x0, x0, x0
    ret
```

### Compilation

`mozhi build` compiles `native/*.S` with:

```bash
cc -c native/simd.S -o build/simd_asm.o
```

> **Note:** Assembly is platform-specific. Write separate `.S` files for x86_64 and ARM64, or use `#ifdef`-style macros if your assembler supports them.

---

## Rust

### `mozhi.toml`

```toml
[build]
rust = true
```

### `native/mylib.rs`

```rust
// Rust implementation
// Functions must be marked with #[no_mangle] and extern "C" to expose the C ABI.

#[no_mangle]
pub extern "C" fn rs_factorial(n: u64) -> u64 {
    (1..=n).product()
}

#[no_mangle]
pub extern "C" fn rs_fibonacci(n: u64) -> u64 {
    if n <= 1 {
        return n;
    }
    let mut a = 0u64;
    let mut b = 1u64;
    for _ in 2..=n {
        let c = a + b;
        a = b;
        b = c;
    }
    b
}

// Rust can use its standard library
#[no_mangle]
pub extern "C" fn rs_sort(arr: *mut i32, len: usize) {
    if arr.is_null() || len == 0 {
        return;
    }
    let slice = unsafe { std::slice::from_raw_parts_mut(arr, len) };
    slice.sort();
}
```

### Compilation

`mozhi build` compiles `native/*.rs` with:

```bash
rustc --crate-type staticlib -O native/mylib.rs -o build/mylib.a
```

The resulting static library (`.a`) is then linked into the final output alongside the C/C++/ASM object files.

> **Important:** All functions callable from Mozhi must be marked with `#[no_mangle]` and `extern "C"`. Otherwise, Rust will apply name mangling and the Mozhi FFI won't find them.

---

## Combining Multiple Languages

You can mix C, C++, Assembly, and Rust in the same library:

```toml
[build]
c = true
cpp = true
assembly = true
rust = true
```

```
native/
├── core.c          # C core
├── algorithms.cpp  # C++ STL algorithms
├── simd.S          # Assembly SIMD kernels
└── crypto.rs       # Rust crypto (memory-safe)
```

`mozhi build` compiles all of them and links the results into a single library:

```
dist/
├── libmylib.a      # contains: core_c.o, algorithms_cpp.o, simd_asm.o, crypto.a
└── mylib.silib     # Mozhi source package
```

---

## Build Output

### Static Library (`--static`)

```bash
mozhi build --static
```

Output: `dist/lib<name>.a`

Contains all object files archived with `ar rcs`. Use this when you want to embed the library into another build.

### Shared Library (`--shared`)

```bash
mozhi build --shared
```

Output:
- Linux: `dist/lib<name>.so`
- macOS: `dist/lib<name>.dylib`
- Windows: `dist/<name>.dll`

Use this for runtime-loaded libraries (plugins, dynamic FFI).

### Native Mozhi Library (`--native`)

```bash
mozhi build --native
```

Output: `dist/<name>.silib`

A ZIP archive containing the `.mz` source files and `mozhi.toml`. No foreign code is compiled. Use this for pure-Mozhi libraries.

---

## Header Files

Place C/C++ headers in `include/`. They are automatically added to the include path (`-Iinclude`) for all C and C++ compilations.

```
include/
└── mylib.h
```

---

## Compiler Detection

mozhi-pkg auto-detects available compilers:

| Language | Compilers tried (in order) |
|----------|---------------------------|
| C | `cc`, `gcc`, `clang` |
| C++ | `c++`, `g++`, `clang++` |
| Assembly | `cc`, `gcc`, `clang` |
| Rust | `rustc` |
| Archiver | `ar` |
| Git | `git` |

Check detected compilers with:

```bash
mozhi version
```

---

## Requirements

| Feature | Requirement |
|---------|-------------|
| C builds | `cc` or `gcc` or `clang` |
| C++ builds | `c++` or `g++` or `clang++` |
| Assembly builds | `cc` or `gcc` or `clang` |
| Rust builds | `rustc` |
| Static libraries | `ar` |
| GitHub dependencies | `git` |

Install missing tools:

```bash
# Debian/Ubuntu
sudo apt install build-essential git

# Fedora/RHEL
sudo dnf install gcc g++ make git

# Alpine
apk add build-base git

# macOS (Xcode Command Line Tools)
xcode-select --install

# Rust (all platforms)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```
