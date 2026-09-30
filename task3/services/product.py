from decimal import Decimal

from fastapi import HTTPException, status

from sqlalchemy import (
    asc,
    desc,
    func,
    or_
)

from sqlalchemy.exc import (
    IntegrityError,
    SQLAlchemyError
)

from sqlalchemy.orm import Session

from database.models import Product

from schemas.product import (
    ProductCreate,
    ProductUpdate,
    StockUpdate
)


# -------------------------
# Allowed Sorting Fields
# -------------------------

ALLOWED_SORT_FIELDS = {
    "product_name": Product.product_name,
    "price": Product.price,
    "quantity": Product.quantity,
    "created_at": Product.created_at
}


# -------------------------
# Transaction Helper
# -------------------------

def commit_transaction(
    db: Session
):

    try:

        db.commit()

    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Product code already exists"
        )

    except SQLAlchemyError:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Database error"
        )


# -------------------------
# Get Product
# -------------------------

def get_product_or_404(
    db: Session,
    product_id: int
):

    product = (
        db.query(Product)
        .filter(
            Product.product_id == product_id
        )
        .first()
    )

    if not product:

        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product


def get_product(
    db: Session,
    product_id: int
):

    return get_product_or_404(
        db,
        product_id
    )


# -------------------------
# Create Product
# -------------------------

def create_product(
    db: Session,
    product_data: ProductCreate
):

    existing = (
        db.query(Product)
        .filter(
            Product.product_code
            == product_data.product_code
        )
        .first()
    )

    if existing:

        raise HTTPException(
            status_code=409,
            detail="Product code already exists"
        )

    product = Product(
        **product_data.model_dump()
    )

    db.add(product)

    commit_transaction(db)

    db.refresh(product)

    return product


# -------------------------
# Get Products
# -------------------------

def get_products(
    db: Session,
    category=None,
    is_active=None,
    min_price=None,
    max_price=None,
    in_stock=None,
    sort_by="created_at",
    sort_order="desc",
    page=1,
    limit=10
):

    if min_price is not None and max_price is not None:

        if min_price > max_price:

            raise HTTPException(
                status_code=400,
                detail="min_price cannot be greater than max_price"
            )

    if sort_by not in ALLOWED_SORT_FIELDS:

        raise HTTPException(
            status_code=400,
            detail="Invalid sort field"
        )

    if sort_order not in ["asc", "desc"]:

        raise HTTPException(
            status_code=400,
            detail="sort_order must be asc or desc"
        )

    query = db.query(Product)

    if category is not None:

        query = query.filter(
            Product.category == category
        )

    if is_active is not None:

        query = query.filter(
            Product.is_active == is_active
        )

    if min_price is not None:

        query = query.filter(
            Product.price >= min_price
        )

    if max_price is not None:

        query = query.filter(
            Product.price <= max_price
        )

    if in_stock is True:

        query = query.filter(
            Product.quantity > 0
        )

    elif in_stock is False:

        query = query.filter(
            Product.quantity == 0
        )

    total = query.count()

    sort_column = ALLOWED_SORT_FIELDS[sort_by]

    if sort_order == "asc":

        query = query.order_by(
            asc(sort_column)
        )

    else:

        query = query.order_by(
            desc(sort_column)
        )

    offset = (page - 1) * limit

    products = (
        query
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "products": products,
        "page": page,
        "limit": limit,
        "total": total
    }


# -------------------------
# Search
# -------------------------

def search_products(
    db: Session,
    search_text: str,
    page: int,
    limit: int
):

    search_pattern = f"%{search_text}%"

    query = (
        db.query(Product)
        .filter(
            or_(
                Product.product_name.ilike(
                    search_pattern
                ),
                Product.product_code.ilike(
                    search_pattern
                ),
                Product.category.ilike(
                    search_pattern
                ),
                Product.supplier_name.ilike(
                    search_pattern
                )
            )
        )
    )

    total = query.count()

    offset = (page - 1) * limit

    products = (
        query
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "products": products,
        "page": page,
        "limit": limit,
        "total": total
    }


# -------------------------
# Update Product
# -------------------------

def update_product(
    db: Session,
    product_id: int,
    product_data,
    partial: bool
):

    product = get_product_or_404(
        db,
        product_id
    )

    if partial:

        update_data = product_data.model_dump(
            exclude_unset=True
        )

    else:

        update_data = product_data.model_dump()

    if "product_code" in update_data:

        existing = (
            db.query(Product)
            .filter(
                Product.product_code
                == update_data["product_code"],

                Product.product_id
                != product_id
            )
            .first()
        )

        if existing:

            raise HTTPException(
                status_code=409,
                detail="Product code already exists"
            )

    for field, value in update_data.items():

        setattr(
            product,
            field,
            value
        )

    commit_transaction(db)

    db.refresh(product)

    return product


# -------------------------
# Soft Delete
# -------------------------

def delete_product(
    db: Session,
    product_id: int
):

    product = get_product_or_404(
        db,
        product_id
    )

    product.is_active = False

    commit_transaction(db)

    db.refresh(product)

    return product


# -------------------------
# Stock Update
# -------------------------

def update_stock(
    db: Session,
    product_id: int,
    stock_data: StockUpdate
):

    product = get_product_or_404(
        db,
        product_id
    )

    if stock_data.operation == "add":

        product.quantity += stock_data.quantity

    elif stock_data.operation == "remove":

        if product.quantity < stock_data.quantity:

            raise HTTPException(
                status_code=400,
                detail="Insufficient stock"
            )

        product.quantity -= stock_data.quantity

    commit_transaction(db)

    db.refresh(product)

    return product


# -------------------------
# Statistics
# -------------------------

def get_statistics(
    db: Session
):

    total_products = (
        db.query(
            func.count(Product.product_id)
        )
        .scalar()
        or 0
    )

    active_products = (
        db.query(
            func.count(Product.product_id)
        )
        .filter(
            Product.is_active == True
        )
        .scalar()
        or 0
    )

    inactive_products = (
        db.query(
            func.count(Product.product_id)
        )
        .filter(
            Product.is_active == False
        )
        .scalar()
        or 0
    )

    total_stock = (
        db.query(
            func.coalesce(
                func.sum(Product.quantity),
                0
            )
        )
        .scalar()
        or 0
    )

    total_inventory_value = (
        db.query(
            func.coalesce(
                func.sum(
                    Product.price
                    * Product.quantity
                ),
                0
            )
        )
        .scalar()
        or 0
    )

    return {
        "total_products": total_products,
        "active_products": active_products,
        "inactive_products": inactive_products,
        "total_stock": total_stock,
        "total_inventory_value": total_inventory_value
    }


# -------------------------
# Low Stock
# -------------------------

def low_stock_products(
    db: Session,
    threshold: int,
    page: int,
    limit: int
):

    query = (
        db.query(Product)
        .filter(
            Product.quantity <= threshold,
            Product.is_active == True
        )
        .order_by(
            asc(Product.quantity)
        )
    )

    total = query.count()

    offset = (page - 1) * limit

    products = (
        query
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "products": products,
        "page": page,
        "limit": limit,
        "total": total
    }