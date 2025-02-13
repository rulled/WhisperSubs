# 🎬 WhisperSubs: Automated Video Subtitling Tool

**One-click solution for adding multi-language subtitles to your videos using OpenAI's Whisper AI**

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FFmpeg Required](https://img.shields.io/badge/FFmpeg-Required-orange)](https://ffmpeg.org/)

## 🌟 Features

- 🚀 **Fast Processing** - Multi-threaded conversion and hardware acceleration support
- 🌐 **Multi-language Support** - Generate subtitles in multiple languages simultaneously
- 🔄 **Seamless Replacement** - Option to replace original file or create new output
- 🧹 **Auto-cleanup** - Removes temporary files automatically
- 🎚️ **Quality Preservation** - Maintains original video/audio quality
- 📊 **Progress Tracking** - Real-time progress indicators and time estimates
- 🛠️ **Flexible Configuration** - Choose different Whisper AI models

## 📦 Installation

### Prerequisites
- Python 3.8+
- FFmpeg ([Installation Guide](https://ffmpeg.org/download.html))

```bash
# Clone repository
git clone https://github.com/yourusername/WhisperSubs.git
cd WhisperSubs

# Install dependencies
pip install -r requirements.txt
```

## 🚀 Quick Start

**Basic Usage:**
```bash
python whispersubs.py input.mp4 --replace
```

**Advanced Usage:**
```bash
python whispersubs.py input.mp4 \
  --output output.mkv \
  --model large-v3 \
  --langs en,es,fr \
  --replace
```

## 🛠️ Configuration Options

| Parameter       | Description                          | Default    |
|-----------------|--------------------------------------|------------|
| `input`         | Input video file                     | Required   |
| `-o, --output`  | Output file name                     | (Optional) |
| `-m, --model`   | Whisper model size                   | `base`     |
| `-l, --langs`   | Comma-separated language codes       | `en`       |
| `-r, --replace` | Replace original file                | False      |

**Available Whisper Models:**
- `tiny` *(Fastest)*
- `base`
- `small`
- `medium`
- `large-v3` *(Most accurate)*

## 🌍 Supported Languages

WhisperSubs supports all languages available in Whisper AI models. Use standard [ISO 639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) language codes.

**Popular Options:**
- English (`en`)
- Spanish (`es`)
- French (`fr`)
- German (`de`)
- Chinese (`zh`)
- Japanese (`ja`)
- Russian (`ru`)
