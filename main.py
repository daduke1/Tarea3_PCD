from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from typing import List, Optional

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
    return db.query(models.Users).all()

@app.get("/{user_id}") # Query que filtra a través de ID de usuario y regresa error si no existe
def get_user(user_id: int, db: Session = Depends(get_db)):
    user_model = db.query(models.Users).filter(models.Users.id == user_id).first()

    if user_model is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user_model

@app.post("/") # Agrega user y lo asigna al esquema de la tabla
def create_user(user: User, db: Session = Depends(get_db)):

    user_model = models.Users()
    user_model.user_name = user.user_name
    user_model.user_email = user.user_email
    user_model.age = user.age
    user_model.recommendations = user.recommendations
    user_model.ZIP = user.ZIP

    db.add(user_model) # agregar a db
    db.commit() # commit a db

    return user


@app.put("/{user_id}") # Actualiza el libro con la lógica necesaria para hacerlo
def update_book(user_email: str, user: User, db: Session = Depends(get_db)):

    user_email = db.query(models.Users).filter(models.Users.user_email == user_email).first() # query y filtrar por el ID

    if user_email:
        raise HTTPException(
            status_code=404,
            detail=f"User already exists with email {user_email}"
        )

    user_email.user_name = user.user_name
    user_email.user_email = user.user_email
    user_email.age = user.age
    user_email.recommendations = user.recommendations
    user_email.ZIP = user.ZIP

    db.add(user_email)
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