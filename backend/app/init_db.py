from .database import engine, Base
from .models import Task, Document

print("Creating database tables...")

# This line creates the tables in the database
Base.metadata.create_all(bind=engine)

print("Tables created successfully.")