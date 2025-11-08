from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class Item(BaseModel):
    time: str
    name: str
    type: str
    description: Optional[str] = None
    est_cost: Optional[Dict[str, int]] = Field(default_factory=dict)

class Day(BaseModel):
    day: int
    date: Optional[str]
    items: List[Item]

class Estimate(BaseModel):
    accommodation: int
    transportation: int
    activity: int
    total: Optional[int]

class PlanOutput(BaseModel):
    itinerary: List[Day]
    tips: Optional[List[str]] = []
    estimate: Estimate
