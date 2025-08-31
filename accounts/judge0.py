import requests
import time
from django.conf import settings

HEADERS = {
    "X-RapidAPI-Host": settings.JUDGE0_API_HOST,
    "X-RapidAPI-Key": settings.JUDGE0_API_KEY,
    "Content-Type": "application/json",
}

API_URL = settings.JUDGE0_API_URL

def submit_code_to_judge0(sourcecode, language_id, stdin = "", expected_output = "", time_limit = 2, memory_limit = 141000 ):
    payload ={
        "source_code": sourcecode,
        "language_id" : language_id,
        "stdin": stdin,
        "expected_output": expected_output,
        "cpu_time_limit": time_limit,
        "memory_limit": memory_limit,
    }

    response = requests.post(
         f"{API_URL}/submissions?base64_encoded=false&wait=false",
         json = payload,
         headers= HEADERS,
    )

    response.raise_for_status()
    return response.json()["token"]

def get_submission_result(token, retries = 20, wait_time = 0.5):
    for _ in range(retries):
        response = requests.get(
            f"{API_URL}/submissions/{token}?base64_encoded=false",
            headers=HEADERS
        )

        response.raise_for_status()
        result = response.json()
        status_id = result.get("status", {}).get("id",0)

        if status_id in [1,2]:
            time.sleep(wait_time)
            continue
        return result
    return None