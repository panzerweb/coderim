from datetime import datetime
from pydantic import Field, model_validator
from .models import StrictModel


class TeamJoin(StrictModel):
    contest_id: str = Field(min_length=1, max_length=80)
    team_name: str = Field(min_length=1, max_length=120)
    join_code: str = Field(min_length=1, max_length=200)


class OrganizerLogin(StrictModel):
    username: str = Field(min_length=1, max_length=120)
    password: str = Field(min_length=1, max_length=1024)


class ContestEdit(StrictModel):
    name: str = Field(min_length=1, max_length=150)
    starts_at: datetime
    duration_minutes: int = Field(default=210, ge=1, le=10080)
    timezone: str = 'Asia/Manila'

    @model_validator(mode='after')
    def valid(self):
        from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
        if self.starts_at.tzinfo is None:
            raise ValueError('Start time must include a timezone offset')
        try:
            ZoneInfo(self.timezone)
        except ZoneInfoNotFoundError:
            raise ValueError('Unknown IANA timezone')
        if not self.name.strip():
            raise ValueError('Contest name is required')
        return self


class PublishContest(StrictModel):
    problem_ids: list[str] = Field(min_length=1, max_length=30)


class TeamCreate(StrictModel):
    name: str = Field(min_length=1, max_length=120)


class TeamActivity(StrictModel):
    is_active: bool


class Confirmation(StrictModel):
    confirm: bool
