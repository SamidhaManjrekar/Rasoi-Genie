# main.py - CORRECTED VERSION
import json
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import agents
from . import models, schema, utils, database, auth

import os

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

# In a real-world scenario, get this key from a secure environment variable
TOGETHER_API_KEY = "tgp_v1_3L1Gq3VKiuALrOxkGgBUe9sRPnZWVSx8gcL18coxquI"
# Also, set it as an environment variable for LangChain's convenience
os.environ["TOGETHER_API_KEY"] = TOGETHER_API_KEY

@app.post("/generate-menu", response_model=schema.MenuResponse)
def generate_menu(req: schema.MenuGenerateRequest, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    pref = db.query(models.Preference).filter(models.Preference.user_id == current_user.id).first()
    if not pref:
        raise HTTPException(status_code=400, detail="Set preferences before generating menu")

    preferences = {
        "diet_type": pref.diet_type,
        "cuisine": pref.cuisine.split(","),
        "meals": pref.meals.split(","),
        "cooking_time": pref.cooking_time,
        "health_conditions": pref.health_conditions.split(",")
    }

    agent = agents.IndianMenuAgent(together_api_key=TOGETHER_API_KEY)
    menu_result = agent.generate_weekly_menu(preferences)

    # Deactivate previous menu
    db.query(models.WeeklyMenu).filter(models.WeeklyMenu.user_id == current_user.id, models.WeeklyMenu.is_active == 1).update({"is_active": 0})

    new_menu = models.WeeklyMenu(
        user_id=current_user.id,
        menu_data=json.dumps(menu_result["menu"]),
        generation_prompt=json.dumps(menu_result["preferences_used"]),
        created_at=menu_result["generated_at"],
        is_active=1
    )
    db.add(new_menu)
    db.commit()
    db.refresh(new_menu)

    return {
        "menu": menu_result["menu"],
        "preferences_used": menu_result["preferences_used"],
        "generated_at": menu_result["generated_at"],
        "menu_id": new_menu.id
    }

@app.get("/current-menu", response_model=schema.MenuResponse)
def get_current_menu(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    menu = db.query(models.WeeklyMenu).filter(models.WeeklyMenu.user_id == current_user.id, models.WeeklyMenu.is_active == 1).first()
    if not menu:
        raise HTTPException(status_code=404, detail="No active menu found")
    return {
        "menu": json.loads(menu.menu_data),
        "preferences_used": json.loads(menu.generation_prompt),
        "generated_at": menu.created_at,
        "menu_id": menu.id
    }

@app.post("/regenerate-meal", response_model=schema.MenuResponse)
def regenerate_meal(req: schema.MenuRegenerateRequest, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    menu = db.query(models.WeeklyMenu).filter(models.WeeklyMenu.id == req.menu_id, models.WeeklyMenu.user_id == current_user.id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")

    preferences = json.loads(menu.generation_prompt)
    agent = agents.IndianMenuAgent(together_api_key=TOGETHER_API_KEY)
    
    # Use the agent to find a new dish, which might involve a search
    prompt = f"Suggest one new dish for {req.day}'s {req.meal} with cuisine '{preferences['cuisine'][0]}' and diet type '{preferences['diet_type']}'. The current dishes are: {json.loads(menu.menu_data)[req.day].values()}. Do not repeat any of them."
    
    response = agent.agent_executor.invoke({"input": prompt})
    new_dish = response['output']

    current_menu = json.loads(menu.menu_data)
    current_menu[req.day][req.meal] = new_dish
    menu.menu_data = json.dumps(current_menu)
    db.commit()

    return {
        "menu": current_menu,
        "preferences_used": preferences,
        "generated_at": menu.created_at,
        "menu_id": menu.id
    }

@app.get("/menu-history", response_model=schema.MenuHistoryResponse)
def get_menu_history(limit: int = 10, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    history = db.query(models.WeeklyMenu).filter(models.WeeklyMenu.user_id == current_user.id).order_by(models.WeeklyMenu.id.desc()).limit(limit).all()
    result = []

    for item in history:
        full_menu = json.loads(item.menu_data)
        preview = {day: list(meals.values()) for day, meals in full_menu.items()}
        result.append(schema.MenuHistoryItem(
            id=item.id,
            generated_at=item.created_at,
            is_active=bool(item.is_active),
            menu_preview=preview
        ))

    return {"menus": result}