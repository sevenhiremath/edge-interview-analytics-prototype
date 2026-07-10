from pathlib import Path
import json
import time
from interview_pipeline.chunking import split_video_into_chunks
from interview_pipeline.audio_extract import extract_audio
from interview_pipeline.stt import transcribe_audio
from interview_pipeline.filler_detection import detect_filler_words


def run_pipeline():
    print("==================================================")
    print("[PIPELINE] Starting interview processing pipeline")
    print("==================================================")
    start_time = time.time()
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    input_video = PROJECT_ROOT / "data/input/sample.mp4"
    chunks_dir = PROJECT_ROOT / "data/chunks"
    audio_dir = PROJECT_ROOT / "data/audio"
    outputs_dir = PROJECT_ROOT / "data/outputs"
    model_path = PROJECT_ROOT / "models/vosk/vosk-model-small-en-us-0.15"

    outputs_dir.mkdir(parents=True, exist_ok=True)
    chunks_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Chunking
    print(f"\n--- STAGE 1: Video Chunking ---")
    chunking_start_time = time.time()
    existing_chunks = list(chunks_dir.glob("chunk_*.mp4"))
    
    if existing_chunks:
        print(f"[PIPELINE] Found {len(existing_chunks)} existing chunks. Skipping chunking step.")
        chunks = sorted(existing_chunks, key=lambda x: x.name)
    else:
        print(f"[PIPELINE] Chunking video {input_video.name}")
        chunks = split_video_into_chunks(
            input_path=input_video,
            output_dir=chunks_dir,
            chunk_duration=10
        )
        cchunks = sorted(chunks, key=lambda x: x.name)
        print(f"[PIPELINE] Total chunks generated: {len(chunks)}")
        
    chunking_time = time.time() - chunking_start_time
    print(f"[PIPELINE] Stage 1 completed in {chunking_time:.2f} seconds")

    print(f"\n--- STAGE 2: Audio Extraction ---")
    print(f"--- STAGE 3: Speech-to-Text ---")
    # Process each chunk
    for i, chunk in enumerate(chunks, 1):
        chunk_start_time = time.time()
        print(f"\n[PIPELINE] Processing chunk {i}/{len(chunks)}: {chunk.name}")
        
        output_file = outputs_dir / f"{chunk.stem}.json"
        
        # Skip logic for transcription
        if output_file.exists():
            print(f"  -> Output JSON exists ({output_file.name}). Skipping processing for {chunk.name}.")
            continue
            
        # Step 2: Extract Audio
        audio_start_time = time.time()
        expected_audio_path = audio_dir / f"{chunk.stem}.wav"
        
        if expected_audio_path.exists():
            print(f"  -> Audio exists ({expected_audio_path.name}). Skipping extraction.")
            audio_path = expected_audio_path
        else:
            audio_path = extract_audio(chunk, audio_dir)
            print(f"  -> Extracted audio in {time.time() - audio_start_time:.2f} seconds")
        
        # Step 3: Transcribe Audio
        stt_start_time = time.time()
        transcript_result = transcribe_audio(audio_path, model_path)
        print(f"  -> Transcription completed in {time.time() - stt_start_time:.2f} seconds")
        
        # Step 3.5: Filler Word Detection
        filler_result = detect_filler_words(transcript_result)
        transcript_result["filler_analysis"] = {
            "filler_count": filler_result["filler_count"],
            "filler_words": filler_result["filler_words"]
        }
        
        # Step 4: Save Output
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(transcript_result, f, indent=2)
            
        chunk_end_time = time.time()
        print(f"[PIPELINE] Finished processing {chunk.name} in {chunk_end_time - chunk_start_time:.2f} seconds")

    total_time = time.time() - start_time
    print("==================================================")
    print(f"[PIPELINE] Pipeline processing complete in {total_time:.2f} seconds")
    print("==================================================")