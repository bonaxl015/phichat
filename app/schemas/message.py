from pydantic import BaseModel, ConfigDict, UUID4
from app.models.message import MessageStatus
from datetime import datetime

class MessageRead(BaseModel):
    id: UUID4
    conversation_id: UUID4
    sender_id: UUID4
    receiver_id: UUID4
    content: str
    status: MessageStatus
    sent_at: datetime
    delivered_at: datetime | None
    read_at: datetime | None

    model_config = ConfigDict(from_attributes=True)

class MessageCreate(BaseModel):
    content: str
