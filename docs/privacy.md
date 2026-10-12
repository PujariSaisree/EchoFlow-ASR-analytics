# Privacy

EchoFlow is local-first.

Stored on disk:

- original uploaded audio (`storage/uploads`)
- converted 16 kHz mono WAV (`storage/processed`)
- SQLite database (`data/echoflow.db`) containing filenames, timestamps, transcripts, segments, keywords, and KPIs

Not sent to external speech services.

The optional AI Analyst in this version is a Python function over stored JSON metrics. It does not receive raw audio.
