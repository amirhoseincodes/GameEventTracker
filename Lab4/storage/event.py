from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, func, false
import uuid


class Base(DeclarativeBase):
    pass



class LoginReport(Base):
    __tablename__ = "login_report"
    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    trace_id : Mapped[str] = mapped_column(String(36),nullable=False) # برای uuid4 مناسب
    user_id: Mapped[str] = mapped_column(String(50), nullable=False)
    client_id: Mapped[str] = mapped_column(String(50), nullable=False)
    event_id: Mapped[str] = mapped_column(String(50), nullable=False)
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    local: Mapped[str] = mapped_column(String(50), nullable=False)
    ip: Mapped[str] = mapped_column(String(50), nullable=False)

    timestamp: Mapped[DateTime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    date_created: Mapped[DateTime] = mapped_column(DateTime, nullable=False, server_default=func.now())


class ScoreReport(Base):
    __tablename__ = "score_report"

    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    trace_id : Mapped[str] = mapped_column(String(36),nullable=False) # برای uuid4 مناسب
    user_id: Mapped[str] = mapped_column(String(50), nullable=False)
    client_id: Mapped[str] = mapped_column(String(50), nullable=False)
    event_id: Mapped[str] = mapped_column(String(50), nullable=False)
    level_id: Mapped[int] = mapped_column(Integer, nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False)

    timestamp: Mapped[DateTime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    date_created: Mapped[DateTime] = mapped_column(DateTime, nullable=False, server_default=func.now())


