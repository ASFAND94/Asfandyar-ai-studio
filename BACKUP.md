# Backup and restore

The application stores owner data in SQLite. The database path is controlled by `APP_DB_PATH`, `AUTH_DB_PATH`, and `SOCIAL_DB_PATH`; production should point all three at one private persistent volume.

## Safe backup
1. Stop writes or use SQLite's online backup API (preferred over copying a live database file).
2. Create an encrypted backup using a strong key stored separately from the backup.
3. Store a second copy in a private location. Do not put database backups or encryption keys in this Git repository.
4. Test restoring into a separate staging instance before relying on a backup.

## Docker volume
The Compose volume is named `asfandyar_data`. Preserve it when upgrading the container. Removing the volume permanently removes the database unless a backup exists.
