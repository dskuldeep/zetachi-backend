from typing import AsyncGenerator, Dict, Any
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .database import SessionLocal, engine, Base
from .schemas import UserCreate, User as UserSchema, Token
from .auth import create_access_token, create_refresh_token, decode_token
from .crud import create_user, authenticate_user
from .models import User as UserModel  # Ensure this is the SQLAlchemy model
from fastapi.middleware.cors import CORSMiddleware
import logging
from .schemas import DocumentSchema, EditorData
from .models import DocumentModel
from .utils import generate_unique_id, generate_sample_document
from .mongo import add_json_to_collection, list_all_jsons, fetch_doc_by_id, delete_json_from_collection, update_json_in_collection
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    payload = decode_token(token)
    print(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    username = payload.get("sub")
    result = await db.execute(select(UserModel).filter(UserModel.username == username))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    return user

@app.post("/register", response_model=UserSchema)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # Use SQLAlchemy model UserModel for queries
    result = await db.execute(select(UserModel).filter(UserModel.username == user.username))
    db_user = result.scalar_one_or_none()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    result = await db.execute(select(UserModel).filter(UserModel.email == user.email))
    db_user = result.scalar_one_or_none()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = await create_user(user.username, user.email, user.password, user.company, db)
    logger.info("######")
    return_json = {"id": user_id, "username": user.username, "email": user.email, "company": user.company}
    logger.info(return_json)
    return return_json

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):

    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@app.post("/refresh", response_model=Token)
async def refresh_token(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    username = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    access_token = create_access_token(data={"sub": username})
    new_refresh_token = token # can be issued new refresh token instead
    return {"access_token": access_token, "refresh_token": new_refresh_token,  "token_type": "bearer"}

@app.get("/dashboard", response_model=UserSchema)
async def get_dashboard(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    username = payload.get("sub")
    result = await db.execute(select(UserModel).filter(UserModel.username == username))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return {"id": user.id, "username": user.username, "email": user.email}

@app.post("/create-document", response_model=DocumentSchema)
async def create_document(user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    new_document = DocumentModel(
        id = await generate_unique_id(db),
        collection=user.mongo_collection
    )
    db.add(new_document)
    await db.commit()
    await db.refresh(new_document)
    new_json = generate_sample_document(new_document.id)
    new_json = json.loads(new_json)
    collection_name = new_document.collection
    add_json_to_collection(collection_name, new_json)

    return {"document_id": new_document.id, "mongo_collection": new_document.collection}

@app.get("/list-documents")
async def list_documents(user: UserModel = Depends(get_current_user)):
    collection_name = user.email
    document_list = list_all_jsons(collection_name)
    return document_list

@app.get("/fetch-document", response_model=Dict[str, Any])
async def fetch_document(document_id: str, user: UserModel = Depends(get_current_user)):
    collection_name = user.email
    document = fetch_doc_by_id(collection_name, document_id)
    return document

@app.post("/delete-document", response_model=Dict[str, Any])
async def delete_document(document_id: str, user: UserModel = Depends(get_current_user)):
    collection_name = user.email
    message = delete_json_from_collection(collection_name=collection_name, doc_id=document_id)
    return{"doc_id": document_id, "collection": collection_name, "message": message}

@app.post("/save-document", response_model=Dict[str, Any])
async def save_document(document_id: str, data: EditorData, user: UserModel = Depends(get_current_user)):
    collection_name = user.email
    print("Received Data: ", data)
    existing_doc = fetch_doc_by_id(collection_name=collection_name, doc_id=document_id)

    if not existing_doc:
        raise HTTPException(status_code=404, detail="Document not found")

    #Prepare the data to be uploaded
    updated_data = {
        "id": document_id,
        "content": data.dict()
    }

    update_json_in_collection(collection_name, updated_data)
    return{"message": "Document updated successfully"}
