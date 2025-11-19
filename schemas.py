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

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    first_name: str = Field(..., description="Prénom")
    last_name: str = Field(..., description="Nom")
    phone: str = Field(..., description="Numéro de téléphone")
    email: EmailStr = Field(..., description="Adresse email")
    location: str = Field(..., description="Localisation (ville)")
    status: Literal[
        "Étudiant", "Salarié", "Travailleur indépendant", "TPE/PME", "Auto-entrepreneur", "Au chômage"
    ] = Field(..., description="Statut de la personne")
    reason: str = Field(..., description="Pourquoi utiliser PassaQui")
    password: str = Field(..., min_length=6, description="Mot de passe (démonstration)")
    is_active: bool = Field(True, description="Compte actif")

# You can add additional schemas (e.g., Trip, Message) later as needed.
