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

ensure_weasyprint_native_libs
ensure_tesseract_binary

if ! python -c "import uvicorn" >/dev/null 2>&1; then
  echo "ERROR: uvicorn is not installed. Deploy must run Oryx remote build (SCM_DO_BUILD_DURING_DEPLOYMENT=true)." >&2
  exit 1
fi

exec python -m uvicorn main:app \
  --host 0.0.0.0 \
  --port "${PORT:-8000}"