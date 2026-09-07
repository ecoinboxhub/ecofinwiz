#!/usr/bin/env bash
# backup_redis.sh - Redis RDB snapshot to S3-compatible storage
# Runs daily via GitHub Actions at 03:00 UTC
#
# Required Environment Variables:
#   REDIS_URL - Redis connection string (redis://user:pass@host:port/db)
#   BACKUP_S3_BUCKET - S3 bucket name (default: finwize-backups)
#   BACKUP_S3_ENDPOINT - S3 endpoint URL (for R2, MinIO, etc.)
#   BACKUP_S3_REGION - S3 region (default: auto)
#   BACKUP_ENCRYPTION_KEY - age encryption passphrase
#   AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY - S3 credentials

set -euo pipefail

# Configuration with defaults
REDIS_URL="${REDIS_URL:-}"
S3_BUCKET="${BACKUP_S3_BUCKET:-finwize-backups}"
S3_ENDPOINT="${BACKUP_S3_ENDPOINT:-}"
S3_REGION="${BACKUP_S3_REGION:-auto}"
ENCRYPTION_KEY="${BACKUP_ENCRYPTION_KEY:-}"

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
if [[ -z "${REDIS_URL}" ]]; then
  echo "ERROR: REDIS_URL not set" >&2
  exit 1
fi

if [[ -z "${ENCRYPTION_KEY}" ]]; then
  echo "ERROR: BACKUP_ENCRYPTION_KEY not set" >&2
  exit 1
fi

# Check dependencies
for cmd in redis-cli age aws sha256sum; do
  if ! command -v "${cmd}" &> /dev/null; then
    echo "ERROR: Required command '${cmd}' not found" >&2
    exit 1
  fi
done

# Timestamp
TIMESTAMP=$(date -u +"%Y%m%d_%H%M%S")
FILENAME="redis_${TIMESTAMP}.rdb"
ENCRYPTED_FILE="${FILENAME}.age"

# Temp directory
TMPDIR=$(mktemp -d)
trap "rm -rf ${TMPDIR}" EXIT

echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] Starting Redis backup..."
echo "  Redis: $(echo "${REDIS_URL}" | sed 's/:[^:@]*@/:***@/')"
echo "  S3 Bucket: ${S3_BUCKET}"
echo "  File: ${ENCRYPTED_FILE}"

# 1. Trigger BGSAVE (background save)
echo "  Triggering BGSAVE..."
redis-cli -u "${REDIS_URL}" BGSAVE > /dev/null

# 2. Wait for BGSAVE to complete
echo "  Waiting for BGSAVE to complete..."
LAST_SAVE=$(redis-cli -u "${REDIS_URL}" LASTSAVE)
while true; do
  CURRENT_SAVE=$(redis-cli -u "${REDIS_URL}" LASTSAVE)
  if [[ "${CURRENT_SAVE}" -gt "${LAST_SAVE}" ]]; then
    break
  fi
  sleep 1
done
echo "  BGSAVE completed"

# 3. Generate RDB dump using redis-cli --rdb
# This streams the RDB directly from Redis without needing filesystem access
echo "  Generating RDB dump..."
redis-cli -u "${REDIS_URL}" --rdb "${TMPDIR}/${FILENAME}"

# Verify dump
if [[ ! -s "${TMPDIR}/${FILENAME}" ]]; then
  echo "ERROR: RDB dump file is empty!" >&2
  exit 1
fi

DUMP_SIZE=$(du -h "${TMPDIR}/${FILENAME}" | cut -f1)
echo "  Dump size: ${DUMP_SIZE}"

# 4. Encrypt with age
echo "  Encrypting..."
echo "${ENCRYPTION_KEY}" | age --encrypt --passphrase --output "${TMPDIR}/${ENCRYPTED_FILE}" "${TMPDIR}/${FILENAME}"

ENCRYPTED_SIZE=$(du -h "${TMPDIR}/${ENCRYPTED_FILE}" | cut -f1)
echo "  Encrypted size: ${ENCRYPTED_SIZE}"

# 5. Calculate checksum
CHECKSUM=$(sha256sum "${TMPDIR}/${ENCRYPTED_FILE}" | cut -d' ' -f1)

# 6. Upload to S3
S3_PATH="s3://${S3_BUCKET}/redis/daily/${ENCRYPTED_FILE}"
echo "  Uploading to ${S3_PATH}..."
aws ${AWS_CLI_OPTS:-} s3 cp "${TMPDIR}/${ENCRYPTED_FILE}" "${S3_PATH}" --storage-class STANDARD_IA

# 7. Update Redis backup manifest
MANIFEST_FILE="redis-backup-manifest.json"
cat > "${TMPDIR}/${MANIFEST_FILE}" <<EOF
{
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "redis": {
    "latest_backup": {
      "file": "${ENCRYPTED_FILE}",
      "path": "redis/daily/${ENCRYPTED_FILE}",
      "size_bytes": $(stat -c%s "${TMPDIR}/${ENCRYPTED_FILE}"),
      "checksum_sha256": "${CHECKSUM}",
      "dump_size_bytes": $(stat -c%s "${TMPDIR}/${FILENAME}")
    },
    "retention_policy": {
      "daily": 7
    }
  },
  "storage": {
    "bucket": "${S3_BUCKET}",
    "prefix": "redis",
    "encryption": "age (AES-256/ChaCha20-Poly1305)"
  }
}
EOF

echo "  Updating manifest..."
aws ${AWS_CLI_OPTS:-} s3 cp "${TMPDIR}/${MANIFEST_FILE}" "s3://${S3_BUCKET}/redis/metadata/${MANIFEST_FILE}"

# 8. Cleanup old daily backups (keep 7)
if command -v jq &> /dev/null; then
  echo "  Cleaning up old Redis backups (keeping 7)..."
  aws ${AWS_CLI_OPTS:-} s3 ls "s3://${S3_BUCKET}/redis/daily/" --recursive | \
    awk '{print $4}' | \
    sort -r | \
    tail -n +8 | \
    while read -r old_file; do
      if [[ -n "${old_file}" ]]; then
        echo "    Deleting old backup: ${old_file}"
        aws ${AWS_CLI_OPTS:-} s3 rm "s3://${S3_BUCKET}/${old_file}"
      fi
    done
fi

echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] Redis backup completed successfully: ${ENCRYPTED_FILE}"
echo "  Manifest: s3://${S3_BUCKET}/redis/metadata/${MANIFEST_FILE}"