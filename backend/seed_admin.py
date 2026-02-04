import asyncio
from app.database.connection import database
from app.core.security import hash_password

async def seed_admin():
    await database.connect()
    
    # Check if admin already exists
    admin = await database.fetchrow("SELECT id FROM users WHERE username = 'admin'")
    if admin:
        print("Admin user already exists")
        await database.disconnect()
        return
    
    # Create admin user
    hashed_password = hash_password("Admin123")
    await database.execute(
        """INSERT INTO users (username, email, hashed_password, role, is_active)
           VALUES ($1, $2, $3, $4, $5)""",
        "admin",
        "admin@example.com",
        hashed_password,
        "admin",
        True
    )
    
    print("Admin user created successfully")
    print("Username: admin")
    print("Password: Admin123")
    
    await database.disconnect()

if __name__ == "__main__":
    asyncio.run(seed_admin())
