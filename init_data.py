from app import app, db
from models import User

with app.app_context():
    db.create_all()

    # Check if the custom admin already exists
    if not User.query.filter_by(username='custom_admin').first():
        # Create the custom admin user
        admin = User(
            username='custom_admin',
            full_name='Custom Admin',
            is_admin=True
        )
        admin.set_password('custom_password')
        db.session.add(admin)
        print("Admin user added.")

    # Check if the sample user already exists
    if not User.query.filter_by(username='student').first():
        student = User(
            username='student',
            full_name='Student'
        )
        student.set_password('student123')
        db.session.add(student)
        print("Sample user added.")

    db.session.commit()
    print("Database initialized successfully.")

