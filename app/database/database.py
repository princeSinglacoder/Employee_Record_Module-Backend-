from app.config import engine, Base
from app.models.employee import Employee
from app.models.department import Department
from app.models.leave import Leave
from app.models.user import User
import alembic.config
import alembic.command

def run_migrations():
    """Run database migrations"""
    try:
        alembic_cfg = alembic.config.Config("alembic.ini")
        alembic.command.upgrade(alembic_cfg, "head")
        print("Migrations completed successfully!")
    except Exception as e:
        print(f"Error running migrations: {e}")
        raise

def create_tables():
    """Create all database tables (fallback if not using migrations)"""
    Base.metadata.create_all(bind=engine)

def init_database():
    """Initialize database with default data"""
    from app.config import SessionLocal

    # First create all tables directly
    print("Creating database tables...")
    try:
        create_tables()
        print("Tables created successfully!")
    except Exception as e:
        print(f"Error creating tables: {e}")

    db = SessionLocal()
    try:
        # Check if default admin user exists
        admin_user = db.query(User).filter(User.userName == "Prince349").first()
        if not admin_user:
            # Create default admin user
            admin = User(
                userName="Prince349",
                password="singla123",
                role="admin"
            )
            db.add(admin)
            db.commit()
            print("Default admin user created!")

        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Run migrations first
    run_migrations()
    # Then initialize with default data
    init_database()
