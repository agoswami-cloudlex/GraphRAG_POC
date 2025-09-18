
from datetime import datetime, timezone
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class User(SQLModel, table=True):
	id: Optional[int] = Field(default=None, primary_key=True)
	username: str = Field(index=True, unique=True)
	password_hash: str

	# Relationships
	cases: List["Case"] = Relationship(back_populates="owner")
	documents: List["Document"] = Relationship(back_populates="owner")


class Case(SQLModel, table=True):
	id: str = Field(primary_key=True)
	owner_user_id: int = Field(index=True, foreign_key="user.id")
	name: str
	assigned_lawyer: Optional[str] = Field(default=None)
	plaintiff: Optional[str] = Field(default=None)
	created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

	# Relationships
	owner: Optional[User] = Relationship(back_populates="cases")
	documents: List["Document"] = Relationship(back_populates="case")


class Document(SQLModel, table=True):
	id: str = Field(primary_key=True)
	owner_user_id: int = Field(index=True, foreign_key="user.id")
	case_id: str = Field(index=True, foreign_key="case.id")
	filename: str
	uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

	# Relationships
	owner: Optional[User] = Relationship(back_populates="documents")
	case: Optional[Case] = Relationship(back_populates="documents")


# Chat session and message models
class ChatSession(SQLModel, table=True):
	id: Optional[int] = Field(default=None, primary_key=True)
	user_id: int = Field(index=True, foreign_key="user.id")
	created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
	last_active: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

	# Relationships
	user: Optional[User] = Relationship()
	messages: List["ChatMessage"] = Relationship(back_populates="session")


class ChatMessage(SQLModel, table=True):
	id: Optional[int] = Field(default=None, primary_key=True)
	session_id: int = Field(index=True, foreign_key="chatsession.id")
	user_id: int = Field(index=True, foreign_key="user.id")
	role: str = Field(index=True)  # 'user' or 'assistant'
	content: str
	timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

	# Relationships
	session: Optional[ChatSession] = Relationship(back_populates="messages")
