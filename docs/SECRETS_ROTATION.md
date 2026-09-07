# Secrets Rotation Procedure

> **Purpose**: Secure rotation of all production API keys and secrets.
> **Frequency**: Every 90 days or immediately upon suspected compromise.
> **Responsible**: DevOps Engineer + Security Lead

---

## Rotation Schedule

| Secret | Rotation Interval | Trigger |
|--------|-------------------|---------|
| `SECRET_KEY` (JWT) | 90 days | Scheduled / breach |
| `OPENROUTER_API_KEY` | 90 days | Scheduled / quota issues |
| `GROQ_API_KEY` | 90 days | Scheduled / quota issues |
| `PINECONE_API_KEY` | 90 days | Scheduled / index issues |
| `PAYSTACK_SECRET_KEY` | 90 days | Scheduled / fraud alerts |
| `PAYSTACK_PUBLIC_KEY` | 90 days | With secret key |
| `FLUTTERWAVE_SECRET_KEY` | 90 days | Scheduled |
| `FLUTTERWAVE_PUBLIC_KEY` | 90 days | With secret key |
| `SENDGRID_API_KEY` | 90 days | Scheduled / deliverability |
| `POSTHOG_API_KEY` | 90 days | Scheduled |
| `SENTRY_DSN` | 180 days | Scheduled |
| `GOOGLE_CLIENT_SECRET` | 180 days | Scheduled / OAuth changes |
| `AFRICAS_TALKING_API_KEY` | 90 days | Scheduled |
| `TWILIO_AUTH_TOKEN` | 90 days | Scheduled |
| `S3_ACCESS_KEY_ID` / `S3_SECRET_ACCESS_KEY` | 90 days | Scheduled / IAM rotation |

---

## Pre-Rotation Checklist

- [ ] Notify team of maintenance window (15 min downtime for key swap)
- [ ] Verify new keys work in staging environment
- [ ] Prepare rollback plan (keep old keys for 24h)
- [ ] Ensure GitHub Environments secrets are accessible

---

## Rotation Steps

### 1. Generate New Keys

#### OpenRouter
1. Go to https://openrouter.ai/keys
2. Create new key with same permissions
3. Copy immediately (shown once)

#### Groq
1. Go to https://console.groq.com/keys
2. Create new API key
3. Copy immediately

#### Pinecone
1. Go to https://app.pinecone.io/organization/api-keys
2. Create new key with `Project Read/Write` permissions
3. Copy immediately

#### Paystack
1. Go to Dashboard → Settings → API Keys
2. Generate new Secret Key (starts with `sk_live_` for production)
3. Public Key remains same (starts with `pk_live_`)
4. Update webhook URL if changed

#### Flutterwave
1. Go to Dashboard → Settings → API
2. Generate new Secret Key (`FLWSECK_`)
3. Public Key (`FLWPUBK_`) remains same
4. Update webhook URL if changed

#### SendGrid
1. Go to Settings → API Keys
2. Create new key with `Mail Send` permissions
3. Copy immediately

#### PostHog
1. Go to Organization Settings → API Keys
2. Create new personal API key
3. Copy immediately

#### Sentry
1. Go to Settings → Projects → Client Keys (DSN)
2. Regenerate DSN
3. Update all clients (backend, frontend, mobile)

#### Google OAuth
1. Go to Google Cloud Console → APIs & Services → Credentials
2. Edit OAuth 2.0 Client ID → Regenerate Client Secret
3. Update Authorized Redirect URIs if changed

#### Africa's Talking
1. Go to https://account.africastalking.com/apps
2. Generate new API key
3. Copy immediately

#### Twilio
1. Go to Console → Account → API Keys
2. Create new Standard API Key
3. Copy SID and Secret immediately

#### AWS S3 / R2
1. Go to IAM → Users → Security Credentials
2. Create new Access Key
3. Update bucket policies if using key-specific conditions

---

### 2. Update Staging First

```bash
# 1. Update GitHub Environment secrets for 'staging'
# GitHub UI: Settings → Environments → staging → Environment secrets

# 2. Deploy to staging
git push origin staging  # triggers workflow

# 3. Validate in staging
python -m app.scripts.validate_keys  # Should pass with new keys
curl https://staging-api.finwize.com/health  # Should return 200
```

### 3. Update Production

```bash
# 1. Update GitHub Environment secrets for 'production'
# GitHub UI: Settings → Environments → production → Environment secrets

# 2. Deploy to production (via GitHub Actions or manual)
# Monitor deployment logs for config validation warnings

# 3. Validate in production
python -m app.scripts.validate_keys  # Should pass
curl https://api.finwize.com/health  # Should return 200
```

### 4. Verify & Cleanup

- [ ] All health checks pass
- [ ] Payment test transaction succeeds (Paystack/Flutterwave)
- [ ] AI chat works (Kemi/Chidi/Musa respond)
- [ ] RAG queries return results (Pinecone)
- [ ] Email sends (SendGrid)
- [ ] Analytics events appear (PostHog)
- [ ] Error tracking works (Sentry)
- [ ] After 24h: Revoke old keys in provider dashboards
- [ ] Update password manager / secrets vault

---

## Emergency Rotation (Breach Response)

**Time Target**: < 30 minutes

1. **Immediately** revoke compromised key in provider dashboard
2. **Generate** new key
3. **Update** GitHub Environment secret
4. **Trigger** manual workflow dispatch for `validate-secrets` on `production` environment
5. **Monitor** deployment and health checks
4. **Audit** logs for unauthorized usage (check provider usage dashboards)
5. **Document** incident in security log

---

## GitHub Environments Configuration

### Required Environments
- `development` - Auto-deploy on push to `develop`
- `staging` - Manual approval required
- `production` - Manual approval + required reviewers

### Environment Secrets (per environment)

| Secret | Development | Staging | Production |
|--------|-------------|---------|------------|
| `SECRET_KEY` | ✅ | ✅ | ✅ |
| `OPENROUTER_API_KEY` | ✅ | ✅ | ✅ |
| `GROQ_API_KEY` | ✅ | ✅ | ✅ |
| `PINECONE_API_KEY` | ✅ | ✅ | ✅ |
| `PINECONE_INDEX_NAME` | ✅ | ✅ | ✅ |
| `PAYSTACK_SECRET_KEY` | test | test | live |
| `PAYSTACK_PUBLIC_KEY` | test | test | live |
| `FLUTTERWAVE_SECRET_KEY` | test | test | live |
| `FLUTTERWAVE_PUBLIC_KEY` | test | test | live |
| `SENDGRID_API_KEY` | ✅ | ✅ | ✅ |
| `POSTHOG_API_KEY` | ✅ | ✅ | ✅ |
| `SENTRY_DSN` | ✅ | ✅ | ✅ |
| `GOOGLE_CLIENT_ID` | ✅ | ✅ | ✅ |
| `GOOGLE_CLIENT_SECRET` | ✅ | ✅ | ✅ |
| `DATABASE_URL` | local | staging | prod |
| `REDIS_URL` | local | staging | prod |

---

## Validation Commands

```bash
# Local validation (requires .env with keys)
cd backend
python -m app.scripts.validate_keys

# Expected output:
# [
#   {"service": "openrouter", "status": "valid", "latency_ms": 145, "error": null},
#   {"service": "groq", "status": "valid", "latency_ms": 89, "error": null},
#   {"service": "pinecone", "status": "valid", "latency_ms": 234, "error": null},
#   {"service": "paystack", "status": "valid", "latency_ms": 567, "error": null},
#   ...
# ]

# Check specific service
python -c "
import asyncio, httpx
async def test():
    async with httpx.AsyncClient() as c:
        r = await c.get('https://openrouter.ai/api/v1/models', headers={'Authorization': 'Bearer \$KEY'})
        print(r.status_code)
asyncio.run(test())
"
```

---

## Audit Trail

All rotations logged in:
- GitHub Actions workflow runs (`.github/workflows/validate-secrets.yml`)
- Provider audit logs (OpenRouter, Pinecone, Paystack, etc.)
- Internal security log (Confluence/Notion)

**Record for each rotation**:
- Date/time
- Secrets rotated
- Person who performed rotation
- Validation results
- Any issues encountered