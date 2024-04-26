#!/bin/bash
CRON_FILE="/app/src/tasks/crontab.$CRON_FILE_NAME"
echo " ⏰  Loading crontab file: $CRON_FILE"

crontab $CRON_FILE

echo " 📏 Rules:  "
cat $CRON_FILE

echo " 🎸 Starting cron..."
cron -f
echo " ✅ Finish" 