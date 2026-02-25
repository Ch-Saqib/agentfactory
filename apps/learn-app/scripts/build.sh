#!/bin/bash
set -euo pipefail

# Build script for Docusaurus with i18n support
#
# Docusaurus has a known memory leak between locale builds (gray-matter cache,
# MDX processor cache, webpack compiler objects) — see:
# https://github.com/facebook/docusaurus/issues/10944
#
# Strategy: Build each locale in a SEPARATE Node process so leaked memory is
# reclaimed by the OS between builds. This keeps peak usage under 4 GB,
# fitting comfortably on Vercel's standard 8 GB build machines.
#
# @docusaurus/faster flags (SWC + Lightning CSS) are enabled for speed.
# rspackBundler is intentionally DISABLED — it leaks more memory per locale.

# Change to learn-app directory (parent of scripts/)
cd "$(dirname "$0")/.."

# Flashcard validation + Anki generation run via nx dependsOn (project.json)
# before this script is invoked — no need to duplicate here.

NODE_VERSION=$(node -v | cut -d'.' -f1 | sed 's/v//')

# 4 GB heap per locale — each build runs in its own process
HEAP_SIZE="--max-old-space-size=4096"

# Node.js 25+ requires --localstorage-file flag
EXTRA_FLAGS=""
if [ "$NODE_VERSION" -ge 25 ]; then
  EXTRA_FLAGS="--localstorage-file=/tmp/docusaurus-localstorage"
fi

export NODE_OPTIONS="$HEAP_SIZE $EXTRA_FLAGS"

echo "==> Building locale: en (default)"
npx docusaurus build --locale en

echo "==> Building locale: ur"
npx docusaurus build --locale ur --out-dir build-ur

# Merge: Docusaurus puts non-default locale at <outDir>/ur/ for single-domain
# deployment. Copy it into the main build directory.
if [ -d "build-ur/ur" ]; then
  cp -r build-ur/ur build/ur
else
  # Fallback: if ur content is at root of build-ur (no subdirectory)
  mkdir -p build/ur
  cp -r build-ur/* build/ur/
fi
rm -rf build-ur

echo "==> Build complete (en + ur merged into build/)"
