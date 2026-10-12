# Requirements traceability

| Requirement | Feature | Implementation | Validation method |
| --- | --- | --- | --- |
| BR-01 | Audio upload | Transcriptions page + `/api/recordings/upload` | Upload validation tests |
| BR-02 | Automatic transcription | `asr_engine.py` (Faster-Whisper) | Integration when a model is available |
| BR-03 | Timestamped transcript | `segments` table + transcript viewer | Segment payload checks |
| BR-04 | Speech analytics | `speech_metrics.py` | Unit tests for WPM, silence, RTF |
| BR-05 | Text analytics | `text_metrics.py` | Keyword and question tests |
| BR-06 | Dashboard | `frontend/index.html` | UI review of KPI cards and charts |
| BR-07 | Transcript inspection | Transcriptions page | Manual UI validation |
| BR-08 | Business insights | `insight_service.py` | Output tied to stored metrics |
| BR-09 | ASR performance | processing time, RTF | Metric unit tests |
| BR-10 | History | SQLite `recordings` | Database insert/retrieve/delete tests |
| BR-11 | Useful errors | `EchoFlowError` handlers | Invalid upload API test |
| BR-12 | Local processing | Faster-Whisper + local files | Settings privacy copy |
| FR-11 | Dashboard KPIs | `/api/dashboard/overview` | API structure test |
| FR-13 | Export | TXT/JSON/SRT/VTT | Manual export from UI |
