from pydantic import BaseModel, ConfigDict, UUID4
from app.models.friendship import FriendshipStatus


class FriendshipRead(BaseModel):
    id: UUID4
    requester_id: UUID4
    receiver_id: UUID4
    status: FriendshipStatus

    model_config = ConfigDict(from_attributes=True)
