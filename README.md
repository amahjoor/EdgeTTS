# Ultra-Simple TTS Program

A simple text-to-speech program that uses Microsoft Edge TTS voices from your `voices.txt` file.

## Setup

1. Install Python 3.7 or higher
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Interactive Mode (Recommended)
```bash
python simple_tts.py
```

This will start an interactive session where you can:
- Browse and search voices
- Select voices by number
- Convert text to speech
- Save audio files

### Command Line Mode
```bash
# Speak text with a specific voice
python simple_tts.py "en-US-AriaNeural" "Hello, this is a test!"

# Save to file
python simple_tts.py "en-US-AriaNeural" "Hello world" "output.mp3"
```

## Interactive Commands

- `list` or `l` - Show all available voices
- `search <query>` or `s <query>` - Search voices (by language, gender, or name)
- `speak <text>` - Use the last selected voice to speak text
- `bulk <number>` - Test multiple voices (e.g., `bulk 10`)
- `bulk all` - Test ALL 302 voices (may take a while!)
- `quit` or `q` - Exit the program
- Type a number to select a voice from the displayed list
- Type any text to speak it with the currently selected voice

## Examples

### Search for English voices:
```
🎯 Enter command: search english
```

### Select a voice and speak:
```
🎯 Enter command: 1
💬 Enter text to speak: Hello, how are you today?
```

### Quick speak with selected voice:
```
🎯 Enter command: This is a test of the text to speech system
```

## Voice File

Make sure your `voices.txt` file is in the same directory as the script. The program automatically parses this file to load all available voices.

## Bulk Voice Testing

For comprehensive voice testing, use the dedicated bulk testing script:

### Test All Voices
```bash
# Quick test (first 20 voices)
python bulk_voice_test.py --quick

# Test all 302 voices
python bulk_voice_test.py

# Test with 5 concurrent processes (faster)
python bulk_voice_test.py --concurrent 10
```

### Test Specific Languages
```bash
# Test all English voices
python bulk_voice_test.py --language en

# Test all Chinese voices
python bulk_voice_test.py --language zh

# Test all Spanish voices and save audio samples
python bulk_voice_test.py --language es --save-audio
```

### Save Audio Samples
```bash
# Save audio files for all voices (creates voice_samples directory)
python bulk_voice_test.py --save-audio

# Save samples for specific language
python bulk_voice_test.py --language en --save-audio
```

The bulk tester will:
- Test each voice with appropriate text in its native language
- Show real-time progress and results
- Generate comprehensive statistics
- Save audio samples (optional)
- Handle errors gracefully

## Notes

- Audio will play automatically on your system
- Temporary files are cleaned up automatically
- Works on Windows, macOS, and Linux
- No internet connection required after initial setup