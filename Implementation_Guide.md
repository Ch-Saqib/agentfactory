# Video Generation System - Implementation Guide for Claude Code

## 🎯 Final Specifications

- **Video Duration:** 30 seconds max per chapter
- **Aspect Ratio:** 9:16 (vertical - Instagram Reel format)
- **Frame Rate:** 30fps
- **Text Animation:** Fade in/out with smooth transitions
- **Update Frequency:** Daily (one video per chapter)
- **Display:** `/shorts` page already created
- **Output:** MP4 files uploaded to R2

---

## 📁 Project Structure

```
project-root/
├── scripts/
│   ├── video_generation/
│   │   ├── __init__.py
│   │   ├── audio_generator.py       # TTS + timing
│   │   ├── frame_generator.py       # Image creation
│   │   ├── video_composer.py        # FFmpeg combining
│   │   ├── r2_uploader.py          # R2 upload
│   │   ├── db_manager.py           # NeonDB operations
│   │   └── main.py                 # Orchestrator
│   ├── config.py                   # Configuration & env vars
│   └── requirements.txt             # Python dependencies
├── website/
│   ├── src/
│   │   ├── components/
│   │   │   └── VideoReel.jsx       # Video display component
│   │   └── pages/
│   │       └── shorts/
│   │           └── index.md        # Shorts page
│   └── docusaurus.config.js
├── .env.example                    # Template for env vars
└── cron_job.js                     # Node-cron scheduler
```

---

## 🔐 Environment Variables (.env)

```bash
# Google Cloud TTS
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
GOOGLE_PROJECT_ID=your-project-id

# Cloudflare R2
R2_ACCOUNT_ID=your-account-id
R2_ACCESS_KEY_ID=your-access-key
R2_SECRET_ACCESS_KEY=your-secret-key
R2_BUCKET_NAME=your-bucket-name
R2_PUBLIC_URL=https://your-bucket.r2.dev

# NeonDB (PostgreSQL)
DATABASE_URL=postgresql://user:password@host:port/dbname

# Video Settings
VIDEO_DURATION_SECONDS=30
DOCASAURUS_CHAPTERS_PATH=./docs
TTS_VOICE_NAME=en-US-Neural2-C
TTS_VOICE_GENDER=FEMALE

# Background Settings
VIDEO_BACKGROUND_COLOR=#1a1a2e
VIDEO_TEXT_COLOR=#ffffff
VIDEO_ACCENT_COLOR=#0f3460
```

---

## 📦 Dependencies (requirements.txt)

```txt
google-cloud-texttospeech==1.11.1
google-cloud-storage==2.10.0
Pillow==10.0.0
opencv-python==4.8.0.76
ffmpeg-python==0.2.1
psycopg2-binary==2.9.9
python-dotenv==1.0.0
requests==2.31.0
boto3==1.28.0
```

---

## 🎨 Text Animation Strategy

### **Fade In/Out with Smooth Transitions**

```python
# Animation Timeline for 30-second video

Timeline:
├─ 0-2s:    Title fade in + hold
├─ 2-3s:    Title fade out
├─ 3-5s:    Subtitle fade in + hold
├─ 5-6s:    Subtitle fade out
├─ 6-27s:   Content text with word-by-word timing
│           (synced to TTS audio)
├─ 27-29s:  Content fade out
└─ 29-30s:  End screen with CTA

# Each text segment:
- Fade in: 0.5 seconds
- Hold: variable based on audio duration
- Fade out: 0.5 seconds
```

### **Python Implementation**

```python
def create_fade_animation(text, start_time, end_time, frame_width, frame_height):
    """
    Creates frames for text animation with fade effect
    
    Args:
        text: Text to animate
        start_time: When animation starts (seconds)
        end_time: When animation ends (seconds)
        frame_width: 1080px (for 1080x1920)
        frame_height: 1920px
    
    Returns:
        List of frame paths with timing info
    """
    
    fade_in_duration = 0.5   # 0.5 seconds
    fade_out_duration = 0.5  # 0.5 seconds
    total_duration = end_time - start_time
    hold_duration = total_duration - fade_in_duration - fade_out_duration
    
    # Timeline:
    # [Fade In: 0-0.5s] [Hold: 0.5-X s] [Fade Out: X-X+0.5s]
    
    frames = []
    fps = 30
    
    for frame_num in range(int(total_duration * fps)):
        frame_time = frame_num / fps
        
        # Calculate opacity (0-1)
        if frame_time < fade_in_duration:
            opacity = frame_time / fade_in_duration  # 0 to 1
        elif frame_time < (total_duration - fade_out_duration):
            opacity = 1.0  # Fully opaque
        else:
            opacity = 1.0 - ((frame_time - (total_duration - fade_out_duration)) / fade_out_duration)
        
        frame = create_text_frame(
            text=text,
            opacity=opacity,
            width=frame_width,
            height=frame_height
        )
        frames.append(frame)
    
    return frames
```

---

## 🔊 Step 1: Audio Generation (audio_generator.py)

```python
"""
Generates audio from text using Google Cloud TTS
Returns: Audio file + timing data for synchronization
"""

import json
from google.cloud import texttospeech

class AudioGenerator:
    def __init__(self, voice_name="en-US-Neural2-C"):
        self.client = texttospeech.TextToSpeechClient()
        self.voice_name = voice_name
    
    def generate_audio_with_timing(self, text, output_path):
        """
        Generate audio and extract word-level timing
        
        Returns:
            {
                'audio_file': path,
                'duration_seconds': float,
                'words': [
                    {'word': 'Hello', 'start_ms': 0, 'end_ms': 500},
                    ...
                ]
            }
        """
        
        # TTS Request
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name=self.voice_name
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        
        response = self.client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        # Save audio file
        with open(output_path, "wb") as out:
            out.write(response.audio_content)
        
        # Get duration using librosa or ffprobe
        duration = get_audio_duration(output_path)
        
        # Extract timing (Google TTS returns timing in response if requested)
        # For now, we'll estimate based on word count
        timing_data = self._estimate_word_timing(text, duration)
        
        return {
            'audio_file': output_path,
            'duration_seconds': duration,
            'words': timing_data
        }
    
    def _estimate_word_timing(self, text, total_duration):
        """Estimate when each word is spoken"""
        words = text.split()
        timing_data = []
        words_per_second = len(words) / total_duration
        
        cumulative_time = 0
        for word in words:
            word_duration = 1.0 / words_per_second
            timing_data.append({
                'word': word,
                'start_ms': int(cumulative_time * 1000),
                'end_ms': int((cumulative_time + word_duration) * 1000)
            })
            cumulative_time += word_duration
        
        return timing_data

def get_audio_duration(audio_path):
    """Get duration of audio file using ffprobe"""
    import subprocess
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'default=noprint_wrappers=1:nokey=1:novalue=1', audio_path],
        capture_output=True,
        text=True
    )
    return float(result.stdout.strip())
```

---

## 🎬 Step 2: Frame Generation (frame_generator.py)

```python
"""
Generate video frames with text animation
Creates PNG images timed to audio
"""

from PIL import Image, ImageDraw, ImageFont
import os

class FrameGenerator:
    def __init__(self, width=1080, height=1920, bg_color="#1a1a2e", text_color="#ffffff"):
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.text_color = text_color
        self.fps = 30
    
    def generate_video_frames(self, title, content, audio_timing, output_dir):
        """
        Generate all frames for 30-second video
        
        Args:
            title: Chapter title
            content: Chapter content (split into 30s worth)
            audio_timing: Word timing data from TTS
            output_dir: Where to save frame images
        
        Returns:
            List of frame file paths
        """
        
        os.makedirs(output_dir, exist_ok=True)
        frame_paths = []
        
        # Phase 1: Title (0-3 seconds)
        title_frames = self._create_title_frames(title, duration=3, output_dir=output_dir)
        frame_paths.extend(title_frames)
        
        # Phase 2: Content with word-by-word animation (3-27 seconds)
        content_frames = self._create_content_frames(
            content, 
            audio_timing, 
            start_time=3,
            duration=24,
            output_dir=output_dir,
            frame_offset=len(title_frames)
        )
        frame_paths.extend(content_frames)
        
        # Phase 3: Outro/End screen (27-30 seconds)
        outro_frames = self._create_outro_frames(duration=3, output_dir=output_dir, frame_offset=len(frame_paths))
        frame_paths.extend(outro_frames)
        
        return frame_paths
    
    def _create_title_frames(self, title, duration, output_dir):
        """Create title with fade in/out"""
        frames = []
        frame_count = int(duration * self.fps)
        
        for frame_num in range(frame_count):
            # Calculate opacity: fade in 0.5s, hold, fade out 0.5s
            time = frame_num / self.fps
            fade_in = 0.5
            fade_out = duration - 0.5
            
            if time < fade_in:
                opacity = time / fade_in
            elif time > fade_out:
                opacity = 1.0 - ((time - fade_out) / 0.5)
            else:
                opacity = 1.0
            
            frame = self._create_text_frame(
                title,
                opacity=opacity,
                font_size=80,
                position='center'
            )
            
            frame_path = os.path.join(output_dir, f"frame_{frame_num:05d}.png")
            frame.save(frame_path)
            frames.append(frame_path)
        
        return frames
    
    def _create_content_frames(self, content, audio_timing, start_time, duration, output_dir, frame_offset):
        """Create content frames synced to audio timing"""
        frames = []
        frame_count = int(duration * self.fps)
        
        # Split content into displayable chunks
        words = content.split()
        
        for frame_num in range(frame_count):
            time = (frame_offset + frame_num) / self.fps
            relative_time = time - start_time
            
            # Find which word(s) should be displayed at this time
            displayed_text = self._get_text_for_time(relative_time, audio_timing)
            
            frame = self._create_text_frame(
                displayed_text,
                opacity=1.0,
                font_size=48,
                position='center'
            )
            
            frame_path = os.path.join(output_dir, f"frame_{frame_offset + frame_num:05d}.png")
            frame.save(frame_path)
            frames.append(frame_path)
        
        return frames
    
    def _create_outro_frames(self, duration, output_dir, frame_offset):
        """Create end screen"""
        frames = []
        frame_count = int(duration * self.fps)
        
        for frame_num in range(frame_count):
            time = frame_num / self.fps
            fade_out = 0.5
            
            if time > (duration - fade_out):
                opacity = 1.0 - ((time - (duration - fade_out)) / fade_out)
            else:
                opacity = 1.0
            
            frame = self._create_text_frame(
                "Continue reading on our website →",
                opacity=opacity,
                font_size=48,
                position='center'
            )
            
            frame_path = os.path.join(output_dir, f"frame_{frame_offset + frame_num:05d}.png")
            frame.save(frame_path)
            frames.append(frame_path)
        
        return frames
    
    def _create_text_frame(self, text, opacity=1.0, font_size=48, position='center'):
        """Create single frame with text"""
        img = Image.new('RGB', (self.width, self.height), color=self.bg_color)
        draw = ImageDraw.Draw(img, 'RGBA')
        
        # Use system font (in production, use custom font)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Text color with opacity
        r, g, b = int(self.text_color[1:3], 16), int(self.text_color[3:5], 16), int(self.text_color[5:7], 16)
        text_color_rgba = (r, g, b, int(255 * opacity))
        
        # Wrap text to fit frame
        wrapped_text = self._wrap_text(text, font, self.width - 100)
        
        # Calculate position
        bbox = draw.textbbox((0, 0), wrapped_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        if position == 'center':
            x = (self.width - text_width) // 2
            y = (self.height - text_height) // 2
        else:
            x, y = 50, self.height // 2
        
        draw.text((x, y), wrapped_text, font=font, fill=text_color_rgba)
        
        return img
    
    def _wrap_text(self, text, font, max_width):
        """Wrap text to fit width"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = ImageDraw.Draw(Image.new('RGB', (1, 1))).textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return '\n'.join(lines)
    
    def _get_text_for_time(self, time_seconds, audio_timing):
        """Get text to display at specific time"""
        displayed_words = []
        
        for word_data in audio_timing:
            start_ms = word_data['start_ms']
            end_ms = word_data['end_ms']
            time_ms = time_seconds * 1000
            
            if start_ms <= time_ms < end_ms:
                displayed_words.append(word_data['word'])
        
        return ' '.join(displayed_words) if displayed_words else ''
```

---

## 🎥 Step 3: Video Composer (video_composer.py)

```python
"""
Combine frames + audio using FFmpeg
Creates final MP4 video file
"""

import subprocess
import os

class VideoComposer:
    def __init__(self, fps=30):
        self.fps = fps
    
    def compose_video(self, frames_dir, audio_file, output_video_path):
        """
        Combine image frames + audio into MP4
        
        Args:
            frames_dir: Directory with frame_00000.png, frame_00001.png, etc.
            audio_file: Path to MP3/WAV audio file
            output_video_path: Where to save final MP4
        
        Returns:
            Path to created video file
        """
        
        # FFmpeg command to combine frames + audio
        cmd = [
            'ffmpeg',
            '-framerate', str(self.fps),
            '-i', os.path.join(frames_dir, 'frame_%05d.png'),
            '-i', audio_file,
            '-c:v', 'libx264',          # Video codec: H.264
            '-pix_fmt', 'yuv420p',      # Pixel format
            '-c:a', 'aac',              # Audio codec
            '-b:a', '128k',             # Audio bitrate
            '-shortest',                # Stop at shortest stream
            '-y',                       # Overwrite output
            output_video_path
        ]
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"FFmpeg Error: {result.stderr}")
            raise Exception(f"Video composition failed: {result.stderr}")
        
        print(f"✅ Video created: {output_video_path}")
        return output_video_path
```

---

## ☁️ Step 4: R2 Upload (r2_uploader.py)

```python
"""
Upload video to Cloudflare R2 bucket
"""

import boto3
import os
from datetime import datetime

class R2Uploader:
    def __init__(self, account_id, access_key, secret_key, bucket_name, public_url):
        self.s3_client = boto3.client(
            's3',
            endpoint_url=f'https://{account_id}.r2.cloudflarestorage.com',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name='auto'
        )
        self.bucket_name = bucket_name
        self.public_url = public_url
    
    def upload_video(self, video_path, chapter_id):
        """
        Upload video to R2 and return public URL
        
        Returns:
            {
                'url': 'https://...',
                'file_size_mb': float,
                'upload_time': datetime
            }
        """
        
        # Generate S3 key (path in bucket)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        s3_key = f"videos/{chapter_id}/{timestamp}_video.mp4"
        
        file_size = os.path.getsize(video_path) / (1024 * 1024)  # Convert to MB
        
        print(f"Uploading {video_path} ({file_size:.2f}MB) to R2...")
        
        # Upload file
        self.s3_client.upload_file(
            video_path,
            self.bucket_name,
            s3_key,
            ExtraArgs={'ContentType': 'video/mp4'}
        )
        
        # Generate public URL
        public_video_url = f"{self.public_url}/{s3_key}"
        
        print(f"✅ Video uploaded: {public_video_url}")
        
        return {
            'url': public_video_url,
            'file_size_mb': file_size,
            'upload_time': datetime.now()
        }
```

---

## 💾 Step 5: Database Manager (db_manager.py)

```python
"""
Manage video metadata in NeonDB (PostgreSQL)
"""

import psycopg2
from datetime import datetime
import json

class DBManager:
    def __init__(self, database_url):
        self.conn_string = database_url
    
    def save_video_metadata(self, chapter_id, title, video_url, duration, content_preview):
        """Save video info to database"""
        
        conn = psycopg2.connect(self.conn_string)
        cursor = conn.cursor()
        
        query = """
            INSERT INTO videos 
            (chapter_id, chapter_title, video_url, duration_seconds, 
             content_snippet, status, created_at)
            VALUES (%s, %s, %s, %s, %s, 'completed', %s)
            ON CONFLICT (chapter_id) DO UPDATE SET
            video_url = EXCLUDED.video_url,
            duration_seconds = EXCLUDED.duration_seconds,
            updated_at = %s
        """
        
        cursor.execute(query, (
            chapter_id,
            title,
            video_url,
            duration,
            content_preview[:200],
            datetime.now(),
            datetime.now()
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ Saved metadata for {chapter_id}")
    
    def get_videos_for_shorts_page(self, limit=20):
        """Fetch videos for /shorts page"""
        
        conn = psycopg2.connect(self.conn_string)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT chapter_id, chapter_title, video_url, duration_seconds, created_at
            FROM videos
            WHERE status = 'completed'
            ORDER BY created_at DESC
            LIMIT %s
        """, (limit,))
        
        videos = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [
            {
                'chapter_id': v[0],
                'title': v[1],
                'url': v[2],
                'duration': v[3],
                'created_at': v[4].isoformat()
            }
            for v in videos
        ]
```

---

## 🎯 Step 6: Main Orchestrator (main.py)

```python
"""
Main script to orchestrate entire video generation pipeline
"""

import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from audio_generator import AudioGenerator
from frame_generator import FrameGenerator
from video_composer import VideoComposer
from r2_uploader import R2Uploader
from db_manager import DBManager

class VideoGenerator:
    def __init__(self):
        self.audio_gen = AudioGenerator()
        self.frame_gen = FrameGenerator()
        self.video_composer = VideoComposer()
        self.r2_uploader = R2Uploader(
            account_id=os.getenv('R2_ACCOUNT_ID'),
            access_key=os.getenv('R2_ACCESS_KEY_ID'),
            secret_key=os.getenv('R2_SECRET_ACCESS_KEY'),
            bucket_name=os.getenv('R2_BUCKET_NAME'),
            public_url=os.getenv('R2_PUBLIC_URL')
        )
        self.db_manager = DBManager(os.getenv('DATABASE_URL'))
        self.temp_dir = './temp_video_generation'
    
    def generate_video_for_chapter(self, chapter_id, chapter_title, chapter_content):
        """
        End-to-end video generation for a chapter
        
        Steps:
        1. Generate audio from text
        2. Generate frames with animation
        3. Compose video (frames + audio)
        4. Upload to R2
        5. Save metadata to database
        6. Cleanup temporary files
        """
        
        try:
            print(f"\n{'='*60}")
            print(f"Generating video for: {chapter_title}")
            print(f"{'='*60}")
            
            # Create temporary directories
            temp_chapter_dir = os.path.join(self.temp_dir, chapter_id)
            os.makedirs(temp_chapter_dir, exist_ok=True)
            
            frames_dir = os.path.join(temp_chapter_dir, 'frames')
            os.makedirs(frames_dir, exist_ok=True)
            
            # Step 1: Generate Audio
            print("\n[1/5] Generating audio...")
            audio_path = os.path.join(temp_chapter_dir, 'audio.mp3')
            audio_data = self.audio_gen.generate_audio_with_timing(
                chapter_content, 
                audio_path
            )
            print(f"    Audio duration: {audio_data['duration_seconds']:.2f}s")
            
            # Truncate content to fit 30 seconds
            max_words = int(audio_data['duration_seconds'] * 3)  # Roughly 3 words/second
            truncated_content = ' '.join(chapter_content.split()[:max_words])
            
            # Step 2: Generate Frames
            print("\n[2/5] Generating frames with animation...")
            frames = self.frame_gen.generate_video_frames(
                title=chapter_title,
                content=truncated_content,
                audio_timing=audio_data['words'],
                output_dir=frames_dir
            )
            print(f"    Created {len(frames)} frames")
            
            # Step 3: Compose Video
            print("\n[3/5] Composing video (frames + audio)...")
            video_path = os.path.join(temp_chapter_dir, 'output.mp4')
            self.video_composer.compose_video(frames_dir, audio_path, video_path)
            
            # Step 4: Upload to R2
            print("\n[4/5] Uploading to R2...")
            upload_result = self.r2_uploader.upload_video(video_path, chapter_id)
            
            # Step 5: Save Metadata
            print("\n[5/5] Saving metadata to database...")
            self.db_manager.save_video_metadata(
                chapter_id=chapter_id,
                title=chapter_title,
                video_url=upload_result['url'],
                duration=audio_data['duration_seconds'],
                content_preview=chapter_content[:100]
            )
            
            print("\n✅ Video generation complete!")
            print(f"   URL: {upload_result['url']}")
            print(f"   Size: {upload_result['file_size_mb']:.2f}MB")
            
            return {
                'success': True,
                'video_url': upload_result['url'],
                'chapter_id': chapter_id
            }
        
        except Exception as e:
            print(f"\n❌ Error generating video: {str(e)}")
            return {
                'success': False,
                'chapter_id': chapter_id,
                'error': str(e)
            }
        
        finally:
            # Cleanup temporary files
            if os.path.exists(temp_chapter_dir):
                shutil.rmtree(temp_chapter_dir)
                print("\n🧹 Cleaned up temporary files")
    
    def generate_from_markdown_file(self, md_file_path):
        """
        Parse markdown file and generate video
        """
        from markdown_parser import parse_markdown
        
        chapter_data = parse_markdown(md_file_path)
        
        return self.generate_video_for_chapter(
            chapter_id=chapter_data['id'],
            chapter_title=chapter_data['title'],
            chapter_content=chapter_data['content']
        )


if __name__ == "__main__":
    generator = VideoGenerator()
    
    # Example: Generate video for a chapter
    result = generator.generate_from_markdown_file('./docs/chapter-1.md')
    
    if result['success']:
        print(f"\n🎉 Success! Video available at: {result['video_url']}")
    else:
        print(f"\n⚠️ Failed: {result['error']}")
```

---

## 📄 Step 7: Markdown Parser (markdown_parser.py)

```python
"""
Extract chapter information from markdown files
"""

import os
import re
from pathlib import Path

def parse_markdown(file_path):
    """
    Parse markdown file and extract:
    - Chapter ID (from filename)
    - Title (first H1)
    - Content (all paragraphs)
    """
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract title (first H1)
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else "Untitled"
    
    # Extract ID from filename
    filename = Path(file_path).stem
    chapter_id = filename
    
    # Remove markdown syntax and get clean text
    # Remove code blocks
    clean_content = re.sub(r'```[\s\S]*?```', '', content)
    # Remove HTML comments
    clean_content = re.sub(r'<!--[\s\S]*?-->', '', clean_content)
    # Remove markdown headers
    clean_content = re.sub(r'^#+\s+', '', clean_content, flags=re.MULTILINE)
    # Remove markdown links
    clean_content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1', clean_content)
    # Remove bold/italic
    clean_content = re.sub(r'[*_]{1,2}', '', clean_content)
    # Clean up whitespace
    clean_content = re.sub(r'\n\n+', '\n', clean_content)
    
    return {
        'id': chapter_id,
        'title': title,
        'content': clean_content.strip()
    }
```

---

## ⏰ Step 8: Cron Job Scheduler (cron_job.js)

```javascript
/**
 * Node.js cron job to generate video daily
 * Runs at 12:00 AM UTC every day
 */

const cron = require('node-cron');
const { spawn } = require('child_process');
const path = require('path');

// Run daily at 12:00 AM UTC
cron.schedule('0 0 * * *', async () => {
    console.log('🎬 Starting daily video generation...');
    
    try {
        // Execute Python script
        const result = await runPythonScript('./scripts/video_generation/daily_generator.py');
        console.log('✅ Daily video generation completed');
        console.log(result);
    } catch (error) {
        console.error('❌ Error in daily generation:', error);
        // Send error notification (email, Slack, etc.)
    }
});

function runPythonScript(scriptPath) {
    return new Promise((resolve, reject) => {
        const python = spawn('python3', [scriptPath]);
        
        let output = '';
        let errorOutput = '';
        
        python.stdout.on('data', (data) => {
            output += data.toString();
        });
        
        python.stderr.on('data', (data) => {
            errorOutput += data.toString();
        });
        
        python.on('close', (code) => {
            if (code !== 0) {
                reject(new Error(`Script exited with code ${code}: ${errorOutput}`));
            } else {
                resolve(output);
            }
        });
    });
}

console.log('✅ Cron job scheduler started');
```

---

## 🌐 Step 9: Website Component (VideoReel.jsx)

```jsx
/**
 * React component for displaying videos on /shorts page
 * Fetches from NeonDB and displays in Instagram Reel style
 */

import React, { useState, useEffect } from 'react';
import styles from './VideoReel.module.css';

export default function VideoReel() {
    const [videos, setVideos] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchVideos();
    }, []);

    const fetchVideos = async () => {
        try {
            // This endpoint should return videos from your NeonDB
            const response = await fetch('/api/videos');
            const data = await response.json();
            setVideos(data);
            setLoading(false);
        } catch (err) {
            setError(err.message);
            setLoading(false);
        }
    };

    if (loading) return <div className={styles.loading}>Loading videos...</div>;
    if (error) return <div className={styles.error}>Error: {error}</div>;
    if (videos.length === 0) return <div className={styles.empty}>No videos yet</div>;

    return (
        <div className={styles.container}>
            <div className={styles.reelsContainer}>
                {videos.map((video, index) => (
                    <div key={index} className={styles.reelCard}>
                        <div className={styles.videoWrapper}>
                            <video
                                src={video.url}
                                controls
                                className={styles.video}
                                poster="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1080 1920'%3E%3Crect fill='%231a1a2e' width='1080' height='1920'/%3E%3C/svg%3E"
                            />
                        </div>
                        <div className={styles.videoInfo}>
                            <h3>{video.title}</h3>
                            <p className={styles.date}>
                                {new Date(video.created_at).toLocaleDateString()}
                            </p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
```

---

## 🗄️ Database Setup (SQL)

```sql
-- Create videos table
CREATE TABLE videos (
    id SERIAL PRIMARY KEY,
    chapter_id VARCHAR(255) UNIQUE NOT NULL,
    chapter_title VARCHAR(255) NOT NULL,
    chapter_number INT,
    content_snippet TEXT,
    
    -- Video Details
    video_url VARCHAR(500) NOT NULL,
    thumbnail_url VARCHAR(500),
    duration_seconds DECIMAL(5,2),
    
    -- Status & Metadata
    status VARCHAR(50) DEFAULT 'pending', -- pending, processing, completed, failed
    error_message TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster queries
CREATE INDEX idx_videos_status ON videos(status);
CREATE INDEX idx_videos_created_at ON videos(created_at DESC);

-- Create videos_archive table for logging
CREATE TABLE videos_archive (
    id SERIAL PRIMARY KEY,
    video_id INT REFERENCES videos(id),
    event VARCHAR(100),
    details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🚀 Ready for Implementation

### Next Steps for Claude Code:

1. **Setup Environment**
   - Create project structure
   - Setup .env file
   - Install dependencies

2. **Phase 1: Audio Generation**
   - Implement `audio_generator.py`
   - Test with sample text

3. **Phase 2: Frame Generation**
   - Implement `frame_generator.py`
   - Create test frames with animation

4. **Phase 3: Video Composition**
   - Implement `video_composer.py`
   - Test FFmpeg integration

5. **Phase 4: R2 Integration**
   - Implement `r2_uploader.py`
   - Test upload & URL generation

6. **Phase 5: Database**
   - Setup NeonDB schema
   - Implement `db_manager.py`

7. **Phase 6: Website**
   - Create VideoReel component
   - Add to /shorts page

8. **Phase 7: Automation**
   - Setup daily cron job
   - Test end-to-end

---

## ✅ Verification Checklist

- [ ] Audio is 30 seconds or less
- [ ] Text fades in/out smoothly
- [ ] Text syncs with spoken words
- [ ] Video is 1080x1920 (9:16 aspect ratio)
- [ ] Video uploads to R2 successfully
- [ ] Metadata saves to NeonDB
- [ ] Videos display on /shorts page
- [ ] Cron job runs daily
- [ ] Error handling for all steps

---

**Ready to start? Tell Claude Code:**

> "Build the video generation system following this implementation guide. Start with Phase 1: Create the audio generation pipeline using Google Cloud TTS."