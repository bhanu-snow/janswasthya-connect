from fastapi import FastAPI

from app.api import router


app = FastAPI(
    title="JanSwasthya Analytics Service",
    version="1.0.0",
)

app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok"}