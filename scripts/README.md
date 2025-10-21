# Remote Script Execution Guide for ATC-CAP-V2

## Overview

This system allows you to create scripts locally in VS Code and execute them on the VPS via SSH.

## Quick Start

### 1. Make the executor executable (first time only)

```bash
chmod +x scripts/execute_on_vps.sh
```

### 2. Execute any script

```bash
./scripts/execute_on_vps.sh scripts/example_hello.sh
```

## Available Scripts

### `example_hello.sh`
Simple hello world example to test the setup.

```bash
./scripts/execute_on_vps.sh scripts/example_hello.sh
```

### `logs_app.sh`
View Docker container logs in real-time.

```bash
# Last 100 lines
./scripts/execute_on_vps.sh scripts/logs_app.sh

# Last 50 lines
./scripts/execute_on_vps.sh scripts/logs_app.sh 50
```

### `deploy.sh`
Pull latest code and rebuild Docker containers.

```bash
./scripts/execute_on_vps.sh scripts/deploy.sh
```

### `backup.sh`
Create timestamped backup of uploads, outputs, and data directories.

```bash
./scripts/execute_on_vps.sh scripts/backup.sh
```

### `status.sh`
Check application status and disk usage.

```bash
./scripts/execute_on_vps.sh scripts/status.sh
```

### Rules

- **Name convention**: Use descriptive names like `my_task.sh`
- **Always make executable locally**: `chmod +x scripts/my_task.sh`
- **Always include shebang**: `#!/bin/bash` (first line)
- **Add comments**: Document what the script does
- **Use absolute paths**: Reference `/root/atc-cap-v2/` for the app directory
- **Exit codes**: Use `exit 0` for success, `exit 1` for errors

### Example: Custom Cleanup Script

Create `scripts/cleanup_old_jobs.sh`:

```bash
#!/bin/bash
#
# Cleanup Old Job Directories
#
# Removes job directories older than 30 days
#

APP_DIR="/root/atc-cap-v2"
DAYS_OLD=30

echo "Cleaning up jobs older than $DAYS_OLD days..."

cd "$APP_DIR/outputs"
find . -maxdepth 1 -type d -name "job_*" -mtime +$DAYS_OLD -exec rm -rf {} \; 2>/dev/null

cd "$APP_DIR/uploads"
find . -maxdepth 1 -type d -name "job_*" -mtime +$DAYS_OLD -exec rm -rf {} \; 2>/dev/null

echo "✓ Cleanup completed"
```

Then execute:

```bash
chmod +x scripts/cleanup_old_jobs.sh
./scripts/execute_on_vps.sh scripts/cleanup_old_jobs.sh
```

## How It Works

The `execute_on_vps.sh` wrapper does the following:

1. **Uploads** your script to `/root/atc-cap-v2/scripts/` on the VPS
2. **Sets permissions** to make it executable (chmod +x)
3. **Executes** the script on the VPS with access to the app directory
4. **Streams output** back to your terminal in real-time
5. **Returns exit codes** for error handling

## Environment

When your script runs on the VPS:

- **Working directory**: `/root/atc-cap-v2/`
- **User**: `root`
- **Shell**: `/bin/bash`
- **SSH key**: `~/.ssh/mcp_vps`

## Passing Arguments

Scripts can receive command-line arguments:

```bash
./scripts/execute_on_vps.sh scripts/logs_app.sh 50
```

In the script, access them with `$1`, `$2`, etc.:

```bash
#!/bin/bash
LINES="${1:-100}"  # Use argument or default to 100
echo "Showing $LINES lines"
```

## Troubleshooting

### "SSH key not found"

Ensure your SSH key exists:
```bash
ls -la ~/.ssh/mcp_vps
```

If missing, configure it first.

### "Permission denied"

Make the executor script executable:
```bash
chmod +x scripts/execute_on_vps.sh
chmod +x scripts/your_script.sh
```

### "Connection refused"

Check VPS is accessible:
```bash
ssh -i ~/.ssh/mcp_vps root@147.79.82.234 "echo 'Connected'"
```

### Script not found on VPS

Ensure `/root/atc-cap-v2/scripts/` directory exists on VPS:
```bash
ssh -i ~/.ssh/mcp_vps root@147.79.82.234 "mkdir -p /root/atc-cap-v2/scripts"
```

## Integration with VS Code Tasks

You can also integrate these with VS Code's task system by adding to `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "VPS: View Logs",
      "type": "shell",
      "command": "./scripts/execute_on_vps.sh",
      "args": ["scripts/logs_app.sh", "100"],
      "group": "test",
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "VPS: Deploy",
      "type": "shell",
      "command": "./scripts/execute_on_vps.sh",
      "args": ["scripts/deploy.sh"],
      "group": "build"
    }
  ]
}
```

Then you can run from VS Code with `Ctrl+Shift+P` → "Tasks: Run Task"

## Best Practices

✓ **Do:**
- Keep scripts focused on a single task
- Use meaningful output messages
- Include error checking
- Document your scripts
- Test locally first if possible

✗ **Don't:**
- Use hardcoded credentials
- Rely on relative paths
- Skip error handling
- Run dangerous commands without warnings
- Forget to commit scripts to git
