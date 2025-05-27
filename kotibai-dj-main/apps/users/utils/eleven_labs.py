from elevenlabs import ElevenLabs
import os

from root.settings import ELEVENLABS_API_KEY


def speech_to_text_eleven_labs(file_path, model_id="scribe_v1", language_code=None,
                   tag_audio_events=True, num_speakers=None,
                   timestamps_granularity="word", diarize=False):

    """
    Convert speech to text using ElevenLabs API.

    Args:
        api_key (str): Your ElevenLabs API key
        file_path (str): Path to the audio or video file to transcribe
        model_id (str): The ID of the model to use for transcription (default: "scribe_v1")
        language_code (str, optional): ISO-639-1 or ISO-639-3 language code
        tag_audio_events (bool): Whether to tag audio events like (laughter), (footsteps), etc.
        num_speakers (int, optional): Maximum number of speakers in the audio (1-32)
        timestamps_granularity (str): Granularity of timestamps ('none', 'word', 'character')
        diarize (bool): Whether to annotate which speaker is talking

    Returns:
        dict: Transcription result containing text, words with timing info, etc.
    """


    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

    params = {
        "model_id": model_id,
        "tag_audio_events": tag_audio_events,
        "timestamps_granularity": timestamps_granularity,
        "diarize": diarize
    }

    if language_code:
        params["language_code"] = language_code

    if num_speakers:
        if not 1 <= num_speakers <= 32:
            raise ValueError("Number of speakers must be between 1 and 32")
        params["num_speakers"] = num_speakers

    with open(file_path, "rb") as file:
        params["file"] = file
        result = client.speech_to_text.convert(**params)

    return result

