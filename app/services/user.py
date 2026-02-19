from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserCreate
from typing import List
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user(self, user_id: int) -> User | None:
        return await self.db.get(User, user_id)
    
    async def get_all_users(self) -> List[User]:
        stmt = select(User).order_by(User.id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create_user(self, user_data: UserCreate) -> User:
        user = User(**user_data.model_dump())
        self.db.add(user)
        try:
            await self.db.commit()
            await self.db.refresh(user)
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(status_code=400, detail="Username already exists")
        return user

    async def get_or_create_user(self, user_data: UserCreate) -> User:
        stmt = select(User).where(User.username == user_data.username)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            user = await self.create_user(user_data)
        return user