from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from typing import List, Optional
import json

app = FastAPI()

models.Base.metadata.create_all(bind=engine) # Crea la tabla si no está creada


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class User(BaseModel):
    user_name: str = Field(min_length=1)
    user_email: str = Field(min_length=1, max_length=100)
    age: Optional[int] = Field(ge=0, le=150)
    recommendations: List[str] = None
    ZIP: Optional[int] = Field(ge=10000, le=99999)


@app.get("/") # Query que regresa toda la base de datos
def read_api(db: Session = Depends(get_db)): # Te regresa la base de datos
    users = db.query(models.Users).all()
    for user in users:
        user.recommendations = json.loads(user.recommendations) if user.recommendations else []
    return users


@app.get("/{user_id}") # Query que filtra a través de ID de usuario y regresa error si no existe
def get_user(user_id: int, db: Session = Depends(get_db)):
    user_model = db.query(models.Users).filter(models.Users.id == user_id).first()

    if user_model is None:
        raise HTTPException(status_code=404, detail="User not found")

    user_model.recommendations = json.loads(user_model.recommendations) if user_model.recommendations else []

    return user_model

@app.post("/") # Agrega user y lo asigna al esquema de la tabla
def create_user(user: User, db: Session = Depends(get_db)):

    user_email = db.query(models.Users).filter(models.Users.user_email == user.user_email).first() # query y filtrar por el ID

    if user_email:
        raise HTTPException(
            status_code=404,
            detail=f"User already associated with that email"
        )

    user_model = models.Users(
        user_name=user.user_name,
        user_email=user.user_email,
        age=user.age,
        recommendations=json.dumps(user.recommendations) if user.recommendations else None,
        ZIP=user.ZIP
    )

    # Add the new user to the database
    db.add(user_model)
    db.commit()  # Commit the transaction
    db.refresh(user_model)  # Refresh the instance to get the new ID

    return user_model


@app.put("/{user_id}") # Actualiza el usuario con la lógica necesaria para hacerlo
def update_book(user_id: int, user: User, db: Session = Depends(get_db)):

    user_model = db.query(models.Users).filter(models.Users.id == user_id).first()

    if user_model is None:
        raise HTTPException(
            status_code=404,
            detail=f"ID {user_id} : Does not exist"
        )

    user_model.user_name = user.user_name
    user_model.user_email = user.user_email
    user_model.age = user.age
    user_model.recommendations = json.dumps(user.recommendations) if user.recommendations else None
    user_model.ZIP = user.ZIP

    db.add(user_model)
    db.commit()

    return user


@app.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):

    user_model = db.query(models.Users).filter(models.Users.id == user_id).first()

    if user_model is None:
        raise HTTPException(
            status_code=404,
            detail=f"ID {user_id} : Does not exist"
        )

    db.query(models.Users).filter(models.Users.id == user_id).delete()

    db.commit()