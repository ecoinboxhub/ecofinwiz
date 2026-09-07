# Disaster Recovery Plan

> **Purpose**: Define procedures for data backup, restoration, and business continuity
> **Audience**: DevOps Engineer, Engineering Lead
> **Review Cycle**: Quarterly

---

## Recovery Objectives

| Metric | Current | Target | Notes |
|--------|---------|--------|-------|
| **RTO (Recovery Time Objective)** | 4 hours | < 1 hour | Time to restore service |
| **RPO (Recovery Point Objective)** | 24 hours | < 1 hour | Max data loss acceptable |
| **Availability Target** | 99.9% | 99.95% | Monthly uptime |
| **Backup Retention** | 7d/4w/12m | 30d/12w/36m | Daily/Weekly/Monthly |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Production Environment                    │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────┐  │
│  │   API       │    │  Frontend   │    │  PostgreSQL     │  │
│  │  (Railway)  │    │  (Vercel)   │    │  (Managed PG)   │  │
│  └──────┬──────┘    └──────┬──────┘    └────────┬────────┘  │
│         │                  │                    │            │
│         └──────────────────┼────────────────────┘            │
│                            ▼                                  │
│                   ┌─────────────────┐                         │
│                   │  Automated      │                         │
│                   │  Backup Job     │                         │
│                   │  (GitHub Actions)│                        │
│                   └────────┬────────┘                         │
│                            ▼                                  │
│                   ┌─────────────────┐                         │
│                   │  S3/R2 Storage  │                         │
│                   │  (Encrypted)    │                         │
│                   └─────────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Backup Strategy

### What We Back Up

| Data Source | Method | Frequency | Retention | Encryption |
|-------------|--------|-----------|-----------|------------|
| PostgreSQL | `pg_dump` (custom) | Daily 02:00 UTC | 7 daily, 4 weekly, 12 monthly | AES-256 (age) |
| Redis | RDB snapshot | Daily 03:00 UTC | 7 daily | AES-256 (age) |
| Application Config | Git repo | Continuous | Forever | N/A (public) |
| Secrets | GitHub Environments | N/A | N/A | Encrypted at rest |

### What We DON'T Back Up
- MongoDB (deprecated, migrated to PostgreSQL)
- Container images (stored in Docker Hub)
- Logs (shipped to Loki/CloudWatch)
- Temporary files, caches

### Backup Storage

- **Primary**: Cloudflare R2 (S3-compatible, zero egress fees)
- **Secondary**: AWS S3 (cross-region replication)
- **Bucket Structure**:
  ```
  s3://finwize-backups/
  ├── postgres/
  │   ├── daily/     (7 files)
  │   ├── weekly/    (4 files)
  │   └── monthly/   (12 files)
  ├── redis/
  │   └── daily/     (7 files)
  └── metadata/
      └── backup-manifest.json
  ```

---

## Backup Scripts

### PostgreSQL Backup (`scripts/backup_postgres.sh`)

```bash
#!/usr/bin/env bash
# backup_postgres.sh - Encrypted PostgreSQL backup to S3
# Runs daily via GitHub Actions at 02:00 UTC

set -euo pipefail

# Configuration
DB_URL="${DATABASE_URL}"
S3_BUCKET="${BACKUP_S3_BUCKET:-finwize-backups}"
S3_PREFIX="postgres"
ENCRYPTION_KEY="${BACKUP_ENCRYPTION_KEY}"
RETENTION_DAILY=7
RETENTION_WEEKLY=4
RETENTION_MONTHLY=12

# Timestamp
TIMESTAMP=$(date -u +"%Y%m%d_%H%M%S")
DATE_DIR=$(date -u +"%Y/%m/%d")
FILENAME="finwize_${TIMESTAMP}.dump"
ENCRYPTED_FILE="${FILENAME}.age"

# Temp directory
TMPDIR=$(mktemp -d)
trap "rm -rf ${TMPDIR}" EXIT

echo "[$(date -u)] Starting PostgreSQL backup..."

# 1. Dump database (custom format, compressed, no owner/privileges)
pg_dump \
  --format=custom \
  --compress=9 \
  --no-owner \
  --no-privileges \
  --dbname="${DB_URL}" \
  --file="${TMPDIR}/${FILENAME}"

# Verify dump
if [[ ! -s "${TMPDIR}/${FILENAME}" ]]; then
  echo "ERROR: Dump file is empty!"
  exit 1
fi

DUMP_SIZE=$(du -h "${TMPDIR}/${FILENAME}" | cut -f1)
echo "Dump size: ${DUMP_SIZE}"

# 2. Encrypt with age
echo "${ENCRYPTION_KEY}" | age --encrypt --passphrase --output "${TMPDIR}/${ENCRYPTED_FILE}" "${TMPDIR}/${FILENAME}"

ENCRYPTED_SIZE=$(du -h "${TMPDIR}/${ENCRYPTED_FILE}" | cut -f1)
echo "Encrypted size: ${ENCRYPTED_SIZE}"

# 3. Upload to S3 (daily)
S3_DAILY_PATH="s3://${S3_BUCKET}/${S3_PREFIX}/daily/${DATE_DIR}/${ENCRYPTED_FILE}"
aws s3 cp "${TMPDIR}/${ENCRYPTED_FILE}" "${S3_DAILY_PATH}" --storage-class STANDARD_IA

# 4. Manage retention (weekly on Sundays, monthly on 1st)
DOW=$(date -u +"%u")  # 1=Mon, 7=Sun
DOM=$(date -u +"%d")

if [[ "${DOW}" == "7" ]]; then
  S3_WEEKLY_PATH="s3://${S3_BUCKET}/${S3_PREFIX}/weekly/${DATE_DIR}/${ENCRYPTED_FILE}"
  aws s3 cp "${TMPDIR}/${ENCRYPTED_FILE}" "${S3_WEEKLY_PATH}" --storage-class STANDARD_IA
  echo "Weekly backup stored"
fi

if [[ "${DOM}" == "01" ]]; then
  S3_MONTHLY_PATH="s3://${S3_BUCKET}/${S3_PREFIX}/monthly/${DATE_DIR}/${ENCRYPTED_FILE}"
  aws s3 cp "${TMPDIR}/${ENCRYPTED_FILE}" "${S3_MONTHLY_PATH}" --storage-class GLACIER_IR
  echo "Monthly backup stored"
fi

# 5. Cleanup old backups (handled by S3 lifecycle policy)
# But we can also clean locally if needed

# 6. Update manifest
cat > "${TMPDIR}/manifest.json" <<EOF
{
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "database": "finwize",
  "file": "${ENCRYPTED_FILE}",
  "size_bytes": $(stat -c%s "${TMPDIR}/${ENCRYPTED_FILE}"),
  "checksum": "$(sha256sum "${TMPDIR}/${ENCRYPTED_FILE}" | cut -d' ' -f1)",
  "pg_version": "$(psql "${DB_URL}" -t -c 'SHOW server_version;' | xargs)",
  "retention": {
    "daily": ${RETENTION_DAILY},
    "weekly": ${RETENTION_WEEKLY},
    "monthly": ${RETENTION_MONTHLY}
  }
}
EOF

aws s3 cp "${TMPDIR}/manifest.json" "s3://${S3_BUCKET}/${S3_PREFIX}/metadata/backup-manifest.json"

echo "[$(date -u)] Backup completed successfully: ${ENCRYPTED_FILE}"
```

### Redis Backup (`scripts/backup_redis.sh`)

```bash
#!/usr/bin/env bash
# backup_redis.sh - Redis RDB snapshot to S3

set -euo pipefail

REDIS_URL="${REDIS_URL}"
S3_BUCKET="${BACKUP_S3_BUCKET:-finwize-backups}"
ENCRYPTION_KEY="${BACKUP_ENCRYPTION_KEY}"

TIMESTAMP=$(date -u +"%Y%m%d_%H%M%S")
FILENAME="redis_${TIMESTAMP}.rdb"
ENCRYPTED_FILE="${FILENAME}.age"

TMPDIR=$(mktemp -d)
trap "rm -rf ${TMPDIR}" EXIT

echo "[$(date -u)] Starting Redis backup..."

# Trigger BGSAVE
redis-cli -u "${REDIS_URL}" BGSAVE

# Wait for completion
while [[ $(redis-cli -u "${REDIS_URL}" LASTSAVE) -eq $(redis-cli -u "${REDIS_URL}" LASTSAVE) ]]; do
  sleep 1
done

# Copy RDB file (location depends on Redis config)
# For managed Redis, use redis-cli --rdb
redis-cli -u "${REDIS_URL}" --rdb "${TMPDIR}/${FILENAME}"

# Encrypt and upload
echo "${ENCRYPTION_KEY}" | age --encrypt --passphrase --output "${TMPDIR}/${ENCRYPTED_FILE}" "${TMPDIR}/${FILENAME}"
aws s3 cp "${TMPDIR}/${ENCRYPTED_FILE}" "s3://${S3_BUCKET}/redis/daily/${ENCRYPTED_FILE}" --storage-class STANDARD_IA

echo "[$(date -u)] Redis backup completed: ${ENCRYPTED_FILE}"
```

---

## Restore Procedures

### PostgreSQL Restore (`scripts/restore_postgres.sh`)

```bash
#!/usr/bin/env bash
# restore_postgres.sh - Restore PostgreSQL from encrypted backup
# Usage: ./restore_postgres.sh <backup_file> [target_db_url]

set -euo pipefail

BACKUP_FILE="${1:-}"
TARGET_DB_URL="${2:-${DATABASE_URL}}"
ENCRYPTION_KEY="${BACKUP_ENCRYPTION_KEY}"

if [[ -z "${BACKUP_FILE}" ]]; then
  echo "Usage: $0 <s3://bucket/path/file.dump.age> [target_db_url]"
  exit 1
fi

if [[ -z "${ENCRYPTION_KEY}" ]]; then
  echo "ERROR: BACKUP_ENCRYPTION_KEY not set"
  exit 1
fi

TMPDIR=$(mktemp -d)
trap "rm -rf ${TMPDIR}" EXIT

echo "[$(date -u)] Starting restore from ${BACKUP_FILE}..."

# 1. Download from S3
LOCAL_ENCRYPTED="${TMPDIR}/$(basename "${BACKUP_FILE}")"
aws s3 cp "${BACKUP_FILE}" "${LOCAL_ENCRYPTED}"

# 2. Decrypt
LOCAL_DUMP="${TMPDIR}/restore.dump"
echo "${ENCRYPTION_KEY}" | age --decrypt --passphrase --output "${LOCAL_DUMP}" "${LOCAL_ENCRYPTED}"

# 3. Verify dump
if [[ ! -s "${LOCAL_DUMP}" ]]; then
  echo "ERROR: Decrypted dump is empty!"
  exit 1
fi

# 4. Restore (requires superuser for clean restore)
echo "Restoring to ${TARGET_DB_URL}..."
pg_restore \
  --clean \
  --if-exists \
  --no-owner \
  --no-privileges \
  --dbname="${TARGET_DB_URL}" \
  "${LOCAL_DUMP}"

# 5. Verify restore
TABLE_COUNT=$(psql "${TARGET_DB_URL}" -t -c "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';" | xargs)
echo "Restored ${TABLE_COUNT} tables"

# 6. Run migrations to ensure schema is current
alembic -c /app/alembic.ini upgrade head

echo "[$(date -u)] Restore completed successfully"
```

### Point-in-Time Recovery (Future: WAL-G)

```bash
# TODO: Implement WAL-G for continuous archiving
# This would enable RPO < 1 minute
# 
# Setup:
# 1. Configure PostgreSQL wal_level = replica
# 2. Set archive_command to WAL-G
# 3. WAL-G pushes WAL files to S3 continuously
# 4. Restore: wal-g backup-fetch + wal-g replay
```

---

## Disaster Scenarios & Response

### Scenario 1: Database Corruption / Accidental Deletion

**Detection**: Application errors, monitoring alerts
**Response Time**: < 30 minutes
**Steps**:
1. Confirm corruption (check pg_dump, pg_verifybackup)
2. Identify last good backup (check manifest)
3. Provision new PostgreSQL instance (Railway/Cloud SQL)
4. Run `restore_postgres.sh` with latest daily backup
5. Verify data integrity (row counts, key tables)
6. Update DNS/API config to point to new DB
7. Run smoke tests
8. Notify stakeholders

**Data Loss**: Up to 24 hours (since last daily backup)

---

### Scenario 2: Primary Region Outage (Cloud Provider)

**Detection**: Health checks failing, Cloudflare origin errors
**Response Time**: < 15 minutes
**Steps**:
1. Confirm outage (check provider status page)
2. Failover to secondary region (pre-provisioned)
3. Restore database from latest backup to secondary region
4. Update DNS (Cloudflare) to point to secondary
5. Verify all services healthy
6. Communicate status

**Preparation**:
- Secondary PostgreSQL instance in different region (warm standby)
- Infrastructure as Code (Terraform) for quick provisioning
- DNS TTL set to 60s for fast failover

---

### Scenario 3: Ransomware / Data Breach

**Detection**: Unusual access patterns, encryption alerts
**Response Time**: < 1 hour
**Steps**:
1. **Isolate**: Revoke all API keys, rotate secrets immediately
2. **Assess**: Determine scope (which tables, when)
3. **Contain**: Disable affected services, enable maintenance mode
4. **Restore**: From last known clean backup (before breach)
5. **Investigate**: Forensics on compromised systems
6. **Notify**: Users, regulators (NDPA/GDPR within 72h)
7. **Harden**: Implement additional controls

**Preparation**:
- Immutable backups (S3 Object Lock / R2 retention)
- Encryption keys stored separately (HashiCorp Vault / AWS KMS)
- Incident response runbook tested quarterly

---

### Scenario 4: Complete Data Center Loss

**Detection**: All services down, provider confirms
**Response Time**: < 4 hours (RTO)
**Steps**:
1. Provision infrastructure in new region (Terraform)
2. Restore PostgreSQL from latest monthly + daily backups
3. Restore Redis from latest backup
4. Deploy application (Docker images from Docker Hub)
5. Update DNS globally
6. Run full integration test suite
7. Gradual traffic ramp-up

---

## Testing Schedule

| Test | Frequency | Owner | Success Criteria |
|------|-----------|-------|------------------|
| Backup script execution | Daily (automated) | CI/CD | Backup file exists in S3, manifest updated |
| Restore to staging | Weekly | DevOps | Staging DB matches production schema/data |
| Full DR drill | Quarterly | Engineering Lead | RTO < 4h, RPO < 24h, all services healthy |
| Backup encryption verify | Monthly | Security | `age --decrypt` works, checksum matches |
| Cross-region restore | Semi-annually | DevOps | Secondary region functional |

### Weekly Restore Test (Automated)

```yaml
# .github/workflows/test-restore.yml
name: Test Restore
on:
  schedule:
    - cron: '0 4 * * 0'  # Weekly Sunday 04:00 UTC
  workflow_dispatch:

jobs:
  test-restore:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Restore to staging
        env:
          BACKUP_ENCRYPTION_KEY: ${{ secrets.BACKUP_ENCRYPTION_KEY }}
          DATABASE_URL: ${{ secrets.STAGING_DATABASE_URL }}
        run: |
          # Get latest backup
          LATEST=$(aws s3 ls s3://finwize-backups/postgres/daily/ --recursive | sort | tail -1 | awk '{print $4}')
          ./scripts/restore_postgres.sh "s3://finwize-backups/${LATEST}"
      - name: Run smoke tests
        run: pytest tests/test_integration.py -v -k "smoke"
```

---

## Runbooks

### Runbook: Manual Backup Trigger
```bash
# Trigger backup manually
gh workflow run backup.yml -f environment=production

# Or run locally
BACKUP_ENCRYPTION_KEY=$(cat ~/.age/finwize.key) \
DATABASE_URL=postgresql://... \
BACKUP_S3_BUCKET=finwize-backups \
./scripts/backup_postgres.sh
```

### Runbook: Emergency Restore
```bash
# 1. Get latest backup manifest
aws s3 cp s3://finwize-backups/postgres/metadata/backup-manifest.json -

# 2. Choose backup file (daily/weekly/monthly)
# 3. Run restore
./scripts/restore_postgres.sh s3://finwize-backups/postgres/daily/2026/01/15/finwize_20260115_020000.dump.age

# 4. Verify
psql $DATABASE_URL -c "SELECT count(*) FROM users;"
```

### Runbook: Secret Rotation After Breach
1. Rotate all secrets (see `SECRETS_ROTATION.md`)
2. Re-deploy all services
3. Verify backup encryption key still works
4. Test restore with new key

---

## Contacts & Escalation

| Role | Name | Contact | Backup |
|------|------|---------|--------|
| Primary DevOps | [Name] | [Phone/Slack] | [Backup] |
| Engineering Lead | [Name] | [Phone/Slack] | [Backup] |
| Security Lead | [Name] | [Phone/Slack] | [Backup] |
| Cloud Provider Support | - | AWS/Cloudflare/Railway support | - |

---

## Compliance

| Regulation | Requirement | Implementation |
|------------|-------------|----------------|
| **NDPA (Nigeria)** | Data localization, breach notification 72h | Backups in EU region, automated alerts |
| **GDPR** | Right to erasure, data portability | Backup encryption, selective restore |
| **PCI DSS** | Encrypted backups, access logging | age encryption, S3 access logs |
| **SOC 2** | Backup testing, monitoring | Quarterly DR drills, Sentry alerts |

---

## Appendix: Key Commands Quick Reference

```bash
# List backups
aws s3 ls s3://finwize-backups/postgres/daily/ --recursive --human-readable

# Get latest backup
aws s3 ls s3://finwize-backups/postgres/daily/ --recursive | sort -k1,2 | tail -1

# Download specific backup
aws s3 cp s3://finwize-backups/postgres/daily/2026/01/15/finwize_20260115_020000.dump.age .

# Decrypt backup
age --decrypt --passphrase "$BACKUP_ENCRYPTION_KEY" -o backup.dump backup.dump.age

# Verify dump contents
pg_restore --list backup.dump | head -20

# Check backup size trend
aws s3 ls s3://finwize-backups/postgres/daily/ --recursive --human-readable --summarize
```