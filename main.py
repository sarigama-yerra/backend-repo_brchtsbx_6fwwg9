import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson.objectid import ObjectId

from database import db, create_document, get_documents
from schemas import Product, Order, OrderItem

app = FastAPI(title="E-Commerce API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "E-Commerce API running"}


# Utility to convert Mongo docs
class ProductOut(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    price: float
    category: str
    images: List[str] = []
    thumbnail: Optional[str] = None
    tags: List[str] = []
    specs: dict = {}
    in_stock: bool = True
    inventory: int = 0
    featured: bool = False
    rating: float = 0


@app.get("/api/products", response_model=List[ProductOut])
def list_products():
    docs = get_documents("product")
    result = []
    for d in docs:
        d["id"] = str(d.get("_id"))
        d.pop("_id", None)
        result.append(ProductOut(**d))
    return result


@app.get("/api/products/featured", response_model=List[ProductOut])
def list_featured_products():
    docs = get_documents("product", {"featured": True})
    result = []
    for d in docs:
        d["id"] = str(d.get("_id"))
        d.pop("_id", None)
        result.append(ProductOut(**d))
    return result


@app.get("/api/products/{product_id}", response_model=ProductOut)
def get_product(product_id: str):
    doc = db["product"].find_one({"_id": ObjectId(product_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Product not found")
    doc["id"] = str(doc.get("_id"))
    doc.pop("_id", None)
    return ProductOut(**doc)


@app.post("/api/seed")
def seed_products():
    # Only seed if empty
    count = db["product"].count_documents({}) if db else 0
    if count > 0:
        return {"seeded": False, "message": "Products already exist"}

    products = [
        Product(
            title="Nebula Runner Sneakers",
            description="Lightweight knit with iridescent sole for anti-gravity vibes.",
            price=189.0,
            category="Footwear",
            images=[
                "https://images.unsplash.com/photo-1542291026-7eec264c27ff",
                "https://images.unsplash.com/photo-1519741497674-611481863552",
            ],
            thumbnail="https://images.unsplash.com/photo-1542291026-7eec264c27ff",
            tags=["sneakers", "iridescent", "knit"],
            specs={"Weight": "210g", "Material": "AeroKnit", "Drop": "6mm"},
            in_stock=True,
            inventory=24,
            featured=True,
            rating=4.7,
        ),
        Product(
            title="Quantum Mesh Backpack",
            description="Suspended compartments with anti-sag structure.",
            price=129.0,
            category="Accessories",
            images=[
                "https://images.unsplash.com/photo-1618354691510-58fbe6b3ac8b",
                "https://images.unsplash.com/photo-1516542076529-1ea3854896e1",
            ],
            thumbnail="https://images.unsplash.com/photo-1618354691510-58fbe6b3ac8b",
            tags=["backpack", "mesh"],
            specs={"Capacity": "24L", "Weight": "650g", "Material": "Tessellate Mesh"},
            featured=True,
        ),
        Product(
            title="Aurora Layered Jacket",
            description="Thermo-reactive panels shift hue with temperature.",
            price=259.0,
            category="Outerwear",
            images=[
                "https://images.unsplash.com/photo-1551024709-8f23befc6cf7",
                "https://images.unsplash.com/photo-1551537482-f2075a1d41f2",
            ],
            thumbnail="https://images.unsplash.com/photo-1551024709-8f23befc6cf7",
            tags=["jacket", "heat-reactive"],
            specs={"Shell": "PolyPhase", "Lining": "AeroWeave"},
            featured=True,
        ),
        Product(
            title="Flux Knit Tee",
            description="Zero-seam knit with breathable micro vents.",
            price=69.0,
            category="Apparel",
            images=[
                "https://images.unsplash.com/photo-1520975916090-3105956dac38",
            ],
            thumbnail="https://images.unsplash.com/photo-1520975916090-3105956dac38",
            tags=["tee", "knit"],
        ),
        Product(
            title="HoloCore Bottle",
            description="Double-wall with prismatic inner coating.",
            price=39.0,
            category="Accessories",
            images=[
                "https://images.unsplash.com/photo-1517336714731-489689fd1ca8",
            ],
            thumbnail="https://images.unsplash.com/photo-1517336714731-489689fd1ca8",
            tags=["bottle", "holographic"],
        ),
        Product(
            title="PulseTrack Watch",
            description="Ceramic body with spectral heart-rate wave.",
            price=349.0,
            category="Wearables",
            images=[
                "https://images.unsplash.com/photo-1511739001486-6bfe10ce785f",
            ],
            thumbnail="https://images.unsplash.com/photo-1511739001486-6bfe10ce785f",
            tags=["watch"],
            featured=True,
        ),
        Product(
            title="Vector Grid Cap",
            description="Laser-perf brim with 3D embroidered grid.",
            price=45.0,
            category="Apparel",
            images=[
                "https://images.unsplash.com/photo-1520975916090-3105956dac38",
            ],
            thumbnail="https://images.unsplash.com/photo-1520975916090-3105956dac38",
            tags=["cap"],
        ),
        Product(
            title="Iridesse Socks",
            description="Gradient yarn with reinforced arch.",
            price=19.0,
            category="Apparel",
            images=[
                "https://images.unsplash.com/photo-1542291026-7eec264c27ff",
            ],
            thumbnail="https://images.unsplash.com/photo-1542291026-7eec264c27ff",
            tags=["socks"],
        ),
    ]

    ids = []
    for p in products:
        ids.append(create_document("product", p))

    return {"seeded": True, "count": len(ids), "ids": ids}


class CheckoutRequest(BaseModel):
    items: List[OrderItem]
    email: str
    notes: Optional[str] = None


@app.post("/api/checkout")
def checkout(payload: CheckoutRequest):
    # Simulate pricing
    subtotal = sum([item.price * item.quantity for item in payload.items])
    tax = round(subtotal * 0.08, 2)
    total = round(subtotal + tax, 2)

    order = Order(
        items=payload.items,
        subtotal=subtotal,
        tax=tax,
        total=total,
        email=payload.email,
        status="paid",
        notes=payload.notes,
    )

    order_id = create_document("order", order)

    return {"order_id": order_id, "status": "paid", "total": total}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
