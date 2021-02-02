#!/bin/sh

RESULT=$(curl https://api.telegram.org/bot${TELEGRAM_AUTH_TOKEN}/getWebhookInfo | jq '.ok')
if [ "$RESULT" = "true" ]; then
  exit 0
else
  exit
