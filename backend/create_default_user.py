from app.database import SessionLocal
from app.models import User

db = SessionLocal()

# Check if user exists
existing_user = db.query(User).filter(User.id == 1).first()

if existing_user:
    print("Default user already exists!")
else:
    # Create default user
    default_user = User(
        id=1,
        email="demo@example.com",
        hashed_password="placeholder_password"
    )
    db.add(default_user)
    db.commit()
    print("Default user created successfully!")

db.close()