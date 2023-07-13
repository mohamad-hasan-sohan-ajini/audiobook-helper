"""Flask app to run audio crop service"""

import io
import json
from uuid import uuid4

from flask import Flask, redirect, render_template, request, send_file, url_for

from crop import crop_audio, find_phrase_index

with open('static/e2p_dict.json') as f:
    e2p_dict = json.load(f)
app = Flask(__name__)


@app.route('/', methods=('GET', 'POST'))
def root():
    if request.method == 'GET':
        return render_template(
            'index.html',
            start_offset=5,
            audio_duration=180,
        )
    elif request.method == 'POST':
        # data integrity
        try:
            phrase = request.form['phrase'].strip()
            start_offset = int(request.form['start_offset'])
            audio_duration = int(request.form['audio_duration'])
        except:
            return render_template('error.html')
        # load and normalize alignment
        with open('static/the subtle art of not giving a fuck.json') as f:
            alignment = json.load(f)
        start, end = 0, 0
        words = []
        for item in alignment['words']:
            if 'start' in item:
                start = item['start']
                end = item['end']
            else:
                item['start'] = start
                item['end'] = end
            words.append(item)
        # try to find phrase
        try:
            phrase_index = find_phrase_index(phrase, alignment)
            max_index = len(words) - len(phrase.split(' ')) - 1
            if phrase_index == max_index:
                raise ValueError('phrase not found!')
            phrase_time = words[phrase_index]['start']
            start_time = max(phrase_time - start_offset, 0)
            end_time = start_time + audio_duration
            text = '\n'.join(
                [
                    (
                        item['word']
                        + ','
                        + str(round(item['start'] - start_time, 2))
                        + ','
                        + str(round(item['end'] - start_time, 2))
                        + ','
                        + ' + '.join(e2p_dict.get(item['word'].lower(), ['']))
                    )
                    for item
                    in words
                    if start_time < item['start'] < end_time
                ]
            )
            mp3_filename = f'{uuid4().hex}_{start_time:.2f}_{audio_duration}.mp3'
            return render_template(
                'result.html',
                text=text,
                mp3_filename=mp3_filename,
            )
        except Exception:
            return render_template('error.html')


@app.route('/<mp3_filename>')
def get_file(mp3_filename):
    print(f'{mp3_filename = }')
    _, start_time, audio_duration = mp3_filename.rstrip('.mp3').split('_')
    start_time = float(start_time)
    audio_duration = float(audio_duration)
    in_memory_mp3_file = crop_audio(
        'static/the subtle art of not giving a fuck.mp3',
        start_time,
        audio_duration,
    )
    return send_file(in_memory_mp3_file, mimetype="audio/mpeg")


if __name__ == '__main__':
    # python -m flask --debug --app app run
    app.run(host='0.0.0.0', port=8080, debug=True)
