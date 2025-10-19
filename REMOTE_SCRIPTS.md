# Quick Start: Remote Script Execution

## Setup (First Time)

1. Ensure scripts are executable:
```bash
chmod +x scripts/execute_on_vps.sh
```

2. Test SSH connection:
```bash
ssh -i ~/.ssh/mcp_vps root@147.79.82.234 "echo 'Connected to VPS'"
```

## Usage

### Via Terminal

```bash
# View logs
./scripts/execute_on_vps.sh scripts/logs_app.sh 50

# Deploy
./scripts/execute_on_vps.sh scripts/deploy.sh

# Backup
./scripts/execute_on_vps.sh scripts/backup.sh

# Status
./scripts/execute_on_vps.sh scripts/status.sh
```

### Via VS Code Tasks

Press `Ctrl+Shift+P` → Type "Tasks: Run Task" → Select:
- **VPS: View Logs** - See Docker container logs
- **VPS: Status Check** - Check app status
- **VPS: Deploy** - Pull & rebuild
- **VPS: Backup** - Create backup
- **VPS: Test Connection** - Test setup

## Create New Scripts

1. Create file in `scripts/` directory with `.sh` extension
2. Add shebang: `#!/bin/bash`
3. Make executable: `chmod +x scripts/myscript.sh`
4. Execute: `./scripts/execute_on_vps.sh scripts/myscript.sh`

See `scripts/README.md` for full documentation.
