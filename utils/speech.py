import asyncio
import edge_tts
from pydub import AudioSegment
from pydub.playback import play
import tempfile
import os


DEFAULT_VOICE = "en-US-GuyNeural"  # Race engineer voice


async def synthesize_speech(text: str, voice: str = DEFAULT_VOICE):
    """Convert text → spoken audio using Edge-TTS."""
    communicate = edge_tts.Communicate(text, voice)

    # Temp output WAV
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        out_path = tmp.name

    await communicate.save(out_path)
    return out_path


def text_to_speech(text: str, voice: str = DEFAULT_VOICE):
    """Blocking wrapper that Streamlit can call safely."""
    try:
        audio_path = asyncio.run(synthesize_speech(text, voice))

        # Load WAV and play
        audio = AudioSegment.from_wav(audio_path)
        play(audio)

        # Remove temp file
        os.remove(audio_path)

    except Exception as e:
        print("TTS error:", e)
