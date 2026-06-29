# AirKeys ⌨️
### Vision-Based Virtual Keyboard Using Hand Gesture Recognition

![Python](https://img.shields.io/badge/Python-3.10-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10-orange)
![Flask](https://img.shields.io/badge/Flask-2.x-red)

## 🚀 About The Project
AirKeys is a Vision-Based Virtual Keyboard that allows
users to type using hand gestures captured through a
standard webcam — no physical keyboard required!

## ⚙️ How It Works
1. Camera captures live video feed
2. MediaPipe detects hand in real time
3. Index fingertip position is tracked
4. Fingertip checks which key it hovers over
5. Hold finger for 1 second to type the letter
6. Typed text appears on screen instantly

## 🧠 Algorithms Used
- CNN Hand Detection — detects hand from camera
- Landmark Tracking — finds index fingertip point 8
- AABB Collision Detection — checks finger on key
- Dwell Time Algorithm — types after 1 second hold
- EMA Smoothing — removes shaky finger movements

## 🔧 Tech Stack
- Python 3.10
- OpenCV — Camera processing
- MediaPipe — Hand detection
- Flask — Web framework
- HTML, CSS, JavaScript — Frontend

## 📁 Project Structure
airkeys_web/
├── app.py
├── camera.py
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── script.js

## ▶️ How to Run
Install dependencies:
pip install opencv-python mediapipe flask numpy

Run the app:
py -3.10 app.py

Open browser:
http://localhost:5000

## 🎮 How to Use
- Show hand to camera — Hand detected
- Point index finger at key — Key highlights
- Hold finger for 1 second — Letter typed
- Point at BS — Backspace
- Point at SP — Space

## 🎓 About
This project is part of my MSc Artificial Intelligence
and Machine Learning course. It demonstrates how
Computer Vision can create touchless human-computer
interaction solutions.

## 👨‍💻 Author
Prasanth
MSc Artificial Intelligence and Machine Learning
