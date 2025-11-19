import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import User

app = FastAPI(title="PassaQui API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "PassaQui backend en ligne"}

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
            response["database_url"] = "✅ Set"
            response["database_name"] = db.name
            response["connection_status"] = "Connected"
            try:
                response["collections"] = db.list_collection_names()[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

# Simple models for auth demo (not secure - demo only)
class SignupPayload(BaseModel):
    first_name: str
    last_name: str
    phone: str
    email: EmailStr
    location: str
    status: str
    reason: str
    password: str

class LoginPayload(BaseModel):
    email: EmailStr
    password: str

@app.post("/auth/signup")
def signup(payload: SignupPayload):
    # Check if email already exists
    existing = db["user"].find_one({"email": payload.email}) if db else None
    if existing:
        raise HTTPException(status_code=400, detail="Cet email est déjà utilisé.")

    user = User(
        first_name=payload.first_name,
        last_name=payload.last_name,
        phone=payload.phone,
        email=payload.email,
        location=payload.location,
        status=payload.status,  # Validated by schema
        reason=payload.reason,
        password=payload.password,
    )
    user_id = create_document("user", user)
    return {"message": "Compte créé avec succès", "user_id": user_id}

@app.post("/auth/login")
def login(payload: LoginPayload):
    if db is None:
        raise HTTPException(status_code=500, detail="Base de données non disponible")
    doc = db["user"].find_one({"email": payload.email, "password": payload.password})
    if not doc:
        raise HTTPException(status_code=401, detail="Identifiants invalides")
    return {
        "message": "Connexion réussie",
        "user": {
            "id": str(doc.get("_id")),
            "first_name": doc.get("first_name"),
            "last_name": doc.get("last_name"),
            "email": doc.get("email"),
        }
    }

# Fictive trips endpoint for search demo
class TripSearch(BaseModel):
    from_city: str
    to_city: str
    date: Optional[str] = None

@app.post("/search")
def search_trips(payload: TripSearch):
    results = [
        {"id": "t1", "driver": "Marie L.", "from": payload.from_city, "to": payload.to_city, "date": payload.date or "Demain", "price": 8.5, "rating": 4.8},
        {"id": "t2", "driver": "Antoine P.", "from": payload.from_city, "to": payload.to_city, "date": payload.date or "Aujourd'hui", "price": 6.0, "rating": 4.6},
        {"id": "t3", "driver": "Giulia R.", "from": payload.from_city, "to": payload.to_city, "date": payload.date or "Cette semaine", "price": 10.0, "rating": 4.9},
    ]
    return {"results": results}

# Demo endpoints for features
@app.get("/demo/messages")
def demo_messages():
    convo = [
        {"from": "Vous", "text": "Bonjour ! Le colis tient dans un sac à dos ?", "time": "10:02"},
        {"from": "Livreur", "text": "Oui, pas de souci. Je passe par Bastia vers 17h.", "time": "10:05"},
        {"from": "Vous", "text": "Parfait, je réserve. Merci !", "time": "10:06"},
    ]
    return {"conversation": convo}

@app.get("/demo/wallet")
def demo_wallet():
    return {"balance": 30.0, "history": [
        {"label": "Paiement reçu", "amount": "+15,00€", "date": "Hier"},
        {"label": "Réservation", "amount": "-5,00€", "date": "Cette semaine"},
        {"label": "Bonus parrainage", "amount": "+5,00€", "date": "Cette semaine"},
    ]}

@app.get("/demo/profiles")
def demo_profiles():
    return {"profiles": [
        {"name": "Camille", "rating": 4.9, "reviews": 58},
        {"name": "Paulu", "rating": 4.7, "reviews": 32},
        {"name": "Lina", "rating": 5.0, "reviews": 12},
    ]}

@app.get("/demo/achievements")
def demo_achievements():
    return {"achievements": [
        {"title": "Intermédiaire", "desc": "5e livraison effectuée", "icon": "trophy"},
        {"title": "Ambassadeur", "desc": "1 filleul actif", "icon": "badge"},
    ]}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
