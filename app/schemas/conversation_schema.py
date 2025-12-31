from pydantic import BaseModel, UUID4, ConfigDict


class ConversationRead(BaseModel):
    id: UUID4
    user1_id: UUID4
    user2_id: UUID4

    model_config = ConfigDict(from_attributes=True)
