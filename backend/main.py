from fastapi import FastAPI

app = FastAPI(title="Resource Wise API")


@app.get("/health")
def health():
    return {"status": "ok"}
