File Structure
.
├── app/
│   ├── main.py
│   ├── crud.py
│   ├── models.py
│   ├── schemas.py
│   ├── models.py
│   ├── database.py
│   ├── auth.py
|── .env
├── alembic/
│   ├── env.py
│   |__ versions/
│── alembic.ini
└── requirements.txt


To run migrations: 
 - alembic revision --autogenerate -m "Message"
 - alembic upgrade head

 To run the app:
 uvicorn app.main:app --reload

