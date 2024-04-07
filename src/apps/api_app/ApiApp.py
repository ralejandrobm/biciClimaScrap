from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from src.contexts.api.controllers import HealthCheckController

from src.contexts.api.controllers import DynamicPredictorController


class ApiApp:
    def __init__(self):
        self.app = FastAPI()
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self.setup_routes()

    def setup_routes(self):
        self.app.add_api_route(
            "/api/health-check",
            HealthCheckController().execute, 
            methods=["GET"],
        )
      
        self.app.add_api_route(
            "/api/ai/dynamic",
            DynamicPredictorController().execute, 
            methods=["POST"],
        )
      

    def start(self):
        print(f"\n 🚀 init ApiApp")
        uvicorn.run(self.app, host="0.0.0.0", port=8000)
