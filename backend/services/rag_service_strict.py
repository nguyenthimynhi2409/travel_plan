import os
import json
import re
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, ValidationError

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Pinecone as LangPinecone
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser

from pinecone import Pinecone, ServerlessSpec
from utils import config

try:
    from services.places_service import get_places_nearby
except Exception:
    from services.places_service import get_places_nearby


# === Schema Models ===
class Item(BaseModel):
    time: str
    name: str
    type: str
    description: Optional[str] = None
    est_cost: Optional[Dict[str, int]] = Field(
        default_factory=lambda: {"accommodation": 0, "transportation": 0, "activity": 0}
    )


class Day(BaseModel):
    day: int
    date: Optional[str]
    items: List[Item]


class Estimate(BaseModel):
    accommodation: int
    transportation: int
    activity: int
    total: Optional[int]


class ExtraInfo(BaseModel):
    changes: Optional[List[str]] = Field(default_factory=list)
    best_time_to_visit: Optional[Dict[str, str]] = Field(default_factory=dict)
    tickets: Optional[Dict[str, int]] = Field(default_factory=dict)


class PlanOutput(BaseModel):
    itinerary: List[Day]
    tips: Optional[List[str]] = Field(default_factory=list)
    estimate: Estimate
    extra_info: Optional[ExtraInfo] = None  # thêm phần này


# === RAG Service Strict (Vietnamese Version) ===
class RAGServiceStrict:
    def __init__(self):
        OPENAI_API_KEY_1 = config.OPENAI_API_KEY_1
        OPENAI_BASE_URL = getattr(
            config, "OPENAI_BASE_URL", "https://api.openai.com/v1"
        )
        PINECONE_API_KEY = config.PINECONE_API_KEY
        PINECONE_ENV = config.PINECONE_ENVIRONMENT
        PINECONE_INDEX = config.PINECONE_INDEX_NAME
        MODEL = config.OPENAI_MODEL or "gpt-4o-mini"

        if not OPENAI_API_KEY_1 or not PINECONE_API_KEY:
            raise ValueError("OPENAI_API_KEY_1 và PINECONE_API_KEY là bắt buộc")

        # === Pinecone setup ===
        try:
            self.pc = Pinecone(api_key=PINECONE_API_KEY)
            existing_indexes = [idx["name"] for idx in self.pc.list_indexes()]
            if PINECONE_INDEX not in existing_indexes:
                self.pc.create_index(
                    name=PINECONE_INDEX,
                    dimension=1536,
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region="us-east-1"),
                )
            self.index = self.pc.Index(PINECONE_INDEX)
        except Exception as e:
            print(f"[WARN] Pinecone init failed: {e}")
            self.index = None

        # === LLM setup ===
        self.llm = ChatOpenAI(
            temperature=0.25,
            model=MODEL,
            api_key=OPENAI_API_KEY_1,
            base_url=OPENAI_BASE_URL,
        )

        # === Vectorstore ===
        try:
            embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
            self.vectorstore = LangPinecone(
                index=self.index, embedding=embeddings, text_key="content"
            )
        except Exception as e:
            print(f"[WARN] Vectorstore not initialized: {e}")
            self.vectorstore = None

        # === Output Parser & Prompt ===
        self.parser = PydanticOutputParser(pydantic_object=PlanOutput)

        # 🧭 Prompt tiếng Việt: có cả di chuyển, khách sạn, hoạt động
        template = (
            "Bạn là TravelPlannerGPT — một trợ lý chuyên gia lập kế hoạch du lịch.\n\n"
            "Nhiệm vụ của bạn: tạo kế hoạch chi tiết cho chuyến đi, bao gồm khách sạn, phương tiện di chuyển và hoạt động vui chơi.\n\n"
            "Yêu cầu:\n"
            "- Phải trả về JSON **đúng theo schema PlanOutput**.\n"
            "- Mỗi hoạt động (item) cần có `time`, `name`, `type`, `description`, và `est_cost`.\n"
            "- `est_cost` luôn là dictionary có đủ 3 khóa: accommodation, transportation, activity.\n"
            "- Mô tả rõ ràng, logic về thời gian và chi phí thực tế.\n"
            "- Ưu tiên gợi ý hợp lý theo sở thích và ngân sách.\n\n"
            "Thông tin người dùng:\n{user_request}\n\n"
            "Dữ liệu tham khảo (địa điểm, khách sạn, di chuyển, tài liệu hướng dẫn):\n{support}\n\n"
            "Cấu trúc schema:\n{output_schema}\n\n"
            "Trả về đúng JSON, không thêm lời nói hay văn bản khác."
        )

        self.prompt = PromptTemplate(
            input_variables=["user_request", "support", "output_schema"],
            template=template,
        )

        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)

    # === Extract JSON safely ===
    def _safe_extract_json(self, text: str) -> str:
        match = re.search(r"(\{[\s\S]*\})", text)
        if match:
            return match.group(1)
        alt = re.search(r"(\[[\s\S]*\])", text)
        if alt:
            return alt.group(1)
        raise ValueError("Không tìm thấy JSON hợp lệ trong đầu ra của mô hình")

    # === Generate Trip Plan ===
    def generate_trip_plan(
        self,
        departure: str,
        destination: str,
        travelers: int = 1,
        days: int = 3,
        budget: int = 1000,
        preferences: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        current_plan: Optional[PlanOutput] = None,  # nếu muốn so sánh
    ) -> PlanOutput:

        preferences = preferences or []
        pref_str = ", ".join(preferences) if preferences else "tổng hợp"

        user_request = (
            f"Lên kế hoạch {days} ngày cho {travelers} người từ {departure} đến {destination}. "
            f"Ngân sách: {budget} VN. Sở thích: {pref_str}. "
            f"Ngày khởi hành: {start_date or 'chưa xác định'}.\n"
            "Bao gồm chi tiết chi phí từng hoạt động, phương tiện di chuyển và nơi ở."
        )

        # === RapidAPI: lấy dữ liệu từ các dịch vụ phụ trợ ===
        try:
            attractions = get_places_nearby(
                destination, category="tourist_attraction", limit=10
            )
            hotels = get_places_nearby(destination, category="lodging", limit=5)
            transports = get_places_nearby(
                destination, category="transportation", limit=5
            )
        except Exception as e:
            print(f"[WARN] Lỗi khi lấy dữ liệu RapidAPI: {e}")
            attractions, hotels, transports = [], [], []

        support_text = (
            f"🏞️ Địa điểm tham quan:\n{json.dumps(attractions, ensure_ascii=False)}\n\n"
            f"🏨 Khách sạn gợi ý:\n{json.dumps(hotels, ensure_ascii=False)}\n\n"
            f"🚗 Phương tiện di chuyển:\n{json.dumps(transports, ensure_ascii=False)}"
        )

        # === Pinecone retrieval ===
        try:
            retriever = self.vectorstore.as_retriever(search_kwargs={"k": 5})
            docs = retriever.get_relevant_documents(
                f"Hướng dẫn du lịch cho {destination}"
            )
            docs_text = "\n---\n".join(d.page_content for d in docs)[:4000]
        except Exception as e:
            print(f"[WARN] Pinecone retrieval failed: {e}")
            docs_text = ""

        full_support = f"{support_text}\n\n📘 Dữ liệu từ Pinecone:\n{docs_text}"

        schema_instructions = self.parser.get_format_instructions()
        prompt_inputs = {
            "user_request": user_request,
            "support": full_support,
            "output_schema": schema_instructions,
        }

        raw_output = self.chain.run(prompt_inputs)

        # === Parse kết quả ===
        try:
            parsed = self.parser.parse(raw_output)
        except ValidationError:
            json_str = self._safe_extract_json(raw_output)
            data = json.loads(json_str)

            # 🔧 Fix nếu est_cost không đúng định dạng
            for day in data.get("itinerary", []):
                for item in day.get("items", []):
                    est = item.get("est_cost", {})
                    if isinstance(est, int):
                        item["est_cost"] = {
                            "activity": est,
                            "accommodation": 0,
                            "transportation": 0,
                        }
                    else:
                        for key in ["activity", "accommodation", "transportation"]:
                            est.setdefault(key, 0)

            parsed = PlanOutput.parse_obj(data)

        # === Auto-fill estimate nếu thiếu ===
        if not parsed.estimate.total or parsed.estimate.total == 0:
            parsed.estimate.total = (
                parsed.estimate.activity
                + parsed.estimate.accommodation
                + parsed.estimate.transportation
            )

        # === Tạo extra_info ===
        extra_info = ExtraInfo()

        # Thêm các địa điểm mới/thay đổi
        if current_plan:
            old_places = {item.name for day in current_plan.itinerary for item in day.items}
            new_places = {item.name for day in parsed.itinerary for item in day.items}
            extra_info.changes = list(new_places - old_places)

        # Thêm best_time_to_visit (giả lập gợi ý)
        for day in parsed.itinerary:
            for item in day.items:
                extra_info.best_time_to_visit[item.name] = item.time

        # Thêm tickets (giả lập dựa trên activity cost)
        for day in parsed.itinerary:
            for item in day.items:
                extra_info.tickets[item.name] = item.est_cost.get("activity", 0)

        parsed.extra_info = extra_info

        return parsed
