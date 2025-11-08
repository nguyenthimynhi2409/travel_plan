import React from "react";
import { useLocation } from "react-router-dom";
import { TravelPlan } from "../components/TravelPlan";

const Result: React.FC = () => {
  const location = useLocation();
  const { planData, plan_req } = location.state as { planData: any, plan_req: any };

  if (!planData) return <div className="p-6">Không có dữ liệu lịch trình.</div>;

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <h1 className="text-3xl font-bold mb-6 text-center">
        Travel Plan
      </h1>
      <TravelPlan itinerary={planData.itinerary} estimate={planData.estimate} plan_req={plan_req} />
    </div>
  );
};

export default Result;
