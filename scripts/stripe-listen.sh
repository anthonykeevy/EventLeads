#!/usr/bin/env bash
set -euo pipefail

: "${STRIPE_WEBHOOK_SECRET:=whsec_replace}"
stripe listen --forward-to localhost:8000/webhooks/stripe --events payment_intent.succeeded --latest --log-level debug --secret "$STRIPE_WEBHOOK_SECRET"



