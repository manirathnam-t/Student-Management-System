from app import create_app
from app.extensions import db, bcrypt
from app.models import User

app = create_app()

with app.app_context():

    # Check if admin already exists
    admin = User.query.filter_by(email="admin@gmail.com").first()

    if admin:
        print("Admin already exists!")

    else:
        hashed_password = bcrypt.generate_password_hash(
            "admin123"
        ).decode("utf-8")

        admin = User(
            name="Administrator",
            email="admin@gmail.com",
            password=hashed_password,
            role="Admin"
        )

        db.session.add(admin)
        db.session.commit()

        print("✅ Admin created successfully!")