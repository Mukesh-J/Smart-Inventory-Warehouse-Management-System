from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator
)


# -------------------------
# Create Product
# -------------------------

class ProductCreate(BaseModel):

    product_code: str = Field(
        min_length=1,
        max_length=50
    )

    product_name: str = Field(
        min_length=1,
        max_length=150
    )

    description: str | None = None

    category: str = Field(
        min_length=1,
        max_length=100
    )

    price: Decimal = Field(
        gt=0
    )

    quantity: int = Field(
        ge=0
    )

    supplier_name: str = Field(
        min_length=1,
        max_length=150
    )

    is_active: bool = True

    @field_validator(
        "product_code",
        "product_name",
        "category",
        "supplier_name"
    )
    @classmethod
    def validate_strings(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Field cannot be empty")

        return value


# -------------------------
# Update Product
# -------------------------

class ProductUpdate(BaseModel):

    product_code: str | None = Field(
        default=None,
        min_length=1,
        max_length=50
    )

    product_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150
    )

    description: str | None = None

    category: str | None = Field(
        default=None,
        min_length=1,
        max_length=100
    )

    price: Decimal | None = Field(
        default=None,
        gt=0
    )

    quantity: int | None = Field(
        default=None,
        ge=0
    )

    supplier_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150
    )

    is_active: bool | None = None

    @field_validator(
        "product_code",
        "product_name",
        "category",
        "supplier_name"
    )
    @classmethod
    def validate_strings(cls, value):

        if value is None:
            return value

        value = value.strip()

        if not value:
            raise ValueError("Field cannot be empty")

        return value


# -------------------------
# Product Response
# -------------------------

class ProductResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    product_id: int
    product_code: str
    product_name: str
    description: str | None
    category: str
    price: Decimal
    quantity: int
    supplier_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


# -------------------------
# Product List Response
# -------------------------

class ProductListResponse(BaseModel):

    products: list[ProductResponse]

    page: int

    limit: int

    total: int


# -------------------------
# Stock Update
# -------------------------

class StockUpdate(BaseModel):

    quantity: int = Field(
        gt=0
    )

    operation: Literal[
        "add",
        "remove"
    ]


# -------------------------
# Statistics Response
# -------------------------

class StatisticsResponse(BaseModel):

    total_products: int

    active_products: int

    inactive_products: int

    total_stock: int

    total_inventory_value: Decimal