from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import User
from .auth import get_password_hash, verify_password
from .mongo import create_collection

async def get_user_by_username(username: str, db: AsyncSession):
    query = select(User).filter(User.username == username)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_user_by_email(email: str, db: AsyncSession):
    query = select(User).filter(User.email == email)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def create_user(username: str, email: str, password: str, company: str, db: AsyncSession):
    hashed_password = get_password_hash(password)
    new_user = User(username=username, email=email, hashed_password=hashed_password, company=company, mongo_collection=email)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    create_collection(email)
    print(new_user)
    return new_user.id

async def authenticate_user(username: str, password: str, db: AsyncSession):
    user = await get_user_by_email(username, db)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user
