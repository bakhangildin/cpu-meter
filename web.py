import logging
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.requests import Request
import psutil

from db import Database

app = FastAPI()


@app.get("/get-cpu-load")
def get_cpu_load():
    load = psutil.cpu_percent(0.5)
    return {"cpu_load": load}


@app.get("/")
def file():
    return FileResponse("index.html")


@app.get("/{filename}")
def file(filename: str):
    return FileResponse(filename)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("web:app", host="127.0.0.1", port=8000, reload=True)
