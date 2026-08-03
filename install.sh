#!/usr/bin/env bash
#
# Mozhi Package Manager — Universal installer
#
# Supported platforms: Linux, macOS, WSL, Termux, Windows (Git Bash/MSYS)
#
# Usage:
#   curl -fsSL https://github.com/crossberry-in/mozhi-pkg/raw/main/install.sh | bash
#
set -e

REPO="crossberry-in/mozhi-pkg"
BINARY_NAME="mozhi"

# --- Helpers (all output to stderr) -------------------------------------

info()    { printf "\033[1;34m[info]\033[0m  %s\n"  "$*" >&2; }
warn()    { printf "\033[1;33m[warn]\033[0m  %s\n"  "$*" >&2; }
error()   { printf "\033[1;31m[error]\033[0m %s\n" "$*" >&2; }
success() { printf "\033[1;32m[ok]\033[0m    %s\n"  "$*" >&2; }

# --- Detect install location --------------------------------------------

install_dir_for() {
    local os="$1"

    case "$os" in
        termux)
            echo "$PREFIX/bin"
            ;;
        macos)
            if [ -d "/opt/homebrew/bin" ] && [ -w "/opt/homebrew/bin" ]; then
                echo "/opt/homebrew/bin"
            elif [ -w "/usr/local/bin" ] || sudo -n true 2>/dev/null; then
                echo "/usr/local/bin"
            else
                echo "$HOME/.local/bin"
            fi
            ;;
        linux|*)
            if [ -w "/usr/local/bin" ] || sudo -n true 2>/dev/null; then
                echo "/usr/local/bin"
            else
                echo "$HOME/.local/bin"
            fi
            ;;
    esac
}

# --- Detect platform ----------------------------------------------------

detect_os() {
    case "$(uname -s 2>/dev/null || echo unknown)" in
        Linux*)  os="linux"  ;;
        Darwin*) os="macos"  ;;
        MINGW*|MSYS*|CYGWIN*) os="windows" ;;
        *) error "Unsupported OS: $(uname -s)"; exit 1 ;;
    esac

    if [ -n "$TERMUX_VERSION" ]; then
        os="termux"
    elif [ -n "$PREFIX" ] && case "$PREFIX" in /data/data/com.termux*) true;; *) false;; esac; then
        os="termux"
    fi
    echo "$os"
}

# --- Download the mozhi script -------------------------------------------

download_mozhi() {
    local tmp_file="$1"
    local url="https://raw.githubusercontent.com/${REPO}/main/mozhi"

    info "Downloading mozhi CLI..."
    if ! curl -fSL --progress-bar -o "$tmp_file" "$url"; then
        error "Download failed. URL: $url"
        exit 1
    fi
    chmod +x "$tmp_file"
}

# --- Check Python -------------------------------------------------------

check_python() {
    if command -v python3 >/dev/null 2>&1; then
        PYTHON_BIN="python3"
    elif command -v python >/dev/null 2>&1; then
        PYTHON_BIN="python"
    else
        error "Python 3 is required but not found."
        error "Install Python 3.8+ from https://python.org or your package manager."
        exit 1
    fi

    local version
    version="$($PYTHON_BIN -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || echo '0.0')"
    local major minor
    major="${version%%.*}"
    minor="${version#*.}"

    if [ "$major" -lt 3 ] || ([ "$major" -eq 3 ] && [ "$minor" -lt 8 ]); then
        error "Python 3.8+ required, found Python $version"
        exit 1
    fi

    info "Using Python $version ($PYTHON_BIN)"
}

# --- Install ------------------------------------------------------------

install_mozhi() {
    local tmp_file="$1"
    local install_dir="$2"
    local final_path
    local need_sudo=0

    final_path="$install_dir/$BINARY_NAME"

    # --- Migration: if an old interpreter binary is installed as 'mozhi', rename it ---
    local existing_mozhi
    existing_mozhi="$(command -v mozhi 2>/dev/null || true)"
    if [ -n "$existing_mozhi" ]; then
        # Check if it's a binary (not a Python script with #!)
        local first_bytes
        first_bytes="$(head -c 2 "$existing_mozhi" 2>/dev/null || echo "")"
        if [ "$first_bytes" != "#!" ]; then
            # It's a binary — likely the old interpreter. Rename it.
            local interp_path="$install_dir/mozhi-interpreter"
            info "Migrating existing 'mozhi' binary to 'mozhi-interpreter'..."
            if [ -w "$install_dir" ]; then
                mv "$existing_mozhi" "$interp_path" 2>/dev/null || true
            else
                sudo mv "$existing_mozhi" "$interp_path" 2>/dev/null || true
            fi
            success "Migrated interpreter to: $interp_path"
        fi
    fi

    mkdir -p "$install_dir" 2>/dev/null || need_sudo=1

    if [ ! -w "$install_dir" ]; then
        need_sudo=1
    fi

    if [ "$need_sudo" = "1" ]; then
        info "Installing to $final_path (sudo required)..."
        sudo cp "$tmp_file" "$final_path"
        sudo chmod +x "$final_path"
    else
        info "Installing to $final_path..."
        cp "$tmp_file" "$final_path"
        chmod +x "$final_path"
    fi
    rm -f "$tmp_file"
}

# --- Verify -------------------------------------------------------------

verify_installation() {
    local mozhi_cmd
    mozhi_cmd="$(command -v mozhi 2>/dev/null || true)"

    if [ -z "$mozhi_cmd" ]; then
        warn "mozhi was installed but is not on your PATH."
        warn "Open a new terminal, or run: source ~/.bashrc  (or ~/.zshrc)"
        return 0
    fi

    info "Verifying installation..."
    if "$mozhi_cmd" version 2>/dev/null; then
        success "mozhi-pkg dispatcher is installed and working!"
    else
        warn "mozhi was installed but 'mozhi version' failed."
        warn "Try opening a new terminal, then run 'mozhi version'."
    fi

    # Check if the Mozhi interpreter is also installed
    local interp
    interp="$(command -v mozhi-interpreter 2>/dev/null || true)"
    if [ -z "$interp" ]; then
        printf '\n' >&2
        warn "The Mozhi interpreter ('mozhi-interpreter') was not found." >&2
        info "Install it for 'mozhi file.mz' and 'mozhi repl' to work:" >&2
        info "  curl -fsSL https://github.com/crossberry-in/mozhi-doc/raw/main/install.sh | bash" >&2
    fi

    printf '\n' >&2
    info "Quick start:" >&2
    info "  mozhi init --lib mylib   # create a library" >&2
    info "  mozhi init --bin myapp   # create an application" >&2
    info "  mozhi build              # build the project" >&2
    info "  mozhi test               # run tests" >&2
    info "  mozhi my_script.mz       # run a script (needs interpreter)" >&2
    info "  mozhi                    # start REPL (needs interpreter)" >&2
    info "" >&2
    info "Docs: https://github.com/crossberry-in/mozhi-pkg" >&2
}

# --- Main ---------------------------------------------------------------

main() {
    printf '\n' >&2
    printf '  \033[1;36m===================================\033[0m\n' >&2
    printf '  \033[1;36m   Mozhi Package Manager Installer\033[0m\n' >&2
    printf '  \033[1;36m===================================\033[0m\n' >&2
    printf '\n' >&2

    check_python

    local os install_dir tmp_dir tmp_file
    os="$(detect_os)"
    install_dir="$(install_dir_for "$os")"
    tmp_dir="${TMPDIR:-/tmp}"
    tmp_file="${tmp_dir}/mozhi-download-$$"

    info "Detected platform: $os"
    info "Install location:  $install_dir"
    printf '\n' >&2

    download_mozhi "$tmp_file"
    install_mozhi "$tmp_file" "$install_dir"

    printf '\n' >&2
    verify_installation

    printf '\n' >&2
    success "Done!" >&2
    printf '\n' >&2
}

main "$@"
