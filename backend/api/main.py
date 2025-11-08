from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers.plan_router import router as plan_router

app = FastAPI(title="Welcome")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(plan_router, prefix="/api", tags=["Plan"])

@app.get("/")
def root():
    return {"message": "Server is running 🚀"}
