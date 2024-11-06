from fastapi import FastAPI, Response
from fastapi.responses import FileResponse
import threading

app = FastAPI()
counter = 0
counter_lock = threading.Lock()

@app.get("/")
async def root():
    return {"message": "tracking your emails!"}

@app.get("/track.png")
async def track():
    global counter
    with counter_lock:
        counter += 1
    # Return the tracking image file
    return FileResponse("track.png", media_type="image/png")

@app.get("/counter")
async def show_counter():
    return {"message": f"Image has been accessed {counter} times."}