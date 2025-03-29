from main import app, datastore
from application.models import db, Role, User
from werkzeug.security import generate_password_hash
import uuid

with app.app_context():
    # Create roles if they don't exist
    admin_role = datastore.find_or_create_role(name="admin", description="User is an admin")
    inst_role = datastore.find_or_create_role(name="inst", description="User is an Instructor")
    stud_role = datastore.find_or_create_role(name="stud", description="User is a Student")
    db.session.commit()

    # Create admin user if not exists
    if not User.query.filter_by(email="admin@email.com").first():
        admin_user = User(
            email="admin@email.com",
            username="Admin User",
            password=generate_password_hash("admin", method='sha256'),
            active=True,
            fs_uniquifier=str(uuid.uuid4())
        )
        admin_user.roles.append(admin_role)
        db.session.add(admin_user)
        print("Admin user created successfully")

    # Create student user if not exists
    if not User.query.filter_by(email="stud1@email.com").first():
        student_user = User(
            email="stud1@email.com",
            username="Student One",
            password=generate_password_hash("stud1", method='sha256'),
            active=True,
            fs_uniquifier=str(uuid.uuid4())
        )
        student_user.roles.append(stud_role)
        db.session.add(student_user)
        print("Student user created successfully")

    db.session.commit()
    print("Database initialized successfully!")