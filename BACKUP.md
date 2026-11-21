# Backup and restore

The application stores owner data in SQLite. The database path is controlled by `APP_DB_PATH`, `AUTH_DB_PATH`, and `SOCIAL_DB_PATH`; production should point all three at one private persistent volume.

## Create an encrypted backup
Set `APP_DB_PATH` and `APP_ENCRYPTION_KEY` in the private environment, then run:

```bash
python scripts/backup_database.py /secure-backup-location/asfandyar-latest.backup.enc
```

The script uses SQLite's online backup API, checks database integrity and encrypts the snapshot with Fernet. Store the encrypted backup separately from APP_ENCRYPTION_KEY. The script creates the backup file with owner-only permissions where supported.

## Restore
Stop the application first, then run:

```bash
python scripts/restore_database.py /secure-backup-location/asfandyar-latest.backup.enc
```

The restore script decrypts and integrity-checks the staged database before replacing the active database. If a database already exists, it creates a `.pre-restore` copy beside it. Restart the app and verify owner login and records.

1. Store a second copy in a private location. Do not put database backups or encryption keys in this Git repository.
2. Test restoring into a separate staging instance before relying on a backup.

## Docker volume
The Compose volume is named `asfandyar_data`. Preserve it when upgrading the container. Removing the volume permanently removes the database unless a backup exists.
