from dataclasses import asdict, dataclass
from enum import Enum
from typing import Protocol


class PointStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    TEMPORARILY_CLOSED = "TEMPORARILY_CLOSED"
    MAINTENANCE = "MAINTENANCE"


@dataclass(frozen=True)
class Point:
    id: str
    name: str
    address: str
    status: PointStatus
    lines: list[str]

    def to_dict(self):
        data = asdict(self)
        data["status"] = self.status.value
        return data


class PointRepository(Protocol):
    def get(self, point_id: str) -> Point | None: ...
    def list(self, limit: int, offset: int) -> tuple[list[Point], int]: ...
