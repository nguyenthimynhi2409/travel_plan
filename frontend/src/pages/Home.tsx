import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createPlan } from "../api/planApi";
import {
  FaUsers,
  FaUserFriends,
  FaUser,
  FaMoneyBillWave,
} from "react-icons/fa";

const Home: React.FC = () => {
  const navigate = useNavigate();

  // --- State ---
  const [departure, setDeparture] = useState(""); // Điểm đi
  const [destination, setDestination] = useState(""); // Điểm đến
  const [startDate, setStartDate] = useState("");
  const [budget, setBudget] = useState<"low" | "medium" | "high" | null>(null);
  const [companions, setCompanions] = useState<
    "solo" | "couple" | "family" | "friends" | null
  >(null);
  const [companionsCount, setCompanionsCount] = useState<number | null>(null);
  const [days, setDays] = useState(3);
  const [loading, setLoading] = useState(false);

  // --- Companion options ---
  const companionsOptions = [
    { key: "solo", label: "Solo", icon: <FaUser />, count: 1 },
    { key: "couple", label: "Couple", icon: <FaUsers />, count: 2 },
    { key: "family", label: "Family", icon: <FaUsers />, count: 4 },
    { key: "friends", label: "Friends", icon: <FaUserFriends />, count: 3 },
  ];

  // --- Submit handler ---
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (
      !departure ||
      !destination ||
      !startDate ||
      !budget ||
      !companions ||
      !companionsCount
    )
      return;

    setLoading(true);

    const budgetValue =
      budget === "low" ? 3000000 : budget === "medium" ? 10000000 : 20000000;

    const payload = {
      departure,
      destination,
      travelers: companionsCount,
      days,
      budget: budgetValue,
      preferences: [],
      start_date: startDate,
    };

    const res = await createPlan(payload);
    setLoading(false);
    navigate("/result", { state: { planData: res, plan_req: payload } });
  };

  return (
    <div className="min-h-screen bg-blue-50 flex items-center justify-center p-6">
      <div className="w-full max-w-3xl bg-white shadow-2xl rounded-3xl p-10">
        <h1 className="text-4xl font-bold text-center text-blue-600 mb-8">
          Plan Your Trip
        </h1>

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Departure & Destination */}
          <div className="grid md:grid-cols-2 gap-4">
            <input
              type="text"
              placeholder="Điểm đi"
              className="p-4 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-400"
              value={departure}
              onChange={(e) => setDeparture(e.target.value)}
              required
            />
            <input
              type="text"
              placeholder="Điểm đến"
              className="p-4 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-400"
              value={destination}
              onChange={(e) => setDestination(e.target.value)}
              required
            />
          </div>

          {/* Start Date */}
          <div>
            <h2 className="font-semibold text-lg mb-2">Ngày bắt đầu</h2>
            <input
              type="date"
              className="p-4 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-400 w-full"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              required
            />
          </div>

          {/* Budget Selection */}
          <div>
            <h2 className="font-semibold text-lg mb-2">Ngân sách</h2>
            <p className="text-gray-500 mb-4">
              Ngân sách này chỉ được phân bổ riêng cho các hoạt động và việc ăn
              uống
            </p>
            <div className="grid grid-cols-3 gap-4">
              {[
                { key: "low", label: "Low", range: "0 - 5,000,000 VND" },
                {
                  key: "medium",
                  label: "Medium",
                  range: "5,000,000 - 10,000,000 VND",
                },
                { key: "high", label: "High", range: "10,000,000+ VND" },
              ].map((b) => (
                <button
                  key={b.key}
                  type="button"
                  onClick={() => setBudget(b.key as any)}
                  className={`flex flex-col items-center p-4 border rounded-xl transition ${
                    budget === b.key
                      ? "border-blue-600 bg-blue-50"
                      : "border-gray-300"
                  } hover:border-blue-400`}
                >
                  <FaMoneyBillWave className="text-2xl mb-2" />
                  <span className="font-medium">{b.label}</span>
                  <span className="text-gray-500 text-sm">{b.range}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Companions Selection */}
          <div>
            <h2 className="font-semibold text-lg mb-2">Đi du lịch cùng:</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {companionsOptions.map((c) => (
                <div
                  key={c.key}
                  className={`flex flex-col items-center p-4 border rounded-xl transition hover:border-blue-400 ${
                    companions === c.key
                      ? "border-blue-600 bg-blue-50"
                      : "border-gray-300"
                  }`}
                >
                  <button
                    type="button"
                    onClick={() => {
                      setCompanions(c.key as any);
                      setCompanionsCount(c.count); // mặc định
                    }}
                    className="flex flex-col items-center"
                  >
                    <div className="text-2xl mb-2">{c.icon}</div>
                    <span className="font-medium">{c.label}</span>
                    <span className="text-gray-500 text-sm">
                      {c.count} người
                    </span>
                  </button>

                  {companions === c.key && (
                    <input
                      type="number"
                      min={1}
                      value={companionsCount || ""}
                      onChange={(e) =>
                        setCompanionsCount(Number(e.target.value))
                      }
                      className="mt-2 p-2 border rounded w-20 text-center focus:outline-none focus:ring-2 focus:ring-blue-400"
                    />
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Days Picker */}
          <div>
            <h2 className="font-semibold text-lg mb-2">
              Bạn dự định đi du lịch trong bao nhiêu ngày?
            </h2>
            <div className="flex items-center gap-4 mt-2">
              <button
                type="button"
                onClick={() => setDays(Math.max(1, days - 1))}
                className="p-3 border rounded-full hover:bg-gray-100 w-[50px]"
              >
                -
              </button>
              <span className="font-bold text-xl">{days}</span>
              <button
                type="button"
                onClick={() => setDays(days + 1)}
                className="p-3 border rounded-full hover:bg-gray-100 w-[50px]"
              >
                +
              </button>
            </div>
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={loading}
            className={`w-full py-4 rounded-xl font-bold text-white transition-colors ${
              loading
                ? "bg-gray-400 cursor-not-allowed"
                : "bg-blue-600 hover:bg-blue-700"
            }`}
          >
            {loading ? "Đang tạo kế hoạch..." : "Tạo kế hoạch"}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Home;
