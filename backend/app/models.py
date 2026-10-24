"""Versioned content and request contracts. Participant DTOs are built explicitly."""
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

MAX_SOURCE_BYTES = 65536
MAX_STDIN_BYTES = 8 * 1024 * 1024
MAX_STDOUT_BYTES = 2 * 1024 * 1024
# An ASCII control character can occupy six bytes (\\uXXXX) in JSON.
MAX_REQUEST_BYTES = 6 * (MAX_SOURCE_BYTES + MAX_STDIN_BYTES) + 65536


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class Limits(StrictModel):
    time_ms: int = Field(default=2000, ge=10, le=5000)
    source_bytes: int = Field(default=65536, ge=1, le=MAX_SOURCE_BYTES)
    stdin_bytes: int = Field(default=1048576, ge=1, le=MAX_STDIN_BYTES)
    stdout_bytes: int = Field(default=1048576, ge=1, le=MAX_STDOUT_BYTES)
    stderr_bytes: int = Field(default=65536, ge=1, le=65536)
    memory_mb: int = Field(default=256, ge=1)


class Checker(StrictModel):
    type: Literal["text"] = "text"
    normalize_line_endings: bool = True
    trim_trailing_whitespace_per_line: bool = True
    ignore_final_newline: bool = True


class Requirement(StrictModel):
    id: str = Field(pattern=r"^[a-z0-9-]+$")
    text: str = Field(min_length=1)


Bound = Annotated[str, Field(min_length=1, max_length=240)]


class ReferenceComplexity(StrictModel):
    variables: dict[str, Bound] = Field(min_length=1, max_length=10)
    time_by_phase: dict[str, Bound] = Field(min_length=1, max_length=10)
    auxiliary_space: Bound
    notes: str = Field(min_length=1, max_length=4000)


class ReviewedComplexity(StrictModel):
    status: Literal["assessed", "unable_to_assess"]
    worst_case_time: Bound | None = None
    auxiliary_space: Bound | None = None
    total_space: Bound | None = None
    reasoning: str = Field(min_length=1, max_length=4000)

    @model_validator(mode="after")
    def valid(self):
        if not self.reasoning.strip():
            raise ValueError("Complexity analysis requires an explanation")
        bounds = (self.worst_case_time, self.auxiliary_space, self.total_space)
        if self.status == "assessed" and any(not value or not value.strip() for value in bounds):
            raise ValueError("An assessed analysis requires all three complexity bounds")
        if self.status == "unable_to_assess" and any(value is not None for value in bounds):
            raise ValueError("Unable to assess must not assert complexity bounds")
        return self


class Rubric(StrictModel):
    version: int = Field(default=1, ge=1)
    weights: dict[str, float] = Field(default_factory=lambda: {
        "correctness": 50, "requirements": 20, "readability": 15, "technical": 15})
    readability: list[str] = Field(default_factory=lambda: [
        "Naming", "Clarity", "Useful explanations and comments", "Ease of handoff"])
    technical: list[str] = Field(default_factory=lambda: [
        "Structure", "State management", "Algorithm and data structures", "Avoiding unnecessary complexity"])

    @model_validator(mode="after")
    def valid(self):
        if set(self.weights) != {"correctness", "requirements", "readability", "technical"}:
            raise ValueError("Rubric must contain the four assessment criteria")
        if any(v < 0 for v in self.weights.values()) or abs(sum(self.weights.values()) - 100) > 1e-8:
            raise ValueError("Rubric weights must total 100")
        if len(self.readability) != 4 or len(self.technical) != 4:
            raise ValueError("Each human rubric has four dimensions")
        return self


class ProblemMetadata(StrictModel):
    schema_version: Literal[1] = 1
    id: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    version: int = Field(ge=1)
    title: str = Field(min_length=1)
    difficulty: Literal["Easy", "Medium", "Hard"]
    tags: list[str]
    status: Literal["draft", "published"] = "draft"
    order: int = 1
    suggested_duration_minutes: int = Field(default=60, ge=1)
    submission_mode: Literal["stdin_stdout"] = "stdin_stdout"
    statement_file: str = "statement.md"
    samples_file: str = "samples.json"
    tests_manifest: str = "tests/manifest.json"
    limits: Limits = Field(default_factory=Limits)
    checker: Checker = Field(default_factory=Checker)
    starters: dict[str, str] = Field(default_factory=dict)
    category_weights: dict[str, float]
    requirements: list[Requirement] = Field(min_length=1)
    rubric: Rubric = Field(default_factory=Rubric)
    reference_complexity: ReferenceComplexity | None = None

    @model_validator(mode="after")
    def valid(self):
        if not self.category_weights or any(v <= 0 for v in self.category_weights.values()):
            raise ValueError("Categories must have positive weights")
        if abs(sum(self.category_weights.values()) - 100) > 1e-8:
            raise ValueError("Category weights must total 100")
        ids = [r.id for r in self.requirements]
        if len(set(ids)) != len(ids):
            raise ValueError("Duplicate requirement IDs")
        return self


class Sample(StrictModel):
    id: str
    input: str
    expected_output: str
    explanation: str
    category: str
    requirements: list[str] = Field(min_length=1)


class HiddenCase(StrictModel):
    id: str
    input_file: str
    output_file: str
    category: str
    requirements: list[str] = Field(min_length=1)


class Manifest(StrictModel):
    cases: list[HiddenCase]


class SubmissionRequest(StrictModel):
    problem_id: str
    problem_version: int = Field(ge=1)
    language: Literal["python", "javascript", "cpp", "java"]
    code: str = Field(min_length=1, max_length=65536)


class RunRequest(SubmissionRequest):
    mode: Literal["samples", "custom"] = "samples"
    stdin: str = Field(default="", max_length=MAX_STDIN_BYTES)


class ReviewRequest(StrictModel):
    readability: list[Annotated[int, Field(strict=True, ge=0, le=4)]] = Field(min_length=4, max_length=4)
    technical: list[Annotated[int, Field(strict=True, ge=0, le=4)]] = Field(min_length=4, max_length=4)
    rationale: str = Field(min_length=1, max_length=4000)
    complexity: ReviewedComplexity | None = None

    @model_validator(mode="after")
    def valid(self):
        if any(type(x) is not int or not 0 <= x <= 4 for x in self.readability + self.technical):
            raise ValueError("Ratings must be integers from 0 to 4")
        if not self.rationale.strip():
            raise ValueError("A review rationale is required")
        return self
