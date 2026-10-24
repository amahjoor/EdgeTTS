# Speak text with a Microsoft Edge neural voice

A small command-line player on top of the [`edge-tts`](https://pypi.org/project/edge-tts/) package. It is not that library. Voices come from `voices.txt` in this folder. You can talk to it interactively, or pass a voice short name, the text, and an optional MP3 path.

## Speak or save an MP3

```bash
pip install -r requirements.txt
python simple_tts.py
python simple_tts.py "en-US-AriaNeural" "Hello, this is a test!"
python simple_tts.py "en-US-AriaNeural" "Hello world" "output.mp3"
```

`requirements.txt` contains `edge-tts>=6.1.0`.

In the interactive prompt, `list` shows voices, `search english` filters them, a number selects one, and `speak ...` uses the last selection. `bulk 10` tries ten voices. `quit` exits.

## License

[MIT](LICENSE)
