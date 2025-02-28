import os

class Config:
    SECRET_KEY = '226da76adec88964a0b689e2b639ee71b852a3e33031b7ebdc4697c3949ccf21439b784c8005403f2a35a051e17ad63acd8cf9a99b496cbc9bc19a3ddbb2556ef7558e15b1a73d82fff825be4652d30c2b681faad04860c74910fbd78e77318bae23458a2f282658bb986766e4e9e0c78bf7613c17d8d260993f14fd9304106'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # PostgreSQL info
    USERNAME = 'postgres'
    PASSWORD = 'postgres'
    HOST = 'db'  
    PORT = '5432'  
    DATABASE = 'robotremote'
    
    # SQLAlchemy config
    SQLALCHEMY_DATABASE_URI = f'postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}'

