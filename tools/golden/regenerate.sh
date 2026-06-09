#!/usr/bin/env bash
#
# Regenerate the committed golden JVM fixtures consumed (without a JVM) by the
# Python port's tests.
#
# Deliverable 1 (always): tests/golden/javarandom_vectors.json
#   Compiled + run from tools/golden/JavaRandomDump.java. Depends ONLY on
#   java.util.Random (no SGMT jar), so it is robust to the upstream build.
#
# Deliverable 2 (only if tools/golden/SgmtDump.java exists):
#   tests/golden/sgmt_matrices.json — built against the SGMT jar, which is
#   compiled from the read-only upstream source zip in a TEMP dir (upstream/ is
#   never modified). See docs/spikes/golden-fixtures.md for the deliverable-2
#   outcome; if SgmtDump.java is absent, deliverable 2 was deferred to Phase 4.
#
# Determinism: regenerating must produce byte-identical JSON. After running,
# `git status` on the committed JSON must show no diff. Requires JDK 8.
#
# Usage:  tools/golden/regenerate.sh
set -euo pipefail

# Resolve repo paths from this script's own location (worktree-safe).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
GOLDEN_DIR="$REPO_ROOT/tests/golden"
UPSTREAM_ZIP="$REPO_ROOT/upstream/Matrices/Matrix Generation Software/SandiaGeneratedMatrixTool-1.0.0-source.zip"

# --- Toolchain check: require JDK 8 (1.8) javac AND java -------------------
# JAVA_HOME may be unset; in that case fall back to PATH java/javac after
# confirming they report 1.8. (`java -version`/`javac -version` print to stderr.)
require_jdk8() {
  local tool="$1" ver
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "ERROR: $tool not found on PATH" >&2
    exit 1
  fi
  ver="$("$tool" -version 2>&1 | head -n1)"
  # java prints: openjdk version "1.8.0_492"
  # javac prints: javac 1.8.0_492   (no quotes) — match the bare 1.8 token too.
  case "$ver" in
    *1.8.*) : ;;
    *) echo "ERROR: $tool is not JDK 8 (got: $ver)" >&2; exit 1 ;;
  esac
  echo "ok: $tool -> $ver"
}

echo "== verifying JDK 8 toolchain =="
require_jdk8 javac
require_jdk8 java

mkdir -p "$GOLDEN_DIR"

# --- Single cleanup function registered once at the top -------------------
# Vars are initialised empty; rm -rf runs only when the var is non-empty,
# so this is safe whether or not deliverable 2 is attempted.
RNG_BUILD=""
SGMT_BUILD=""
cleanup() {
  [ -n "$RNG_BUILD"  ] && rm -rf "$RNG_BUILD"
  [ -n "$SGMT_BUILD" ] && rm -rf "$SGMT_BUILD"
}
trap cleanup EXIT

# --- Deliverable 1: java.util.Random golden vectors -----------------------
echo "== deliverable 1: javarandom_vectors.json =="
RNG_BUILD="$(mktemp -d)"
javac -d "$RNG_BUILD" "$SCRIPT_DIR/JavaRandomDump.java"
java -Djava.awt.headless=true -cp "$RNG_BUILD" JavaRandomDump \
  > "$GOLDEN_DIR/javarandom_vectors.json"
echo "wrote $GOLDEN_DIR/javarandom_vectors.json"

# --- Deliverable 2: SGMT matrix fixtures (only if the driver exists) -------
if [ -f "$SCRIPT_DIR/SgmtDump.java" ]; then
  echo "== deliverable 2: sgmt_matrices.json =="
  if [ ! -f "$UPSTREAM_ZIP" ]; then
    echo "ERROR: upstream source zip not found at: $UPSTREAM_ZIP" >&2
    echo "       run: git submodule update --init" >&2
    exit 1
  fi
  SGMT_BUILD="$(mktemp -d)"
  unzip -q "$UPSTREAM_ZIP" -d "$SGMT_BUILD"
  SRC_DIR="$SGMT_BUILD/SandiaGeneratedMatrixTool-1.0.0-source"
  # Build the jar in the temp copy only (upstream/ stays untouched). The
  # documented fix drops the project's -Werror by overriding compilerargs.
  ( cd "$SRC_DIR" && ant -Djavac.compilerargs="-Xlint:none" clean jar )
  JAR="$SRC_DIR/Distribution/gov-sandia-cognition-generator-matrix.jar"
  LIB="$SRC_DIR/Distribution/lib"
  CP="$JAR:$LIB/*"
  mkdir -p "$SGMT_BUILD/driver"
  javac -cp "$CP" -d "$SGMT_BUILD/driver" "$SCRIPT_DIR/SgmtDump.java"
  java -Djava.awt.headless=true -cp "$SGMT_BUILD/driver:$CP" SgmtDump \
    > "$GOLDEN_DIR/sgmt_matrices.json"
  echo "wrote $GOLDEN_DIR/sgmt_matrices.json"
else
  echo "== deliverable 2: SgmtDump.java absent -> deferred (see docs/spikes/golden-fixtures.md) =="
fi

echo "== done =="
