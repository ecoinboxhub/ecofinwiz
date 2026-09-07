import json
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import BusinessPlan, Task, Invoice, User
from app.modules.business.schemas import (
    BusinessPlanGenerate,
    TaskCreate, TaskUpdate,
    InvoiceCreate, InvoiceUpdate,
)


# =====================================================================
# BUSINESS PLANS
# =====================================================================

GENERATION_PROMPT = """You are a professional business plan writer for African entrepreneurs.
Generate a comprehensive business plan in JSON format with these sections:
- executive_summary (2-3 paragraphs)
- company_description (details about the business)
- market_analysis (industry overview, target market, competition)
- product_services (what they offer)
- marketing_strategy (how they'll reach customers)
- operational_plan (how the business will run)
- financial_projections (3-year revenue forecast, startup costs, break-even analysis)
- funding_request (how much is needed and how it will be used)

Business: {business_name}
Industry: {industry}
Description: {description}
Target Market: {target_market}
Revenue Model: {revenue_model}
Funding Needed: {funding_needed}
Team Size: {team_size}

Return ONLY valid JSON, no markdown formatting."""


async def generate_business_plan(data: BusinessPlanGenerate, user_id: UUID, db: AsyncSession) -> dict:
    from app.config import get_settings
    settings = get_settings()

    if settings.openrouter_api_key:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.openrouter_api_key,
        )
        model = settings.openrouter_model
    elif settings.groq_api_key:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=settings.groq_api_key,
        )
        model = settings.groq_model
    else:
        raise HTTPException(status_code=503, detail="No AI provider configured")

    prompt = GENERATION_PROMPT.format(
        business_name=data.business_name,
        industry=data.industry,
        description=data.description,
        target_market=data.target_market or "Not specified",
        revenue_model=data.revenue_model or "Not specified",
        funding_needed=f"${data.funding_needed:,.2f}" if data.funding_needed else "Not specified",
        team_size=data.team_size or "Not specified",
    )

    try:
        resp = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=4096,
        )
        content = resp.choices[0].message.content
        plan_data = json.loads(content)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI generation failed: {str(e)}")

    bp = BusinessPlan(
        user_id=user_id,
        title=f"{data.business_name} - Business Plan",
        content=plan_data,
        status="completed",
    )
    db.add(bp)
    await db.commit()
    await db.refresh(bp)
    return bp


async def list_business_plans(user_id: UUID, db: AsyncSession) -> list[BusinessPlan]:
    result = await db.execute(
        select(BusinessPlan).where(BusinessPlan.user_id == user_id)
        .order_by(BusinessPlan.created_at.desc())
    )
    return list(result.scalars().all())


async def get_business_plan(plan_id: UUID, user_id: UUID, db: AsyncSession) -> BusinessPlan:
    result = await db.execute(
        select(BusinessPlan).where(and_(BusinessPlan.id == plan_id, BusinessPlan.user_id == user_id))
    )
    bp = result.scalar_one_or_none()
    if not bp:
        raise HTTPException(status_code=404, detail="Business plan not found")
    return bp


async def delete_business_plan(plan_id: UUID, user_id: UUID, db: AsyncSession) -> bool:
    result = await db.execute(
        select(BusinessPlan).where(and_(BusinessPlan.id == plan_id, BusinessPlan.user_id == user_id))
    )
    bp = result.scalar_one_or_none()
    if not bp:
        raise HTTPException(status_code=404, detail="Business plan not found")
    await db.delete(bp)
    await db.commit()
    return True


# =====================================================================
# TASKS
# =====================================================================

async def create_task(data: TaskCreate, user_id: UUID, db: AsyncSession) -> Task:
    task = Task(
        user_id=user_id,
        title=data.title,
        description=data.description,
        priority=data.priority,
        due_date=data.due_date,
        assigned_to=data.assigned_to,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def list_tasks(
    user_id: UUID,
    db: AsyncSession,
    status: Optional[str] = None,
    priority: Optional[str] = None,
) -> list[Task]:
    query = select(Task).where(Task.user_id == user_id)
    if status:
        query = query.where(Task.status == status)
    if priority:
        query = query.where(Task.priority == priority)
    result = await db.execute(query.order_by(Task.created_at.desc()))
    return list(result.scalars().all())


async def get_task(task_id: UUID, user_id: UUID, db: AsyncSession) -> Task:
    result = await db.execute(
        select(Task).where(and_(Task.id == task_id, Task.user_id == user_id))
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


async def update_task(task_id: UUID, data: TaskUpdate, user_id: UUID, db: AsyncSession) -> Task:
    task = await get_task(task_id, user_id, db)
    updates = data.model_dump(exclude_unset=True)
    for key, val in updates.items():
        if val is not None:
            setattr(task, key, val)
    await db.commit()
    await db.refresh(task)
    return task


async def delete_task(task_id: UUID, user_id: UUID, db: AsyncSession) -> bool:
    task = await get_task(task_id, user_id, db)
    await db.delete(task)
    await db.commit()
    return True


# =====================================================================
# INVOICES
# =====================================================================

async def generate_invoice_number(db: AsyncSession, user_id: UUID) -> str:
    result = await db.execute(
        select(func.count(Invoice.id)).where(Invoice.user_id == user_id)
    )
    count = result.scalar() or 0
    now = datetime.now(timezone.utc)
    return f"INV-{now.strftime('%Y%m')}-{count + 1:04d}"


async def create_invoice(data: InvoiceCreate, user_id: UUID, db: AsyncSession) -> Invoice:
    items = [item.model_dump() for item in data.items]
    subtotal = sum(item["amount"] for item in items)
    tax_amount = subtotal * (data.tax_rate / 100)
    total = subtotal + tax_amount
    number = await generate_invoice_number(db, user_id)

    invoice = Invoice(
        user_id=user_id,
        number=number,
        client_name=data.client_name,
        client_email=data.client_email,
        client_address=data.client_address,
        items=items,
        subtotal=subtotal,
        tax_rate=data.tax_rate,
        tax_amount=tax_amount,
        total=total,
        currency=data.currency,
        notes=data.notes,
        due_date=data.due_date,
    )
    db.add(invoice)
    await db.commit()
    await db.refresh(invoice)
    return invoice


async def list_invoices(
    user_id: UUID, db: AsyncSession, status: Optional[str] = None
) -> list[Invoice]:
    query = select(Invoice).where(Invoice.user_id == user_id)
    if status:
        query = query.where(Invoice.status == status)
    result = await db.execute(query.order_by(Invoice.created_at.desc()))
    return list(result.scalars().all())


async def get_invoice(invoice_id: UUID, user_id: UUID, db: AsyncSession) -> Invoice:
    result = await db.execute(
        select(Invoice).where(and_(Invoice.id == invoice_id, Invoice.user_id == user_id))
    )
    inv = result.scalar_one_or_none()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return inv


async def update_invoice(invoice_id: UUID, data: InvoiceUpdate, user_id: UUID, db: AsyncSession) -> Invoice:
    inv = await get_invoice(invoice_id, user_id, db)
    updates = data.model_dump(exclude_unset=True)
    if "items" in updates:
        items = [item if isinstance(item, dict) else item.model_dump() for item in updates["items"]]
        subtotal = sum(item["amount"] for item in items)
        tax_rate = updates.get("tax_rate", inv.tax_rate)
        tax_amount = subtotal * (tax_rate / 100)
        updates["items"] = items
        updates["subtotal"] = subtotal
        updates["tax_amount"] = tax_amount
        updates["total"] = subtotal + tax_amount
    for key, val in updates.items():
        if val is not None:
            setattr(inv, key, val)
    await db.commit()
    await db.refresh(inv)
    return inv


async def mark_invoice_paid(invoice_id: UUID, user_id: UUID, db: AsyncSession) -> Invoice:
    inv = await get_invoice(invoice_id, user_id, db)
    inv.status = "paid"
    inv.paid_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(inv)
    return inv


async def delete_invoice(invoice_id: UUID, user_id: UUID, db: AsyncSession) -> bool:
    inv = await get_invoice(invoice_id, user_id, db)
    await db.delete(inv)
    await db.commit()
    return True
