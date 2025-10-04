# Caliper Ops

Shortcuts and queries for day-to-day repo work.

## Logs
```query
path:logs/ *.log
```

## Jobs (artifacts)
```query
path:data_v2/jobs/
```

## Metadata
```query
path:data_v2/metadata/
```

## Cleanup
- PowerShell (dry-run): `./scripts/cleanup_sweeper.ps1`
- PowerShell (apply): `./scripts/cleanup_sweeper.ps1 -Execute`
- Bash (dry-run): `bash scripts/cleanup_sweeper.sh`
- Bash (apply): `bash scripts/cleanup_sweeper.sh --execute`

