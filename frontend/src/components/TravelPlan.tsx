import { FC, useEffect, useRef, useState } from "react";
import { updatePlan } from "../api/planApi";

interface EstCost {
  accommodation: number;
  transportation: number;
  activity: number;
}

interface Item {
  time: string;
  name: string;
  type: string;
  description: string;
  est_cost: EstCost;
}

interface DayPlan {
  day: number;
  date: string;
  items: Item[];
}

interface Estimate {
  accommodation: number;
  transportation: number;
  activity: number;
  total: number;
}

interface TravelPlanProps {
  itinerary: DayPlan[];
  estimate: Estimate;
  plan_req: any;
}

const typeColors: Record<string, string> = {
  Accommodation: "bg-blue-200 text-blue-800",
  Activity: "bg-green-200 text-green-800",
  Transportation: "bg-yellow-200 text-yellow-800",
};

export const TravelPlan: FC<TravelPlanProps> = ({ itinerary, estimate, plan_req }) => {
  const prevData: any = useRef(undefined);
  const [prompt, setPrompt] = useState("");
  const [plan, setPlan] = useState(itinerary);
  const [totalEstimate, setTotalEstimate] = useState(estimate);
  const [loading, setLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState<{ user: string; bot: string }[]>([]);

  const handleUpdatePlan = async () => {
    if (!prompt.trim()) return;

    setLoading(true);
    setChatHistory((prev) => [...prev, { user: prompt, bot: "Đang xử lý..." }]);

    try {
      const data = await updatePlan(prompt, prevData.current, plan_req);
      if (data.itinerary && data.estimate) {
        setPlan(data.itinerary);
        setTotalEstimate(data.estimate);
        setChatHistory((prev) => {
          const newHistory = [...prev];
          newHistory[newHistory.length - 1].bot = "Cập nhật kế hoạch thành công!";
          return newHistory;
        });
      } else {
        setChatHistory((prev) => {
          const newHistory = [...prev];
          newHistory[newHistory.length - 1].bot = "Không có dữ liệu trả về.";
          return newHistory;
        });
      }

      setPrompt("");
    } catch (err) {
      console.error("Update plan failed:", err);
      setChatHistory((prev) => {
        const newHistory = [...prev];
        newHistory[newHistory.length - 1].bot = "Cập nhật thất bại!";
        return newHistory;
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    prevData.current = {
      itinerary,
      estimate,
    };
  }, [itinerary, estimate]);

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 h-[90vh]">
        {/* Chatbot */}
        <div className="flex flex-col bg-white rounded-xl shadow-md p-6 overflow-y-auto">
          <h2 className="text-xl font-semibold mb-4">Chatbot cập nhật kế hoạch</h2>
          <div className="flex-1 space-y-4 overflow-y-auto">
            {chatHistory.map((msg, idx) => (
              <div key={idx}>
                <p className="text-right text-gray-700 mt-2">
                  <span className="bg-blue-100 px-3 py-1 rounded-lg inline-block">
                    {msg.user}
                  </span>
                </p>
                <p className="text-left text-gray-700 mt-2">
                  <span className="bg-green-100 px-3 py-1 rounded-lg inline-block">
                    {msg.bot}
                  </span>
                </p>
              </div>
            ))}
          </div>
          <div className="mt-4 flex space-x-2">
            <textarea
              className="flex-1 border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-400"
              rows={2}
              placeholder="Nhập prompt..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
            />
            <button
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition disabled:opacity-50"
              onClick={handleUpdatePlan}
              disabled={loading}
            >
              {loading ? "Đang cập nhật..." : "Gửi"}
            </button>
          </div>
        </div>

        {/* Travel plan */}
        <div className="flex flex-col overflow-y-auto space-y-6">
          {plan.map((day) => (
            <div key={day.day} className="bg-white rounded-xl shadow-md p-6">
              <h2 className="text-2xl font-semibold mb-6">
                Ngày {day.day} - {new Date(day.date).toLocaleDateString("vi-VN")}
              </h2>
              <div className="relative border-l-2 border-gray-300 pl-6 space-y-6">
                {day.items.map((item, idx) => (
                  <div
                    key={idx}
                    className="relative flex flex-col md:flex-row md:justify-between items-start md:items-center"
                  >
                    <span className="absolute -left-3 top-1 w-5 h-5 rounded-full bg-blue-500 border-2 border-white shadow-md"></span>
                    <div className="flex-1">
                      <div className="flex items-center space-x-4">
                        <span className="font-mono text-gray-500 w-20">{item.time}</span>
                        <div>
                          <h3 className="text-lg font-medium">{item.name}</h3>
                          <p className="text-gray-600 text-sm">{item.description}</p>
                        </div>
                      </div>
                    </div>
                    <div className="mt-2 md:mt-0 flex items-center space-x-3">
                      <span
                        className={`px-3 py-1 rounded-full text-sm font-semibold ${
                          typeColors[item.type]
                        }`}
                      >
                        {item.type}
                      </span>
                      <span className="text-sm text-gray-700">
                        {(
                          item.est_cost.accommodation +
                          item.est_cost.transportation +
                          item.est_cost.activity
                        ).toLocaleString()}{" "}
                        VND
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}

          {/* Tổng chi phí */}
          <div className="bg-white rounded-xl shadow-md p-6">
            <h2 className="text-2xl font-semibold mb-4">Tổng chi phí ước tính</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-gray-700">
              <div className="p-4 bg-blue-50 rounded-lg text-center">
                <p>Khách sạn</p>
                <p className="font-bold">{totalEstimate.accommodation.toLocaleString()} VND</p>
              </div>
              <div className="p-4 bg-yellow-50 rounded-lg text-center">
                <p>Di chuyển</p>
                <p className="font-bold">{totalEstimate.transportation.toLocaleString()} VND</p>
              </div>
              <div className="p-4 bg-green-50 rounded-lg text-center">
                <p>Hoạt động</p>
                <p className="font-bold">{totalEstimate.activity.toLocaleString()} VND</p>
              </div>
              <div className="p-4 bg-purple-50 rounded-lg text-center">
                <p>Tổng cộng</p>
                <p className="font-bold">{totalEstimate.total.toLocaleString()} VND</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
