from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.referral_code import ReferralCode


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    invited_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    referral_code: Mapped["ReferralCode"] = relationship("ReferralCode", back_populates="owner")
    invited_users: Mapped[list["User"]] = relationship(
        "User", 
        back_populates="invited_by", 
        remote_side=[id]
    )
    invited_by: Mapped["User"] = relationship(
        "User",
        back_populates="invited_users", 
        remote_side=[id]
    )
