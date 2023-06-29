"""Audio cropping script"""

import io
import subprocess
from typing import Any

import ffmpeg
import librosa
import soundfile as sf


def find_phrase_index(
        phrase: str,
        alignment: list[dict[str, Any]],
        plus_phrase_length: bool = False,
) -> int:
    phrase = phrase.lower()
    num_words = len(phrase.split())
    num_items = len(alignment['words'])
    for i in range(num_items - num_words):
        items = alignment['words'][i:i + num_words]
        try:
            words = ' '.join([item['word'] for item in items])
            aligned_words = ' '.join([item['alignedWord'] for item in items])
        except KeyError:
            aligned_words = words = ''
        if phrase == aligned_words.lower() or phrase == words.lower():
            break
    if plus_phrase_length:
        return i + num_words
    return i


def crop_audio(
        audio_path: str,
        start_time: float,
        audio_duration: float,
) -> None:
    # crop audio
    segment, sr = librosa.load(
        audio_path,
        offset=start_time,
        duration=audio_duration,
        sr=None,
    )
    in_memory_file = io.BytesIO()
    sf.write(in_memory_file, segment, sr, format='wav')
    in_memory_file.seek(0)
    input = in_memory_file.read()
    with open('/tmp/tmp.wav', 'wb') as f:
        f.write(input)
    # convert to mp3
    args = (
        ffmpeg
        .input('pipe:')
        .output(
            'pipe:',
            format='mp3',
            ac=2,
            ar=22050,
            # acodec='libmp3lame',
        )
        .get_args()
    )
    ffmpeg_process = subprocess.Popen(
        ['ffmpeg'] + args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    mp3_content, _ = ffmpeg_process.communicate(input=input)
    ffmpeg_process.kill()
    return io.BytesIO(mp3_content)
