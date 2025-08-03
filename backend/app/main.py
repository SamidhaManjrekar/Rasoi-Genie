# main.py - CORRECTED VERSION
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, schema, utils, database, auth

models.Base.metadata.create_all(bind=database.engine)
app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Add React dev server ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register")
def register(user: schema.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    existing_email = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = utils.hash_password(user.password)
    db_user = models.User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"msg": "User registered successfully"}

@app.post("/login", response_model=schema.Token)
def login(user: schema.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or not utils.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
        
    token = auth.create_access_token(data={"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/preferences")
def save_preferences(pref: schema.PreferenceCreate, db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    existing = db.query(models.Preference).filter(models.Preference.user_id == user.id).first()

    pref_data = {
        "diet_type": pref.diet_type,
        "cuisine": ",".join(pref.cuisine) if pref.cuisine else "",
        "meals": ",".join(pref.meals) if pref.meals else "",
        "cooking_time": pref.cooking_time,
        "health_conditions": ",".join(pref.health_conditions) if pref.health_conditions else "",
    }

    if existing:
        for key, value in pref_data.items():
            setattr(existing, key, value)
    else:
        new_pref = models.Preference(user_id=user.id, **pref_data)
        db.add(new_pref)

    db.commit()
    return {"msg": "Preferences saved successfully"}

@app.get("/preferences", response_model=schema.PreferenceCreate)
def get_preferences(db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    pref = db.query(models.Preference).filter(models.Preference.user_id == user.id).first()
    if not pref:
        raise HTTPException(status_code=404, detail="Preferences not found")

    return schema.PreferenceCreate(
        diet_type=pref.diet_type or "",
        cuisine=pref.cuisine.split(",") if pref.cuisine else [],
        meals=pref.meals.split(",") if pref.meals else [],
        cooking_time=pref.cooking_time or "",
        health_conditions=pref.health_conditions.split(",") if pref.health_conditions else [],
    )

# Optional: Add a protected endpoint for testing
@app.get("/protected")
def get_protected_data(user: models.User = Depends(auth.get_current_user)):
    return {
        "message": "This is protected data", 
        "user": user.username,
        "user_id": user.id
    }