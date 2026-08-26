#!/bin/bash

set -euo pipefail

check_weasyprint_native_libs() {
  python - <<'PY'
import ctypes.util

required = (
    "gobject-2.0",
    "pango-1.0",
    "pangocairo-1.0",
    "gdk_pixbuf-2.0",
    "cairo",
)
missing = [name for name in required if not ctypes.util.find_library(name)]
raise SystemExit(1 if missing else 0)
PY
}

current_deploy_id() {
  # Oryx writes a Build Operation ID into the manifest on every deploy.
  # Restarts without a redeploy keep the same ID; a fresh deploy rotates it.
  local manifest="/home/site/wwwroot/oryx-manifest.toml"
  if [ -f "$manifest" ]; then
    grep -E '^OperationId=' "$manifest" | head -n1 | cut -d= -f2- | tr -d '"' | tr -d '[:space:]'
  fi
}

ensure_weasyprint_native_libs() {
  if [[ "$(uname -s)" != "Linux" ]]; then
    return
  fi

  local marker="/home/site/.weasyprint-native-libs-installed"
  local deploy_id
  deploy_id="$(current_deploy_id || true)"

  # Marker stores the deploy id it was created for. If the current deploy id
  # differs (new deploy) or the libs don't actually resolve, reinstall.
  if [ -f "$marker" ] && [ -n "$deploy_id" ] \
     && [ "$(cat "$marker" 2>/dev/null)" = "$deploy_id" ] \
     && check_weasyprint_native_libs; then
    echo "WeasyPrint native libs valid for deploy $deploy_id — skipping install."
    return
  fi

  if [ -f "$marker" ]; then
    echo "Marker stale or libs missing — reinstalling."
    rm -f "$marker"
  fi

  if check_weasyprint_native_libs; then
    echo "WeasyPrint native libraries already available."
    touch "$marker"
    return
  fi

  echo "Installing missing WeasyPrint native libraries..."
  export DEBIAN_FRONTEND=noninteractive
  apt-get update
  apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    shared-mime-info \
    fonts-dejavu-core
  rm -rf /var/lib/apt/lists/*

  # Only write the marker if the install actually resolved the libs.
  if check_weasyprint_native_libs; then
    echo "${deploy_id:-unknown}" > "$marker"
    echo "WeasyPrint native libraries installed and verified for deploy ${deploy_id:-unknown}."
  else
    echo "ERROR: apt install completed but required libs still missing." >&2
    exit 1
  fi
}

check_tesseract_binary() {
  # Both the binary and the Spanish traineddata must be present: receipts are
  # recognised with `spa+eng`, and a missing language pack fails at OCR time.
  command -v tesseract >/dev/null 2>&1 || return 1
  tesseract --list-langs 2>/dev/null | grep -qx "spa" || return 1
  tesseract --list-langs 2>/dev/null | grep -qx "eng" || return 1
}

ensure_tesseract_binary() {
  if [[ "$(uname -s)" != "Linux" ]]; then
    return
  fi

  local marker="/home/site/.tesseract-installed"
  local deploy_id
  deploy_id="$(current_deploy_id || true)"

  if [ -f "$marker" ] && [ -n "$deploy_id" ] \
     && [ "$(cat "$marker" 2>/dev/null)" = "$deploy_id" ] \
     && check_tesseract_binary; then
    echo "Tesseract valid for deploy $deploy_id — skipping install."
    return
  fi

  if [ -f "$marker" ]; then
    echo "Tesseract marker stale or binary missing — reinstalling."
    rm -f "$marker"
  fi

  if check_tesseract_binary; then
    echo "Tesseract already available."
    touch "$marker"
    return
  fi

  echo "Installing Tesseract OCR and language packs..."
  export DEBIAN_FRONTEND=noninteractive
  apt-get update
  apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-spa \
    tesseract-ocr-eng
  rm -rf /var/lib/apt/lists/*

  if check_tesseract_binary; then
    echo "${deploy_id:-unknown}" > "$marker"
    echo "Tesseract installed and verified for deploy ${deploy_id:-unknown}."
  else
    # Receipt OCR degrades to manual capture rather than taking the API down.
    echo "WARNING: Tesseract install did not resolve; receipt OCR will be unavailable." >&2
  fi
}

ensure_python_dependencies() {
  # Oryx normally builds the virtualenv at deploy time and points PYTHONPATH at
  # it. When that does not happen the app cannot boot at all, so build the
  # environment here instead of failing. /home is the only persisted path, so
  # the venv survives restarts and the install is paid once per requirements
  # change rather than on every cold start.
  if python -c "import uvicorn" >/dev/null 2>&1; then
    echo "Dependencies already importable (Oryx build present)."
    return
  fi

  local script_dir venv="/home/site/antenv"
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

  if [ -f "$venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    . "$venv/bin/activate"
    if python -c "import uvicorn" >/dev/null 2>&1; then
      echo "Using persisted virtualenv at $venv."
      return
    fi
    echo "Persisted virtualenv at $venv is incomplete — rebuilding."
    rm -rf "$venv"
  fi

  echo "Oryx build output not found. Building virtualenv at $venv..."
  python -m venv "$venv"
  # shellcheck disable=SC1091
  . "$venv/bin/activate"
  python -m pip install --upgrade pip
  python -m pip install -r "$script_dir/requirements.txt"

  if ! python -c "import uvicorn" >/dev/null 2>&1; then
    echo "ERROR: pip install finished but uvicorn is still missing." >&2
    echo "       python: $(command -v python || echo 'not on PATH')" >&2
    echo "       requirements: $script_dir/requirements.txt" >&2
    exit 1
  fi
  echo "Virtualenv ready at $venv."
}

ensure_weasyprint_native_libs
ensure_tesseract_binary
ensure_python_dependencies

exec python -m uvicorn main:app \
  --host 0.0.0.0 \
  --port "${PORT:-8000}"