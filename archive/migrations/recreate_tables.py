from app.database import engine
from app.models import Base

# Drop and recreate all tables
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

print("Database tables recreated with new schema")