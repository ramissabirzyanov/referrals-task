from app.db.base import Base
from app.models.user import User

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from datetime import datetime

class ReferralCode(Base):
    __tablename__ = "referral_codes"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(str, unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)

    owner: Mapped["User"] = relationship(back_populates="referral_code")
