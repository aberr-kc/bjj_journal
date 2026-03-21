from app.database import engine
from app.models import Base

try:
    Base.metadata.create_all(bind=engine)
    print('Database schema updated successfully')
    print('New Garmin fields added to Entry table')
except Exception as e:
    print(f'Error updating schema: {e}')