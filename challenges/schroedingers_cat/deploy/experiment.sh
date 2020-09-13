#!/usr/bin/env bash
set -euo pipefail
# redirect stderr
exec 2>&1

# setup new trace dir
tmp=$(mktemp -d)
#trap "rm -rf $tmp" EXIT
export _RR_TRACE_DIR=$tmp


echo "Please pick your poison"
read poison

if [[ "0$poison" =~ [^x0-9a-f] ]]; then
    echo "only numbers please!"
    exit 1;
fi

set -x
echo "Running experiment"
rr record -n ./cat "$poison" || echo "it crashed!"
rr pack $tmp/cat-0

echo "Your experiment has been recorded. Display trace (base64 zstd-compressed tar)? ([y]/n) "
read display || true
if [[ "x$display" != "xn" ]]; then
    tar -c --zstd $tmp/cat-0 | base64 -w 0
    echo
fi
