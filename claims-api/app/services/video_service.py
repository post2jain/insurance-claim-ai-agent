import os
import tempfile
from pathlib import Path
from typing import Dict, Any
from openai import OpenAI
from moviepy.editor import VideoFileClip
import magic
from app.config import get_settings

class VideoService:
    def __init__(self):
        self.client = OpenAI(api_key=get_settings().OPENAI_API_KEY)
        self.model_version = "gpt-4-vision-preview"
        self.allowed_mime_types = [
            "video/mp4",
            "video/quicktime",
            "video/x-msvideo",
            "video/x-matroska"
        ]
        self.max_video_size = 100 * 1024 * 1024  # 100MB
        self.max_video_duration = 300  # 5 minutes
        
    def validate_video(self, file_path: str) -> bool:
        """Validate video file type and size"""
        # Check file type
        mime = magic.Magic(mime=True)
        file_type = mime.from_file(file_path)
        if file_type not in self.allowed_mime_types:
            raise ValueError(f"Unsupported video format: {file_type}")
            
        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size > self.max_video_size:
            raise ValueError(f"Video file too large. Maximum size is {self.max_video_size/1024/1024}MB")
            
        # Check video duration
        with VideoFileClip(file_path) as video:
            if video.duration > self.max_video_duration:
                raise ValueError(f"Video too long. Maximum duration is {self.max_video_duration} seconds")
                
        return True
        
    def extract_frames(self, video_path: str, num_frames: int = 5) -> list:
        """Extract key frames from video for analysis"""
        frames = []
        with VideoFileClip(video_path) as video:
            # Calculate frame intervals
            duration = video.duration
            interval = duration / (num_frames + 1)
            
            # Extract frames at regular intervals
            for i in range(1, num_frames + 1):
                timestamp = i * interval
                frame = video.get_frame(timestamp)
                frames.append(frame)
                
        return frames
        
    def analyze_video(self, video_path: str) -> Dict[str, Any]:
        """Analyze video content using OpenAI Vision API"""
        try:
            # Validate video
            self.validate_video(video_path)
            
            # Extract frames
            frames = self.extract_frames(video_path)
            
            # Prepare messages for OpenAI
            messages = [
                {
                    "role": "system",
                    "content": """You are an expert insurance claims analyst. 
                    Analyze the provided video frames and identify:
                    1. Visible damage or loss
                    2. Property condition
                    3. Potential fraud indicators
                    4. Quality of evidence
                    
                    Provide a detailed analysis in JSON format with the following structure:
                    {
                        "damage_assessment": {
                            "visible_damage": [],
                            "severity": "low|medium|high",
                            "confidence": 0.0-1.0
                        },
                        "property_condition": {
                            "overall_state": "good|fair|poor",
                            "maintenance_level": "well_maintained|average|neglected"
                        },
                        "fraud_indicators": {
                            "suspicious_elements": [],
                            "risk_level": "low|medium|high",
                            "confidence": 0.0-1.0
                        },
                        "evidence_quality": {
                            "coverage": "comprehensive|partial|limited",
                            "clarity": "clear|moderate|poor",
                            "recommendations": []
                        }
                    }"""
                }
            ]
            
            # Add frames to messages
            for frame in frames:
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{frame.tobytes()}"
                            }
                        }
                    ]
                })
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model_version,
                messages=messages,
                max_tokens=1000,
                temperature=0.3
            )
            
            # Parse and return analysis
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"Error analyzing video: {str(e)}")
            
    def save_video(self, file_content: bytes, claim_id: str) -> str:
        """Save uploaded video to temporary storage"""
        # Create temporary directory if it doesn't exist
        temp_dir = Path("temp/videos")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        video_path = temp_dir / f"claim_{claim_id}_video.mp4"
        
        # Save video file
        with open(video_path, "wb") as f:
            f.write(file_content)
            
        return str(video_path) 