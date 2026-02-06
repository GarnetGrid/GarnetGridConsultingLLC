from app.db.session import SessionLocal
from app.db.models import User
from app.util.auth import get_password_hash

db = SessionLocal()
try:
    user = db.query(User).filter(User.email == "user@jgpt.com").first()
    if user:
        print("User exists. Resetting password.")
        user.hashed_password = get_password_hash("jgpt-premium")
        user.is_active = True
    else:
        print("User does not exist. Creating user.")
        user = User(
            email="user@jgpt.com",
            hashed_password=get_password_hash("jgpt-premium"),
            role="user",
            is_active=True
        )
        db.add(user)
    db.commit()
    print("User user@jgpt.com fixed.")
except Exception as e:
    print(f"Error: {e}")
    db.rollback()
finally:
    db.close()
