#!/usr/bin/env bash
# Run once from the repo root. Requires the gh CLI, authenticated.
#   chmod +x scripts/setup-repo.sh && ./scripts/setup-repo.sh
set -euo pipefail

echo "creating labels"
mklabel() { gh label create "$1" --color "$2" --description "$3" --force; }

mklabel "track:ml"        "7F77DD" "Training, quantization, eval spec"
mklabel "track:rtl"       "1D9E75" "SystemVerilog, FPGA, verification"
mklabel "track:embedded"  "D85A30" "PCB, firmware, sensing"
mklabel "track:mech"      "888780" "Gantry, carriage, motion"

mklabel "type:task"       "185FA5" "Unit of work"
mklabel "type:bug"        "E24B4A" "Something built is wrong"
mklabel "type:learning"   "EF9F27" "80-20 cross-track work"
mklabel "type:port"       "D4537E" "Changes a cross-track contract"

mklabel "status:ready"    "639922" "Scoped, unblocked, pick it up"
mklabel "status:blocked"  "A32D2D" "Waiting on another issue or part"
mklabel "status:review"   "BA7517" "PR open, needs eyes"

mklabel "good first issue" "97C459" "Newcomer friendly"
mklabel "size:S"          "D3D1C7" "Under 2 hours"
mklabel "size:M"          "B4B2A9" "A week of evenings"
mklabel "size:L"          "888780" "Split this"

echo "creating milestones"
mkms() { gh api repos/:owner/:repo/milestones -f title="$1" -f description="$2" >/dev/null || true; }

mkms "P0 eval spec published"        "Feature encoding and accumulator semantics frozen"
mkms "P1 golden vectors generated"   "Positions plus expected int8 evals committed"
mkms "P2 first board scan"           "64 squares read reliably into the FPGA"
mkms "P3 int8 blob in BRAM"          "Quantized weights loaded and matching reference"
mkms "P4 playable prototype"         "Legal move chosen and displayed end to end"

echo "protecting main"
gh api -X PUT repos/:owner/:repo/branches/main/protection \
  -H "Accept: application/vnd.github+json" \
  -F "required_pull_request_reviews[required_approving_review_count]=1" \
  -F "required_pull_request_reviews[require_code_owner_reviews]=true" \
  -F "enforce_admins=false" \
  -F "required_status_checks=null" \
  -F "restrictions=null" \
  -F "allow_force_pushes=false" \
  -F "allow_deletions=false" || echo "protection failed, set it in Settings > Branches"

echo "done"
