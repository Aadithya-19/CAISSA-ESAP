#!/usr/bin/env bash
# Scaffold a module plus its testbench. Called by `make new`.
#   scripts/new.sh <name> [subdir]
set -euo pipefail

NAME="${1:-}"
DIR="${2:-}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
T="$ROOT/scripts/templates"

[ -n "$NAME" ] || { echo "need a name"; exit 1; }
case "$NAME" in
  [a-z_]*) ;;
  *) echo "module names are lowercase and start with a letter or underscore"; exit 1 ;;
esac

REL="${DIR:+$DIR/}$NAME.sv"
SV="$ROOT/rtl/$REL"
TB="$ROOT/tb/${NAME}_tb.py"
PY="$ROOT/tb/test_${NAME}.py"

for f in "$SV" "$TB" "$PY"; do
  [ -e "$f" ] && { echo "already exists: ${f#$ROOT/}"; exit 1; }
done

mkdir -p "$(dirname "$SV")"
sed -e "s|__NAME__|$NAME|g" -e "s|__PATH__|$REL|g" "$T/module.sv.in"  > "$SV"
sed -e "s|__NAME__|$NAME|g" -e "s|__PATH__|$REL|g" "$T/tb.py.in"      > "$TB"
sed -e "s|__NAME__|$NAME|g" -e "s|__PATH__|$REL|g" "$T/test.py.in"    > "$PY"

echo "made:"
echo "  rtl/$REL"
echo "  tb/${NAME}_tb.py"
echo "  tb/test_${NAME}.py"
echo
echo "next: fill in the ports, then  make test_$NAME"
