#!/usr/bin/env python3
"""
Web Service for Notion Button Integration
Generates project snapshot on webhook trigger
"""

from flask import Flask, send_file, jsonify, request, make_response
from flask_cors import CORS
import subprocess
from pathlib import Path
import os
import json
from datetime import datetime
import hashlib
import hmac

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

# Configuration
BASE_DIR = Path(__file__).parent.parent
SNAPSHOTS_DIR = BASE_DIR / "snapshots"
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")  # Optional webhook verification

# Ensure snapshots directory exists
SNAPSHOTS_DIR.mkdir(exist_ok=True)

@app.route('/generate-snapshot', methods=['POST'])
def generate_snapshot():
    """Generate project snapshot on POST request"""
    try:
        # Optional: Verify webhook signature if secret is set
        if WEBHOOK_SECRET:
            signature = request.headers.get('X-Webhook-Signature', '')
            if not verify_webhook_signature(request.data, signature):
                return jsonify({'error': 'Invalid signature'}), 401

        print(f"[{datetime.now()}] Generating snapshot...")

        # Run the snapshot script
        result = subprocess.run(
            ['python', 'scripts/compile_project_snapshot.py', '--no-pull'],
            capture_output=True,
            text=True,
            cwd=BASE_DIR
        )

        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return jsonify({'error': 'Failed to generate snapshot', 'details': result.stderr}), 500

        # Find the latest snapshot
        files = sorted(SNAPSHOTS_DIR.glob('project_snapshot_*.md'),
                      key=lambda x: x.stat().st_mtime,
                      reverse=True)

        if not files:
            return jsonify({'error': 'No snapshot file found'}), 500

        latest_file = files[0]
        print(f"[{datetime.now()}] Snapshot generated: {latest_file.name}")

        # Return file as download
        response = make_response(send_file(
            latest_file,
            as_attachment=True,
            download_name=f"project_snapshot_{datetime.now().strftime('%Y%m%d')}.md",
            mimetype='text/markdown'
        ))

        # Add headers for better compatibility
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['X-Snapshot-Generated'] = datetime.now().isoformat()

        return response

    except Exception as e:
        print(f"Exception: {str(e)}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/generate-snapshot-json', methods=['POST'])
def generate_snapshot_json():
    """Generate snapshot and return as JSON (alternative to file download)"""
    try:
        print(f"[{datetime.now()}] Generating snapshot (JSON response)...")

        # Run the snapshot script
        result = subprocess.run(
            ['python', 'scripts/compile_project_snapshot.py', '--no-pull'],
            capture_output=True,
            text=True,
            cwd=BASE_DIR
        )

        if result.returncode != 0:
            return jsonify({'error': 'Failed to generate snapshot', 'details': result.stderr}), 500

        # Find and read the latest snapshot
        files = sorted(SNAPSHOTS_DIR.glob('project_snapshot_*.md'),
                      key=lambda x: x.stat().st_mtime,
                      reverse=True)

        if not files:
            return jsonify({'error': 'No snapshot file found'}), 500

        latest_file = files[0]

        with open(latest_file, 'r', encoding='utf-8') as f:
            content = f.read()

        return jsonify({
            'success': True,
            'filename': latest_file.name,
            'generated': datetime.now().isoformat(),
            'content': content,
            'size': len(content),
            'download_url': f"/download/{latest_file.name}"
        })

    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/download/<filename>', methods=['GET'])
def download_snapshot(filename):
    """Download a specific snapshot file"""
    try:
        filepath = SNAPSHOTS_DIR / filename

        # Security: Ensure file is in snapshots directory
        if not filepath.exists() or not filepath.is_relative_to(SNAPSHOTS_DIR):
            return jsonify({'error': 'File not found'}), 404

        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='text/markdown'
        )

    except Exception as e:
        return jsonify({'error': 'Failed to download file', 'details': str(e)}), 500

@app.route('/list-snapshots', methods=['GET'])
def list_snapshots():
    """List all available snapshots"""
    try:
        files = sorted(SNAPSHOTS_DIR.glob('project_snapshot_*.md'),
                      key=lambda x: x.stat().st_mtime,
                      reverse=True)

        snapshots = []
        for f in files[:10]:  # Last 10 snapshots
            stat = f.stat()
            snapshots.append({
                'filename': f.name,
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'download_url': f"/download/{f.name}"
            })

        return jsonify({
            'snapshots': snapshots,
            'total': len(files)
        })

    except Exception as e:
        return jsonify({'error': 'Failed to list snapshots', 'details': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Notion Snapshot Generator',
        'timestamp': datetime.now().isoformat(),
        'snapshots_dir': str(SNAPSHOTS_DIR)
    })

@app.route('/', methods=['GET'])
def index():
    """Simple web interface"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Project Snapshot Generator</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
            }
            button {
                background: #2563eb;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
            }
            button:hover {
                background: #1d4ed8;
            }
            .status {
                margin-top: 20px;
                padding: 10px;
                border-radius: 5px;
            }
            .success {
                background: #d4edda;
                color: #155724;
            }
            .error {
                background: #f8d7da;
                color: #721c24;
            }
            .snapshots {
                margin-top: 30px;
            }
            .snapshot-item {
                padding: 10px;
                margin: 5px 0;
                background: #f0f0f0;
                border-radius: 5px;
                display: flex;
                justify-content: space-between;
            }
        </style>
    </head>
    <body>
        <h1>🎅 Project Snapshot Generator</h1>
        <p>Generate a comprehensive markdown snapshot of the Santa's Workshop project.</p>

        <button onclick="generateSnapshot()">Generate New Snapshot</button>

        <div id="status"></div>

        <div class="snapshots">
            <h2>Available Snapshots</h2>
            <div id="snapshot-list">Loading...</div>
        </div>

        <script>
            async function generateSnapshot() {
                const status = document.getElementById('status');
                status.className = 'status';
                status.textContent = 'Generating snapshot...';

                try {
                    const response = await fetch('/generate-snapshot-json', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({})
                    });

                    const data = await response.json();

                    if (data.success) {
                        status.className = 'status success';
                        status.innerHTML = `
                            ✅ Snapshot generated successfully!<br>
                            Size: ${data.size.toLocaleString()} characters<br>
                            <a href="${data.download_url}" download>Download ${data.filename}</a>
                        `;
                        loadSnapshots();
                    } else {
                        throw new Error(data.error);
                    }
                } catch (error) {
                    status.className = 'status error';
                    status.textContent = '❌ Error: ' + error.message;
                }
            }

            async function loadSnapshots() {
                try {
                    const response = await fetch('/list-snapshots');
                    const data = await response.json();

                    const list = document.getElementById('snapshot-list');
                    if (data.snapshots.length === 0) {
                        list.innerHTML = '<p>No snapshots available</p>';
                    } else {
                        list.innerHTML = data.snapshots.map(s => `
                            <div class="snapshot-item">
                                <div>
                                    <strong>${s.filename}</strong><br>
                                    <small>${new Date(s.created).toLocaleString()}</small>
                                </div>
                                <a href="${s.download_url}" download>Download</a>
                            </div>
                        `).join('');
                    }
                } catch (error) {
                    console.error('Failed to load snapshots:', error);
                }
            }

            // Load snapshots on page load
            loadSnapshots();
        </script>
    </body>
    </html>
    """
    return html

def verify_webhook_signature(payload, signature):
    """Verify webhook signature if secret is set"""
    if not WEBHOOK_SECRET:
        return True

    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, signature)

if __name__ == '__main__':
    print("=" * 50)
    print("🎅 Santa's Workshop Snapshot Generator")
    print("=" * 50)
    print(f"Base directory: {BASE_DIR}")
    print(f"Snapshots directory: {SNAPSHOTS_DIR}")
    print("")
    print("Endpoints:")
    print("  POST /generate-snapshot - Generate and download snapshot")
    print("  POST /generate-snapshot-json - Generate and return as JSON")
    print("  GET  /list-snapshots - List available snapshots")
    print("  GET  /download/<filename> - Download specific snapshot")
    print("  GET  /health - Health check")
    print("  GET  / - Web interface")
    print("")
    print("Starting server on http://0.0.0.0:5000")
    print("=" * 50)

    # Run on all network interfaces
    app.run(host='0.0.0.0', port=5000, debug=True)