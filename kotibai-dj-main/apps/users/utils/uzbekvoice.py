import os.path

import requests
from rest_framework.exceptions import ValidationError

from root.settings import UZBEK_VOICE_KEY


def stt_api(file_path, endpoint_url, lang):
    url = 'https://uzbekvoice.ai/api/v1/stt'
    headers = {
        "Authorization": UZBEK_VOICE_KEY
    }

    files = {
        "file": (os.path.basename(file_path), open(file_path, "rb")),
    }
    data = {
        "return_offsets": "false",
        "run_diarization": "false",
        "language": 'ru-uz',
        "blocking": "false",
        "webhook_notification_url": endpoint_url
    }

    try:
        response = requests.post(url, headers=headers, files=files, data=data)
        if response.status_code == 200:
            return response.json()
        else:
            raise ValidationError(
                {"detail": f"Request failed with status code {response.status_code}: {response.text}"})

    except requests.exceptions.Timeout:
        raise ValidationError({"detail": "Request timed out. The API response took too long to arrive."})
