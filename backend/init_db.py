import asyncio
from app.database.connection import database
from app.database.schema import init_database

async def setup():
    await database.connect()
    print('Creating tables...')
    await init_database()
    await database.disconnect()
    print('Tables created successfully')

if __name__ == "__main__":
    asyncio.run(setup())
