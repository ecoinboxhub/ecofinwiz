from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
import datetime

doc = Document()

# ── Styles ──
style = doc.styles['Normal']
font = style.font
font.name = 'Calibri'
font.size = Pt(11)
font.color.rgb = RGBColor(0x1a, 0x1a, 0x2e)

for level in range(1, 4):
    hs = doc.styles[f'Heading {level}']
    hs.font.color.rgb = RGBColor(0x00, 0x3d, 0x6b)
    hs.font.name = 'Calibri'

# ── Helper functions ──
def add_shaded_cell(cell, text, bold=False, color=RGBColor(0xff, 0xff, 0xff), bg='003D6B', size=Pt(9)):
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(text)
    run.bold = bold
    run.font.color.rgb = color
    run.font.size = size
    run.font.name = 'Calibri'
    shading = cell._element.get_or_add_tcPr()
    shading_elem = shading.makeelement(qn('w:shd'), {
        qn('w:fill'): bg,
        qn('w:val'): 'clear'
    })
    shading.append(shading_elem)

def add_cell(cell, text, bold=False, size=Pt(9), color=RGBColor(0x1a, 0x1a, 0x2e)):
    p = cell.paragraphs[0]
    run = p.add_run(text)
    run.bold = bold
    run.font.size = size
    run.font.color.rgb = color
    run.font.name = 'Calibri'

def set_col_widths(table, widths):
    for row in table.rows:
        for i, w in enumerate(widths):
            row.cells[i].width = Cm(w)

def add_bullet(doc, text, level=0, bold_prefix=None):
    p = doc.add_paragraph(style='List Bullet')
    if bold_prefix:
        r = p.add_run(bold_prefix)
        r.bold = True
        r.font.size = Pt(10)
        r.font.name = 'Calibri'
        r2 = p.add_run(text)
        r2.font.size = Pt(10)
        r2.font.name = 'Calibri'
    else:
        r = p.add_run(text)
        r.font.size = Pt(10)
        r.font.name = 'Calibri'

def add_para(doc, text, bold=False, size=Pt(10), italic=False, space_after=Pt(6)):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.bold = bold
    r.italic = italic
    r.font.size = size
    r.font.name = 'Calibri'
    p.paragraph_format.space_after = space_after
    return p

# ═══════════════════════════════════════════════════════════════════
# TITLE PAGE
# ═══════════════════════════════════════════════════════════════════
for _ in range(6):
    doc.add_paragraph()

title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = title.add_run('EcoFinwize\nAfrican Market Analysis')
r.bold = True
r.font.size = Pt(28)
r.font.color.rgb = RGBColor(0x00, 0x3d, 0x6b)
r.font.name = 'Calibri'

doc.add_paragraph()

subtitle = doc.add_paragraph()
subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = subtitle.add_run('Comprehensive Multi-Market Competitive Matrix,\nSector Analysis, and Strategic Positioning\nfor the African Fintech Market')
r.font.size = Pt(14)
r.font.color.rgb = RGBColor(0x55, 0x55, 0x77)
r.font.name = 'Calibri'

doc.add_paragraph()
doc.add_paragraph()

date_p = doc.add_paragraph()
date_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = date_p.add_run(f'July 2026')
r.font.size = Pt(12)
r.font.color.rgb = RGBColor(0x55, 0x55, 0x77)
r.font.name = 'Calibri'

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════
# TABLE OF CONTENTS
# ═══════════════════════════════════════════════════════════════════
doc.add_heading('Table of Contents', level=1)
toc_items = [
    '1. Executive Summary',
    '2. African Fintech Market Overview (2026)',
    '3. EcoFinwize Comprehensive Multi-Market Competitive Matrix',
    '4. Deep-Dive Sector Analysis',
    '   4.1 Wealth Management Platforms',
    '   4.2 Digital Banks & Super Apps',
    '   4.3 SME Business Management Platforms',
    '   4.4 Banking AI / Chatbots',
    '   4.5 General AI Assistants',
    '   4.6 Financial Education Platforms',
    '   4.7 Global AI Financial Copilots',
    '5. Emerging Competitive Threats in the African Market',
    '6. How EcoFinwize Wins: Competitive Advantage Framework',
    '7. EcoFinwize Sustainable Competitive Advantages (Moats)',
    '8. Strategic Positioning for the African Market',
    '9. Market Validation & African Fintech Data (2026)',
    '10. Risk Factors & Mitigation for African Markets',
]
for item in toc_items:
    add_para(doc, item, size=Pt(11))

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════
# 1. EXECUTIVE SUMMARY
# ═══════════════════════════════════════════════════════════════════
doc.add_heading('1. Executive Summary', level=1)
add_para(doc, (
    'The African fintech sector in 2026 has crossed a historic threshold. After enduring a sharp funding downturn '
    'from 2023 through 2024, the sector entered a recovery phase defined by institutional maturity, strategic '
    'consolidation, and a decisive shift toward sustainable business models. African fintech attracted $3.4 billion '
    'in funding during 2025 (33% YoY increase), with Q1 2026 alone registering $187.1 million across 21 deals — '
    'a 400% quarter-over-quarter rebound. Sector revenues are projected to expand 13-fold to approximately $65 billion '
    'by 2030, making Africa the fastest-growing fintech market globally (BCG, March 2026).'
))
add_para(doc, (
    'EcoFinwize enters this market at a unique inflection point. The first wave of African fintech — mobile money, '
    'digital payments, and consumer lending — has largely matured. The second wave is being defined by AI-driven '
    'financial intelligence, embedded finance, open banking interoperability, and SME-focused infrastructure. '
    'EcoFinwize is positioned at the intersection of these converging trends: an AI-native, conversation-first '
    'financial intelligence platform built specifically for African consumers and small businesses.'
))
add_para(doc, (
    'This market analysis provides a rigorous, evidence-based examination of the African fintech competitive '
    'landscape in 2026. It maps every major competitor across seven sectors, identifies structural gaps in the '
    'market, articulates EcoFinwize\'s sustainable competitive advantages, and establishes why the platform is '
    'uniquely positioned to capture and defend its target market as an ecosystem enabler rather than an isolated disruptor.'
))

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════
# 2. AFRICAN FINTECH MARKET OVERVIEW
# ═══════════════════════════════════════════════════════════════════
doc.add_heading('2. African Fintech Market Overview (2026)', level=1)

doc.add_heading('2.1 Market Size & Growth Trajectory', level=2)
add_para(doc, (
    'The African fintech market has entered its second wave. BCG\'s March 2026 report "Beyond Payments: Unlocking '
    'Africa\'s Second FinTech Wave" confirms that Africa is the fastest-growing fintech market globally, with revenues '
    'projected to expand 13x to approximately $65 billion by 2030. The Middle East and Africa fintech market is '
    'anticipated to reach $103.65 billion by 2033 from $18.07 billion in 2024, at a CAGR of 21.42% (Market Data Forecast, 2025).'
))
add_para(doc, (
    'Key structural indicators underpin this growth: nearly 300 million African adults remain unbanked, mobile '
    'internet users are approaching 475 million, and the continent already accounts for 74% of global mobile money '
    'transaction volume. While the first wave built domestic payment rails, the second wave is defined by B2B payments, '
    'government digitisation, interoperable credit rails, and AI-driven underwriting as the engines of the next growth phase.'
))

doc.add_heading('2.2 Funding Landscape (2025–2026)', level=2)

t = doc.add_table(rows=8, cols=4)
t.style = 'Light Grid Accent 1'
t.alignment = WD_TABLE_ALIGNMENT.CENTER
headers = ['Metric', '2024', '2025', 'Q1 2026']
for i, h in enumerate(headers):
    add_shaded_cell(t.rows[0].cells[i], h, bold=True)

data = [
    ['Total African Tech Funding', '$1.1B', '$4.1B', '$705M'],
    ['Fintech Equity Funding', '~$600M', '$769M', '$187M'],
    ['Fintech % of Total Equity', '~55%', '25%', '~34%'],
    ['Debt Financing (All Sectors)', '~$1.0B', '$1.64B', 'Growing YoY'],
    ['Deal Count (Fintech)', '~55', '54', '21'],
    ['Average Deal Size (Nigeria)', '~$8M', '$18.6M', 'Increasing'],
    ['No. of Fintech Unicorns', '7', '9', '9+'],
]
for ri, row_data in enumerate(data, 1):
    for ci, val in enumerate(row_data):
        add_cell(t.rows[ri].cells[ci], val, bold=(ci == 0))

set_col_widths(t, [6, 4, 4, 4])
add_para(doc, 'Sources: Partech Africa 2025 Report, Empower Africa, TechCabal, Disrupt Africa 2025', size=Pt(8), italic=True)

doc.add_heading('2.3 The Big Four Markets', level=2)
add_para(doc, (
    'African fintech investment is concentrated in four dominant hubs. Understanding the distinct profiles of each '
    'market is essential because the regulatory environment, investor community, infrastructure constraints, and '
    'competitive dynamics differ substantially across all four.'
))

t2 = doc.add_table(rows=5, cols=5)
t2.style = 'Light Grid Accent 1'
t2.alignment = WD_TABLE_ALIGNMENT.CENTER
h2 = ['Market', '2025 Funding', 'Key Advantage', 'Fintech Focus']
for i, h in enumerate(h2):
    add_shaded_cell(t2.rows[0].cells[i], h, bold=True)

mdata = [
    ['Nigeria', '$464.8M (28.4%)', 'Largest market, CBN open banking framework', 'Payments, lending, wealthtech, AI fintech'],
    ['Egypt', '$378.95M', '105M population, supportive regulator', 'Digital lending, payments, B2B fintech'],
    ['South Africa', '$335.9M', 'Most developed banking infra, POPIA', 'Digital banking, wealth management, insurtech'],
    ['Kenya', '$273.2M', 'M-Pesa infrastructure, mobile money primacy', 'Mobile money, lending, cross-border payments'],
]
for ri, row_data in enumerate(mdata, 1):
    for ci, val in enumerate(row_data):
        add_cell(t2.rows[ri].cells[ci], val, bold=(ci == 0), size=Pt(8.5))

set_col_widths(t2, [3.5, 4, 6, 5.5])

doc.add_heading('2.4 Structural Market Shifts Defining 2026', level=2)
add_bullet(doc, ' The "growth at all costs" era is over. Investors demand unit economics, clear paths to profitability, and regulatory compliance as prerequisites for capital.', bold_prefix='Profitability over growth: ')
add_bullet(doc, ' The number of fintech startups that raised seed in 2021 and successfully raised Series A within two years dropped to 5.1%. The bar for Series A is structurally higher.', bold_prefix='Harder conversion environment: ')
add_bullet(doc, ' Fintech debt financing surged 63% YoY in 2025 to a record $1.64 billion. Debt now accounts for 41% of all capital deployed in African tech, up from 17% in 2019.', bold_prefix='Debt financing explosion: ')
add_bullet(doc, ' Flutterwave acquired Mono, Moniepoint acquired Sumac Microfinance Bank, Stitch acquired ExiPay. M&A is now the primary mechanism for scaling across markets.', bold_prefix='Consolidation wave: ')
add_bullet(doc, ' The CBN released its Open Banking Implementation Framework. Nigeria leads Africa in open banking. South Africa, Kenya, and Ghana are developing regulatory frameworks.', bold_prefix='Open banking acceleration: ')
add_bullet(doc, ' PAPSS is live in 19 countries with 160+ banks, enabling cross-border payments in local currencies. PAPSSCARD launched as Africa\'s first continental card scheme in June 2025.', bold_prefix='Pan-African payment rails: ')
add_bullet(doc, ' The CBN restricted POS agents to one financial institution and capped market share at 25% for card issuing. Regulatory sandboxes exist in 15 African countries.', bold_prefix='Regulatory maturation: ')

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════
# 3. COMPREHENSIVE MULTI-MARKET COMPETITIVE MATRIX
# ═══════════════════════════════════════════════════════════════════
doc.add_heading('3. EcoFinwize Comprehensive Multi-Market Competitive Matrix (Updated 2026)', level=1)
add_para(doc, (
    'The following matrix provides a rigorous, cross-sector analysis of every major competitive category in the '
    'African fintech ecosystem. For each sector, we identify market strengths, structural limitations, and the '
    'specific gap that EcoFinwize is uniquely positioned to address.'
))

doc.add_heading('3.1 Competitive Landscape Summary Table', level=2)

# Big competitive matrix table
sectors = [
    ['Sector', 'Dominant Players', 'Market Strengths', 'Key Limitation', 'EcoFinwize Opportunity'],
    ['Wealth Management',
     'PiggyVest (7M+ users)\nCowrywise (2M+ users)\nRisevest (600K+ users)\nBamboo (500K+ users)\nTrove (500K+ users)',
     'Strong regulatory partnerships\nSEC-licensed fund managers\nMature investment infrastructure\nHigh customer trust',
     'Assume predictable salaries/formal employment\nAdvisory is educational, not conversational\nNo irregular income adaptation',
     'Serve pre-investment advisory\nAdaptive budgeting for irregular income\nConversational financial guidance\nPartner rather than compete'],
    ['Digital Banks & Super Apps',
     'OPay (50M+ users, $4B IPO planned)\nPalmPay (35M+ users)\nMoniepoint (20M+ users, ₦412T processed)\nKuda (7M+ users)\nCarbon (5M+ users)',
     'Massive distribution\nReal-time payments\nAgent banking networks\nDebit cards, lending',
     'AI = operational (transfers/support)\nNo long-term financial planning\nNo SME mentorship\nNo investment education',
     'Platform-agnostic advisory layer\nComplement digital banking\nMulti-bank intelligence\nOpen banking integration'],
    ['SME Business Tools',
     'Bumpa, Oze, Dukka\nZoho Books, QuickBooks\nPaidHR',
     'Inventory tracking\nBookkeeping\nInvoicing & payroll\nAccounting & reporting',
     'Manual data entry burden\nHigh abandonment rates\nSteep learning curve\nNo AI-assisted workflows',
     'Conversational bookkeeping\nVoice-to-record transactions\nAI-powered business planning\nLower barrier for informal SMEs'],
    ['Banking AI / Chatbots',
     'UBA Leo\nAccess Bank AI\nOPay AI Support',
     'Rule-based operational efficiency\nIntegrated with banking systems\nCustomer support automation',
     'No deep financial advisory\nNo contextual reasoning\nNo financial coaching\nNo regulatory intelligence',
     'RAG-grounded advisory\nExplainable AI with citations\nMulti-persona expertise\nFinancial education integration'],
    ['General AI Assistants',
     'ChatGPT, Claude, Gemini\nMicrosoft Copilot\nPerplexity',
     'Broad general knowledge\nAdvanced reasoning\nMassive user bases\nRapid improvement cycles',
     'Not Africa-specific\nNo local tax/regulatory knowledge\nNo African financial products\nNo SME compliance guidance',
     'Domain-specific localization\nAfrican regulatory intelligence\n13 African languages\nActionable financial tools'],
    ['Financial Education',
     'Money Africa\nClever Girl Finance\nNairametrics Learning',
     'Structured learning content\nGrowing user engagement\nBrand authority',
     'Passive learning only\nNo connection to action\nNo practical tools integration\nNo personalized guidance',
     'Learning + execution integration\nAI-tutored financial education\nReal-world tool application\nProgress-linked achievements'],
    ['Global AI Financial Copilots',
     'Cleo ($400M ARR, 7M+ users)\nMonarch Money ($14.99/mo)\nRocket Money\nCopilot Money ($13/mo)\nOrigin',
     'Advanced AI/ML features\nAgentic architecture (Cleo 3.0)\nReal-time voice conversations\nTransaction categorization >95%',
     'US/Europe optimized\nAssume Plaid/open banking coverage\nNo emerging economy features\nNo irregular income handling',
     'Emerging-market specialization\nOffline/low-bandwidth design\n13-language i18n\nSME-specific tools\nAffordable AI delivery'],
]

t3 = doc.add_table(rows=len(sectors), cols=5)
t3.style = 'Light Grid Accent 1'
t3.alignment = WD_TABLE_ALIGNMENT.CENTER
for ri, row_data in enumerate(sectors):
    for ci, val in enumerate(row_data):
        if ri == 0:
            add_shaded_cell(t3.rows[ri].cells[ci], val, bold=True, size=Pt(8))
        else:
            add_cell(t3.rows[ri].cells[ci], val, bold=(ci == 0), size=Pt(7.5))

set_col_widths(t3, [3, 4.5, 4.5, 4.5, 4])

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════
# 4. DEEP-DIVE SECTOR ANALYSIS
# ═══════════════════════════════════════════════════════════════════
doc.add_heading('4. Deep-Dive Sector Analysis', level=1)

# ── 4.1 Wealth Management ──
doc.add_heading('4.1 Wealth Management Platforms', level=2)
doc.add_heading('Market Leaders', level=3)
add_para(doc, (
    'The Nigerian wealthtech sector has become one of African fintech\'s most successful verticals. '
    'PiggyVest has surpassed 7 million users and paid out ₦1.3 trillion in 2025 (up 56% from ₦835 billion in 2024). '
    'Cowrywise crossed 2 million users and launched stock trading in March 2025 following ISA reforms, gaining 12,000 '
    'new accounts in one week. Risevest operates across five African countries with over 600,000 users and $42 million '
    'in payouts. Bamboo and Trove each serve 500,000+ users with access to US and Nigerian equities.'
))
doc.add_heading('Structural Gap', level=3)
add_para(doc, (
    'These platforms excel at wealth accumulation for users with disposable income, but they assume predictable '
    'monthly salaries, fixed saving schedules, and formal employment. The approximately 60 million financially '
    'excluded or underserved Nigerian adults (EFInA 2025) — freelancers, gig workers, informal sector participants, '
    'and micro-entrepreneurs — require a fundamentally different financial approach. None of these platforms offers '
    'conversational AI advisory, adaptive budgeting for irregular income, or integrated financial education that '
    'bridges financial literacy with practical execution.'
))
doc.add_heading('EcoFinwize Strategic Position', level=3)
add_para(doc, (
    'EcoFinwize addresses the earlier stages of financial decision-making: understanding cash flow, building sustainable '
    'budgets, preparing for investments, improving financial literacy, and growing business income before investing. '
    'The adaptive budgeting algorithm dynamically adjusts savings recommendations based on fluctuating income patterns. '
    'Rather than competing for investment assets, EcoFinwize becomes the trusted advisor that prepares users for '
    'investment — creating partnership opportunities with platforms like PiggyVest, Cowrywise, and Risevest.'
))

# ── 4.2 Digital Banks ──
doc.add_heading('4.2 Digital Banks & Super Apps', level=2)
doc.add_heading('Market Leaders', level=3)
add_para(doc, (
    'Nigeria\'s "Fintech Six" — Moniepoint, OPay, PalmPay, Kuda, Carbon, and FairMoney — now serve a combined '
    'estimated 160+ million registered users (with significant overlap). OPay is preparing a $4 billion US IPO (H2 2026), '
    'with 50 million+ users and ~$12 billion monthly transaction volume. Moniepoint processed ₦412 trillion in 2025, '
    'claiming ~80% of Nigeria\'s in-person payments. Kuda reached 7 million users with ₦14.3 trillion in Q1 2025 '
    'transactions. PalmPay hit 35 million users with 15 million daily transactions.'
))
doc.add_heading('Structural Gap', level=3)
add_para(doc, (
    'Current AI capabilities across all six platforms remain overwhelmingly operational. Most digital assistants '
    'help customers transfer money, check balances, pay bills, or resolve support issues. None provides long-term '
    'financial planning, investment education, tax guidance, SME mentorship, or multi-persona advisory. The CBN\'s '
    'anti-dominance regulations (June 2026) — capping card issuing at 25% and merchant acquiring at 15% market share — '
    'create additional pressure on dominant players to differentiate through value-added services rather than scale alone.'
))
doc.add_heading('EcoFinwize Strategic Position', level=3)
add_para(doc, (
    'EcoFinwize complements digital banking by acting as an AI financial intelligence layer. Instead of replacing '
    'banks, it helps users make better financial decisions before and after transactions. As open banking expands '
    'across Africa — Nigeria released its Open Banking Implementation Framework in 2025, and South Africa, Kenya, '
    'and Ghana are developing frameworks — EcoFinwize\'s platform-agnostic design enables integration with multiple '
    'financial institutions, delivering personalized intelligence across banks while remaining neutral.'
))

# ── 4.3 SME Business Tools ──
doc.add_heading('4.3 SME Business Management Platforms', level=2)
doc.add_heading('Market Leaders', level=3)
add_para(doc, (
    'African SME tools — Bumpa, Oze, Dukka, alongside global players Zoho Books and QuickBooks — offer inventory '
    'tracking, bookkeeping, invoicing, and payroll. However, most small businesses struggle with manual data entry, '
    'and many abandon bookkeeping software because it competes with daily operational priorities.'
))
doc.add_heading('Structural Gap', level=3)
add_para(doc, (
    'Africa\'s informal sector accounts for approximately 80% of employment and a significant portion of GDP. '
    'Form-based bookkeeping tools assume a level of digital literacy and operational consistency that many micro-entrepreneurs '
    'do not possess. There is no major platform offering conversational or voice-based business management tailored '
    'to Africa\'s informal and semi-formal SME sector.'
))
doc.add_heading('EcoFinwize Strategic Position', level=3)
add_para(doc, (
    'EcoFinwize transforms structured bookkeeping into conversational workflows. Users interact naturally through '
    'voice or chat in any of 13 African languages, while AI converts conversations into structured financial records. '
    'This dramatically reduces friction and lowers the learning curve for first-time entrepreneurs. The AI business '
    'plan generator, SME task manager, and invoice system are already implemented and verified in the codebase.'
))

# ── 4.4 Banking AI ──
doc.add_heading('4.4 Banking AI / Chatbots', level=2)
doc.add_heading('Market Leaders', level=3)
add_para(doc, 'UBA Leo, Access Bank AI assistants, OPay AI Support, and Carbon\'s AI chatbot.')
doc.add_heading('Structural Gap', level=3)
add_para(doc, (
    'Most banking AI systems are rules-based, designed for operational efficiency rather than deep financial advisory. '
    'They lack contextual reasoning, long-term personalized planning, financial coaching, and localized regulatory '
    'intelligence. Trust in banking chatbots remains low — the Nigerian Fintech Trust Index (Q2 2026) found that '
    'even leading platforms like OPay (2.5/5 Trustpilot), Kuda (2.0/5), and Moniepoint (2.8/5) score poorly on '
    'consumer trust, despite having 4.5-star app store ratings.'
))
doc.add_heading('EcoFinwize Strategic Position', level=3)
add_para(doc, (
    'EcoFinwize employs Retrieval-Augmented Generation (RAG) combined with a curated financial knowledge base to '
    'deliver explainable, evidence-based guidance. Users receive not only answers but also context, education, and '
    'verifiable source references — addressing the trust deficit that plagues existing banking AI systems. This '
    'grounding in verified financial and regulatory information positions EcoFinwize as a reliable advisory platform '
    'rather than a transactional chatbot.'
))

# ── 4.5 General AI Assistants ──
doc.add_heading('4.5 General AI Assistants', level=2)
doc.add_heading('Market Leaders', level=3)
add_para(doc, 'ChatGPT, Claude, Gemini, Microsoft Copilot, Perplexity.')
doc.add_heading('Structural Gap', level=3)
add_para(doc, (
    'General AI assistants are not designed for African financial ecosystems. They lack localized tax regulations, '
    'SME compliance frameworks, country-specific financial products, and regional investment guidance. Their training '
    'data underrepresents African financial contexts, and they have no mechanism for executing financial actions '
    '(creating budgets, recording transactions, generating invoices). The cost of API access also remains prohibitive '
    'for mass-market African deployment without aggressive optimization.'
))
doc.add_heading('EcoFinwize Strategic Position', level=3)
add_para(doc, (
    'EcoFinwize combines foundation models with localized retrieval systems and action dispatch tools. Rather than '
    'competing on model size, EcoFinwize competes on domain expertise, localization, and execution. The platform '
    'delivers Africa-specific financial intelligence at under $0.05 per conversation — a cost structure enabled by '
    'Redis caching, token budget management, and efficient model routing (GPT-4o-mini via OpenRouter).'
))

# ── 4.6 Financial Education ──
doc.add_heading('4.6 Financial Education Platforms', level=2)
doc.add_heading('Market Leaders', level=3)
add_para(doc, 'Money Africa, Clever Girl Finance, Nairametrics Learning.')
doc.add_heading('Structural Gap', level=3)
add_para(doc, (
    'Financial education in Africa remains predominantly passive. Users consume content — articles, videos, courses — '
    'but must independently translate lessons into practical financial actions. There is no integrated feedback loop '
    'between learning and doing. This disconnect results in low engagement and limited behaviour change.'
))
doc.add_heading('EcoFinwize Strategic Position', level=3)
add_para(doc, (
    'EcoFinwize integrates learning with execution. Educational content immediately connects to budgeting, planning, '
    'document generation, and business management tools. The platform\'s quiz engine, progress tracking, and badge '
    'system gamify financial education, while AI tutors (Kemi, Chidi, Musa) provide contextual guidance that bridges '
    'theory and practice. This action-oriented approach drives stronger user retention and measurable financial '
    'behaviour change.'
))

# ── 4.7 Global AI Financial Copilots ──
doc.add_heading('4.7 Global AI Financial Copilots', level=2)
doc.add_heading('Market Leaders', level=3)
add_para(doc, (
    'Cleo ($400M ARR, 7M+ users), Monarch Money ($14.99/mo, 2,000% post-Mint growth), Rocket Money, '
    'Copilot Money ($13/mo, 95%+ AI categorization), Origin ($13/mo with human CFPs).'
))
doc.add_heading('Structural Gap', level=3)
add_para(doc, (
    'These platforms represent the global state of the art in AI-powered personal finance. Cleo 3.0 introduced '
    'agentic architecture with multi-step reasoning, real-time voice, and conversational memory. Monarch AI added '
    'scenario modelling for household financial planning. Copilot achieves 93% first-pass categorization accuracy. '
    'However, every single platform is optimized for North American and European financial systems. They assume '
    'mature credit markets, widespread open banking adoption (Plaid/MX/Finicity), formal employment, consistent '
    'internet access, and English-only interfaces. None supports African languages. None handles irregular income '
    'patterns common in African markets. None integrates with African payment rails (PAPSS, mobile money, USSD). '
    'None offers SME-specific tools. None costs less than $5–15/month — a significant barrier in price-sensitive markets.'
))
doc.add_heading('EcoFinwize Strategic Position', level=3)
add_para(doc, (
    'EcoFinwize is designed from the ground up for emerging economies. The platform\'s architecture reflects the '
    'realities of African financial life: irregular income management, localized regulations, SME advisory, '
    'low-bandwidth optimization (7.1 MB APK), affordable AI delivery (under $0.05/chat), multilingual expansion '
    '(13 African languages with 384 UI strings each), mobile-first design, and voice-first interaction for users '
    'with limited literacy. By solving local problems exceptionally well, EcoFinwize creates a defensible niche '
    'that global platforms cannot easily replicate without massive localization investments.'
))

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════
# 5. EMERGING COMPETITIVE THREATS
# ═══════════════════════════════════════════════════════════════════
doc.add_heading('5. Emerging Competitive Threats in the African Market', level=1)
add_para(doc, (
    'The 2026 African fintech landscape is being reshaped by several powerful forces that create both threats '
    'and opportunities for EcoFinwize. Understanding these dynamics is essential for strategic positioning.'
))

doc.add_heading('5.1 Agentic AI in Personal Finance', level=2)
add_para(doc, (
    'The most significant competitive development of 2026 is the emergence of "agentic AI" — software that plans, '
    'reasons, and acts autonomously across multiple steps. Cleo\'s Autopilot (launched June 2026) represents the '
    'state of the art: it builds financial health scores, generates multi-month roadmaps, creates daily plans, '
    'and executes actions (savings transfers, spending limits) with user consent. Cleo\'s $400M ARR validates '
    'mass-market demand for autonomous financial AI. However, Cleo remains entirely US/UK-focused with no African '
    'market presence, African language support, or integration with African financial rails.'
))
add_para(doc, (
    'EcoFinwize\'s action dispatch system (10 tools that create budgets, transactions, invoices, tasks, and '
    'business plans) already implements a foundational version of this pattern. Expanding agentic capabilities — '
    'particularly autonomous financial planning, proactive insights, and goal-based action execution — is the '
    'most important product development priority for 2026–2027.'
))

doc.add_heading('5.2 Open Banking & Embedded Finance Expansion', level=2)
add_para(doc, (
    'The Pan-African Payment and Settlement System (PAPSS) is live in 19 countries with 160+ commercial banks, '
    'enabling real-time cross-border payments in local currencies. The embedded finance market was valued at $11.9 '
    'billion in 2024 and is projected to reach $18 billion by 2030. Paystack launched Paystack Index (June 2026) — '
    'an experimental product allowing AI agents (ChatGPT, Claude) to make payments on behalf of users, representing '
    'the first major African payment infrastructure for agentic commerce. Anchor launched an MCP server enabling '
    'AI agents to interact with its API resources. These developments signal that Africa\'s payment infrastructure '
    'is actively preparing for AI-mediated financial transactions.'
))
add_para(doc, (
    'EcoFinwize\'s platform-agnostic intelligence layer is well-positioned to integrate with multiple financial '
    'institutions as open banking matures. The built-in Paystack and Flutterwave integrations provide immediate '
    'downstream channels for embedded finance and affiliate distribution.'
))

doc.add_heading('5.3 AI-Driven Lending & Credit Scoring', level=2)
add_para(doc, (
    'AI-driven lending using alternative data (mobile usage, payment behaviour, e-commerce transactions) is '
    'rapidly expanding access to credit for the unbanked across Africa. In Ethiopia, 380,000+ MSMEs accessed '
    '$150 million through uncollateralized AI-scored credit. Carbon and FairMoney use AI to underwrite loans '
    'without traditional credit histories. While EcoFinwize does not currently offer lending, its financial data — '
    'budgets, transactions, savings patterns, learning progress — could serve as creditworthiness signals for '
    'lending partners. This represents a potential revenue stream via data partnerships (with user consent) and '
    'a natural product expansion path.'
))

doc.add_heading('5.4 Emerging African AI Fintech Natives', level=2)
add_para(doc, (
    'New entrants are beginning to target the AI personal finance gap in Africa. Budge AI (launched July 2026) '
    'reads transactional SMS and email alerts to categorize spending, using conversational AI for queries. '
    'While Budge AI\'s approach is innovative — no bank login required, works with 1,500+ financial institution '
    'notification templates — it has several critical limitations: cash transactions are invisible, crypto is '
    'unsupported, deduplication errors can double-count, and the "Ask Budge" feature lacks financial advisory '
    'depth, multi-persona support, business tools, and the comprehensive financial management capabilities '
    'EcoFinwize already provides.'
))
add_para(doc, (
    'The emergence of Budge AI validates the thesis that African consumers want AI-powered financial intelligence. '
    'It also underscores the importance of first-mover advantage and the defensibility of EcoFinwize\'s more '
    'comprehensive feature set — 142 API routes, 33 database models, 3 AI personas, 10 action tools, 20 learning '
    'courses, and SME business management — which would require years of development for any new entrant to replicate.'
))

doc.add_heading('5.5 Regulatory Sandboxes & Licensing Evolution', level=2)
add_para(doc, (
    'By October 2024, 25 national regulatory sandboxes were established across 15 African countries. Nigeria and '
    'South Africa exited the FATF grey list in 2025. The CBN\'s June 2026 anti-dominance regulations will reshape '
    'the competitive landscape for Nigeria\'s largest fintechs. EcoFinwize should consider applying for sandbox '
    'participation in Nigeria and Kenya to accelerate regulatory approval for AI-driven financial advisory. The '
    'platform\'s existing safety architecture — PII redaction, input/output guardrails, citation enforcement, '
    'financial red-flag scanning — provides a strong foundation for regulatory engagement.'
))

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════
# 6. HOW ECOFINWIZE WINS
# ═══════════════════════════════════════════════════════════════════
doc.add_heading('6. How EcoFinwize Wins: Competitive Advantage Framework', level=1)
add_para(doc, (
    'EcoFinwize\'s competitive strategy is not built on displacing incumbents but on occupying a structural '
    'gap that no existing platform addresses: the intersection of conversational AI, localized financial '
    'intelligence, adaptive personal finance, and SME business tools for African markets.'
))

doc.add_heading('6.1 The Convergence Advantage', level=2)
add_para(doc, (
    'No competing platform — in Africa or globally — combines all of the following: conversational AI with '
    '3 specialized personas (Kemi, Chidi, Musa), RAG-grounded regulatory intelligence, adaptive budgeting for '
    'irregular income, 13-language i18n, voice TTS/STT, SME business tools (invoices, tasks, business plans), '
    'gamified education with 20 courses, and a 7.1 MB mobile APK — all in a single unified platform. '
    'This convergence creates a structural competitive advantage that individual category leaders cannot replicate '
    'without years of development across multiple domains.'
))

doc.add_heading('6.2 Partnership Over Disruption', level=2)
add_para(doc, (
    'EcoFinwize\'s ecosystem symbiosis strategy positions the platform as an intermediary intelligence layer '
    'rather than a competitor to established financial institutions. Key partnership pathways include:'
))
add_bullet(doc, ' Wealth management platforms (PiggyVest, Cowrywise) — refer pre-investment users for advisory and receive referral traffic for investment-ready users')
add_bullet(doc, ' Digital banks (OPay, Kuda, Moniepoint) — integrate as an AI advisory layer accessible within banking apps via API')
add_bullet(doc, ' Payment processors (Paystack, Flutterwave) — embed financial intelligence at the point of transaction')
add_bullet(doc, ' Telecom operators (MTN, Airtel, Safaricom) — deliver financial education and AI advisory via mobile money platforms')
add_bullet(doc, ' Enterprise employers — offer financial wellness benefits for employees (workplace financial health)')

doc.add_heading('6.3 Cost Structure Advantage', level=2)
add_para(doc, (
    'EcoFinwize\'s engineering decisions create a structural cost advantage that is difficult to replicate: '
))
add_bullet(doc, ' Redis caching for repetitive queries (regulatory information, financial definitions)')
add_bullet(doc, ' GPT-4o-mini via OpenRouter for efficient inference (under $0.05/conversation)')
add_bullet(doc, ' Fallback provider chain (Groq → OpenRouter) eliminates single-provider dependency')
add_bullet(doc, ' 7.1 MB APK enables distribution in low-bandwidth environments')
add_bullet(doc, ' Modular monolith architecture minimizes infrastructure overhead')

doc.add_heading('6.4 Data Moat & Localization Advantage', level=2)
add_para(doc, (
    'As EcoFinwize grows, it accumulates a proprietary dataset of African financial behaviour, spending patterns, '
    'savings preferences, SME cash flow dynamics, and financial literacy gaps across 13 languages. This dataset: '
))
add_bullet(doc, ' Improves RAG knowledge base accuracy over time')
add_bullet(doc, ' Enables personalized recommendations based on actual African user behaviour')
add_bullet(doc, ' Creates a regulatory compliance asset (demonstrable understanding of local financial contexts)')
add_bullet(doc, ' Generates anonymized market intelligence valuable to development finance institutions and policymakers')
add_bullet(doc, ' Provides a defensible moat that pure-play AI platforms (ChatGPT, Claude) cannot replicate without years of Africa-specific deployment')

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════
# 7. SUSTAINABLE COMPETITIVE ADVANTAGES
# ═══════════════════════════════════════════════════════════════════
doc.add_heading('7. EcoFinwize Sustainable Competitive Advantages (Moats)', level=1)

doc.add_heading('7.1 Localized Intelligence (The RAG Moat)', level=2)
add_para(doc, (
    'A continuously updated Retrieval-Augmented Generation knowledge base connected to a Pinecone vector database '
    'forces all conversational responses to be explicitly grounded in verified African financial regulations, '
    'localized tax policies, and region-specific SME guidance. This infrastructure delivers explainable outputs '
    'with verifiable citations — differentiating EcoFinwize from general-purpose AI that may hallucinate '
    'Africa-specific financial information.'
))

doc.add_heading('7.2 AI-Native Multi-Persona Experience', level=2)
add_para(doc, (
    'Three distinct AI personas — Kemi (Financial Advisor), Chidi (Business Mentor), Musa (Investment Advisor) — '
    'with unique system prompts, conversation histories, and tool access. This multi-persona architecture addresses '
    'the reality that personal finance, business management, and investment require different expertise, tone, '
    'and context. No African fintech platform offers this capability.'
))

doc.add_heading('7.3 Adaptive Budgeting for Informal Economies', level=2)
add_para(doc, (
    'Traditional finance applications rely on rigid, fixed monthly spending caps that fail freelancers, '
    'gig workers, and informal earners — who represent the majority of African workers. EcoFinwize\'s '
    'percentage-based adaptive budgeting algorithm automatically scales limits relative to shifting income '
    'inputs with month-over-month rollover. This is a structural advantage for African markets where irregular '
    'income is the norm, not the exception.'
))

doc.add_heading('7.4 Full-Stack Financial Platform', level=2)
add_para(doc, (
    'Personal finance tracking, interactive SME task and invoice management, gamified financial education '
    '(20 courses with quizzes and badges), an AI business plan generator, and multi-persona AI advisory — '
    'all unified under a single cross-surface client interface (23 React web pages + 19 Flutter mobile screens). '
    'This convergence eliminates the need for users to juggle multiple apps for different financial needs.'
))

doc.add_heading('7.5 Low-Bandwidth, Cost-Efficient Engineering', level=2)
add_para(doc, (
    'Engineered for African infrastructure realities: 7.1 MB Flutter APK for limited storage environments, '
    'aggressive Redis caching to reduce API costs, Token Budget Management keeping per-conversation costs '
    'under $0.05, and offline-resilient architecture. These design decisions make EcoFinwize viable in markets '
    'where data costs are high and connectivity is intermittent.'
))

doc.add_heading('7.6 Ecosystem Symbiosis Strategy', level=2)
add_para(doc, (
    'Rather than competing with established banks, payment providers, or wealthtech platforms, EcoFinwize '
    'is architected as a platform-agnostic intelligence layer. Built-in Paystack and Flutterwave integration, '
    'open banking readiness, and API-first design create natural partnership channels. As Africa\'s open banking '
    'framework matures, EcoFinwize\'s ability to aggregate financial data across multiple institutions will '
    'become increasingly valuable.'
))

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════
# 8. STRATEGIC POSITIONING
# ═══════════════════════════════════════════════════════════════════
doc.add_heading('8. Strategic Positioning for the African Market', level=1)

doc.add_heading('8.1 Positioning Statement', level=2)
add_para(doc, (
    'EcoFinwize is Africa\'s AI-powered Financial Intelligence Platform — a conversation-first, multi-persona '
    'financial ecosystem that integrates conversational AI, localized regulatory intelligence, financial education, '
    'SME advisory, and business productivity into a unified cross-surface platform. Rather than competing solely '
    'as a budgeting application, digital bank, bookkeeping platform, or AI chatbot, EcoFinwize operates as an '
    'intelligent financial companion that meets African users where they are — in their language, on their device, '
    'at their financial stage.'
), bold=True)

doc.add_heading('8.2 How EcoFinwize Positions Better', level=2)

add_para(doc, 'EcoFinwize positions better than incumbents across six key dimensions:', bold=True)

t4 = doc.add_table(rows=7, cols=3)
t4.style = 'Light Grid Accent 1'
t4.alignment = WD_TABLE_ALIGNMENT.CENTER
h4 = ['Dimension', 'Incumbent Approach', 'EcoFinwize Advantage']
for i, h in enumerate(h4):
    add_shaded_cell(t4.rows[0].cells[i], h, bold=True, size=Pt(9))

pos_data = [
    ['User Interface', 'Form-based, dashboard-heavy, requires financial literacy', 'Conversation-first, voice-enabled, works in 13 African languages'],
    ['Income Model', 'Assumes fixed monthly salary', 'Adaptive to irregular, freelance, and informal income'],
    ['Geographic Scope', 'Global (US/Europe optimized) or single-country', 'Pan-African by design — 13 languages, multi-jurisdiction regulatory knowledge'],
    ['AI Capability', 'Single-purpose chatbots (support) or general-purpose AI (no financial domain)', 'Multi-persona AI, RAG-grounded, 10 action tools, citation-enforced'],
    ['Business Tools', 'Separate apps for accounting, invoicing, planning', 'Unified platform — AI generates plans, invoices, tasks from conversation'],
    ['Cost to User', 'Free tier limited or $5–15/month (out of reach for most Africans)', 'Free tier with ads, Pro at $3–5/mo, Business at $10–15/mo — under $0.05/chat'],
]
for ri, row_data in enumerate(pos_data, 1):
    for ci, val in enumerate(row_data):
        add_cell(t4.rows[ri].cells[ci], val, bold=(ci == 0), size=Pt(8.5))

set_col_widths(t4, [3.5, 6, 8])

doc.add_heading('8.3 Target Market Segments', level=2)
add_bullet(doc, ' Students and young professionals building foundational financial literacy (ages 18–30)', bold_prefix='Segment 1: ')
add_bullet(doc, ' Freelancers, gig workers, and informal sector earners needing irregular income management', bold_prefix='Segment 2: ')
add_bullet(doc, ' Micro and small business owners (1–10 employees) needing affordable business management', bold_prefix='Segment 3: ')
add_bullet(doc, ' Users seeking financial education in local languages (pan-African, especially Nigeria, Kenya, Ghana, South Africa)', bold_prefix='Segment 4: ')
add_bullet(doc, ' Users underserved by existing wealthtech (no predictable salary, no formal employment)', bold_prefix='Segment 5: ')

doc.add_heading('8.4 Go-to-Market Positioning Principles', level=2)
add_bullet(doc, ' Not "another fintech app" — position as an AI financial companion', bold_prefix='Complement, don\'t compete: ')
add_bullet(doc, ' 13 languages across Nigeria, Kenya, Ghana, South Africa, and pan-African diaspora', bold_prefix='African-first, not Africa-added: ')
add_bullet(doc, ' Free tier with ads for acquisition; Pro/Business tiers for revenue; AI at under $0.05/chat', bold_prefix='Affordable by design: ')
add_bullet(doc, ' RAG-grounded citations, PII redaction, input/output guardrails, financial red-flag scanning', bold_prefix='Safety as differentiator: ')
add_bullet(doc, ' Collaborate with banks, wealthtech, payment processors — EcoFinwize as the intelligence layer', bold_prefix='Ecosystem enabler: ')

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════
# 9. MARKET VALIDATION
# ═══════════════════════════════════════════════════════════════════
doc.add_heading('9. Market Validation & African Fintech Data (2026)', level=1)

doc.add_heading('9.1 Structural Market Validation', level=2)
add_para(doc, (
    'The following macroeconomic and market indicators validate the African market opportunity that EcoFinwize addresses:'
))

t5 = doc.add_table(rows=10, cols=3)
t5.style = 'Light Grid Accent 1'
t5.alignment = WD_TABLE_ALIGNMENT.CENTER
h5 = ['Indicator', 'Value', 'Source']
for i, h in enumerate(h5):
    add_shaded_cell(t5.rows[0].cells[i], h, bold=True, size=Pt(9))

val_data = [
    ['Projected African fintech revenue by 2030', '$65 billion (13x growth)', 'BCG, March 2026'],
    ['African adults still unbanked', '~300 million', 'EFInA, World Bank 2025'],
    ['Mobile internet users in Africa', '~475 million and growing', 'GSMA 2025'],
    ['African fintech funding (2025)', '$3.4 billion', 'Partech Africa, 2026'],
    ['ME&A fintech market by 2033', '$103.65 billion (21.4% CAGR)', 'Market Data Forecast, 2025'],
    ['Nigeria\'s digital investment market by 2028', '$14.34 billion', 'Statista, 2025'],
    ['African banking sector ROE (2024)', '19% (vs. 10% global average)', 'McKinsey, 2026'],
    ['AI\'s potential GDP contribution to Africa by 2035', 'Up to $1 trillion', 'African Development Bank'],
    ['Embedded finance market (Africa, by 2030)', '$18 billion', 'Industry projections'],
]
for ri, row_data in enumerate(val_data, 1):
    for ci, val in enumerate(row_data):
        add_cell(t5.rows[ri].cells[ci], val, bold=(ci == 0), size=Pt(8.5))

set_col_widths(t5, [6, 5, 5])

doc.add_heading('9.2 Competitive Gap Validation', level=2)
add_para(doc, (
    'The 2026 competitive landscape confirms a structural gap in the African fintech market: there is no existing '
    'platform that combines conversational AI with multi-persona financial advisory, localized regulatory intelligence, '
    'adaptive budgeting, SME business tools, and multilingual support for African markets. The closest global analogues '
    '(Cleo, Monarch Money, Copilot Money) are exclusively US/Europe-focused. The closest African platforms '
    '(PiggyVest, Cowrywise, Kuda, OPay) lack AI-native financial advisory. The gap is real, large, and growing '
    'as African consumers become more sophisticated in their financial needs and more comfortable with AI-powered interfaces.'
))

doc.add_heading('9.3 Total Addressable Market', level=2)
add_para(doc, (
    'EcoFinwize\'s total addressable market encompasses the ~300 million unbanked or underbanked African adults, '
    'plus millions more with bank accounts who lack access to personalized financial intelligence. Within this, '
    'the near-term addressable market focuses on Nigeria (the largest fintech market in Africa with the most '
    'sophisticated digital financial ecosystem), with expansion to Kenya, Ghana, and South Africa. Even capturing '
    '0.5% of the ~200 million smartphone users in these markets represents a potential user base of 1 million users. '
    'At current projected monetization rates (free tier → 5% paid conversion, Pro at $3–5/mo, Business at $10–15/mo), '
    'this translates to meaningful revenue potential while maintaining the free tier as the primary acquisition engine.'
))

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════
# 10. RISK FACTORS & MITIGATION
# ═══════════════════════════════════════════════════════════════════
doc.add_heading('10. Risk Factors & Mitigation for African Markets', level=1)

t6 = doc.add_table(rows=8, cols=3)
t6.style = 'Light Grid Accent 1'
t6.alignment = WD_TABLE_ALIGNMENT.CENTER
h6 = ['Risk', 'Severity', 'Mitigation Strategy']
for i, h in enumerate(h6):
    add_shaded_cell(t6.rows[0].cells[i], h, bold=True, size=Pt(9))

risk_data = [
    ['Global AI platforms enter African market', 'Medium', 'Localization moat: 13 languages, RAG knowledge base, offline engineering. General AI cannot match domain-specific African financial intelligence without 2–3 years of investment.'],
    ['Wealthtech incumbents add AI advisory', 'Medium', 'Partnership strategy positions EcoFinwize as intelligence layer. Incumbents\' AI will likely remain operational; true financial advisory requires RAG, guardrails, and multi-persona architecture that is non-trivial to build.'],
    ['Regulatory uncertainty for AI financial advice', 'High', 'Safety architecture already implemented: PII redaction, input/output guardrails, citation enforcement, financial disclaimers. Sandbox participation in Nigeria/Kenya recommended. NDPA/GDPR compliance.'],
    ['Internet connectivity and data cost barriers', 'Medium', '7.1 MB APK, offline-capable architecture, Redis caching reduces API calls, free tier removes cost barrier for initial adoption. SMS/USSD fallback for basic features.'],
    ['Consumer trust in AI financial advice', 'High', 'RAG-grounded citations for every claim. Transparent disclaimer system. Multi-layer safety architecture. Banking AI trust deficit (Trustpilot scores of 2.0–2.8/5) creates opportunity for a trustworthy alternative.'],
    ['Competition from new African AI fintech entrants (e.g., Budge AI)', 'Medium', 'First-mover advantage with full stack already built. Entrants need 2–3 years to replicate 142 API routes, 33 DB models, 3 AI personas, 10 action tools, 20 courses, 13 languages, 3 platforms (web + mobile + API).'],
    ['Currency volatility and macroeconomic instability', 'Medium', 'Multi-currency architecture, local pricing in each market, AI cost optimization ensures sustainable unit economics even with FX volatility. Revenue diversification across multiple African markets.'],
]
for ri, row_data in enumerate(risk_data, 1):
    for ci, val in enumerate(row_data):
        add_cell(t6.rows[ri].cells[ci], val, bold=(ci == 0), size=Pt(8))

set_col_widths(t6, [4, 2.5, 11.5])

# ── CLOSING ──
doc.add_paragraph()
doc.add_paragraph()
add_para(doc, (
    'This market analysis confirms that EcoFinwize occupies a structural gap in the African fintech ecosystem '
    'that no existing platform — African or global — currently addresses. The convergence of conversational AI, '
    'localized financial intelligence, adaptive personal finance, SME business tools, and multilingual support '
    'for 13 African languages creates a defensible competitive position that would require years and significant '
    'capital for any competitor to replicate.'
), bold=True)
add_para(doc, (
    'The African fintech market is entering its second wave — defined by AI-driven financial intelligence, '
    'open banking interoperability, embedded finance, and SME-focused infrastructure. EcoFinwize is uniquely '
    'positioned at the intersection of these trends. With a verified production codebase of 142 API routes, '
    '33 database models, 3 AI personas, and 23 web + 19 mobile screens; a proven cost structure delivering '
    'AI conversations at under $0.05 each; and a strategic positioning that enables partnership rather than '
    'direct competition with incumbents, EcoFinwize has a credible path to capturing a meaningful share of '
    'Africa\'s $65 billion fintech market by 2030.'
), bold=True)

# ── CREDITS ──
doc.add_paragraph()
p_cred = doc.add_paragraph()
p_cred.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p_cred.add_run('— End of Document —')
r.font.size = Pt(10)
r.italic = True
r.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
r.font.name = 'Calibri'

p_date = doc.add_paragraph()
p_date.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p_date.add_run(f'Generated July 2026 | Research sources: BCG, Partech Africa, Disrupt Africa, Empower Africa, TechCabal, IMF, McKinsey, EFInA, Market Data Forecast')
r.font.size = Pt(8)
r.italic = True
r.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
r.font.name = 'Calibri'

# ═══════════════════════════════════════════════════════════════════
# SAVE
# ═══════════════════════════════════════════════════════════════════
output_path = r'C:\Users\ibrah\Documents\Gemini\Fellow_AI_Fintech_NextGen_Leaders_Fellowship_2026\Finwize\EcoFinwize_African_Market_Analysis_2026.docx'
doc.save(output_path)
print(f'Document saved to: {output_path}')
