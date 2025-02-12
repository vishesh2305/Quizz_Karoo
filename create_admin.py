from extensions import db, bcrypt
from models import User
from app import app  # Import your Flask app

# Create an admin user
def create_admin():
    with app.app_context():  # Ensure Flask context is active
        hashed_password = bcrypt.generate_password_hash("adminpass").decode("utf-8")
        
        # Check if admin already exists
        existing_admin = User.query.filter_by(email="admin@example.com").first()
        if existing_admin:
            print("Admin user already exists.")
        else:
            admin = User(
                username="admin",
                email="admin@example.com",
                password=hashed_password,
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")

# Run the function
if __name__ == "__main__":
    create_admin()
