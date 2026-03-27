import asyncio
from src.database.connect_db import async_session_maker 
from src.auth.password_hashing import hash_password
from src.models.users import Users
from src.auth.password_hashing import verify_password

hashed_password = hash_password("UporDown!31")

async def main():
    async with async_session_maker() as db_session: 
        async with db_session.begin(): 
            user = Users(
                name="Maksim",
                email="safranov01@gmail.com",
                hashed_password=hashed_password,
                role="admin",
                room_number=0
            )
            db_session.add(user)
        
        await db_session.refresh(user)
        print(f"Added user with id: {user.id}")

if __name__ == "__main__":
    asyncio.run(main())
# print(hashed_password)
# print(verify_password("UporDown!31", hashed_password))