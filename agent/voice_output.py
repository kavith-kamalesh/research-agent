from kokoro import KPipeline
import soundfile as sf
import numpy as np
import subprocess
import re
import threading

pipeline = KPipeline(lang_code='a')

def clean_text(text):
    text = re.sub(r'[*#`_]', '', text)
    text = re.sub(r'\n+', '. ', text)
    # Strip emojis and other symbol/pictograph unicode ranges
    text = re.sub(
        r'[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF\u2700-\u27BF\u2600-\u26FF]',
        '',
        text
    )
    return text.strip()

def _generate_and_play(text, voice, output_path):
    clean = clean_text(text)
    if not clean:
        return
    try:
        generator = pipeline(clean, voice=voice)
        all_audio = []
        for i, (gs, ps, audio) in enumerate(generator):
            all_audio.append(audio)
        if not all_audio:
            return
        full_audio = np.concatenate(all_audio)
        sf.write(output_path, full_audio, 24000)
        subprocess.run(["afplay", output_path])
    except Exception as e:
        print(f"[voice error] {e}")

def speak(text, voice="af_bella", output_path="voice_output.wav"):
    # Run in background thread so Mitchell doesn't freeze waiting for audio
    thread = threading.Thread(target=_generate_and_play, args=(text, voice, output_path))
    thread.start()
