from app.db.session import SessionLocal
from app.models.user import User

db = SessionLocal()

user = User(age=28, gender="female", interests="jewelry")
db.add(user)
db.commit()
db.close()
