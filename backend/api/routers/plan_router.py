from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from services.rag_service_strict import (
    RAGServiceStrict,
    PlanOutput,
    Day,
    Item,
    Estimate,
)

router = APIRouter()
rag_service = RAGServiceStrict()


# === Request schema cho create-plan (đã có) ===
class PlanRequest(BaseModel):
    departure: str
    destination: str
    travelers: int = 1
    days: int = 3
    budget: int = 1000
    preferences: Optional[List[str]] = None
    start_date: Optional[str] = None


@router.post("/create-plan")
async def create_plan(req: PlanRequest):
    try:
        result = rag_service.generate_trip_plan(
            departure=req.departure,
            destination=req.destination,
            travelers=req.travelers,
            days=req.days,
            budget=req.budget,
            preferences=req.preferences,
            start_date=req.start_date,
        )
        return result.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Request schema cho update-plan ===
class UpdatePlanRequest(BaseModel):
    prompt: str
    current_plan: Optional[PlanOutput] = None
    plan_req: Optional[PlanRequest] = None


@router.post("/update-plan")
async def update_plan(req: UpdatePlanRequest):
    try:
        # Nếu có current_plan, dùng prompt mới kết hợp để tạo plan cập nhật
        if req.current_plan:
            current_plan_json = req.current_plan.json()
            user_request = f"Cập nhật kế hoạch hiện tại theo nội dung sau:\n{req.prompt}\n\nKế hoạch hiện tại:\n{current_plan_json}"

            # Gọi RAGServiceStrict để generate JSON mới dựa trên prompt + plan hiện tại
            updated_plan: PlanOutput = rag_service.generate_trip_plan(
                departure=req.plan_req.departure,
                destination=req.plan_req.destination,
                travelers=req.plan_req.travelers,
                days=req.plan_req.days,
                budget=req.plan_req.budget,
                preferences=[
                    user_request,
                ],  # Đưa prompt + plan hiện tại vào preferences để LLM dùng
            )
            return updated_plan.dict()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
