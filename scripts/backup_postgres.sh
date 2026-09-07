#!/usr/bin/env bash
# backup_postgres.sh - Encrypted PostgreSQL backup to S3-compatible storage
# Runs daily via GitHub Actions at 02:00 UTC
#
# Required Environment Variables:
#   DATABASE_URL - PostgreSQL connection string
#   BACKUP_S3_BUCKET - S3 bucket name (default: finwize-backups)
#   BACKUP_S3_ENDPOINT - S3 endpoint URL (for R2, MinIO, etc.)
#   BACKUP_S3_REGION - S3 region (default: auto)
#   BACKUP_ENCRYPTION_KEY - age encryption passphrase
#   AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY - S3 credentials
#
# Optional:
#   RETENTION_DAILY - Daily backups to keep (default: 7)
#   RETENTION_WEEKLY - Weekly backups to keep (default: 4)
#   RETENTION_MONTHLY - Monthly backups to keep (default: 12)

set -euo pipefail

# Configuration with defaults
DB_URL="${DATABASE_URL:-}"
S3_BUCKET="${BACKUP_S3_BUCKET:-finwize-backups}"
S3_ENDPOINT="${BACKUP_S3_ENDPOINT:-}"
S3_REGION="${BACKUP_S3_REGION:-auto}"
S3_PREFIX="postgres"
ENCRYPTION_KEY="${BACKUP_ENCRYPTION_KEY:-}"
RETENTION_DAILY="${RETENTION_DAILY:-7}"
RETENTION_WEEKLY="${RETENTION_WEEKLY:-4}"
RETENTION_MONTHLY="${RETENTION_MONTHLY:-12}"

# AWS CLI config for S3-compatible endpoints
if [[ -n "${S3_ENDPOINT}" ]]; then
  AWS_CLI_OPTS="--endpoint-url ${S3_ENDPOINT}"
else
  AWS_CLI_OPTS=""
fi

if [[ -n "${S3_REGION}" && "${S3_REGION}" != "auto" ]]; then
  AWS_CLI_OPTS="${AWS_CLI_OPTS} --region ${S3_REGION}"
fi

# Validate required variables
if [[ -z "${DB_URL}" ]]; then
  echo "ERROR: DATABASE_URL not set" >&2
  exit 1
fi

if [[ -z "${ENCRYPTION_KEY}" ]]; then
  echo "ERROR: BACKUP_ENCRYPTION_KEY not set" >&2
  exit 1
fi

# Check dependencies
for cmd in pg_dump age aws sha256sum; do
  if ! command -v "${cmd}" &> /dev/null; then
    echo "ERROR: Required command '${cmd}' not found" >&2
    exit 1
  fi
done

# Timestamp
TIMESTAMP=$(date -u +"%Y%m%d_%H%M%S")
DATE_DIR=$(date -u +"%Y/%m/%d")
FILENAME="finwize_${TIMESTAMP}.dump"
ENCRYPTED_FILE="${FILENAME}.age"
MANIFEST_FILE="backup-manifest.json"

# Temp directory
TMPDIR=$(mktemp -d)
trap "rm -rf ${TMPDIR}" EXIT

echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] Starting PostgreSQL backup..."
echo "  Database: $(echo "${DB_URL}" | sed 's/:[^:@]*@/:***@/')"
echo "  S3 Bucket: ${S3_BUCKET}"
echo "  File: ${ENCRYPTED_FILE}"

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
  echo "ERROR: Dump file is empty!" >&2
  exit 1
fi

DUMP_SIZE=$(du -h "${TMPDIR}/${FILENAME}" | cut -f1)
echo "  Dump size: ${DUMP_SIZE}"

# 2. Encrypt with age (AES-256 via ChaCha20-Poly1305)
echo "${ENCRYPTION_KEY}" | age --encrypt --passphrase --output "${TMPDIR}/${ENCRYPTED_FILE}" "${TMPDIR}/${FILENAME}"

ENCRYPTED_SIZE=$(du -h "${TMPDIR}/${ENCRYPTED_FILE}" | cut -f1)
echo "  Encrypted size: ${ENCRYPTED_SIZE}"

# 3. Calculate checksum
CHECKSUM=$(sha256sum "${TMPDIR}/${ENCRYPTED_FILE}" | cut -d' ' -f1)

# 4. Upload to S3 (daily)
S3_DAILY_PATH="s3://${S3_BUCKET}/${S3_PREFIX}/daily/${DATE_DIR}/${ENCRYPTED_FILE}"
echo "  Uploading to ${S3_DAILY_PATH}..."
aws ${AWS_CLI_OPTS} s3 cp "${TMPDIR}/${ENCRYPTED_FILE}" "${S3_DAILY_PATH}" --storage-class STANDARD_IA

# 5. Manage retention tiers
DOW=$(date -u +"%u")  # 1=Mon, 7=Sun
DOM=$(date -u +"%d")

# Weekly backup (on Sundays)
if [[ "${DOW}" == "7" ]]; then
  S3_WEEKLY_PATH="s3://${S3_BUCKET}/${S3_PREFIX}/weekly/${DATE_DIR}/${ENCRYPTED_FILE}"
  echo "  Storing weekly backup..."
  aws ${AWS_CLI_OPTS} s3 cp "${TMPDIR}/${ENCRYPTED_FILE}" "${S3_WEEKLY_PATH}" --storage-class STANDARD_IA
fi

# Monthly backup (on 1st of month)
if [[ "${DOM}" == "01" ]]; then
  S3_MONTHLY_PATH="s3://${S3_BUCKET}/${S3_PREFIX}/monthly/${DATE_DIR}/${ENCRYPTED_FILE}"
  echo "  Storing monthly backup..."
  aws ${AWS_CLI_OPTS} s3 cp "${TMPDIR}/${ENCRYPTED_FILE}" "${S3_MONTHLY_PATH}" --storage-class GLACIER_IR
fi

# 6. Get PostgreSQL version
PG_VERSION=$(psql "${DB_URL}" -t -c 'SHOW server_version;' 2>/dev/null | xargs || echo "unknown")

# 7. Create/update manifest
cat > "${TMPDIR}/${MANIFEST_FILE}" <<EOF
{
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "database": "finwize",
  "latest_backup": {
    "file": "${ENCRYPTED_FILE}",
    "path": "daily/${DATE_DIR}/${ENCRYPTED_FILE}",
    "size_bytes": $(stat -c%s "${TMPDIR}/${ENCRYPTED_FILE}"),
    "checksum_sha256": "${CHECKSUM}",
    "pg_version": "${PG_VERSION}"
  },
  "retention_policy": {
    "daily": ${RETENTION_DAILY},
    "weekly": ${RETENTION_WEEKLY},
    "monthly": ${RETENTION_MONTHLY}
  },
  "storage": {
    "bucket": "${S3_BUCKET}",
    "prefix": "${S3_PREFIX}",
    "encryption": "age (AES-256/ChaCha20-Poly1305)"
  }
}
EOF

echo "  Updating manifest..."
aws ${AWS_CLI_OPTS} s3 cp "${TMPDIR}/${MANIFEST_FILE}" "s3://${S3_BUCKET}/${S3_PREFIX}/metadata/${MANIFEST_FILE}"

# 8. Cleanup old daily backups (older than retention)
# Note: S3 Lifecycle Policy should handle this, but we can also do it here
if command -v jq &> /dev/null; then
  echo "  Cleaning up old daily backups (keeping ${RETENTION_DAILY})..."
  aws ${AWS_CLI_OPTS} s3 ls "s3://${S3_BUCKET}/${S3_PREFIX}/daily/" --recursive | \
    awk '{print $4}' | \
    sort -r | \
    tail -n +$((RETENTION_DAILY + 1)) | \
    while read -r old_file; do
      if [[ -n "${old_file}" ]]; then
        echo "    Deleting old backup: ${old_file}"
        aws ${AWS_CLI_OPTS} s3 rm "s3://${S3_BUCKET}/${old_file}"
      fi
    done
fi

echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] Backup completed successfully: ${ENCRYPTED_FILE}"
echo "  Manifest: s3://${S3_BUCKET}/${S3_PREFIX}/metadata/${MANIFEST_FILE}"