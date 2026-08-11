"""
BSS YouTube Downloader ...Web Interface
Flask application serves the web UI and handles downloads

Author: Watchman Eugenius
Date: 2026
Version: 1.0.0
"""

from flask import Flask, render_template, request, jsonify, send_file
from downloader import YouTubeDownloader
import os
import tempfile
import json
from datetime import datetime

# initialise Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key'

# initialise downloader
downloader = YouTubeDownloader()

# stats tracking
stats = {
    'total': 0,
    'successful': 0,
    'failed': 0
}

@app.route('/')
def index():
    """
    Render main page
    """
    return render_template('index.html')

@app.route('/api/info', methods=['POST'])
def get_video_info():
    """
    API endpoint to get video info
    """
    try:
        data = request.get_json()
        url = data.get('url')
    
        if not url:
            return jsonify({'error': 'No URL provided'}), 400
        
        # get video info 
        yt = downloader.get_video_info(url)
        
        if yt is None:
            return jsonify({'error': 'Could not fetch video info'}), 404
        
        # prepare response
        info = {
            'title': yt.title,
            'views': yt.views,
            'length': yt.length,
            'publish_date': yt.publish_date.strftime('%Y-%m-%d') if yt.publish_date else None,
            'rating': yt.rating,
            'author': yt.description[:200],
            'thumbnail': yt.thumbnail_url        
        }
        
        return jsonify(info)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/api/download', mathods=['POST'])
def downlaod_video():
    """
    API endpoint to download video
    """
    try:
        data = request.get_json()
        url = data.get('url')
        quality = data.get('quality', 'highest')
        filename = data.get('filename', None)
        
        if not url:
            return jsonify({'error': 'No URL provided'}), 400
        
        # download video
        success = downloader.download_video(url, quality, filename)
        
        # update status
        stats['total'] += 1
        if success:
            stats['successful'] += 1
            return jsonify({
                'success': True,
                'message': 'Download completed',
                'file': filename,
                'stats': stats
            })
        else:
            stats['failed'] += 1   
            return jsonify({
                'success': False,
                'message': 'Download failed',
                'stats': stats
            }), 500
            
    except Exception as e:
        stats['total'] += 1
        stats['failed'] += 1
        return jsonify({'error': str(e)}), 500
    

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """
    Get download stats
    """
    return jsonify(stats)


@app.route('/api/logs', methods=['GET'])
def get_logs():
    """
    Get download logs
    """
    try:
        log_file = downloader.log_file
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = f.read()
            return jsonify({'logs': logs})
        else:
            return jsonify({'logs': 'No logs available'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
if __name__ == '__main__':
    # run app
    app.run(debug=True, host='0.0.0.0', port=5000)
        
                
    
    
    