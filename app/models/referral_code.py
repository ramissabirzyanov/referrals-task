from app.db.base import Base

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    invited_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    referral_code: Mapped["ReferralCode"] = relationship(back_populates="owner")
    invited_users: Mapped[list["User"]] = relationship(
        "User", 
        back_populates="invited_by", 
        remote_side=[id]
    )
    invited_by: Mapped["User"] = relationship(
        back_populates="invited_users", 
        remote_side=[id]
    )


class ReferralCode(Base):
    __tablename__ = "referral_codes"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(str, unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)

    owner: Mapped["User"] = relationship(back_populates="referral_code")\
