from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy import String, ForeignKey, DateTime
from datetime import datetime,timezone

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class ReferralCode(Base):
    __tablename__ = "referral_codes"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    active: Mapped[bool] = mapped_column(default=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    owner: Mapped["User"] = relationship("User", back_populates="referral_code")

    # @validates('expires_at')
    # def validate_expire_at(self, key, expires_at):
    #     if expires_at < datetime.now(timezone.utc):
    #         self.active = False
    #     return expires_at
