"""API Router: Inventory (Estoque) endpoints."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from odontoflow.api.deps import (
    get_current_user,
    get_material_repo,
    get_supplier_repo,
)
from odontoflow.api.schemas.inventory import (
    CreateMaterialRequest,
    CreateSupplierRequest,
    MaterialResponse,
    MaterialsListResponse,
    StockMovementRequest,
    StockMovementResponse,
    SupplierResponse,
    SuppliersListResponse,
    UpdateMaterialRequest,
)
from odontoflow.inventory.application.commands.manage_material import ManageMaterialCommand
from odontoflow.inventory.application.commands.record_stock_movement import (
    RecordStockMovementCommand,
)
from odontoflow.inventory.application.queries.list_materials import ListMaterialsQuery
from odontoflow.inventory.application.queries.list_suppliers import ListSuppliersQuery
from odontoflow.inventory.domain.models import StockMovementType, Supplier
from odontoflow.shared.auth import CurrentUser
from odontoflow.shared.domain.errors import NotFoundError, ValidationError

router = APIRouter(
    prefix="/api/v1",
    tags=["inventory"],
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _material_to_response(mat) -> MaterialResponse:
    return MaterialResponse(
        id=str(mat.id),
        name=mat.name,
        description=mat.description,
        category=mat.category,
        unit=mat.unit,
        current_stock=mat.current_stock,
        min_stock=mat.min_stock,
        cost_centavos=mat.cost_centavos,
        supplier=mat.supplier,
        is_low_stock=mat.is_low_stock,
        active=mat.active,
        created_at=mat.created_at.isoformat(),
    )


def _supplier_to_response(sup) -> SupplierResponse:
    return SupplierResponse(
        id=str(sup.id),
        name=sup.name,
        phone=sup.phone,
        email=sup.email,
        notes=sup.notes,
    )


# ---------------------------------------------------------------------------
# Materials
# ---------------------------------------------------------------------------


@router.post("/materials", response_model=MaterialResponse, status_code=201)
async def create_material(
    req: CreateMaterialRequest,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_material_repo),
):
    """Cadastra material odontologico."""
    cmd = ManageMaterialCommand(
        tenant_id=current_user.tenant_id,
        name=req.name,
        description=req.description,
        category=req.category,
        unit=req.unit,
        min_stock=req.min_stock,
        cost_centavos=req.cost_centavos,
        supplier=req.supplier,
    )
    try:
        material = await cmd.execute(repo)
    except ValidationError as e:
        raise HTTPException(422, e.message)

    return _material_to_response(material)


@router.get("/materials", response_model=MaterialsListResponse)
async def list_materials(
    low_stock_only: bool = Query(False),
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_material_repo),
):
    """Lista materiais com filtro opcional de estoque baixo."""
    query = ListMaterialsQuery(
        tenant_id=current_user.tenant_id,
        low_stock_only=low_stock_only,
    )
    materials = await query.execute(repo)
    return MaterialsListResponse(
        materials=[_material_to_response(m) for m in materials],
        total=len(materials),
    )


@router.get("/materials/low-stock", response_model=MaterialsListResponse)
async def list_low_stock_materials(
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_material_repo),
):
    """Lista materiais com estoque abaixo do minimo (alertas)."""
    query = ListMaterialsQuery(
        tenant_id=current_user.tenant_id,
        low_stock_only=True,
    )
    materials = await query.execute(repo)
    return MaterialsListResponse(
        materials=[_material_to_response(m) for m in materials],
        total=len(materials),
    )


@router.get("/materials/{material_id}", response_model=MaterialResponse)
async def get_material(
    material_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_material_repo),
):
    """Obtem material por ID."""
    material = await repo.get_by_id(material_id)
    if not material or material.tenant_id != current_user.tenant_id:
        raise HTTPException(404, "Material nao encontrado")
    return _material_to_response(material)


@router.put("/materials/{material_id}", response_model=MaterialResponse)
async def update_material(
    material_id: UUID,
    req: UpdateMaterialRequest,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_material_repo),
):
    """Atualiza material odontologico."""
    cmd = ManageMaterialCommand(
        tenant_id=current_user.tenant_id,
        material_id=material_id,
        name=req.name,
        description=req.description,
        category=req.category,
        unit=req.unit,
        min_stock=req.min_stock,
        cost_centavos=req.cost_centavos,
        supplier=req.supplier,
    )
    try:
        material = await cmd.execute(repo)
    except NotFoundError:
        raise HTTPException(404, "Material nao encontrado")
    except ValidationError as e:
        raise HTTPException(422, e.message)

    return _material_to_response(material)


@router.post(
    "/materials/{material_id}/stock-movement",
    response_model=StockMovementResponse,
    status_code=201,
)
async def record_stock_movement(
    material_id: UUID,
    req: StockMovementRequest,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_material_repo),
):
    """Registra movimentacao de estoque (entrada/saida/ajuste)."""
    cmd = RecordStockMovementCommand(
        material_id=material_id,
        movement_type=StockMovementType(req.movement_type),
        quantity=req.quantity,
        reason=req.reason,
        created_by=current_user.user_id,
    )
    try:
        _material, movement = await cmd.execute(repo)
    except NotFoundError:
        raise HTTPException(404, "Material nao encontrado")
    except ValidationError as e:
        raise HTTPException(422, e.message)

    return StockMovementResponse(
        id=str(movement.id),
        material_id=str(movement.material_id),
        movement_type=movement.movement_type.value,
        quantity=movement.quantity,
        reason=movement.reason,
        created_at=movement.created_at.isoformat(),
    )


# ---------------------------------------------------------------------------
# Suppliers
# ---------------------------------------------------------------------------


@router.post("/suppliers", response_model=SupplierResponse, status_code=201)
async def create_supplier(
    req: CreateSupplierRequest,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_supplier_repo),
):
    """Cadastra fornecedor de materiais."""
    supplier = Supplier(
        tenant_id=current_user.tenant_id,
        name=req.name,
        phone=req.phone,
        email=req.email,
        notes=req.notes,
    )
    await repo.save(supplier)
    return _supplier_to_response(supplier)


@router.get("/suppliers", response_model=SuppliersListResponse)
async def list_suppliers(
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_supplier_repo),
):
    """Lista fornecedores."""
    query = ListSuppliersQuery(tenant_id=current_user.tenant_id)
    suppliers = await query.execute(repo)
    return SuppliersListResponse(
        suppliers=[_supplier_to_response(s) for s in suppliers],
        total=len(suppliers),
    )
