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

ensure_weasyprint_native_libs

if ! python -c "import uvicorn" >/dev/null 2>&1; then
  echo "ERROR: uvicorn is not installed. Deploy must run Oryx remote build (SCM_DO_BUILD_DURING_DEPLOYMENT=true)." >&2
  exit 1
fi

exec python -m uvicorn main:app \
  --host 0.0.0.0 \
  --port "${PORT:-8000}"