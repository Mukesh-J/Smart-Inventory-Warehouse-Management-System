from fastapi import FastAPI

from database.connection import Base, engine
from routes.product import router as product_router
from exceptions.handlers import register_exception_handlers


# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Product Inventory Management API",
    version="1.0.0",
    description="FastAPI + MySQL + SQLAlchemy CRUD API"
)

# Register error handlers
register_exception_handlers(app)

# Register routes
app.include_router(product_router)


@app.get("/")
def root():
    return {
        "message": "Product Inventory Management API is running"
    }