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
        if not req.plan_req:
            raise HTTPException(status_code=400, detail="plan_req is required")

        # === Chuẩn bị user_request ===
        user_request = req.prompt
        if req.current_plan:
            current_plan_json = req.current_plan.json()
            user_request = (
                f"Cập nhật kế hoạch hiện tại theo nội dung sau:\n{req.prompt}\n\n"
                f"Kế hoạch hiện tại:\n{current_plan_json}"
            )

        # === Gọi RAGServiceStrict để tạo plan mới ===
        updated_plan: PlanOutput = rag_service.generate_trip_plan(
            departure=req.plan_req.departure,
            destination=req.plan_req.destination,
            travelers=req.plan_req.travelers,
            days=req.plan_req.days,
            budget=req.plan_req.budget,
            preferences=[
                user_request,
                *(req.plan_req.preferences or []),
            ],
            start_date=req.plan_req.start_date,
        )

        # === Tạo chat summary từ plan + extra_info ===
        chat_text = f"📝 **Kế hoạch đã được cập nhật:**\n\n"
        chat_text += f"📅 Tổng số ngày: {len(updated_plan.itinerary)}\n"
        chat_text += f"💰 Tổng chi phí ước tính: {updated_plan.estimate.total:,} VNĐ\n"
        chat_text += f"💡 Số tips gợi ý: {len(updated_plan.tips or [])}\n\n"
        chat_text += "**Chi tiết từng ngày:**\n"

        for day in updated_plan.itinerary:
            chat_text += f"- Ngày {day.day}: {len(day.items)} hoạt động\n"
            for item in day.items:
                chat_text += f"    • {item.time} - {item.name} ({item.type})\n"

        if updated_plan.tips:
            chat_text += "\n**Tips hữu ích:**\n"
            for tip in updated_plan.tips:
                chat_text += f"• {tip}\n"

        # === Thêm thông tin extra_info (nếu có) ===
        if updated_plan.extra_info:
            if updated_plan.extra_info.changes:
                chat_text += "\n**Các địa điểm thay đổi/được thêm:**\n"
                for c in updated_plan.extra_info.changes:
                    chat_text += f"• {c}\n"

            if updated_plan.extra_info.best_time_to_visit:
                chat_text += "\n**Thời gian tham quan gợi ý:**\n"
                for place, time in updated_plan.extra_info.best_time_to_visit.items():
                    chat_text += f"• {place}: {time}\n"

            if updated_plan.extra_info.tickets:
                chat_text += "\n**Chi phí vé tham quan:**\n"
                for place, cost in updated_plan.extra_info.tickets.items():
                    chat_text += f"• {place}: {cost:,} VNĐ\n"

        return {
            "plan": updated_plan.dict(),
            "extra": chat_text,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
