from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
import requests
import random
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# Load proxy credentials from environment variables
PROXY_HTTP = os.getenv('PROXY_HTTP')
PROXY_HTTPS = os.getenv('PROXY_HTTPS')
PROXY_LIST = [
    {
        'http': PROXY_HTTP,
        'https': PROXY_HTTPS
    }
]
# Make sure to set PROXY_HTTP and PROXY_HTTPS in your .env file

# Load shared secret from environment variable
SHARED_SECRET = os.getenv("SHARED_SECRET")

@app.route('/transcript', methods=['POST'])
def get_transcript():
    try:
        data = request.json
        # Check shared secret
        if data.get('secret') != SHARED_SECRET:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        video_id = data.get('video_id')
        if not video_id:
            return jsonify({'success': False, 'error': 'video_id required'}), 400

        proxy = PROXY_LIST[0]  # Use the proxy

        # Try to get transcript (prefer English, fallback to any language)
        transcript_list = None
        language = None
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(
                video_id,
                languages=['en'],
                proxies=proxy
            )
            language = 'en'
        except Exception:
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(
                    video_id,
                    proxies=proxy
                )
                # Try to get language from first segment if available
                if transcript_list and 'language' in transcript_list[0]:
                    language = transcript_list[0]['language']
                else:
                    language = 'unknown'
            except Exception as e:
                return jsonify({'success': False, 'error': f'Transcript failed: {str(e)}'}), 404

        # Compose full transcript and segments
        full_transcript = ' '.join([item['text'] for item in transcript_list])
        segments = [
            {
                'start': item.get('start'),
                'duration': item.get('duration'),
                'text': item.get('text')
            } for item in transcript_list
        ]

        # Try to fetch video metadata via oEmbed (no API key required)
        title = None
        channel = None
        try:
            oembed_url = f'https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json'
            resp = requests.get(oembed_url, timeout=5)
            if resp.status_code == 200:
                meta = resp.json()
                title = meta.get('title')
                channel = meta.get('author_name')
        except Exception:
            pass  # Metadata is optional

        return jsonify({
            'success': True,
            'video_id': video_id,
            'title': title,
            'channel': channel,
            'language': language,
            'transcript': full_transcript,
            'segments': segments
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)