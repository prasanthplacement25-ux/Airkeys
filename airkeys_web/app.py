from flask import Flask, render_template, Response, jsonify, request
from camera import generate_frames, get_typed_text, clear_typed_text

app = Flask(__name__)

# ── Main page ─────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

# ── Video stream route ────────────────────────────────────────
@app.route('/video_feed')
def video_feed():
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

# ── Get typed text ────────────────────────────────────────────
@app.route('/get_text')
def get_text():
    return jsonify({'text': get_typed_text()})

# ── Clear typed text ──────────────────────────────────────────
@app.route('/clear_text', methods=['POST'])
def clear_text():
    clear_typed_text()
    return jsonify({'status': 'cleared'})

# ── Run app ───────────────────────────────────────────────────
if __name__ == '__main__':
    print("✅ AirKeys Web Server Started!")
    print("🌐 Open browser and go to: http://localhost:5000")
    app.run(debug=False, threaded=True)