from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db
from app.modules.auth.dependencies import get_current_user
from app.models import User
from app.modules.business import service
from app.modules.business.schemas import (
    BusinessPlanGenerate, BusinessPlanResponse,
    TaskCreate, TaskUpdate, TaskResponse,
    InvoiceCreate, InvoiceUpdate, InvoiceResponse,
)

router = APIRouter()


# =====================================================================
# BUSINESS PLANS
# =====================================================================

@router.post("/business-plans/generate", status_code=201, tags=["Business Plans"])
async def generate_business_plan(
    data: BusinessPlanGenerate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    bp = await service.generate_business_plan(data, user.id, db)
    from app.services.analytics_service import get_analytics
    analytics = get_analytics()
    await analytics.track_business_plan(user.id, data.industry or "")
    return BusinessPlanResponse(
        id=bp.id, user_id=bp.user_id, title=bp.title,
        content=bp.content, status=bp.status,
        created_at=bp.created_at, updated_at=bp.updated_at,
    )


@router.get("/business-plans", tags=["Business Plans"])
async def list_business_plans(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    plans = await service.list_business_plans(user.id, db)
    return [BusinessPlanResponse(
        id=p.id, user_id=p.user_id, title=p.title,
        content=p.content, status=p.status,
        created_at=p.created_at, updated_at=p.updated_at,
    ) for p in plans]


@router.get("/business-plans/{plan_id}", tags=["Business Plans"])
async def get_business_plan(
    plan_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    bp = await service.get_business_plan(plan_id, user.id, db)
    return BusinessPlanResponse(
        id=bp.id, user_id=bp.user_id, title=bp.title,
        content=bp.content, status=bp.status,
        created_at=bp.created_at, updated_at=bp.updated_at,
    )


@router.delete("/business-plans/{plan_id}", status_code=204, tags=["Business Plans"])
async def delete_business_plan(
    plan_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await service.delete_business_plan(plan_id, user.id, db)


# =====================================================================
# TASKS
# =====================================================================

@router.post("/tasks", status_code=201, tags=["Tasks"])
async def create_task(
    data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    task = await service.create_task(data, user.id, db)
    return TaskResponse(
        id=task.id, user_id=task.user_id, title=task.title,
        description=task.description, status=task.status,
        priority=task.priority, due_date=task.due_date,
        assigned_to=task.assigned_to, created_at=task.created_at,
        updated_at=task.updated_at,
    )


@router.get("/tasks", tags=["Tasks"])
async def list_tasks(
    status: str = Query(None),
    priority: str = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    tasks = await service.list_tasks(user.id, db, status, priority)
    return [TaskResponse(
        id=t.id, user_id=t.user_id, title=t.title,
        description=t.description, status=t.status,
        priority=t.priority, due_date=t.due_date,
        assigned_to=t.assigned_to, created_at=t.created_at,
        updated_at=t.updated_at,
    ) for t in tasks]


@router.get("/tasks/{task_id}", tags=["Tasks"])
async def get_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    task = await service.get_task(task_id, user.id, db)
    return TaskResponse(
        id=task.id, user_id=task.user_id, title=task.title,
        description=task.description, status=task.status,
        priority=task.priority, due_date=task.due_date,
        assigned_to=task.assigned_to, created_at=task.created_at,
        updated_at=task.updated_at,
    )


@router.patch("/tasks/{task_id}", tags=["Tasks"])
async def update_task(
    task_id: UUID,
    data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    task = await service.update_task(task_id, data, user.id, db)
    return TaskResponse(
        id=task.id, user_id=task.user_id, title=task.title,
        description=task.description, status=task.status,
        priority=task.priority, due_date=task.due_date,
        assigned_to=task.assigned_to, created_at=task.created_at,
        updated_at=task.updated_at,
    )


@router.delete("/tasks/{task_id}", status_code=204, tags=["Tasks"])
async def delete_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await service.delete_task(task_id, user.id, db)


# =====================================================================
# INVOICES
# =====================================================================

@router.post("/invoices", status_code=201, tags=["Invoices"])
async def create_invoice(
    data: InvoiceCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    from app.modules.subscriptions.service import SubscriptionService
    svc = SubscriptionService(db)
    if not await svc.check_quota(user, "invoices_created"):
        raise HTTPException(
            status_code=403,
            detail={
                "code": "QUOTA_EXCEEDED",
                "message": "Free tier does not include invoices. Upgrade to Pro for 20 invoices/month or Business for unlimited.",
                "upgrade_plan": svc.get_upgrade_plan(user.plan),
            }
        )
    inv = await service.create_invoice(data, user.id, db)
    await svc.increment_usage(user.id, "invoices_created")
    return InvoiceResponse(
        id=inv.id, user_id=inv.user_id, number=inv.number,
        client_name=inv.client_name, client_email=inv.client_email,
        client_address=inv.client_address, items=inv.items,
        subtotal=float(inv.subtotal), tax_rate=float(inv.tax_rate),
        tax_amount=float(inv.tax_amount), total=float(inv.total),
        currency=inv.currency, status=inv.status, notes=inv.notes,
        due_date=inv.due_date, paid_at=inv.paid_at,
        created_at=inv.created_at, updated_at=inv.updated_at,
    )


@router.get("/invoices", tags=["Invoices"])
async def list_invoices(
    status: str = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    invoices = await service.list_invoices(user.id, db, status)
    return [InvoiceResponse(
        id=inv.id, user_id=inv.user_id, number=inv.number,
        client_name=inv.client_name, client_email=inv.client_email,
        client_address=inv.client_address, items=inv.items,
        subtotal=float(inv.subtotal), tax_rate=float(inv.tax_rate),
        tax_amount=float(inv.tax_amount), total=float(inv.total),
        currency=inv.currency, status=inv.status, notes=inv.notes,
        due_date=inv.due_date, paid_at=inv.paid_at,
        created_at=inv.created_at, updated_at=inv.updated_at,
    ) for inv in invoices]


@router.get("/invoices/{invoice_id}", tags=["Invoices"])
async def get_invoice(
    invoice_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    inv = await service.get_invoice(invoice_id, user.id, db)
    return InvoiceResponse(
        id=inv.id, user_id=inv.user_id, number=inv.number,
        client_name=inv.client_name, client_email=inv.client_email,
        client_address=inv.client_address, items=inv.items,
        subtotal=float(inv.subtotal), tax_rate=float(inv.tax_rate),
        tax_amount=float(inv.tax_amount), total=float(inv.total),
        currency=inv.currency, status=inv.status, notes=inv.notes,
        due_date=inv.due_date, paid_at=inv.paid_at,
        created_at=inv.created_at, updated_at=inv.updated_at,
    )


@router.patch("/invoices/{invoice_id}", tags=["Invoices"])
async def update_invoice(
    invoice_id: UUID,
    data: InvoiceUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    inv = await service.update_invoice(invoice_id, data, user.id, db)
    return InvoiceResponse(
        id=inv.id, user_id=inv.user_id, number=inv.number,
        client_name=inv.client_name, client_email=inv.client_email,
        client_address=inv.client_address, items=inv.items,
        subtotal=float(inv.subtotal), tax_rate=float(inv.tax_rate),
        tax_amount=float(inv.tax_amount), total=float(inv.total),
        currency=inv.currency, status=inv.status, notes=inv.notes,
        due_date=inv.due_date, paid_at=inv.paid_at,
        created_at=inv.created_at, updated_at=inv.updated_at,
    )


@router.post("/invoices/{invoice_id}/mark-paid", tags=["Invoices"])
async def mark_invoice_paid(
    invoice_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    inv = await service.mark_invoice_paid(invoice_id, user.id, db)
    return InvoiceResponse(
        id=inv.id, user_id=inv.user_id, number=inv.number,
        client_name=inv.client_name, client_email=inv.client_email,
        client_address=inv.client_address, items=inv.items,
        subtotal=float(inv.subtotal), tax_rate=float(inv.tax_rate),
        tax_amount=float(inv.tax_amount), total=float(inv.total),
        currency=inv.currency, status=inv.status, notes=inv.notes,
        due_date=inv.due_date, paid_at=inv.paid_at,
        created_at=inv.created_at, updated_at=inv.updated_at,
    )


@router.delete("/invoices/{invoice_id}", status_code=204, tags=["Invoices"])
async def delete_invoice(
    invoice_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await service.delete_invoice(invoice_id, user.id, db)
