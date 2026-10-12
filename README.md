# EchoFlow — AI-Powered Speech Analytics and Business Decision Support Platform

EchoFlow is an AI-powered speech analytics and business decision-support platform that transforms unstructured audio into structured data, analytical KPIs, visual insights, and evidence-based conversation summaries.

It is **not** a transcription-only tool. Automatic speech recognition is one stage in a longer pipeline:

**Business problem → requirements → audio → ASR → structured data → analytics → KPIs → visualization → insights → decision support**

## What is implemented

- Local audio upload (WAV, MP3, M4A, FLAC, OGG, WebM)
- FFmpeg conversion to 16 kHz mono
- Faster-Whisper transcription with timestamps
- Speech KPIs: duration, speech/silence, WPM, CPM, RTF
- Text analytics: keywords, questions, sentence statistics, lexicon sentiment (heuristic)
- SQLite history
- Dashboard, transcript viewer, insights, model evaluation, settings
- Deterministic AI Analyst over structured metrics (no raw audio to an LLM)
- Export: TXT, JSON, SRT, VTT
- PyTest coverage for validation, metrics, database, and API health

## Architecture Overview

```
┌──────────────────┐
│   Frontend       │  HTML, CSS, JavaScript + Chart.js
│   (Static UI)    │  Dashboard, Analytics, Insights, Settings
└────────┬─────────┘
         │ HTTP/JSON
         ↓
┌──────────────────┐
│   FastAPI        │  REST API Layer
│   (app/api)      │  Routes: recordings, dashboard, evaluation, settings
└────────┬─────────┘
         │
         ↓
┌──────────────────┐
│   Services       │  Business Logic & Processing Pipeline
│   (app/services) │
│                  │
│  ┌─────────────┐ │
│  │ Pipeline    │ │  Orchestrates the complete workflow
│  └──────┬──────┘ │
│         │        │
│  ┌──────▼──────┐ │
│  │ Audio       │ │  Validation, FFmpeg conversion, probing
│  │ Processor   │ │
│  └──────┬──────┘ │
│         │        │
│  ┌──────▼──────┐ │
│  │ ASR Engine  │ │  Faster-Whisper transcription
│  └──────┬──────┘ │
│         │        │
│  ┌──────▼──────┐ │
│  │ Metrics     │ │  Speech metrics (WPM, silence, etc.)
│  │             │ │  Text metrics (keywords, sentiment)
│  └──────┬──────┘ │
│         │        │
│  ┌──────▼──────┐ │
│  │ Insights &  │ │  Business intelligence generation
│  │ Evaluation  │ │  WER/CER calculation
│  └─────────────┘ │
└────────┬─────────┘
         │
         ↓
┌──────────────────┐
│   SQLite DB      │  Persistent storage
│   (data/)        │  Recordings, transcripts, segments, analytics
└──────────────────┘
         │
         ↓
┌──────────────────┐
│   File Storage   │  Audio files
│   (storage/)     │  uploads/ → processed/ (WAV 16kHz mono)
└──────────────────┘
```

## API Endpoints

### Recordings
- `POST /api/recordings/upload` - Upload and process audio file
- `GET /api/recordings` - List all recordings with metadata
- `GET /api/recordings/{id}` - Get single recording details
- `GET /api/recordings/{id}/transcript` - Get full transcript
- `GET /api/recordings/{id}/segments` - Get timestamped segments
- `GET /api/recordings/{id}/analytics` - Get computed metrics/KPIs
- `GET /api/recordings/{id}/keywords` - Get extracted keywords
- `GET /api/recordings/{id}/export?format={txt|json|srt|vtt}` - Export transcript
- `DELETE /api/recordings/{id}` - Delete recording and files

### Dashboard
- `GET /api/dashboard/stats` - Summary statistics (count, total duration, avg metrics)
- `GET /api/dashboard/recent` - Recent recordings list

### Insights
- `GET /api/insights/{id}` - Generate business insights for recording

### Evaluation
- `POST /api/evaluation/wer` - Calculate WER/CER with reference transcript

### Settings
- `GET /api/settings` - Get current settings
- `PUT /api/settings` - Update settings (model size, etc.)

### Health
- `GET /api/health` - System health check

## Technology Stack Details

### Backend
- **FastAPI**: Modern async web framework
- **Faster-Whisper**: Local ASR engine (CTranslate2 backend)
- **SQLite**: Zero-config embedded database
- **FFmpeg**: Audio format conversion & processing
- **Python 3.13**: Latest Python with type hints

### Frontend
- **Vanilla JavaScript**: No framework dependencies
- **Chart.js**: Interactive data visualization
- **Fetch API**: HTTP client for REST calls
- **CSS Grid/Flexbox**: Modern responsive layouts

### Processing
- **Audio**: FFmpeg (libavcodec) for format conversion
- **ASR**: Faster-Whisper (optimized Whisper models)
- **Metrics**: NumPy-like computations in pure Python
- **Text Analysis**: Frequency-based keyword extraction, regex patterns

## Local-first privacy

Audio is processed on the machine running EchoFlow. There is no external speech API. SQLite stores recordings metadata, transcripts, segments, keywords, and computed KPIs under `data/` and audio files under `storage/`.

## Requirements

- Python 3.13
- FFmpeg (`ffmpeg` and `ffprobe` on PATH)
- macOS or Linux recommended for local Faster-Whisper

## Setup

```bash
cd echoflow
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Install FFmpeg if it is missing:

```bash
brew install ffmpeg
```

## Run

```bash
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```



The first transcription downloads the selected Whisper model. That step can take several minutes and requires network access.

## Tests

```bash
source .venv/bin/activate
pytest
```

## Complete Workflow

### 1. Audio Upload & Validation
```
User uploads audio → Validate format/size → Save to storage/uploads/
Supported: WAV, MP3, M4A, FLAC, OGG, WebM (max 50MB)
```

### 2. Audio Processing
```
FFmpeg conversion → 16 kHz mono WAV → storage/processed/
Probe duration → Extract audio metadata
```

### 3. Transcription (ASR)
```
Faster-Whisper (local) → Full transcript + timestamped segments
Models: tiny, base, small, medium, large
Language auto-detection
```

### 4. Metrics Computation

**Speech Metrics:**
- Duration (total audio length)
- Speech/silence ratio
- Words per minute (WPM)
- Characters per minute (CPM)
- Real-time factor (RTF = processing_time / duration)
- Segment statistics

**Text Metrics:**
- Keyword extraction (frequency-based)
- Question detection
- Sentence count & average length
- Sentiment analysis (lexicon-based)
- Language patterns

### 5. Data Persistence
```
SQLite database stores:
- recordings (metadata, paths, model info)
- transcripts (full text, word/char counts)
- segments (timestamped chunks with text)
- analytics (all computed KPIs)
- keywords (extracted terms with frequency)
```

### 6. Business Intelligence
```
Deterministic AI Analyst:
- Analyzes structured metrics (not raw audio)
- Generates insights and recommendations
- Identifies patterns and trends
- Provides actionable business intelligence
```

### 7. Visualization & Export
```
Dashboard → Charts (Chart.js) → Interactive analytics
Export options: TXT, JSON, SRT (subtitles), VTT (web video)
```

## Detailed Project Structure

```
echoflow/
│
├── app/                          # FastAPI backend application
│   ├── __init__.py
│   ├── main.py                   # Application entry point, exception handlers
│   ├── config.py                 # Settings, paths, environment variables
│   ├── database.py               # SQLite schema, queries, CRUD operations
│   ├── errors.py                 # Custom exception classes
│   │
│   ├── api/                      # REST API layer
│   │   ├── router.py             # Main API router aggregation
│   │   └── routes/               # Individual route modules
│   │       ├── dashboard.py      # Dashboard statistics & overview
│   │       ├── recordings.py     # Upload, list, retrieve, delete recordings
│   │       ├── evaluation.py     # WER/CER calculation with reference
│   │       ├── settings.py       # App settings (model selection, etc.)
│   │       └── health.py         # Health check endpoint
│   │
│   └── services/                 # Business logic & processing
│       ├── pipeline.py           # Main orchestration: upload → result
│       ├── audio_processor.py    # Validation, FFmpeg conversion, probing
│       ├── asr_engine.py         # Faster-Whisper transcription wrapper
│       ├── speech_metrics.py     # Duration, WPM, CPM, RTF, silence
│       ├── text_metrics.py       # Keywords, sentiment, questions
│       ├── insight_service.py    # Business intelligence generation
│       ├── evaluation.py         # WER/CER computation
│       └── export_service.py     # TXT, JSON, SRT, VTT export
│
├── frontend/                     # Static web UI (vanilla JavaScript)
│   ├── index.html                # Dashboard - overview & recent recordings
│   ├── transcriptions.html       # Full transcript viewer with segments
│   ├── analytics.html            # Speech analytics charts & metrics
│   ├── insights.html             # Business insights & AI analyst
│   ├── evaluation.html           # Model evaluation (WER/CER)
│   ├── settings.html             # App configuration
│   │
│   ├── css/
│   │   └── app.css               # Unified styles for all pages
│   │
│   └── js/                       # Frontend JavaScript modules
│       ├── api.js                # API client & HTTP utilities
│       ├── dashboard.js          # Dashboard page logic
│       ├── transcriptions.js     # Transcript viewer logic
│       ├── analytics.js          # Analytics charts (Chart.js)
│       ├── insights.js           # Insights display
│       ├── evaluation.js         # Evaluation page logic
│       ├── settings.js           # Settings management
│       └── layout.js             # Common layout & navigation
│
├── storage/                      # Audio file storage (gitignored)
│   ├── uploads/                  # Original uploaded files
│   └── processed/                # Converted 16kHz mono WAV files
│
├── data/                         # SQLite database (gitignored)
│   └── echoflow.db               # Main database file
│
├── tests/                        # PyTest test suite
│   ├── test_audio_validation.py  # Audio file validation tests
│   ├── test_metrics.py           # Speech & text metrics tests
│   ├── test_database.py          # Database operations tests
│   └── test_api_health.py        # API endpoint tests
│
├── docs/                         # Documentation
│   ├── requirements-traceability.md  # Requirements mapping
│   ├── privacy.md                # Privacy & data handling policy
│   └── ai-assistance.md          # AI development disclosure
│
├── requirements.txt              # Python dependencies
├── pytest.ini                    # PyTest configuration
├── run.sh                        # Quick start script
├── install_ffmpeg.sh             # FFmpeg installation helper
└── README.md                     # This file
```

## Key Features Explained

### 1. Multi-Format Audio Support
Upload various audio formats which are automatically converted to the optimal format for transcription (16 kHz mono WAV).

### 2. Local ASR Processing
Uses Faster-Whisper models running entirely on your machine:
- **tiny**: Fast, less accurate (~1GB RAM)
- **base**: Balanced speed/accuracy (~1GB RAM)
- **small**: Good accuracy (~2GB RAM)
- **medium**: High accuracy (~5GB RAM)
- **large**: Best accuracy (~10GB RAM)

### 3. Comprehensive Speech Metrics
- **Duration**: Total audio length
- **Speech Ratio**: Percentage of time with speech vs silence
- **WPM**: Words per minute (speaking rate)
- **CPM**: Characters per minute
- **RTF**: Real-time factor (how fast processing is vs audio length)

### 4. Text Analytics
- **Keywords**: Most frequent meaningful words
- **Questions**: Detected interrogative sentences
- **Sentiment**: Positive/negative word analysis
- **Statistics**: Sentence count, average length, vocabulary

### 5. Business Insights
AI Analyst generates actionable insights from structured metrics:
- Communication patterns
- Speaking style analysis
- Content recommendations
- Quality indicators

### 6. Model Evaluation
Calculate accuracy metrics when you have reference transcripts:
- **WER**: Word Error Rate (industry standard)
- **CER**: Character Error Rate (detailed accuracy)

### 7. Export Flexibility
- **TXT**: Plain text transcript
- **JSON**: Full structured data (segments, metrics, metadata)
- **SRT**: Standard subtitle format for video
- **VTT**: Web-compatible subtitle format

## Usage Workflow

1. **Navigate to Dashboard** - View overview and recent recordings
2. **Upload Audio** - Click upload, select file, choose model size
3. **Processing** - Wait for transcription (progress shown)
4. **View Results**:
   - **Transcriptions**: Read full transcript with timestamps
   - **Analytics**: Explore speech metrics and charts
   - **Insights**: Get business intelligence recommendations
5. **Evaluate** (optional) - Upload reference transcript to calculate WER/CER
6. **Export** - Download in desired format
7. **Settings** - Adjust default model and preferences

## Development

### Adding New Features

**New API Endpoint:**
1. Create route in `app/api/routes/`
2. Register in `app/api/router.py`
3. Add service logic in `app/services/`
4. Update database schema if needed in `app/database.py`

**New Metrics:**
1. Add computation in `app/services/speech_metrics.py` or `text_metrics.py`
2. Update database schema to store new metrics
3. Modify `app/services/pipeline.py` to compute and save

**New Frontend Page:**
1. Create HTML in `frontend/`
2. Create JavaScript module in `frontend/js/`
3. Add route in `app/main.py`
4. Update navigation in `frontend/js/layout.js`

### Running in Development Mode

```bash
# Backend with auto-reload
uvicorn app.main:app --reload --port 8000

# Run tests with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_metrics.py -v
```

## Honest limitations

- ASR quality depends on audio, accent, noise, and model size.
- Sentiment is a small local word list, not a clinical or psychological measure.
- Topics are keyword-frequency indicators, not a full topic model.
- WER/CER appear only when a reference transcript is supplied.
- Speaker diarization and cloud LLM analysis are not implemented.

## Academic title

EchoFlow: An AI-Assisted Speech Analytics and Business Intelligence Framework for Converting Unstructured Audio into Decision-Support Insights
