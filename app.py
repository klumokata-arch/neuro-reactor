from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import FileResponse
import numpy as np
from scipy.io.wavfile import write
from moviepy.editor import VideoFileClip, AudioFileClip
import uuid
import os

app = FastAPI()

@app.post("/process")
async def process(video: UploadFile, prompt: str = Form(...)):

    # === 1. Зберігаємо відео ===
    video_filename = f"input_{uuid.uuid4()}.mp4"
    with open(video_filename, "wb") as f:
        f.write(await video.read())

    # === 2. Генеруємо динамічний звук ===
    duration = 10  # секунд
    sample_rate = 44100

    t = np.linspace(0, duration, sample_rate * duration)

    # створюємо дивний "космічний" звук
    base_freq = np.random.uniform(50, 200)
    mod_freq = np.random.uniform(0.1, 1.0)

    signal = 0.5 * np.sin(2 * np.pi * base_freq * t + 5*np.sin(2*np.pi*mod_freq*t))

    audio_filename = f"audio_{uuid.uuid4()}.wav"
    write(audio_filename, sample_rate, signal.astype(np.float32))

    # === 3. Накладаємо звук на відео ===
    video_clip = VideoFileClip(video_filename)
    audio_clip = AudioFileClip(audio_filename)

    final_video = video_clip.set_audio(audio_clip)

    output_filename = f"output_{uuid.uuid4()}.mp4"
    final_video.write_videofile(output_filename, codec="libx264", audio_codec="aac")

    # очищення тимчасових файлів
    os.remove(video_filename)
    os.remove(audio_filename)

    return FileResponse(output_filename, media_type="video/mp4")
