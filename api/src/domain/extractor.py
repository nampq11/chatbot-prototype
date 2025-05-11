import json
from pathlib import Path
from typing import List

from pydantic import BaseModel, Field

class BookingCareExtractor(BaseModel):
    id: str = Field(description="Unique indentifier for the domain")
    urls: List[str] = Field(
        description="List of URLs with information about the domain"
    )

    @classmethod
    def from_json(cls, metadata_file: Path) -> List["BookingCareExtractor"]:
        with open(metadata_file, "r") as f:
            data = json.load(f)
        
        return [cls(**item) for item in data]
    

class BookingCareDomain(BaseModel):
    id: str = Field(description="Unique indentifier for the domain")
    name: str = Field(
        description="Name of the domain"
    )
    perspective: str = Field(
        description="Description of the domain's theoretical views about AI"
    )
    style: str = Field(
        description="Description of the domain's talking style"
    )

    def __str__(self) -> str:
        return f"Domain: {self.name}, Perspective: {self.perspective}, Style: {self.style}"