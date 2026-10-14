# Interview analytics prototype

This is the earlier version of my interview analytics project. I used it to work through video chunking, audio extraction and offline transcription before adding speaker separation and a dashboard in the [current project](https://github.com/sevenhiremath/edge-Interview-analysis-main-).

## What this version does

1. Splits a video into 10-second chunks using FFmpeg.
2. Extracts mono 16 kHz audio from each chunk.
3. Transcribes the audio locally with Vosk.
4. Counts filler words and saves a JSON result for each chunk.

Chunks are processed one after another. Existing audio and JSON files are reused when present.

## Run it

You need Python, FFmpeg and the Vosk English model `vosk-model-small-en-us-0.15`.

```bash
git clone https://github.com/sevenhiremath/edge-interview-analytics-prototype.git
cd edge-interview-analytics-prototype
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Place a recording at `data/input/sample.mp4` and extract the Vosk model to `models/vosk/vosk-model-small-en-us-0.15/`.

From the repository root:

```bash
PYTHONPATH=src python -m interview_pipeline.cli
```

On PowerShell, use `$env:PYTHONPATH = "src"` before `python -m interview_pipeline.cli`.

Output JSON files are saved under `data/outputs/`. Model weights and input recordings are not supplied.

## What I learned from this version

Keeping the intermediate audio and transcript files made it easier to inspect each step. It also showed a weakness in simple file-based caching: an existing output can be reused even after the input recording changes.

For a fresh recording, remove the previous generated chunks, audio and outputs before running again. Check the paths carefully and keep the original recording and model files.

## Scope

This version has no parallel worker pool, Gemini/LLM integration or merged dashboard report. It is a small transcription and filler-word prototype.

See [the implementation notes](docs/technical_brief.md) for the file layout, or start with the current project if you want speaker separation and the browser interface.
