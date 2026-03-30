"""Pydantic v2 schemas for Inventory (Estoque) endpoints."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


class CreateMaterialRequest(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = None
    unit: str = Field(default="un", max_length=10)
    min_stock: int = Field(ge=0, default=0)
    cost_centavos: int = Field(ge=0, default=0)
    supplier: Optional[str] = None


class UpdateMaterialRequest(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = None
    unit: str = Field(default="un", max_length=10)
    min_stock: int = Field(ge=0, default=0)
    cost_centavos: int = Field(ge=0, default=0)
    supplier: Optional[str] = None


class StockMovementRequest(BaseModel):
    movement_type: str  # ENTRY, EXIT, ADJUSTMENT
    quantity: int = Field(ge=0)
    reason: str = Field(min_length=2, max_length=500)


class CreateSupplierRequest(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    phone: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[str] = None


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class MaterialResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    unit: str
    current_stock: int
    min_stock: int
    cost_centavos: int
    supplier: Optional[str] = None
    is_low_stock: bool
    active: bool
    created_at: str


class MaterialsListResponse(BaseModel):
    materials: list[MaterialResponse]
    total: int


class StockMovementResponse(BaseModel):
    id: str
    material_id: str
    movement_type: str
    quantity: int
    reason: str
    created_at: str


class SupplierResponse(BaseModel):
    id: str
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[str] = None


class SuppliersListResponse(BaseModel):
    suppliers: list[SupplierResponse]
    total: int
