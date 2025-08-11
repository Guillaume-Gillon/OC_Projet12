from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.mysql import BINARY
from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Table,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from typing import List, Optional
import uuid


BASE = declarative_base()

# --- Tables d'Associations ---
user_role = Table(
    "user_role",
    BASE.metadata,
    Column(
        "user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    ),
)

role_permission = Table(
    "role_permission",
    BASE.metadata,
    Column(
        "role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "permission_id",
        Integer,
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class User(BASE):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_number: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    jwt_hash: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, onupdate=func.now()
    )
    # Mapped[List["Role"]] indique que 'role' sera une liste d'objets Roles.
    roles: Mapped[List["Role"]] = relationship(
        secondary=user_role, back_populates="users"
    )
    clients: Mapped[List["Client"]] = relationship(back_populates="commercial_contact")
    contracts: Mapped[List["Contract"]] = relationship(
        back_populates="commercial_contact"
    )
    events: Mapped[List["Event"]] = relationship(back_populates="support_contact")

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.first_name} {self.last_name}')>"

    def __str__(self):
        return f"{self.first_name} {self.last_name} (N°{self.employee_number})"


class Role(BASE):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    users: Mapped[List["User"]] = relationship(
        secondary=user_role, back_populates="roles"
    )
    permissions: Mapped[List["Permission"]] = relationship(
        secondary=role_permission, back_populates="roles"
    )

    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}')>"

    def __str__(self):
        return f"{self.name}"


class Permission(BASE):
    __tablename__ = "permissions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    roles: Mapped[List["Role"]] = relationship(
        secondary=role_permission, back_populates="permissions"
    )

    def __repr__(self):
        return f"<Permission(id={self.id}, name='{self.name}')>"

    def __str__(self):
        return f"{self.name}"


class Client(BASE):
    __tablename__ = "clients"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(100), nullable=False)
    company_name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, onupdate=func.now()
    )
    related_user_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    commercial_contact: Mapped["User"] = relationship(back_populates="clients")
    contracts: Mapped[List["Contract"]] = relationship(back_populates="client")

    def __repr__(self):
        return f"<Client(id={self.id}, name='{self.name}')>"

    def __str__(self):
        return f"{self.company_name} - {self.name}"


class Contract(BASE):
    __tablename__ = "contracts"
    id: Mapped[uuid.UUID] = mapped_column(
        BINARY(16), primary_key=True, default=lambda: uuid.uuid4().bytes
    )
    related_client_id: Mapped[int] = mapped_column(ForeignKey(Client.id))
    client: Mapped["Client"] = relationship(back_populates="contracts")
    related_user_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    commercial_contact: Mapped["User"] = relationship(back_populates="contracts")
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    balance_due: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, onupdate=func.now()
    )
    signed: Mapped[bool] = mapped_column(Boolean, default=False)
    event: Mapped[Optional["Event"]] = relationship(
        back_populates="contract", uselist=False
    )

    def __repr__(self):
        return f"<Contract(id={self.id}')>"

    def __str__(self):
        if isinstance(self.id, uuid.UUID):
            display_id = str(self.id)
        elif isinstance(self.id, bytes):
            display_id = str(uuid.UUID(bytes=self.id))
        else:
            display_id = str(self.id)
        return f"{self.client.company_name} - {self.client.name} (N°{display_id})"


class Event(BASE):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    contract_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey(Contract.id), type_=BINARY(16), unique=True
    )
    contract: Mapped["Contract"] = relationship(back_populates="event")
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    related_user_id: Mapped[int] = mapped_column(ForeignKey(User.id), nullable=True)
    support_contact: Mapped["User"] = relationship(back_populates="events")
    location: Mapped[str] = mapped_column(String(100), nullable=False)
    attendees: Mapped[int] = mapped_column(Integer, nullable=False)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, onupdate=func.now()
    )

    def __repr__(self):
        return f"<Event(id={self.id}, name='{self.name}')>"

    def __str__(self):
        return f"({self.contract.client.name} - {self.contract.client.company_name}) {self.name}"
