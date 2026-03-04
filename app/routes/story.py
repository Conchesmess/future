
# This file handles the "story" features in the app.
# Users can create, view, edit, and delete stories.

from app import app, db, confirm_delete  # Import app, database, and delete helper
from app.classes.data import Story  # Story model
from app.classes.forms import StoryForm  # Form for stories
from datetime import datetime, timezone  # For dates and times
from flask import redirect, flash, session, url_for, render_template, request
from flask_login import current_user, login_required  # Login tools
import io
from vosk import Model, KaldiRecognizer
import soundfile as sf
import json
import librosa
import tempfile
import numpy as np

# Path to your Vosk model directory (adjust as needed)
VOSK_MODEL_PATH = "models/vosk-model-small-en-us-0.15"

# Helper function for Vosk transcription
def transcribe_with_vosk(audio_bytes):
    import tempfile
    import numpy as np
    with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
        tmp.write(audio_bytes)
        tmp.flush()
        data, samplerate = sf.read(tmp.name)
        print(f"[VOSK] Loaded audio: shape={data.shape}, dtype={data.dtype}, samplerate={samplerate}")
        # Convert to mono if needed
        if len(data.shape) > 1:
            data = data.mean(axis=1)
            print("[VOSK] Converted to mono.")
        # Resample to 16kHz if needed
        if samplerate != 16000:
            import librosa
            data = librosa.resample(data, orig_sr=samplerate, target_sr=16000)
            samplerate = 16000
            print("[VOSK] Resampled to 16kHz.")
        # Convert float32 PCM to int16 PCM
        if data.dtype != np.int16:
            data = (data * 32767).astype(np.int16)
            print("[VOSK] Converted to int16 PCM.")
        # Check for silence or very short audio
        if np.abs(data).mean() < 100:
            print("[VOSK] Warning: audio appears silent or too quiet.")
        model = Model(VOSK_MODEL_PATH)
        rec = KaldiRecognizer(model, samplerate)
        ok = rec.AcceptWaveform(data.tobytes())
        print(f"[VOSK] AcceptWaveform returned: {ok}")
        result = rec.Result()
        print(f"[VOSK] Raw result: {result}")
        text = json.loads(result).get("text", "")
        print(f"[VOSK] Transcript: {text}")
        return text
        
@app.route('/story/new', methods=['GET', 'POST'])
@app.route('/story/new/<blob>', methods=['GET', 'POST'])    
def newStory(blob=None):
    form = StoryForm()
    if form.validate_on_submit():
        audio_bytes = None
        # Handle file upload from form
        if form.audio.data:
            audio_bytes = form.audio.data.read()
        elif blob:
            if isinstance(blob, str):
                import base64
                try:
                    audio_bytes = base64.b64decode(blob)
                except Exception:
                    audio_bytes = None
            else:
                audio_bytes = blob
        transcript = None
        if audio_bytes:
            try:
                transcript = transcribe_with_vosk(audio_bytes)
            except Exception as e:
                transcript = f"[Transcription failed: {e}]"
        newStory = Story(
            title=form.title.data,
            content=transcript if transcript else form.content.data,
            author_id=current_user.id
        )
        if form.image.data:
            newStory.image = form.image.data.read()
        if audio_bytes:
            newStory.audio = audio_bytes
        db.session.add(newStory)
        db.session.commit()
        return redirect(url_for("story", id=newStory.id))
    return render_template("story_form.html", form=form)

@app.route('/story/list')
def stories():
    stories = Story.query.order_by(Story.createdate.desc()).all()
    return render_template("stories.html", stories=stories)

@app.route("/story/retranscribe/<int:id>")
def storyRetranscribe(id):
    thisStory = db.one_or_404(db.select(Story).filter_by(id=id))
    if thisStory.audio:
        # WTForms FileField gives a FileStorage object, use .read() to get bytes
        audio_bytes = thisStory.audio
    if audio_bytes:
        try:
            transcript = transcribe_with_vosk(audio_bytes)
        except Exception as e:
            flash(f"[Transcription failed: {e}]")
        else:
            thisStory.content = transcript
            db.session.commit()
            flash("New transcription saved")
    return redirect(url_for('story',id=id))


# View a single story
@app.route('/story/<int:id>')
def story(id):
    thisStory = db.one_or_404(db.select(Story).filter_by(id=id))
    return render_template("story.html",story=thisStory)

# Edit a story
@app.route('/story/edit/<int:id>', methods=['GET', 'POST'])
def editStory(id):
    thisStory = db.one_or_404(db.select(Story).filter_by(id=id))
    form = StoryForm()
    if form.validate_on_submit():
        thisStory.title = form.title.data
        thisStory.content = form.content.data
        if form.image.data:
            thisStory.image = form.image.data.read()
        if form.audio.data:
            thisStory.audio = form.audio.data.read()
        db.session.commit()
        return redirect(url_for('story',id=id))
    form.title.data = thisStory.title
    form.content.process_data(thisStory.content)
    return render_template('story_form_edit.html',form=form)

# Delete a story
@app.route('/story/delete/<int:id>', methods=['GET', 'POST'])
@confirm_delete(Story, redirect_url='/story/list', message_fields=['title','author','content'], message_date_field = 'createdate')
def deleteStory(id):
    thisStory = db.one_or_404(db.select(Story).filter_by(id=id))
    db.session.delete(thisStory)
    db.session.commit()
    return redirect(url_for("stories"))

@app.route('/story/recaudio')
def storyAudio():
    print("bob")
    print(request.url_root)
    return render_template("storyAudio.html")