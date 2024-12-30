import os
import shutil
from flask import json
import instaloader
from moviepy.editor import VideoFileClip
import whisper
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload
import os

# Google Drive için ayarlar
FILE = os.getenv("FILE")
SCOPES = ['https://www.googleapis.com/auth/drive']
PARENT_FOLDER_ID = os.getenv("PARENT_FOLDER_ID")

class ReelsTranscript:
    def authenticate(self):
        # JSON içeriğini FILE değişkeninden al
        service_account_info = json.loads(os.getenv("FILE"))  # Ortam değişkeninden JSON içeriği okunuyor

        # JSON içeriğini kullanarak kimlik bilgilerini oluştur
        creds = service_account.Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
        return creds

    def upload_file(self, file_path, file_name):
        creds = self.authenticate()
        service = build('drive', 'v3', credentials=creds)

        file_metadata = {
            'name': file_name,
            'parents': [PARENT_FOLDER_ID]
        }

        media_body = MediaFileUpload(file_path, mimetype="video/mp4" if file_path.endswith('.mp4') else "audio/wav")
        
        file = service.files().create(
            body=file_metadata,
            media_body=media_body
        ).execute()
        
        return file['id']

    def delete_file(self, file_id):
        creds = self.authenticate()
        service = build('drive', 'v3', credentials=creds)

        service.files().delete(fileId=file_id).execute()
        print(f"File with ID {file_id} deleted successfully.")

    def download_instagram_reel(self, reel_url, download_path):
        loader = instaloader.Instaloader()
        loader.download_post(instaloader.Post.from_shortcode(loader.context, reel_url.split('/')[-2]), target=download_path)
        for file in os.listdir(download_path):
            if file.endswith('.mp4'):
                return os.path.join(download_path, file)
        return None
    
    def extract_audio_from_video(self, video_path, audio_path):
        video = VideoFileClip(video_path)
        video.audio.write_audiofile(audio_path)
        
    def transcribe_audio(self, audio_path):
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        return result['text']
    
    def get(self, reel_url):
        download_path = 'downloads'
        audio_path = 'audio.wav'
        os.makedirs(download_path, exist_ok=True)
        video_path = self.download_instagram_reel(reel_url, download_path)
        if not video_path:
            print("Failed to download the Instagram Reel.")
            return

        # Yükleme ve ses dosyasını oluşturma
        video_file_id = self.upload_file(video_path, "reel_video.mp4")
        self.extract_audio_from_video(video_path, audio_path)
        audio_file_id = self.upload_file(audio_path, "audio.wav")

        # Transkript alma
        transcript = self.transcribe_audio(audio_path)
        
        # Dosyaları silme
        self.delete_file(video_file_id)
        self.delete_file(audio_file_id)

        # Silme: Dosyaları yerel sistemden kaldırıyoruz.
        os.remove(video_path)  # Sil video dosyasını
        os.remove(audio_path)  # Sil ses dosyasını
        print(f"Local files {video_path} and {audio_path} deleted successfully.")
        
        shutil.rmtree(download_path)
        print(f"Directory {download_path} deleted successfully.")

        return transcript
