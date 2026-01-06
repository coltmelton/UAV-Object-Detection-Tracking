from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Telemetry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lat: float
    lon: float
    alt_m: float
    yaw_deg: float
    gimbal_pitch_deg: float
    gimbal_yaw_deg: float = 0.0


class MapSession(BaseModel):
    model_config = ConfigDict(extra="forbid")

    active: bool = False
    lat0: float = 0.0
    lon0: float = 0.0
    yaw0_deg: float = 0.0
    size_m: float = 100.0


class FrameMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["frame"] = "frame"
    t_ms: int
    frame_id: int
    jpeg_b64: str
    telemetry: Telemetry
    map_session: MapSession = Field(default_factory=MapSession)


class Track(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    cls: str
    conf: float
    bbox: List[float]
    map_xy_m: Optional[List[float]] = None

    @field_validator("bbox")
    @classmethod
    def _bbox_len(cls, value: List[float]) -> List[float]:
        if len(value) != 4:
            raise ValueError("bbox must have 4 elements [x1, y1, x2, y2]")
        return value


class TracksMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["tracks"] = "tracks"
    t_ms: int
    frame_id: int
    tracks: List[Track] = Field(default_factory=list)
