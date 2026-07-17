from app import create_app
from app.extensions import db, bcrypt
from app.models import User

app = create_app()

with app.app_context():

    admin = User(
        name="Administrator",
        email="admin@gmail.com",
        password=bcrypt.generate_password_hash("admin123").decode("utf-8"),
        role="Admin"
    )

    db.session.add(admin)
    db.session.commit()

    print("✅ Admin created successfully!")