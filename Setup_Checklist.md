# Pre-Implementation Checklist & Quick Reference

## ✅ Before Telling Claude Code to Start

### 1. **Google Cloud Setup**
- [ ] Create Google Cloud Account
- [ ] Enable Text-to-Speech API
- [ ] Create Service Account
- [ ] Download credentials JSON file
- [ ] Save path to `GOOGLE_APPLICATION_CREDENTIALS` in .env

**Quick Links:**
- https://console.cloud.google.com/

### 2. **Cloudflare R2 Setup**
- [ ] Login to Cloudflare dashboard
- [ ] Create R2 bucket (e.g., "book-videos")
- [ ] Create API token with R2 permissions
- [ ] Note: Account ID, Access Key, Secret Key
- [ ] Make bucket public (or use signed URLs)

**Quick Links:**
- https://dash.cloudflare.com/

### 3. **NeonDB Setup**
- [ ] Sign up at neon.tech
- [ ] Create new PostgreSQL database
- [ ] Get connection string: `postgresql://user:password@host:port/dbname`
- [ ] Note: You'll use this as `DATABASE_URL`

**Quick Links:**
- https://neon.tech/

### 4. **System Requirements**
- [ ] Python 3.9+ installed
- [ ] FFmpeg installed (`apt-get install ffmpeg`)
- [ ] Node.js 16+ (for cron job scheduling)
- [ ] npm installed

### 5. **Project Structure**
- [ ] Have your Docasaurus project ready
- [ ] Know the path to your markdown files (e.g., `./docs`)
- [ ] `/shorts` page already created ✅

### 6. **Credentials Gathered**
- [ ] Google Cloud Service Account JSON
- [ ] R2: Account ID, Access Key, Secret Key, Bucket Name, Public URL
- [ ] NeonDB: Connection string
- [ ] Have a `.env` template ready

---

## 🎬 Video Specifications (Quick Reference)

```
Duration:           30 seconds max
Aspect Ratio:       9:16 (vertical)
Resolution:         1080 x 1920 pixels
Frame Rate:         30fps
Format:             MP4 (H.264 + AAC)
Text Animation:     Fade in/out (0.5s)
Color Scheme:       Dark background (#1a1a2e) + white text
Sections:           
  - Title: 0-3s (fade in/hold/fade out)
  - Content: 3-27s (word-by-word with audio sync)
  - Outro: 27-30s (CTA fade out)
```

---

## 🔧 Quick Environment Variables

```bash
# Copy this to .env file and fill in your values

# Google Cloud
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
GOOGLE_PROJECT_ID=your-google-project-id
TTS_VOICE_NAME=en-US-Neural2-C

# Cloudflare R2
R2_ACCOUNT_ID=your-r2-account-id
R2_ACCESS_KEY_ID=your-access-key
R2_SECRET_ACCESS_KEY=your-secret-key
R2_BUCKET_NAME=book-videos
R2_PUBLIC_URL=https://book-videos.r2.dev

# Database
DATABASE_URL=postgresql://user:password@host:port/dbname

# Video Settings
VIDEO_DURATION_SECONDS=30
VIDEO_BACKGROUND_COLOR=#1a1a2e
VIDEO_TEXT_COLOR=#ffffff
DOCASAURUS_CHAPTERS_PATH=./docs

# Optional
LOG_LEVEL=INFO
ENABLE_CRON_JOB=true
```

---

## 🚀 How to Tell Claude Code to Start

### **Option 1: Start from Scratch (Recommended)**

```
"Create the entire book chapter video generation system following 
the IMPLEMENTATION_GUIDE.md. Start by setting up the project structure, 
installing dependencies, and implementing Phase 1: Audio generation 
using Google Cloud TTS. The videos should be 30 seconds max, with 
text animation (fade in/out), and stored in R2. Output will be 
displayed on the /shorts page in NeonDB. Use Python for the pipeline."
```

### **Option 2: Phase by Phase**

```
"Implement Phase 1 of the video generation system:

1. Create the project structure under scripts/video_generation/
2. Install all Python dependencies from requirements.txt
3. Create audio_generator.py that:
   - Uses Google Cloud Text-to-Speech API
   - Returns audio file + word-level timing data
   - Handles 30-second audio duration
4. Create a test script that generates audio for sample text
5. Verify the audio duration is accurate

Reference the IMPLEMENTATION_GUIDE.md for detailed specifications."
```

### **Option 3: Just the Core Pipeline**

```
"Build me a standalone Python script that:

1. Takes a markdown chapter file as input
2. Generates audio using Google Cloud TTS (returns timing data)
3. Creates video frames with text animation (fade in/out)
4. Combines frames + audio using FFmpeg
5. Outputs a 1080x1920 MP4 video (30 seconds max)
6. Returns the file path

Make it production-ready with error handling."
```

---

## 📋 System Dependencies

### **Ubuntu/Debian**
```bash
# Install system packages
sudo apt-get update
sudo apt-get install -y python3.9 python3-pip ffmpeg

# Install Node.js (optional, for cron job)
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### **macOS**
```bash
# Install FFmpeg
brew install ffmpeg

# Python should already be available
# If not: brew install python3
```

### **Windows**
```bash
# Install FFmpeg
choco install ffmpeg

# Or download from: https://ffmpeg.org/download.html

# Python: Download from https://www.python.org/
```

---

## 📊 Expected Output Structure

After implementation, your project should look like:

```
your-docasaurus-project/
├── scripts/
│   ├── video_generation/
│   │   ├── __init__.py
│   │   ├── audio_generator.py
│   │   ├── frame_generator.py
│   │   ├── video_composer.py
│   │   ├── r2_uploader.py
│   │   ├── db_manager.py
│   │   ├── markdown_parser.py
│   │   ├── main.py
│   │   ├── daily_generator.py
│   │   └── requirements.txt
│   ├── config.py
│   └── cron_job.js
├── website/
│   ├── src/
│   │   ├── components/
│   │   │   └── VideoReel.jsx
│   │   └── pages/
│   │       └── shorts/
│   │           └── index.md
│   └── docusaurus.config.js
├── .env (local, not committed)
├── .env.example
└── docs/
    ├── chapter-1.md
    ├── chapter-2.md
    └── ...
```

---

## 🧪 Testing Checklist

### **Phase 1: Audio Generation**
- [ ] Audio file created (MP3)
- [ ] Duration is accurate
- [ ] Timing data includes all words
- [ ] Voice is natural and clear

### **Phase 2: Frame Generation**
- [ ] Frames created as PNG images
- [ ] Resolution is 1080x1920
- [ ] Text is readable
- [ ] Animation timing matches audio

### **Phase 3: Video Composition**
- [ ] Video file created (MP4)
- [ ] Video duration matches audio
- [ ] Text syncs with audio
- [ ] Quality is good (no artifacts)

### **Phase 4: R2 Upload**
- [ ] File uploads successfully
- [ ] Public URL works
- [ ] Video plays in browser
- [ ] No permission errors

### **Phase 5: Database**
- [ ] NeonDB schema created
- [ ] Metadata saves correctly
- [ ] Can query videos
- [ ] Timestamps are correct

### **Phase 6: Website**
- [ ] Component renders
- [ ] Videos load from DB
- [ ] Videos play on page
- [ ] Responsive on mobile

### **Phase 7: Automation**
- [ ] Cron job configured
- [ ] Runs daily automatically
- [ ] Error notifications work
- [ ] Logs saved properly

---

## 🐛 Troubleshooting Quick Links

| Issue | Solution |
|-------|----------|
| FFmpeg not found | Install via: `apt-get install ffmpeg` |
| Google Cloud auth error | Verify GOOGLE_APPLICATION_CREDENTIALS path |
| R2 upload fails | Check bucket name, keys, endpoint URL |
| NeonDB connection error | Verify DATABASE_URL format |
| Video out of sync | Check frame rate (should be 30fps) |
| Text not visible | Verify font size (48-80px) and text color |
| Cron job not running | Check Node.js is installed, cron syntax |

---

## 💡 Pro Tips

1. **Start Small:** Test with one short chapter first
2. **Monitor Costs:** Track Google Cloud and R2 usage
3. **Cache Frames:** Don't regenerate if content hasn't changed
4. **Error Alerts:** Set up Slack/email notifications for failures
5. **Backup Videos:** Use R2 lifecycle policies for old videos
6. **Optimize:** Use lower resolution for testing, full res for production
7. **CI/CD:** Consider GitHub Actions for automated generation

---

## 📞 Support Resources

- **Google Cloud TTS Docs:** https://cloud.google.com/text-to-speech/docs
- **FFmpeg Wiki:** https://trac.ffmpeg.org/wiki
- **Pillow Documentation:** https://pillow.readthedocs.io/
- **Cloudflare R2:** https://developers.cloudflare.com/r2/
- **NeonDB:** https://neon.tech/docs/

---

## ✨ You're Ready!

Once you have credentials for all 3 services (Google Cloud, R2, NeonDB), 
you can tell Claude Code to start building.

**Recommended first message:**

```
"I have Google Cloud TTS, Cloudflare R2, and NeonDB set up. 
Following the IMPLEMENTATION_GUIDE.md, build me the complete video 
generation pipeline. Start with Phase 1: Audio generation. 
The system should generate 30-second vertical videos from my 
Docasaurus chapters with synced text animation, store in R2, 
and track in NeonDB for display on /shorts page."
```

Good luck! 🚀