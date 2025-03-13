from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.referral_code import ReferralCode


class User(Base):
    """
    Класс для представления пользователей в базе данных.
    Атрибуты:
        id: Уникальный идентификатор пользователя.
        email: Электронная почта пользователя (уникальная, используется для входа).
        hashed_password: Хэшированный пароль пользователя.
        invited_by_id: Идентификатор пользователя, который пригласил текущего пользователя.
                                   Если None, пользователь не был приглашен.
        referral_code: Список реферальных кодов, созданных пользователем.
        invited_users: Список пользователей, приглашенных текущим пользователем.
        invited_by: Пользователь, который пригласил текущего пользователя.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    invited_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    referral_code: Mapped[list["ReferralCode"]] = relationship(
        "ReferralCode", back_populates="owner"
    )
    invited_users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="invited_by",
        remote_side=[invited_by_id],
        lazy="selectin"
    )
    invited_by: Mapped["User"] = relationship(
        "User",
        back_populates="invited_users",
        remote_side=[id],
        lazy="selectin"
    )
