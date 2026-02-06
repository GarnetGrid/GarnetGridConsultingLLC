from __future__ import annotations
from app.db.session import engine, SessionLocal
from app.db.models import Base, User
from app.util.auth import get_password_hash

def init_db():
    Base.metadata.create_all(bind=engine)
    seed_admin_user()

def seed_admin_user():
    db = SessionLocal()
    try:
        # Check if any user exists
        admin_user = db.query(User).filter(User.email == "admin@jgpt.com").first()
        if not admin_user:
            print("Seeding default admin user...")
            hashed_pwd = get_password_hash("admin")
            new_admin = User(
                email="admin@jgpt.com",
                hashed_password=hashed_pwd,
                role="admin"
            )
            db.add(new_admin)
            db.commit()
            print("Admin user seeded successfully.")
    except Exception as e:
        print(f"Error seeding admin user: {e}")
        db.rollback()
    finally:
        db.close()
