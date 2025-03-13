from typing import TYPE_CHECKING
from datetime import datetime, timezone

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, DateTime

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class ReferralCode(Base):
    """
    Класс для представления реферальных кодов в базе данных.
    Атрибуты:
        id: Уникальный идентификатор реферального кода.
        code: Уникальный реферальный код.
        active: Флаг, указывающий, активен ли код (по умолчанию False).
        expires_at: Дата и время истечения срока действия кода.
        owner_id: Идентификатор пользователя, которому принадлежит код.
        owner: Связь с пользователем, которому принадлежит код.
    Методы:
        is_code_expired(): Проверяет, истек ли срок действия кода.
    """
    __tablename__ = "referral_codes"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    active: Mapped[bool] = mapped_column(default=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    owner: Mapped["User"] = relationship("User", back_populates="referral_code")

    def is_code_expired(self):
        """Обновление поля active при проверке срока реф. кода"""
        return self.expires_at <= datetime.now(timezone.utc)
