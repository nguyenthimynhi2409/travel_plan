import axios from "axios";

export const createPlan = async (data: any) => {
  const res = await axios.post(`http://localhost:8000/api/create-plan`, data);
  return res.data;
};

export const updatePlan = async (prompt: any, current_plan: any, plan_req: any) => {
  const res = await axios.post(`http://localhost:8000/api/update-plan`, {
    prompt: prompt,
    current_plan: current_plan,
    plan_req: plan_req
  });
  return res.data;
};
