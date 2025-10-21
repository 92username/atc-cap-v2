#!/bin/bash

# Log file
LOG_FILE="/var/log/docker_tatic_limit.log"

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Check if Docker is running
if ! systemctl is-active --quiet docker; then
    log_message "❌ Docker não está ativo. Por favor, inicie o serviço Docker."
    exit 1
fi

# Apply resource limits to the tatic-processor container
log_message "Aplicando limites ao container tatic-processor..."
/usr/bin/docker update --cpus="1.6" --memory="2g" --cpuset-cpus="0,1" tatic-processor >> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    log_message "❌ Falha ao aplicar limites ao container tatic-processor."
    exit 1
fi

# Ensure the cronjob exists
CRON_JOB="@reboot /bin/bash /path/to/limit_tatic_processor.sh"
CRON_FILE="/var/spool/cron/crontabs/root"
if ! crontab -l | grep -q "$CRON_JOB"; then
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    if [ $? -ne 0 ]; then
        log_message "❌ Falha ao configurar o cronjob."
        exit 1
    fi
fi

log_message "✅ Limite do tatic-processor aplicado e cron configurado com sucesso."
echo "✅ Limite do tatic-processor aplicado e cron configurado com sucesso."