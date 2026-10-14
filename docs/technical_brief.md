# Prototype implementation notes

This document describes the code in this repository. The newer interview analytics project is maintained [separately](https://github.com/sevenhiremath/edge-Interview-analysis-main-).

## Processing order

[pipeline.py](../src/interview_pipeline/pipeline.py) calls the chunking function and then loops through the video chunks. For each chunk it extracts audio, transcribes it, counts filler words and writes JSON.

The loop is sequential. The current prototype does not create concurrent workers or call an LLM API.

## Modules

| File | Responsibility |
| --- | --- |
| [cli.py](../src/interview_pipeline/cli.py) | Starts the pipeline |
| [chunking.py](../src/interview_pipeline/chunking.py) | Splits the input video with FFmpeg |
| [audio_extract.py](../src/interview_pipeline/audio_extract.py) | Produces mono 16 kHz WAV audio |
| [stt.py](../src/interview_pipeline/stt.py) | Loads Vosk, reads audio in blocks and returns words with timestamps |
| [filler_detection.py](../src/interview_pipeline/filler_detection.py) | Counts filler words from a transcript |
| [pipeline.py](../src/interview_pipeline/pipeline.py) | Coordinates the steps and writes per-chunk results |

## Paths

The pipeline looks for `data/input/sample.mp4` and the Vosk model under `models/vosk/vosk-model-small-en-us-0.15/`.

Generated files go to `data/chunks/`, `data/audio/` and `data/outputs/`.

## Reusing outputs

The pipeline checks whether chunk, audio and JSON files already exist. That avoids some repeated work, but it does not verify that an existing file belongs to the current input or settings.

For another recording, clear the previous generated outputs first. This limitation was one reason to develop a more explicit input-identity check in the newer project.

## Performance

The code prints total and per-stage durations. This repository does not include a reproducible benchmark supporting a five-minute processing claim for a one-hour recording.

The transcription code reads WAV data in blocks and caches the loaded Vosk model in memory. Those choices reduce repeated model loading and avoid reading the entire audio file at once.
