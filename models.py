from sqlalchemy import Column, Integer, String
from database import Base
import json


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True) # Añade valor ID a cada entrada que pongamos
    user_name = Column(String)
    user_email = Column(String)
    age = Column(Integer)
    recommendations = Column(String)
    ZIP = Column(Integer)

    # Method to set recommendations by serializing the list to JSON
    def set_recommendations(self, recommendations: list):
        self.recommendations = json.dumps(recommendations)

    # Method to get recommendations by deserializing the JSON string back to a list
    def get_recommendations(self) -> list:
        return json.loads(self.recommendations) if self.recommendations else []