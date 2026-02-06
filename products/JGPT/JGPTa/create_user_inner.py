from app.db.session import SessionLocal
from app.db.models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def run():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "user@jgpt.com").first()
        hashed = pwd_context.hash("jgpt-premium")
        if user:
            print("Resetting user password via Python script.")
            user.hashed_password = hashed
            user.is_active = True
        else:
            print("Creating user via Python script.")
            user = User(email="user@jgpt.com", hashed_password=hashed, role="user", is_active=True)
            db.add(user)
        db.commit()
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    run()
