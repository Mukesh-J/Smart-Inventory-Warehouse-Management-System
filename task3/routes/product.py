from decimal import Decimal

from fastapi import (
    APIRouter,
    Depends,
    Path,
    Query,
    status
)

from sqlalchemy.orm import Session

from database.connection import get_db

from schemas.product import (
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
    StatisticsResponse,
    StockUpdate
)

from services.product import (
    create_product,
    delete_product,
    get_product,
    get_products,
    get_statistics,
    low_stock_products,
    search_products,
    update_product,
    update_stock
)


router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


# -------------------------
# Create Product
# -------------------------

@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED
)
def create(
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    return create_product(db, product)


# -------------------------
# Get Products
# -------------------------

@router.get(
    "",
    response_model=ProductListResponse
)
def list_products(
    category: str | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    min_price: Decimal | None = Query(default=None, ge=0),
    max_price: Decimal | None = Query(default=None, ge=0),
    in_stock: bool | None = Query(default=None),

    sort_by: str = Query(
        default="created_at"
    ),

    sort_order: str = Query(
        default="desc"
    ),

    page: int = Query(
        default=1,
        ge=1
    ),

    limit: int = Query(
        default=10,
        ge=1,
        le=100
    ),

    db: Session = Depends(get_db)
):

    return get_products(
        db=db,
        category=category,
        is_active=is_active,
        min_price=min_price,
        max_price=max_price,
        in_stock=in_stock,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        limit=limit
    )


# -------------------------
# Search Products
# -------------------------

@router.get(
    "/search",
    response_model=ProductListResponse
)
def search(
    q: str = Query(
        min_length=1
    ),

    page: int = Query(
        default=1,
        ge=1
    ),

    limit: int = Query(
        default=10,
        ge=1,
        le=100
    ),

    db: Session = Depends(get_db)
):

    return search_products(
        db=db,
        search_text=q,
        page=page,
        limit=limit
    )


# -------------------------
# Statistics
# -------------------------

@router.get(
    "/statistics",
    response_model=StatisticsResponse
)
def statistics(
    db: Session = Depends(get_db)
):

    return get_statistics(db)


# -------------------------
# Low Stock
# -------------------------

@router.get(
    "/low-stock",
    response_model=ProductListResponse
)
def low_stock(
    threshold: int = Query(
        default=10,
        ge=0
    ),

    page: int = Query(
        default=1,
        ge=1
    ),

    limit: int = Query(
        default=10,
        ge=1,
        le=100
    ),

    db: Session = Depends(get_db)
):

    return low_stock_products(
        db=db,
        threshold=threshold,
        page=page,
        limit=limit
    )


# -------------------------
# Get Product By ID
# -------------------------

@router.get(
    "/{product_id}",
    response_model=ProductResponse
)
def get_by_id(
    product_id: int = Path(
        ge=1
    ),

    db: Session = Depends(get_db)
):

    return get_product(
        db,
        product_id
    )


# -------------------------
# Complete Update
# -------------------------

@router.put(
    "/{product_id}",
    response_model=ProductResponse
)
def update_complete(
    product_id: int,

    product: ProductCreate,

    db: Session = Depends(get_db)
):

    return update_product(
        db=db,
        product_id=product_id,
        product_data=product,
        partial=False
    )


# -------------------------
# Partial Update
# -------------------------

@router.patch(
    "/{product_id}",
    response_model=ProductResponse
)
def update_partial(
    product_id: int,

    product: ProductUpdate,

    db: Session = Depends(get_db)
):

    return update_product(
        db=db,
        product_id=product_id,
        product_data=product,
        partial=True
    )


# -------------------------
# Stock Update
# -------------------------

@router.patch(
    "/{product_id}/stock",
    response_model=ProductResponse
)
def stock_update(
    product_id: int,

    stock: StockUpdate,

    db: Session = Depends(get_db)
):

    return update_stock(
        db=db,
        product_id=product_id,
        stock_data=stock
    )


# -------------------------
# Delete Product
# -------------------------

@router.delete(
    "/{product_id}",
    response_model=ProductResponse
)
def delete(
    product_id: int,

    db: Session = Depends(get_db)
):

    return delete_product(
        db,
        product_id
    )