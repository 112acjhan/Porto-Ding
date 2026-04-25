import hashlib
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert

from app.api.tickets import get_database_session
from app.services.ticket_service import users_table

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# --- Schemas for Auth ---
class UserRegister(BaseModel):
    username: str
    password: str
    role: str  # Must be "STAFF" or "MANAGER"

class UserLogin(BaseModel):
    id: int
    password: str

# Helper to hash passwords
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

@router.post("/register", status_code=201)
async def register_user(user: UserRegister, db: AsyncSession = Depends(get_database_session)):
    """Creates a new Staff or Manager account."""
    if user.role.upper() not in ["STAFF", "MANAGER"]:
        raise HTTPException(status_code=400, detail="Role must be STAFF or MANAGER")

    # Check if user exists
    stmt = select(users_table).where(users_table.c.username == user.username)
    existing_user = await db.execute(stmt)
    if existing_user.mappings().one_or_none():
        raise HTTPException(status_code=400, detail="Username already exists")

    # Insert new user
    hashed_pw = hash_password(user.password)
    insert_stmt = (
        insert(users_table)
        .values(username=user.username, role=user.role.upper(), password_hash=hashed_pw)
        .returning(users_table.c.id, users_table.c.username, users_table.c.role)
    )
    
    try:
        result = await db.execute(insert_stmt)
        await db.commit()
        new_user = result.mappings().one()
        return {"status": "success", "user": dict(new_user)}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login")
async def login_user(user: UserLogin, db: AsyncSession = Depends(get_database_session)):
    """Verifies credentials and returns the user's role."""
    hashed_pw = hash_password(user.password)
    
    stmt = select(users_table).where(
        (users_table.c.id == user.id) & 
        (users_table.c.password_hash == hashed_pw)
    )
    result = await db.execute(stmt)
    db_user = result.mappings().one_or_none()

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Return user details so the Frontend can save the Role in LocalStorage
    return {
        "status": "success",
        "message": "Login successful",
        "user": {
            "id": db_user["id"],
            "username": db_user["username"],
            "role": db_user["role"]
        }
    }