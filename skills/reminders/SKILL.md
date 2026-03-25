---
name: reminders
description: "Set one-off or recurring reminders by writing to HEARTBEAT.md. The heartbeat system checks this file periodically and notifies the user."
---

# Reminders Skill

Use `HEARTBEAT.md` to set reminders. The heartbeat polls this file automatically and will notify the user when conditions are met.

## How it works

1. Read the current `HEARTBEAT.md` first
2. Append a reminder entry with a due datetime
3. On each heartbeat, check if any reminders are due — if so, notify the user and remove the entry

## Add a reminder

```bash
# Read current content first, then write the full updated file
```

Format for entries in `HEARTBEAT.md`:
```markdown
## Reminders

- [ ] 2026-03-23 15:30 — Call dentist
- [ ] 2026-03-24 09:00 — Stand-up meeting
```

## Check and fire reminders (run on each heartbeat)

```python
# python script to check reminders
import re
from datetime import datetime

with open(r'C:\Users\Zach Zhang\.openclaw\workspace\HEARTBEAT.md', 'r') as f:
    content = f.read()

now = datetime.now()
pattern = r'- \[ \] (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) — (.+)'
due = []
remaining = []

for m in re.finditer(pattern, content):
    dt = datetime.strptime(m.group(1), '%Y-%m-%d %H:%M')
    if dt <= now:
        due.append(m.group(2))
    else:
        remaining.append(m.group(0))

if due:
    for r in due:
        print(f'REMINDER: {r}')
    # rewrite file without fired reminders (use fs.write_file)
```

## Workflow when user sets a reminder

1. User: "remind me to do X at 3pm"
2. You: read current `HEARTBEAT.md`, append the reminder with full datetime, write it back
3. Confirm: "Got it! I'll remind you at 3:00 PM."
4. On next heartbeat when the time is past: notify the user, then remove the entry from `HEARTBEAT.md`

## Recurring reminders

Add a note like `[daily]`, `[weekly Mon]` etc. — after firing, rewrite the entry with the next due date instead of removing it.

```markdown
- [ ] 2026-03-24 09:00 [daily] — Morning check-in
```
