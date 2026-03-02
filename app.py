from fastapi import FastAPI
from pydantic import BaseModel
import subprocess
import uuid
import os
import requests

app = FastAPI()

class VideoRequest(BaseModel):
    video_url: str
    audio_url: str

@app.post("/process")
def process_video(data: VideoRequest):

    video_filename = f"video_{uuid.uuid4()}.mp4"
    audio_filename = f"audio_{uuid.uuid4()}.wav"
    output_filename = f"output_{uuid.uuid4()}.mp4"

    # Download video
    video_response = requests.get(data.video_url)
    with open(video_filename, "wb") as f:
        f.write(video_response.content)

    # Download audio
    audio_response = requests.get(data.audio_url)
    with open(audio_filename, "wb") as f:
        f.write(audio_response.content)

    # Merge using ffmpeg
    cmd = [
        "ffmpeg",
        "-y",
        "-i", video_filename,
        "-i", audio_filename,
        "-shortest",
        "-c:v", "copy",
        "-c:a", "aac",
        output_filename
    ]

    subprocess.run(cmd)

    return {"output_file": output_filename}
