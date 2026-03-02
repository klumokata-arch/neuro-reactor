from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import subprocess
import uuid
import os
import requests

app = FastAPI()

class VideoRequest(BaseModel):
    video_url: str
    audio_url: str

@app.get("/")
def health_check():
    return {"status": "ok"}

@app.post("/process")
def process_video(data: VideoRequest):
    video_filename = f"/tmp/video_{uuid.uuid4()}.mp4"
    audio_filename = f"/tmp/audio_{uuid.uuid4()}.mp3"
    output_filename = f"/tmp/output_{uuid.uuid4()}.mp4"

    try:
        # Download video
        video_response = requests.get(data.video_url, timeout=60)
        video_response.raise_for_status()
        with open(video_filename, "wb") as f:
            f.write(video_response.content)

        # Download audio
        audio_response = requests.get(data.audio_url, timeout=60)
        audio_response.raise_for_status()
        with open(audio_filename, "wb") as f:
            f.write(audio_response.content)

        # Merge using ffmpeg
        cmd = [
            "ffmpeg", "-y",
            "-i", video_filename,
            "-i", audio_filename,
            "-shortest",
            "-c:v", "copy",
            "-c:a", "aac",
            output_filename
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=f"FFmpeg error: {result.stderr}")

        return FileResponse(
            output_filename,
            media_type="video/mp4",
            filename="output.mp4"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        for f in [video_filename, audio_filename]:
            if os.path.exists(f):
                os.remove(f)
