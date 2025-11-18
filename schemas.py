"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    images: List[HttpUrl] = Field(default_factory=list, description="Image gallery URLs")
    thumbnail: Optional[HttpUrl] = Field(None, description="Primary image URL")
    tags: List[str] = Field(default_factory=list, description="Search/filter tags")
    specs: Dict[str, str] = Field(default_factory=dict, description="Key/value specs")
    in_stock: bool = Field(True, description="Whether product is in stock")
    inventory: int = Field(10, ge=0, description="Units in stock")
    featured: bool = Field(False, description="Show in hero/featured sections")
    rating: float = Field(4.6, ge=0, le=5, description="Average rating")

class OrderItem(BaseModel):
    product_id: str
    title: str
    price: float
    quantity: int = Field(1, ge=1)
    thumbnail: Optional[HttpUrl] = None

class Order(BaseModel):
    """
    Orders collection schema
    Collection name: "order"
    """
    items: List[OrderItem]
    subtotal: float
    tax: float
    total: float
    email: str
    status: str = Field("paid", description="paid | failed | pending")
    notes: Optional[str] = None
