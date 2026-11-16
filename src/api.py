from fastapi import FastAPI

app = FastAPI(title="Late-Delivery Early-Warning System")

@app.get("/health")
def health():
    return {"status": "ok"}