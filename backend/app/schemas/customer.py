from pydantic import BaseModel, Field


class CustomerCreate(BaseModel):
    code: str
    name: str
    active: bool = True


class CustomerUpdate(BaseModel):
    name: str | None = None
    active: bool | None = None
    version: int = Field(ge=1)


class CustomerResponse(BaseModel):
    id: int
    code: str
    name: str
    active: bool
    version: int
