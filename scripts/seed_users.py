from app.db.session import SessionLocal
from app.models.user import User

def seed_users():
    db = SessionLocal()
    try:
        user = User(age=28, gender="female", interests=["jewelry", "fashion"])
        db.add(user)
        db.commit()
        print("✅ Users seeded")
    finally:
        db.close()


if __name__ == "__main__":
    seed_users()

