from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import yt_dlp
import os

app = FastAPI()

class VideoURL(BaseModel):
    url: str

def get_downloads_path():
    downloads_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
    if not os.path.exists(downloads_path):
        os.makedirs(downloads_path)
    return downloads_path

@app.post("/download/")
async def download_video(video: VideoURL):
    if not video.url.strip():
        raise HTTPException(status_code=400, detail="URL boş olamaz!")
    
    save_path = get_downloads_path()
    
    try:
        ydl_opts = {
            'outtmpl': f'{save_path}/%(title)s.%(ext)s',
            'format': 'best',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video.url, download=True)
            video_title = info.get('title', None)
            file_path = ydl.prepare_filename(info)  # İndirilen dosyanın tam yolu
        
        # Dosya doğrudan istemciye gönderilir
        return FileResponse(
            path=file_path,
            filename=os.path.basename(file_path),
            media_type='video/mp4'
        )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"İndirme hatası: {str(e)}")

@app.get("/")
async def root():
    return {"mesaj": "Video İndirme API'sine Hoş Geldiniz"}
