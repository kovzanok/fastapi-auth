from sqlalchemy import BigInteger, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ARRAY
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    email: Mapped[str] = String(40)
    password: Mapped[str]
    roles: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)