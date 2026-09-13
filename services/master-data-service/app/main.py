from fastapi import FastAPI

app = FastAPI(
    title="JanSwasthya Connect - Master Data Service",
    version="0.1.0"
)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "master-data-service"
    }
