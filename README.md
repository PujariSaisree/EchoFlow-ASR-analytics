# EchoFlow — AI-Powered Speech Analytics and Business Decision Support Platform

EchoFlow is an AI-powered speech analytics and business decision-support platform that transforms unstructured audio into structured data, analytical KPIs, visual insights, and evidence-based conversation summaries.

It is **not** a transcription-only tool. Automatic speech recognition is one stage in a longer pipeline:

Business problem → requirements → audio → ASR → structured data → analytics → KPIs → visualization → insights → decision support.

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

Open [http://127.0.0.1:8000](http://127.0.0.1:8000).

The first transcription downloads the selected Whisper model. That step can take several minutes and requires network access.

## Tests

```bash
source .venv/bin/activate
pytest
```

## Project layout

```
app/                FastAPI application
  api/              HTTP routes
  services/         audio, ASR, speech metrics, text metrics, insights
  database.py       SQLite access
frontend/           HTML, CSS, vanilla JavaScript, Chart.js
tests/              PyTest
docs/               requirements, privacy, AI-assistance declaration
```

## Honest limitations

- ASR quality depends on audio, accent, noise, and model size.
- Sentiment is a small local word list, not a clinical or psychological measure.
- Topics are keyword-frequency indicators, not a full topic model.
- WER/CER appear only when a reference transcript is supplied.
- Speaker diarization and cloud LLM analysis are not implemented.

## Academic title

EchoFlow: An AI-Assisted Speech Analytics and Business Intelligence Framework for Converting Unstructured Audio into Decision-Support Insights
