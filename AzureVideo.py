#!/usr/bin/env python
# coding: utf-8

import json
import logging
import os
import sys
import time
from pathlib import Path
import requests


"""
This script provides a Python class for interacting with the Microsoft Azure Text-to-Speech (TTS) API to create and synthesize animated avatars with speech from text input. It allows the user to submit a synthesis job, check its status, and download the resulting video file once the job is completed.

### Key Functions:
1. `submit_synthesis()`: 
   - Sends a request to the Azure TTS service to synthesize speech with a talking avatar based on the provided text.
   - The payload includes avatar style, video format, and codec details.
   - Returns a Job ID upon successful submission.

2. `get_synthesis(job_id)`:
   - Checks the status of the submitted synthesis job using the provided job ID.
   - If the job succeeds, it retrieves the download URL for the synthesized video and triggers the download process.

3. `download_video(video_url)`:
   - Downloads the synthesized avatar video using the provided URL and saves it as 'downloaded.mp4' in the local 'video' folder.

4. `list_synthesis_jobs(skip=0, top=100)`:
   - Retrieves and lists all the batch synthesis jobs under the current Azure subscription, allowing users to track previous jobs.

### How to Use:
1. Ensure you have valid Azure credentials (SPEECH_KEY and SPEECH_REGION) either set as environment variables or manually inserted into the `SUBSCRIPTION_KEY` and `SERVICE_REGION`.
   
2. Run the script, which will:
   - Submit a text-to-avatar synthesis job using predefined text, avatar style, and voice settings.
   - Continuously check the status of the job until it either succeeds or fails.
   - Download the video upon successful synthesis.

### Requirements:
- `requests` library for making HTTP requests.
- Set environment variables `SPEECH_KEY` and `SPEECH_REGION` with your Azure credentials.
"""

logging.basicConfig(stream=sys.stdout, level=logging.INFO,  # set to logging.DEBUG for verbose output
        format="[%(asctime)s] %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p %Z")
logger = logging.getLogger(__name__)

# Your Speech resource key and region
# This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
SUBSCRIPTION_KEY = "YOUR-AZURE-KEYS"
SERVICE_REGION = "westus2"

NAME = "Simple avatar synthesis"
DESCRIPTION = "Simple avatar synthesis description"

# The service host suffix.
SERVICE_HOST = "customvoice.api.speech.microsoft.com"


def submit_synthesis():
    url = f'https://{SERVICE_REGION}.{SERVICE_HOST}/api/texttospeech/3.1-preview1/batchsynthesis/talkingavatar'
    header = {
        'Ocp-Apim-Subscription-Key': SUBSCRIPTION_KEY,
        'Content-Type': 'application/json'
    }

    payload = {
        'displayName': NAME,
        'description': DESCRIPTION,
        "textType": "PlainText",
        'synthesisConfig': {
            "voice": "en-US-JennyNeural",
        },
        # Replace with your custom voice name and deployment ID if you want to use custom voice.
        # Multiple voices are supported, the mixture of custom voices and platform voices is allowed.
        # Invalid voice name or deployment ID will be rejected.
        'customVoices': {
            # "YOUR_CUSTOM_VOICE_NAME": "YOUR_CUSTOM_VOICE_ID"
        },
        "inputs": [
            {
                "text": "Hi, my name is Alexa. I'm a virtual assistant created by Amazon. I'm here to help you",
            },
        ],
        "properties": {
            "customized": False, # set to True if you want to use customized avatar
            "talkingAvatarCharacter": "lisa",  # talking avatar character
            "talkingAvatarStyle": "graceful-sitting",  # talking avatar style, required for prebuilt avatar, optional for custom avatar
            "videoFormat": "mp4",  # mp4 or webm, webm is required for transparent background
            "videoCodec": "vp9",  # hevc, h264 or vp9, vp9 is required for transparent background; default is hevc
            "subtitleType": "soft_embedded",
            "backgroundColor": "white",
        }
    }

    response = requests.post(url, json.dumps(payload), headers=header)
    if response.status_code < 400:
        logger.info('Batch avatar synthesis job submitted successfully')
        logger.info(f'Job ID: {response.json()["id"]}')
        return response.json()["id"]
    else:
        logger.error(f'Failed to submit batch avatar synthesis job: {response.text}')

def download_video(video_url):
    video_download_request = requests.get(video_url)
    if video_download_request.status_code == 200:
        # Save the video to a file
        with open('video/downloaded.mp4', 'wb') as file:
            file.write(video_download_request.content)
        print("Download successful!")

def get_synthesis(job_id):
    url = f'https://{SERVICE_REGION}.{SERVICE_HOST}/api/texttospeech/3.1-preview1/batchsynthesis/talkingavatar/{job_id}'
    header = {
        'Ocp-Apim-Subscription-Key': SUBSCRIPTION_KEY
    }
    response = requests.get(url, headers=header)
    if response.status_code < 400:
        logger.debug('Get batch synthesis job successfully')
        logger.debug(response.json())
        if response.json()['status'] == 'Succeeded':
            logger.info(f'Batch synthesis job succeeded, download URL: {response.json()["outputs"]["result"]}')
            download_video(response.json()["outputs"]["result"])
        return response.json()['status']
    else:
        logger.error(f'Failed to get batch synthesis job: {response.text}')
  
def list_synthesis_jobs(skip: int = 0, top: int = 100):
    """List all batch synthesis jobs in the subscription"""
    url = f'https://{SERVICE_REGION}.{SERVICE_HOST}/api/texttospeech/3.1-preview1/batchsynthesis/talkingavatar?skip={skip}&top={top}'
    header = {
        'Ocp-Apim-Subscription-Key': SUBSCRIPTION_KEY
    }
    response = requests.get(url, headers=header)
    if response.status_code < 400:
        logger.info(f'List batch synthesis jobs successfully, got {len(response.json()["values"])} jobs')
        logger.info(response.json())
    else:
        logger.error(f'Failed to list batch synthesis jobs: {response.text}')
  
  
if __name__ == '__main__':
    job_id = submit_synthesis()
    if job_id is not None:
        while True:
            status = get_synthesis(job_id)
            if status == 'Succeeded':
                logger.info('batch avatar synthesis job succeeded')
                break
            elif status == 'Failed':
                logger.error('batch avatar synthesis job failed')
                break
            else:
                logger.info(f'batch avatar synthesis job is still running, status [{status}]')
                time.sleep(5)
