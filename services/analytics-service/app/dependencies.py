from sqlalchemy.orm import sessionmaker

from app.database import engine
from app.repositories.mariadb_case_analytics import MariaDBCaseAnalyticsRepository
from app.services import AnalyticsService


SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


def get_analytics_service():
    db = SessionLocal()

    try:
        repository = MariaDBCaseAnalyticsRepository(db)
        yield AnalyticsService(repository)
    finally:
        db.close()