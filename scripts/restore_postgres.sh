#!/usr/bin/env bash
# restore_postgres.sh - Restore PostgreSQL from encrypted backup
#
# Usage:
#   ./restore_postgres.sh <s3://bucket/path/file.dump.age> [target_database_url]
#   ./restore_postgres.sh --latest [target_database_url]
#   ./restore_postgres.sh --list
#
# Required Environment Variables:
#   BACKUP_ENCRYPTION_KEY - age decryption passphrase
#   DATABASE_URL - Target database (if not provided as argument)
#   BACKUP_S3_BUCKET - S3 bucket name (default: finwize-backups)
#   BACKUP_S3_ENDPOINT - S3 endpoint URL (for R2, MinIO, etc.)
#   BACKUP_S3_REGION - S3 region
#   AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY - S3 credentials

set -euo pipefail

# Configuration with defaults
S3_BUCKET="${BACKUP_S3_BUCKET:-finwize-backups}"
S3_ENDPOINT="${BACKUP_S3_ENDPOINT:-}"
S3_REGION="${BACKUP_S3_REGION:-auto}"
S3_PREFIX="postgres"
ENCRYPTION_KEY="${BACKUP_ENCRYPTION_KEY:-}"
TARGET_DB_URL="${2:-${DATABASE_URL:-}}"

# AWS CLI config for S3-compatible endpoints
if [[ -n "${S3_ENDPOINT}" ]]; then
  AWS_CLI_OPTS="--endpoint-url ${S3_ENDPOINT}"
else
  AWS_CLI_OPTS=""
fi

if [[ -n "${S3_REGION}" && "${S3_REGION}" != "auto" ]]; then
  AWS_CLI_OPTS="${AWS_CLI_OPTS} --region ${S3_REGION}"
fi

# Validate encryption key
if [[ -z "${ENCRYPTION_KEY}" ]]; then
  echo "ERROR: BACKUP_ENCRYPTION_KEY not set" >&2
  exit 1
fi

# Check dependencies
for cmd in pg_restore age aws; do
  if ! command -v "${cmd}" &> /dev/null; then
    echo "ERROR: Required command '${cmd}' not found" >&2
    exit 1
  fi
done

# Helper functions
usage() {
  cat <<EOF
Usage: $0 <backup_file|--latest|--list> [target_database_url]

Arguments:
  backup_file    S3 path to backup file (e.g., s3://bucket/postgres/daily/2026/01/15/file.dump.age)
  --latest       Use the latest daily backup
  --list         List available backups

Environment Variables:
  BACKUP_ENCRYPTION_KEY   (required) age decryption passphrase
  DATABASE_URL            Target database URL (or pass as 2nd argument)
  BACKUP_S3_BUCKET        S3 bucket (default: finwize-backups)
  BACKUP_S3_ENDPOINT      S3 endpoint for R2/MinIO
  BACKUP_S3_REGION        S3 region
  AWS_ACCESS_KEY_ID       S3 credentials
  AWS_SECRET_ACCESS_KEY   S3 credentials

Examples:
  # Restore specific backup
  $0 s3://finwize-backups/postgres/daily/2026/01/15/finwize_20260115_020000.dump.age

  # Restore latest to default DATABASE_URL
  $0 --latest

  # Restore latest to specific database
  $0 --latest postgresql://user:pass@host:5432/dbname

  # List available backups
  $0 --list
EOF
}

list_backups() {
  echo "Available backups in s3://${S3_BUCKET}/${S3_PREFIX}/:"
  echo ""
  echo "=== DAILY (last 30) ==="
  aws ${AWS_CLI_OPTS} s3 ls "s3://${S3_BUCKET}/${S3_PREFIX}/daily/" --recursive --human-readable | tail -30
  echo ""
  echo "=== WEEKLY ==="
  aws ${AWS_CLI_OPTS} s3 ls "s3://${S3_BUCKET}/${S3_PREFIX}/weekly/" --recursive --human-readable
  echo ""
  echo "=== MONTHLY ==="
  aws ${AWS_CLI_OPTS} s3 ls "s3://${S3_BUCKET}/${S3_PREFIX}/monthly/" --recursive --human-readable
}

get_latest_backup() {
  aws ${AWS_CLI_OPTS} s3 ls "s3://${S3_BUCKET}/${S3_PREFIX}/daily/" --recursive | \
    sort -k1,2 | \
    tail -1 | \
    awk '{print $4}'
}

# Parse arguments
ACTION="${1:-}"

if [[ -z "${ACTION}" || "${ACTION}" == "-h" || "${ACTION}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ "${ACTION}" == "--list" ]]; then
  list_backups
  exit 0
fi

if [[ "${ACTION}" == "--latest" ]]; then
  BACKUP_PATH=$(get_latest_backup)
  if [[ -z "${BACKUP_PATH}" ]]; then
    echo "ERROR: No backups found" >&2
    exit 1
  fi
  echo "Using latest backup: ${BACKUP_PATH}"
else
  BACKUP_PATH="${ACTION}"
  # Normalize: remove s3://bucket/ prefix if provided
  BACKUP_PATH="${BACKUP_PATH#s3://${S3_BUCKET}/}"
fi

# Validate target database
if [[ -z "${TARGET_DB_URL}" ]]; then
  echo "ERROR: Target database URL not provided (set DATABASE_URL or pass as argument)" >&2
  usage
  exit 1
fi

# Full S3 path
S3_FULL_PATH="s3://${S3_BUCKET}/${BACKUP_PATH}"
FILENAME=$(basename "${BACKUP_PATH}")

# Temp directory
TMPDIR=$(mktemp -d)
trap "rm -rf ${TMPDIR}" EXIT

echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] Starting PostgreSQL restore..."
echo "  Source: ${S3_FULL_PATH}"
echo "  Target: $(echo "${TARGET_DB_URL}" | sed 's/:[^:@]*@/:***@/')"

# 1. Download from S3
LOCAL_ENCRYPTED="${TMPDIR}/${FILENAME}"
echo "  Downloading from S3..."
aws ${AWS_CLI_OPTS} s3 cp "${S3_FULL_PATH}" "${LOCAL_ENCRYPTED}"

# Verify download
if [[ ! -s "${LOCAL_ENCRYPTED}" ]]; then
  echo "ERROR: Downloaded file is empty!" >&2
  exit 1
fi

# 2. Decrypt
LOCAL_DUMP="${TMPDIR}/restore.dump"
echo "  Decrypting..."
echo "${ENCRYPTION_KEY}" | age --decrypt --passphrase --output "${LOCAL_DUMP}" "${LOCAL_ENCRYPTED}"

# Verify decryption
if [[ ! -s "${LOCAL_DUMP}" ]]; then
  echo "ERROR: Decrypted dump is empty!" >&2
  exit 1
fi

DUMP_SIZE=$(du -h "${LOCAL_DUMP}" | cut -f1)
echo "  Decrypted dump size: ${DUMP_SIZE}"

# 3. Verify dump integrity
echo "  Verifying dump integrity..."
pg_restore --list "${LOCAL_DUMP}" > /dev/null
TABLE_COUNT=$(pg_restore --list "${LOCAL_DUMP}" | grep -c "TABLE DATA" || echo "0")
echo "  Tables in backup: ${TABLE_COUNT}"

# 4. Confirm restore (unless --force or CI)
if [[ -t 0 && "${FORCE:-}" != "true" ]]; then
  echo ""
  echo "⚠️  WARNING: This will REPLACE all data in the target database!"
  echo "   Target: ${TARGET_DB_URL}"
  echo "   Source: ${S3_FULL_PATH}"
  echo "   Tables to restore: ${TABLE_COUNT}"
  echo ""
  read -p "Continue? [y/N] " -n 1 -r
  echo ""
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Restore cancelled."
    exit 1
  fi
fi

# 5. Restore database
echo "  Restoring database..."
pg_restore \
  --clean \
  --if-exists \
  --no-owner \
  --no-privileges \
  --dbname="${TARGET_DB_URL}" \
  --jobs=4 \
  "${LOCAL_DUMP}"

# 6. Verify restore
echo "  Verifying restore..."
RESTORED_TABLES=$(psql "${TARGET_DB_URL}" -t -c "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';" | xargs)
echo "  Tables restored: ${RESTORED_TABLES}"

# Check key tables
for table in users budgets transactions savings_goals; do
  count=$(psql "${TARGET_DB_URL}" -t -c "SELECT count(*) FROM ${table};" 2>/dev/null | xargs || echo "0")
  echo "    ${table}: ${count} rows"
done

# 7. Run migrations to ensure schema is current
if command -v alembic &> /dev/null; then
  echo "  Running migrations..."
  alembic -c /app/alembic.ini upgrade head 2>/dev/null || echo "  (alembic not available or failed - schema may already be current)"
fi

echo ""
echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] Restore completed successfully!"
echo "  Source backup: ${BACKUP_PATH}"
echo "  Target database: ${TARGET_DB_URL}"
echo "  Tables: ${RESTORED_TABLES}"