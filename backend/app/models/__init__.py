from enum import Enum
from datetime import datetime
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

def now_utc():
    return datetime.now(timezone.utc)

class AgeGroup(str, Enum):
    AGE_18_25 = "18-25"
    AGE_26_40 = "26-40"
    AGE_41_60 = "41-60"
    AGE_60_PLUS = "60+"


def now_utc() -> datetime:
    return datetime.utcnow()


UserDocument = Dict[str, Any]
IssueDocument = Dict[str, Any]
IssueVoteDocument = Dict[str, Any]
PoliticianDocument = Dict[str, Any]
ElectionVoteDocument = Dict[str, Any]
CaseDocument = Dict[str, Any]
CaseMetricDocument = Dict[str, Any]

