from pydantic import BaseModel


class QAMetricsResponse(BaseModel):
    total_ask_runs: int
    failed_ask_runs: int
    avg_latency_ms: float
    feedback_count: int
    avg_rating: float
