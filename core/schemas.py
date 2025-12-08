from typing import Optional, List
from pydantic import BaseModel, Field

class ClientSchema(BaseModel):
    """Schema for the client object returned by /clients."""
    id: int = Field(description="The internal ID of the client.")
    name: str = Field(description="The human-readable name of the client.")
    comment: Optional[str] = Field(None, description="A comment/description for the client.")
    client: str = Field(description="The client's IP address or hostname.")
    groups: List[int] = Field(description="List of group IDs the client belongs to.")
        
class GroupSchema(BaseModel):
    """Schema for the group object returned by /groups."""
    id: int
    name: str
    comment: Optional[str] = None
    enabled: int = Field(description="1 for enabled, 0 for disabled.")

class EditClientRequest(BaseModel):
    """Schema for the request body of the /editclient POST endpoint."""
    client: str
    comment: Optional[str] = None
    group: Optional[int] = None
