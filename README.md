# TeamsCallsSummury

Local meeting assistant for Teams-style calls. It can:

- listen live from your system speaker
- listen live from your microphone
- mix both together for the full meeting conversation
- process local audio files
- process local video files
- process a direct media link when you explicitly provide one
- create categorized meeting notes using local AI models only

## What it generates

- executive summary
- discussed points
- decisions
- action items
- open items
- blockers / risks
- conclusions
- technical notes
- functional notes
- next steps

Outputs are written as:

- transcript text file
- Markdown summary
- JSON summary

## Local-only model flow

The AI part runs locally:

- transcription uses a local Whisper model
- summarization uses an optional local GGUF LLM

If you do not provide an LLM, the app still builds structured notes using heuristic extraction.

Important:

- For local file input and live capture, the program does not need internet access.
- If you provide a direct `http://` or `https://` media link, the program will download that media once and process it locally afterward.
- It does not call cloud transcription or cloud summarization APIs.

## Install

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Local models

### Whisper model

Example:

```text
C:\models\faster-whisper\small.en
```

Pass it with `--whisper-model`.

### GGUF LLM model

Example:

```text
C:\models\llm\mistral-7b-instruct-v0.2.Q4_K_M.gguf
```

Pass it with `--llm-model`.

## Main commands

### 1. List live sources

This shows available microphones and speakers from the local machine.

```powershell
python main.py sources
```

Use the returned `speaker.id` and `microphone.id` values in later commands.

### 2. Capture live audio from system speaker and microphone

This is the mode you asked for instead of depending on a prepared recording file.

```powershell
python main.py capture `
  --speaker-id "<speaker-id>" `
  --microphone-id "<microphone-id>" `
  --audio-out outputs\live_meeting.wav
```

Press `Ctrl+C` to stop.

If you only want the meeting audio coming from Teams and not your microphone:

```powershell
python main.py capture `
  --speaker-id "<speaker-id>" `
  --no-mic `
  --audio-out outputs\teams_audio.wav
```

If you want a fixed duration:

```powershell
python main.py capture `
  --speaker-id "<speaker-id>" `
  --microphone-id "<microphone-id>" `
  --seconds 1800
```

### 3. Capture live audio and generate notes immediately

```powershell
python main.py run `
  --title "Architecture Review" `
  --speaker-id "<speaker-id>" `
  --microphone-id "<microphone-id>" `
  --whisper-model C:\models\faster-whisper\small.en `
  --llm-model C:\models\llm\mistral-7b-instruct-v0.2.Q4_K_M.gguf
```

### 4. Process a local audio file

```powershell
python main.py process `
  --source C:\meetings\call.wav `
  --title "Weekly Delivery Review" `
  --whisper-model C:\models\faster-whisper\small.en `
  --llm-model C:\models\llm\mistral-7b-instruct-v0.2.Q4_K_M.gguf
```

### 5. Process a local video file

```powershell
python main.py process `
  --source C:\meetings\call.mp4 `
  --title "Technical Design Walkthrough" `
  --whisper-model C:\models\faster-whisper\small.en `
  --llm-model C:\models\llm\mistral-7b-instruct-v0.2.Q4_K_M.gguf
```

### 6. Process a direct media link

```powershell
python main.py process `
  --source "https://server.example.local/media/meeting.mp4" `
  --title "Recorded Client Discussion" `
  --whisper-model C:\models\faster-whisper\small.en `
  --llm-model C:\models\llm\mistral-7b-instruct-v0.2.Q4_K_M.gguf
```

This works for direct downloadable media links, not generic web pages.

## How live listening works

The app does not connect to Teams directly. It listens to the machine audio devices:

- system speaker capture: hears what Teams is playing on your computer
- microphone capture: hears your microphone input
- mixed capture: combines both into one WAV file before transcription

This is the closest local-only approach to "listen to the meeting directly" without needing Teams integration or cloud services.

## Output files

Generated files look like:

- `outputs\architecture_review_YYYYMMDD_HHMMSS_transcript.txt`
- `outputs\architecture_review_YYYYMMDD_HHMMSS_summary.md`
- `outputs\architecture_review_YYYYMMDD_HHMMSS_summary.json`

## Notes

- On Windows, speaker capture depends on loopback support from the local audio stack.
- If speaker capture is missing, try a different output device or a virtual audio cable.
- `process --source` accepts audio or video as long as the local environment can decode the file.
- Better local models improve note quality significantly.

## Current limitations

- no speaker diarization yet
- no UI yet
- direct media links must point to the actual media file
- very long meetings can be slow on CPU-only machines
