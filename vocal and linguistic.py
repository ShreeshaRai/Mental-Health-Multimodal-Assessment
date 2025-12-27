import librosa
import numpy as np
import speech_recognition as sr
from textblob import TextBlob
import joblib
import base64
from scipy.io import wavfile


try:
    clf = joblib.load("models/vocal_emotion_model.joblib")
    scaler = joblib.load("models/feature_scaler.joblib")
    MODEL_LOADED = True
    print("✓ Vocal emotion model loaded successfully")
except FileNotFoundError:
    print("⚠ Warning: Vocal emotion model not found. Using neutral predictions.")
    MODEL_LOADED = False


def extract_features_from_audio(audio_data, sample_rate=44100):
    """Extract MFCC-based features from audio"""
    try:
        mfcc = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=40)
        mfcc_mean = np.mean(mfcc, axis=1)
        mfcc_var = np.var(mfcc, axis=1)
        features = np.concatenate((mfcc_mean, mfcc_var))

        if MODEL_LOADED:
            return scaler.transform([features])
        else:
            return features.reshape(1, -1)

    except Exception as e:
        print(f"Feature extraction error: {e}")
        return None


def predict_vocal_emotion(features):
    """Predict emotion from extracted features"""
    if not MODEL_LOADED or features is None:
        return "neutral"

    try:
        return clf.predict(features)[0].lower()
    except Exception as e:
        print(f"Vocal prediction error: {e}")
        return "neutral"


def analyze_audio_chunk(audio_blob, sample_rate=44100):
    """Analyze vocal emotion from audio bytes or base64"""
    try:
        if isinstance(audio_blob, str):
            if "," in audio_blob:
                audio_blob = audio_blob.split(",")[1]
            audio_bytes = base64.b64decode(audio_blob)
        else:
            audio_bytes = audio_blob

        audio_data = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32)
        audio_data /= 32768.0

        features = extract_features_from_audio(audio_data, sample_rate)
        return predict_vocal_emotion(features)

    except Exception as e:
        print(f"Audio analysis error: {e}")
        return "neutral"


def transcribe_audio(audio_bytes, sample_rate=44100):
    """Convert speech to text"""
    recognizer = sr.Recognizer()

    try:
        audio_data = sr.AudioData(audio_bytes, sample_rate, 2)
        return recognizer.recognize_google(audio_data)

    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        print(f"Speech API error: {e}")
        return ""
    except Exception as e:
        print(f"Transcription error: {e}")
        return ""


def analyze_sentiment(text):
    """Analyze sentiment from text"""
    if not text.strip():
        return {"polarity": 0.2, "subjectivity": 0.2}

    try:
        blob = TextBlob(text)
        return {
            "polarity": blob.sentiment.polarity,
            "subjectivity": blob.sentiment.subjectivity
        }
    except Exception as e:
        print(f"Sentiment error: {e}")
        return {"polarity": 0.0, "subjectivity": 0.0}


def aggregate_vocal_emotions(vocal_timeline):
    """Get dominant emotion from timeline"""
    if not vocal_timeline:
        return "neutral"

    from collections import Counter
    return Counter(vocal_timeline).most_common(1)[0][0]


if __name__ == "__main__":
    print("Vocal & linguistic analysis module loaded")
    print(f"Model status: {'Loaded' if MODEL_LOADED else 'Not loaded'}")
