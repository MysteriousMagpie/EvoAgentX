from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.run import router as run_router
from .api.events import router as events_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"] ,
    allow_headers=["*"] ,
)

app.include_router(run_router)
app.include_router(events_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server.main:app", host="0.0.0.0", port=8000, reload=True)
