from app.auth.auth_system import AuthSystem

auth = AuthSystem()

created = auth.create_user(
    "admin",
    "admin123",
    "admin"
)

if created:

    print("Admin created successfully")

else:

    print("Admin already exists")