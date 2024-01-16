# **Attention**!!!!

After create migrations, in migrations versions:
1. import add:
- from datetime import datetime
- import uuid
- from src.services.auth import auth_service
- from src.conf.config import settings

2. Assign a value to a variable: 
user_type_table = op.create_table('user_type', ...
and
users_table = op.create_table('users', ...
3. In "def upgrade() -> None:" add at the end:

    op.bulk_insert(user_type_table, [
        {
            'id': 1,
            'type': "User",
        },
        {
            'id': 2,
            'type': 'Moderator',
        },
        {
            'id': 3,
            'type': 'Admin',
        }
    ])
    op.bulk_insert(users_table, [
        {
            'id': uuid.uuid4(),
            'username': "Admin",
            'email': "admin@admin.com",
            'avatar': "https://asset.cloudinary.com/di5efpq4c/a2755bed968acf16e0f3acacd7f2fe1f",
            'password': auth_service.get_password_hash(settings.ADMIN_PASSWORD),
            'user_type_id': 3,
            'confirmed': True,
            'created_at': datetime.now()

        }
    ])
    

