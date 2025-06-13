from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
import re

app = Flask(__name__)

@app.route('/transcript', methods=['POST'])
def get_transcript():
    try:
        data = request.json
        video_id = data.get('video_id')
        
        if not video_id:
            return jsonify({'error': 'video_id required'}), 400
        
        # Get transcript
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Combine all text
        full_transcript = ' '.join([item['text'] for item in transcript_list])
        
        return jsonify({
            'transcript': full_transcript,
            'segments': transcript_list
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
