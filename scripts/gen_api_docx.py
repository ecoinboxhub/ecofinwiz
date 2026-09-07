from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
import datetime

doc = Document()

for section in doc.sections:
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)

title = doc.add_heading('Finwize \u2014 External API Services', level=0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

sub = doc.add_paragraph()
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = sub.add_run(f'Integration Reference \u2022 Generated {datetime.date.today().strftime("%B %d, %Y")}')
run.font.size = Pt(11)
run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

doc.add_paragraph()

doc.add_heading('Overview', level=1)
doc.add_paragraph(
    'Finwize integrates with 20 external services across 7 categories to power '
    'its AI financial guidance platform. 17 services require API keys; 3 are free/RSS-based. '
    'All services implement graceful degradation \u2014 if a provider is unavailable or unconfigured, '
    'the platform falls back to an alternative or logs a warning and continues.'
)

def style_cell(cell, text, bold=False, size=9):
    cell.text = ''
    p = cell.paragraphs[0]
    run = p.add_run(text)
    run.font.size = Pt(size)
    run.font.name = 'Calibri'
    run.bold = bold
    p.space_before = Pt(2)
    p.space_after = Pt(2)

def style_header(cell, text):
    style_cell(cell, text, bold=True, size=9)
    shading = cell._element.get_or_add_tcPr()
    shading_elm = shading.makeelement(qn('w:shd'), {
        qn('w:fill'): '1F2937',
        qn('w:val'): 'clear',
    })
    shading.append(shading_elm)
    run = cell.paragraphs[0].runs[0]
    run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

doc.add_heading('1. Service Inventory', level=1)

services = [
    ('AI & LLM', 'OpenAI', 'Chat completions + text-embedding-3-small embeddings', 'Yes', 'OPENAI_API_KEY', 'Implemented'),
    ('AI & LLM', 'OpenRouter', 'Primary LLM provider (GPT-4o-mini, etc.)', 'Yes', 'OPENROUTER_API_KEY', 'Implemented'),
    ('AI & LLM', 'Groq', 'Alternative LLM provider (Llama 3.3 70B)', 'Yes', 'GROQ_API_KEY', 'Implemented'),
    ('Payments', 'Paystack', 'Primary payment gateway (Nigeria)', 'Yes', 'PAYSTACK_SECRET_KEY / PUBLIC_KEY', 'Implemented'),
    ('Payments', 'Flutterwave', 'Secondary payment gateway (rest of Africa)', 'Yes', 'FLUTTERWAVE_SECRET_KEY / PUBLIC_KEY', 'Implemented'),
    ('Email', 'SendGrid', 'Primary email delivery (verification, alerts)', 'Yes', 'SENDGRID_API_KEY', 'Implemented'),
    ('Email', 'Mailgun', 'Fallback email delivery', 'Yes', 'MAILGUN_API_KEY / MAILGUN_DOMAIN', 'Implemented'),
    ('SMS', 'AfricasTalking', 'Primary SMS (17+ African countries)', 'Yes', 'AFRICAS_TALKING_API_KEY / USERNAME', 'Implemented'),
    ('SMS', 'Twilio', 'Fallback SMS (global)', 'Yes', 'TWILIO_ACCOUNT_SID / AUTH_TOKEN', 'Implemented'),
    ('Analytics', 'PostHog', 'Product analytics (self-hosted or cloud)', 'Yes', 'POSTHOG_API_KEY', 'Implemented'),
    ('Monitoring', 'Sentry', 'Error tracking and performance monitoring', 'Optional', 'SENTRY_DSN', 'Implemented'),
    ('Storage', 'AWS S3', 'File/document cloud storage', 'Yes', 'S3_ACCESS_KEY_ID / SECRET_ACCESS_KEY', 'Implemented'),
    ('Vector DB', 'Pinecone', 'Vector database for RAG knowledge base', 'Yes', 'PINECONE_API_KEY', 'Implemented'),
    ('Cache/Queue', 'Redis', 'Caching + Celery message broker', 'Self-hosted', 'REDIS_URL', 'Implemented'),
    ('News', 'NewsAPI', 'Supplemental global financial news', 'Yes', 'NEWSAPI_KEY', 'Implemented'),
    ('News (RSS)', 'Nairametrics', 'Nigerian financial news (RSS)', 'No', '(free RSS)', 'Implemented'),
    ('News (RSS)', 'BusinessDay', 'Nigerian business news (RSS)', 'No', '(free RSS)', 'Implemented'),
    ('News (RSS)', 'TechCabal', 'Nigerian tech news (RSS)', 'No', '(free RSS)', 'Implemented'),
    ('News (RSS)', 'Ventures Africa', 'Pan-African business news (RSS)', 'No', '(free RSS)', 'Implemented'),
    ('News (RSS)', 'Bloomberg Africa', 'Global African markets (RSS)', 'No', '(free RSS)', 'Implemented'),
    ('News (RSS)', 'CNBC Africa', 'Pan-African business news (RSS)', 'No', '(free RSS)', 'Implemented'),
    ('Forex', 'ExchangeRate-API', 'Live foreign exchange rates', 'Yes', 'EXCHANGE_RATE_API_KEY', 'Implemented'),
    ('Forex (Fallback)', 'CBN (Central Bank of Nigeria)', 'Official NGN exchange rates', 'No', '(public website scrape)', 'Implemented'),
    ('Auth', 'Google OAuth', 'Social login / Google Sign-In', 'Yes', 'GOOGLE_CLIENT_ID / SECRET', 'Implemented'),
    ('Embedding Alt', 'Jina AI', 'Free embedding API (open-source alt)', 'Yes', 'JINA_EMBEDDING_API_KEY', 'Implemented'),
]

table = doc.add_table(rows=1, cols=6)
table.alignment = WD_TABLE_ALIGNMENT.CENTER
table.style = 'Table Grid'

headers = ['Category', 'Service', 'Purpose', 'API Key', 'Config Variable(s)', 'Status']
for i, h in enumerate(headers):
    style_header(table.rows[0].cells[i], h)

for cat, svc, purpose, key_req, config_var, status in services:
    row = table.add_row()
    style_cell(row.cells[0], cat)
    style_cell(row.cells[1], svc, bold=True)
    style_cell(row.cells[2], purpose)
    style_cell(row.cells[3], key_req)
    style_cell(row.cells[4], config_var)
    style_cell(row.cells[5], status)

widths = [Cm(2.5), Cm(3.0), Cm(5.5), Cm(2.0), Cm(4.5), Cm(2.5)]
for row in table.rows:
    for i, w in enumerate(widths):
        row.cells[i].width = w

doc.add_page_break()
doc.add_heading('2. Graceful Degradation Behavior', level=1)
doc.add_paragraph(
    'Every external service implements fallback behavior so the platform never crashes '
    'when a provider is unavailable or unconfigured. Below is the degradation chain for each category.'
)

deg_table = doc.add_table(rows=1, cols=4)
deg_table.alignment = WD_TABLE_ALIGNMENT.CENTER
deg_table.style = 'Table Grid'

deg_headers = ['Category', 'Primary', 'Fallback 1', 'Fallback 2']
for i, h in enumerate(deg_headers):
    style_header(deg_table.rows[0].cells[i], h)

degradations = [
    ('AI/LLM', 'OpenRouter', 'Groq', 'OpenAI direct'),
    ('Embeddings', 'OpenAI (text-embedding-3-small)', 'Jina AI (jina-embeddings-v2)', 'sentence-transformers (local)'),
    ('Payments', 'Paystack (Nigeria)', 'Flutterwave (rest of Africa)', 'Manual activation (dev mode)'),
    ('Email', 'SendGrid', 'Mailgun', 'Warning log (no-op)'),
    ('SMS', 'AfricasTalking (17+ African countries)', 'Twilio (global)', 'Warning log (no-op)'),
    ('Exchange Rates', 'ExchangeRate-API (v6)', 'CBN official rates scrape', 'Hardcoded approximate rates'),
    ('News', 'RSS feeds (6 African sources)', 'NewsAPI.org', 'Empty list (no news shown)'),
    ('Storage', 'AWS S3 (aioboto3)', 'Local disk storage', '\u2014'),
    ('Analytics', 'PostHog (cloud)', 'PostHog (self-hosted)', 'Silent no-op'),
]

for cat, primary, fallback1, fallback2 in degradations:
    row = deg_table.add_row()
    style_cell(row.cells[0], cat, bold=True)
    style_cell(row.cells[1], primary)
    style_cell(row.cells[2], fallback1)
    style_cell(row.cells[3], fallback2)

doc.add_page_break()
doc.add_heading('3. Environment Variables Quick Reference', level=1)
doc.add_paragraph(
    'All API keys and configuration live in the .env file at the project root. '
    'The Settings class in backend/app/config.py loads them via Pydantic Settings v2.'
)

cfg_table = doc.add_table(rows=1, cols=3)
cfg_table.alignment = WD_TABLE_ALIGNMENT.CENTER
cfg_table.style = 'Table Grid'

cfg_headers = ['Variable', 'Required', 'Default']
for i, h in enumerate(cfg_headers):
    style_header(cfg_table.rows[0].cells[i], h)

configs = [
    ('SENDGRID_API_KEY', 'No (fallback to Mailgun)', '""'),
    ('MAILGUN_API_KEY', 'No (fallback to SendGrid)', '""'),
    ('MAILGUN_DOMAIN', 'Required if Mailgun used', '""'),
    ('EMAIL_FROM_ADDRESS', 'No', 'noreply@finwize.app'),
    ('EMAIL_FROM_NAME', 'No', 'Finwize'),
    ('AFRICAS_TALKING_API_KEY', 'No (fallback to Twilio)', '""'),
    ('AFRICAS_TALKING_USERNAME', 'No', 'finwize'),
    ('SMS_FROM_NUMBER', 'No', 'FINWIZE'),
    ('TWILIO_ACCOUNT_SID', 'No (fallback to AT)', '""'),
    ('TWILIO_AUTH_TOKEN', 'Required if Twilio used', '""'),
    ('TWILIO_FROM_NUMBER', 'Required if Twilio used', '""'),
    ('PAYSTACK_SECRET_KEY', 'No (fallback to Flutterwave)', '""'),
    ('PAYSTACK_PUBLIC_KEY', 'No', '""'),
    ('FLUTTERWAVE_SECRET_KEY', 'No (fallback to Paystack)', '""'),
    ('FLUTTERWAVE_PUBLIC_KEY', 'No', '""'),
    ('POSTHOG_API_KEY', 'No (silent no-op)', '""'),
    ('POSTHOG_HOST', 'No', 'https://app.posthog.com'),
    ('S3_BUCKET_NAME', 'No (fallback to local disk)', '""'),
    ('S3_REGION', 'No', 'eu-west-1'),
    ('S3_ACCESS_KEY_ID', 'Required if S3 used', '""'),
    ('S3_SECRET_ACCESS_KEY', 'Required if S3 used', '""'),
    ('S3_ENDPOINT_URL', 'No', '""'),
    ('S3_USE_PATH_STYLE', 'No', 'false'),
    ('LOCAL_STORAGE_DIR', 'No', 'uploads/'),
    ('NEWSAPI_KEY', 'No (RSS-only mode)', '""'),
    ('EXCHANGE_RATE_API_KEY', 'No (fallback to CBN + hardcoded)', '""'),
    ('JINA_EMBEDDING_API_KEY', 'No (fallback to local)', '""'),
    ('FRONTEND_URL', 'No', 'http://localhost:5300'),
    ('OPENAI_API_KEY', 'Shared with embeddings if set', '""'),
    ('OPENROUTER_API_KEY', 'Yes (primary LLM)', '""'),
    ('OPENROUTER_MODEL', 'No', 'openai/gpt-4o-mini'),
    ('GROQ_API_KEY', 'No (alternative LLM)', '""'),
    ('GROQ_MODEL', 'No', 'llama-3.3-70b-versatile'),
    ('PINECONE_API_KEY', 'Yes for RAG', '""'),
    ('PINECONE_ENVIRONMENT', 'No', 'us-east-1-aws'),
    ('PINECONE_INDEX_NAME', 'No', 'finwize-knowledge'),
    ('GOOGLE_CLIENT_ID', 'Yes for Google OAuth', '""'),
    ('GOOGLE_CLIENT_SECRET', 'Yes for Google OAuth', '""'),
    ('SENTRY_DSN', 'No (optional)', '""'),
]

for var, req, default in configs:
    row = cfg_table.add_row()
    style_cell(row.cells[0], var, bold=True)
    style_cell(row.cells[1], req)
    style_cell(row.cells[2], default)

doc.add_page_break()
doc.add_heading('4. Integration Implementation Status', level=1)

stat_table = doc.add_table(rows=1, cols=4)
stat_table.alignment = WD_TABLE_ALIGNMENT.CENTER
stat_table.style = 'Table Grid'

stat_headers = ['Service', 'Backend Service File', 'Wired Into Routers', 'Webhook']
for i, h in enumerate(stat_headers):
    style_header(stat_table.rows[0].cells[i], h)

impl_status = [
    ('SendGrid + Mailgun', 'services/email_service.py', 'auth/service.py (verify, welcome)', '\u2014'),
    ('Paystack + Flutterwave', 'services/payment_service.py', 'subscriptions/router.py (upgrade)', 'subscriptions/webhook.py'),
    ('AfricasTalking + Twilio', 'services/sms_service.py', 'Not yet wired', '\u2014'),
    ('PostHog', 'services/analytics_service.py', 'auth, finance, ai, business routers', '\u2014'),
    ('AWS S3', 'services/storage_service.py', 'Not yet wired (uses local disk)', '\u2014'),
    ('NewsAPI + RSS', 'services/news_service.py', 'scripts/news_scheduler.py (Celery beat)', '\u2014'),
    ('ExchangeRate-API', 'services/exchange_rate_service.py', 'Not yet wired', '\u2014'),
    ('OpenAI + Jina Embeddings', 'services/embedding_service.py', 'Not yet wired (RAG uses local)', '\u2014'),
]

for svc, file, wired, webhook in impl_status:
    row = stat_table.add_row()
    style_cell(row.cells[0], svc, bold=True)
    style_cell(row.cells[1], file)
    style_cell(row.cells[2], wired)
    style_cell(row.cells[3], webhook)

doc.add_paragraph()
footer = doc.add_paragraph()
footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = footer.add_run('\u2014 End of Document \u2014')
run.font.size = Pt(9)
run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)

output_path = r'C:\Users\ibrah\Documents\Gemini\Fellow_AI_Fintech_NextGen_Leaders_Fellowship_2026\Finwize\docs\external_api_services.docx'
doc.save(output_path)
print(f'DOCX saved to: {output_path}')
