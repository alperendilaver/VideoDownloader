from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import yt_dlp
import os

app = FastAPI()

class DownloadRequest(BaseModel):
    url: str
    format: str = "mp4"  # mp4 veya mp3

def get_downloads_path():
    downloads_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
    if not os.path.exists(downloads_path):
        os.makedirs(downloads_path)
    return downloads_path

@app.post("/download/")
async def download_media(req: DownloadRequest):
    if not req.url.strip():
        raise HTTPException(status_code=400, detail="URL boş olamaz!")

    save_path = get_downloads_path()

    try:
        if req.format == "mp3":
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': f'{save_path}/%(title)s.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '0',  # En yüksek kaliteyi seçer
                }],
                'quiet': True,
            }
        elif req.format == "mp4":
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',
                'outtmpl': f'{save_path}/%(title)s.%(ext)s',
                'merge_output_format': 'mp4',
                'quiet': True,
            }
        else:
            raise HTTPException(status_code=400, detail="Geçersiz format seçimi. mp3 veya mp4 olmalı.")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(req.url, download=True)
            file_path = ydl.prepare_filename(info)

        if req.format == "mp3":
            file_path = os.path.splitext(file_path)[0] + ".mp3"

        return FileResponse(
            path=file_path,
            filename=os.path.basename(file_path),
            media_type='audio/mpeg' if req.format == "mp3" else 'video/mp4'
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"İndirme hatası: {str(e)}")

@app.get("/")
async def root():
    return {"mesaj": "Video/Müzik İndirme API'sine Hoş Geldiniz 🎵🎬"}
