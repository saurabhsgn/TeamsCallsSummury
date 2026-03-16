# TeamsCallsSummury

Local meeting assistant for Teams-style calls. It can:

- listen live from your system speaker
- listen live from your microphone
- mix both together for the full meeting conversation
- create live transcript updates while the call is running
- create live meeting notes and live MoM updates while the call is running
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
- minutes of meeting (MoM)

Outputs are written as:

- transcript text file
- Markdown summary
- JSON summary
- Markdown MoM

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

## No-dependency offline utility

If you want a local utility that works without internet and without installing Python packages, use:

```powershell
python offline_mom.py `
  --source C:\meetings\meeting_transcript.txt `
  --title "Weekly Review"
```

This utility:

- uses only the Python standard library
- does not download anything
- does not call any network APIs
- generates summary Markdown, summary JSON, and MoM Markdown

Important limitations:

- it starts from a local transcript file
- it does not transcribe audio or video
- a ScreenRec share link cannot be processed offline because the media is hosted remotely

Use `main.py` when you want audio or video transcription with already-available local models.

## One-command media to MoM

If your local Whisper model is already available on the machine, you can now use a single command:

```powershell
python mom_ready.py --source C:\meetings\call.mp4
```

Or use the repo-provided launcher with no activation step:

```powershell
run_mom.bat "C:\meetings\call.mp4"
```

It also accepts a direct media URL or supported ScreenRec share URL:

```powershell
python mom_ready.py --source "https://screenrec.com/share/your-link"
```

Notes:

- for a local file, this can run fully locally
- for a URL, internet is required because the media must be fetched first
- summarization is heuristic by default, so no LLM is required
- if no title is provided, the file name is used automatically

## Ready-to-use runtime expectation

This repo is now set up so usage does not require a compile or build step.

What "ready to use" means here:

- no compile step
- no packaging step
- no model flag required in the normal path
- run directly with `mom_ready.py` or `run_mom.bat`

What still must already exist on the machine:

- Python runtime in `.venv`
- `faster-whisper` already installed in that environment
- at least one local cached Whisper model

If you want a truly portable drop-in folder with no Python dependency at all, that would need bundling into an executable, which is a separate packaging task.

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

```powershell
python main.py sources
```

Use the returned `speaker.id` and `microphone.id` values in later commands.

### 2. Capture live audio only

```powershell
python main.py capture `
  --speaker-id "<speaker-id>" `
  --microphone-id "<microphone-id>" `
  --audio-out outputs\live_meeting.wav
```

### 3. Capture live audio and summarize after the call ends

```powershell
python main.py run `
  --title "Architecture Review" `
  --speaker-id "<speaker-id>" `
  --microphone-id "<microphone-id>" `
  --whisper-model C:\models\faster-whisper\small.en `
  --llm-model C:\models\llm\mistral-7b-instruct-v0.2.Q4_K_M.gguf
```

### 4. Listen live and keep updating notes and MoM during the call

```powershell
python main.py live `
  --title "Weekly Functional Review" `
  --speaker-id "<speaker-id>" `
  --microphone-id "<microphone-id>" `
  --whisper-model C:\models\faster-whisper\small.en `
  --llm-model C:\models\llm\mistral-7b-instruct-v0.2.Q4_K_M.gguf `
  --chunk-seconds 45 `
  --summary-every-chunks 2
```

What `live` does:

- listens to system speaker and microphone continuously
- cuts audio into local chunks
- transcribes each chunk locally
- keeps appending to a transcript file
- refreshes summary and MoM files during the meeting
- writes final versions again when the session ends

If you only want Teams audio and not your microphone:

```powershell
python main.py live `
  --title "Client Call" `
  --speaker-id "<speaker-id>" `
  --no-mic `
  --whisper-model C:\models\faster-whisper\small.en
```

### 5. Process a local audio or video file

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

## How live Teams listening works

The app does not connect to Teams directly. It listens to your Windows audio devices:

- system speaker capture: hears what Teams is playing on your computer
- microphone capture: hears your microphone input
- mixed capture: combines both into one stream before transcription

That means it can work live during a Teams call without waiting for a recorded file.

## Live output files

During `live` mode, the following files are refreshed repeatedly:

- `outputs\<meeting>_YYYYMMDD_HHMMSS_transcript.txt`
- `outputs\<meeting>_YYYYMMDD_HHMMSS_summary.md`
- `outputs\<meeting>_YYYYMMDD_HHMMSS_summary.json`
- `outputs\<meeting>_YYYYMMDD_HHMMSS_mom.md`

Chunk WAV files are also stored under:

- `outputs\<meeting>_YYYYMMDD_HHMMSS_chunks\`

## Notes

- On Windows, speaker capture depends on loopback support from the local audio stack.
- If speaker capture is missing, try a different output device or a virtual audio cable.
- Better local models improve note quality significantly.
- Shorter chunks give faster live updates but increase processing overhead.

## Current limitations

- no speaker diarization yet
- no desktop UI yet
- live summaries are refreshed in intervals, not word-by-word
- direct media links must point to actual media or a supported ScreenRec share page
- very long meetings can be slow on CPU-only machines
