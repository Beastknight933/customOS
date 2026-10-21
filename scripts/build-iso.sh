#!/usr/bin/env bash
# Horizon OS - Reproducible ISO Build Script
# Automates deterministic staging and archiso construction via native tools or container.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
PROFILE_DIR="$REPO_ROOT/iso/archiso-profile"
DIST_DIR="$REPO_ROOT/dist"
WORK_DIR="/var/tmp/horizon-iso-work"
OUT_DIR="/var/tmp/horizon-iso-out"
CACHE_DIR="/var/tmp/horizon-iso-build/cache"

echo "=========================================================="
echo "  Horizon OS — Reproducible ISO Build Pipeline"
echo "=========================================================="

# 1. Deterministic Staging
echo "==> Step 1: Running deterministic staging..."
bash "$SCRIPT_DIR/stage-iso.sh"

# 2. Prepare build workspace
mkdir -p "$DIST_DIR" "$WORK_DIR" "$OUT_DIR" "$CACHE_DIR"
rm -rf "$WORK_DIR"/* "$OUT_DIR"/*

# 3. Build ISO
if command -v mkarchiso >/dev/null 2>&1; then
    echo "==> Step 2: Building ISO using host mkarchiso..."
    sudo mkarchiso -v -w "$WORK_DIR" -o "$OUT_DIR" "$PROFILE_DIR"
elif command -v podman >/dev/null 2>&1 && podman image exists localhost/horizon-iso-builder:latest; then
    echo "==> Step 2: Building ISO using horizon-iso-builder container..."
    podman run --rm --privileged \
        -v "$PROFILE_DIR":/profile \
        -v "$WORK_DIR":/work \
        -v "$OUT_DIR":/out \
        -v "$CACHE_DIR":/var/cache/pacman/pkg \
        localhost/horizon-iso-builder:latest \
        mkarchiso -v -w /work -o /out /profile
else
    echo "ERROR: Neither mkarchiso nor horizon-iso-builder container is available." >&2
    echo "To build on Arch host: sudo pacman -S archiso" >&2
    echo "To build with container: podman build -t horizon-iso-builder -f iso/Containerfile ." >&2
    exit 1
fi

# 4. Copy ISO to dist/ and generate checksum
BUILT_ISO="$(find "$OUT_DIR" -maxdepth 1 -name "horizon-os-*.iso" | head -n 1)"
if [[ -f "$BUILT_ISO" ]]; then
    ISO_NAME="$(basename "$BUILT_ISO")"
    echo "==> Step 3: Copying built ISO ($ISO_NAME) to dist/..."
    cp -p "$BUILT_ISO" "$DIST_DIR/$ISO_NAME"

    echo "==> Step 4: Generating cryptographic SHA-256 checksum..."
    (cd "$DIST_DIR" && sha256sum "$ISO_NAME" > SHA256SUMS)
    echo "Checksum recorded in $DIST_DIR/SHA256SUMS:"
    cat "$DIST_DIR/SHA256SUMS"
    echo "=========================================================="
    echo "  ✓ Horizon OS ISO Built & Verified Successfully!"
    echo "=========================================================="
else
    echo "ERROR: Expected ISO output not found in $OUT_DIR" >&2
    exit 1
fi
