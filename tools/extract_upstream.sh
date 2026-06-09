#!/usr/bin/env bash
# Extract the SGMT Java source we port FROM into a committed, registered mirror.
#
# The canonical artifact is the zip vendored in the read-only upstream/Matrices
# submodule (OSTI code-54699, DOI 10.11578/dc.20210416.34, BSD-3). That zip is
# the provenance source; this script produces reference/sgmt-source/ — a derived,
# READ-ONLY mirror of just Source/ and Test/ (no third-party Dependencies/) so we
# can grep/read the Java without re-unzipping. The mirror is committed; you should
# not need to run this again unless re-deriving it from scratch. Idempotent.
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
ZIP="$ROOT/upstream/Matrices/Matrix Generation Software/SandiaGeneratedMatrixTool-1.0.0-source.zip"
DEST="$ROOT/reference/sgmt-source"
INNER="SandiaGeneratedMatrixTool-1.0.0-source"

if [ -d "$DEST/Source" ]; then
    echo "Already present: $DEST (delete it to re-derive)"
    exit 0
fi
if [ ! -f "$ZIP" ]; then
    echo "Missing zip: $ZIP — run 'git submodule update --init' first." >&2
    exit 1
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
# Only the code we care about: the port source and the JUnit spec.
unzip -q "$ZIP" "$INNER/Source/*" "$INNER/Test/*" -d "$TMP"
mkdir -p "$DEST"
mv "$TMP/$INNER/Source" "$DEST/Source"
mv "$TMP/$INNER/Test" "$DEST/Test"
echo "Extracted Source/ + Test/ to: $DEST"
