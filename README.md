# **Attention**!!!!

After create migrations, in migrations versions:
1. assign a value to a variable: user_type_table = op.create_table(...
2. add in "def upgrade() -> None:" next:

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
            'id': 1,
            'username': "Admin",
            'email': "admin@admin.com",
            'password': "$2b$12$oZ6VcFemIpZkcNmTQsi72eDDZ8SGrhtE19k5Tb4yjmeT7DNNgHs4e",
            'user_type_id': 3,
            'confirmed': True,

        }
    ])
    

