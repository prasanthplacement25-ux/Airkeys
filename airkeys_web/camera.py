import cv2
import mediapipe as mp
import numpy as np
import time

# ── MediaPipe setup ──────────────────────────────────────────
mp_hands = mp.solutions.hands
mp_draw  = mp.solutions.drawing_utils
hands    = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# ── Keyboard layout ──────────────────────────────────────────
keys_layout = [
    ["Q","W","E","R","T","Y","U","I","O","P"],
    ["A","S","D","F","G","H","J","K","L"],
    ["Z","X","C","V","B","N","M","BS","SP"]
]

DWELL_TIME   = 1.0
typed_text   = ""
hover_key    = None
hover_start  = 0
last_pressed = None
alpha        = 0.6
smooth_x     = 0
smooth_y     = 0

# ── Build key positions ───────────────────────────────────────
def get_key_positions_scaled(screen_w, screen_h):
    key_positions = {}
    num_cols  = 10
    key_w     = int(screen_w / (num_cols + 1))
    key_h     = int(screen_h * 0.13)
    gap       = int(screen_w * 0.008)
    start_y   = int(screen_h * 0.42)

    for r, row in enumerate(keys_layout):
        n       = len(row)
        row_w   = n * key_w + (n - 1) * gap
        start_x = (screen_w - row_w) // 2

        for c, key in enumerate(row):
            x = start_x + c * (key_w + gap)
            y = start_y + r * (key_h + gap)
            key_positions[key] = (x, y, key_w, key_h)

    return key_positions

# ── Draw modern keyboard ──────────────────────────────────────
def draw_keyboard_modern(frame, key_positions, active_key=None, progress_map={}):
    for key, (x, y, w, h) in key_positions.items():
        is_active = (key == active_key)

        overlay = frame.copy()
        if is_active:
            cv2.rectangle(overlay, (x, y), (x+w, y+h), (0, 200, 80), -1)
        else:
            cv2.rectangle(overlay, (x, y), (x+w, y+h), (40, 40, 40), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

        border_color = (0, 255, 100) if is_active else (255, 255, 255)
        cv2.rectangle(frame, (x, y), (x+w, y+h), border_color, 3)

        inner_color = (0, 200, 80) if is_active else (180, 180, 180)
        cv2.rectangle(frame, (x+3, y+3), (x+w-3, y+h-3), inner_color, 1)

        cv2.line(frame, (x+4, y+2),  (x+w-4, y+2),  (255,255,255), 1)
        cv2.line(frame, (x+2, y+4),  (x+2, y+h-4),  (255,255,255), 1)

        if key in progress_map:
            prog  = progress_map[key]
            bar_w = int(w * prog)
            cv2.rectangle(frame, (x, y+h-6),
                          (x+bar_w, y+h), (0, 255, 200), -1)

        label      = key
        font       = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.55 if key in ("BS","SP") else 0.75
        thickness  = 2
        (tw, th), _ = cv2.getTextSize(label, font, font_scale, thickness)
        tx = x + (w - tw) // 2
        ty = y + (h + th) // 2

        cv2.putText(frame, label, (tx+1, ty+1), font,
                    font_scale, (0,0,0), thickness+1)
        text_color = (0, 255, 100) if is_active else (255, 255, 255)
        cv2.putText(frame, label, (tx, ty), font,
                    font_scale, text_color, thickness)

# ── Text display box ──────────────────────────────────────────
def draw_text_box(frame, text, screen_w, screen_h):
    bx1, by1 = 30, 20
    bx2, by2 = screen_w - 30, int(screen_h * 0.12)

    overlay = frame.copy()
    cv2.rectangle(overlay, (bx1, by1), (bx2, by2), (20, 20, 20), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

    cv2.rectangle(frame, (bx1, by1), (bx2, by2), (0, 220, 120), 2)
    cv2.rectangle(frame, (bx1+3, by1+3), (bx2-3, by2-3), (0, 120, 60), 1)

    cursor  = "|" if int(time.time() * 2) % 2 == 0 else " "
    display = text[-60:] if len(text) > 60 else text

    font_scale = screen_w / 1400
    cv2.putText(frame, "  " + display + cursor,
                (bx1 + 20, by1 + int((by2-by1) * 0.68)),
                cv2.FONT_HERSHEY_SIMPLEX,
                font_scale, (0, 255, 180), 2)

# ── Status bar ────────────────────────────────────────────────
def draw_status(frame, hand_detected, screen_w, screen_h):
    sy = int(screen_h * 0.17)

    if hand_detected:
        label = "Hand Detected"
        color = (0, 255, 100)
    else:
        label = "No Hand - Show your index finger"
        color = (60, 60, 255)

    cv2.putText(frame, label,
                (30, sy),
                cv2.FONT_HERSHEY_SIMPLEX,
                screen_w / 2000, color, 2)

    cv2.putText(frame,
                "Point index finger | Hold 1s to type | ESC to quit",
                (30, int(screen_h * 0.96)),
                cv2.FONT_HERSHEY_SIMPLEX,
                screen_w / 2800, (160, 160, 160), 1)

# ── Detect hovered key ────────────────────────────────────────
def get_hovered_key(fx, fy, key_positions):
    for key, (x, y, w, h) in key_positions.items():
        if x < fx < x+w and y < fy < y+h:
            return key
    return None

# ── Frame generator for Flask ────────────────────────────────
def generate_frames():
    global hover_key, hover_start, typed_text
    global smooth_x, smooth_y, last_pressed

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    screen_w      = 0
    screen_h      = 0
    key_positions = {}
    prev_hand_state = False

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame  = cv2.flip(frame, 1)
        h_, w_ = frame.shape[:2]

        if screen_w == 0:
            screen_w      = w_
            screen_h      = h_
            key_positions = get_key_positions_scaled(screen_w, screen_h)

        frame = cv2.resize(frame, (screen_w, screen_h))

        rgb    = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        current_state = result.multi_hand_landmarks is not None
        if current_state != prev_hand_state:
            print("✋ Hand Detected!" if current_state else "❌ No Hand Detected")
            prev_hand_state = current_state

        progress_map = {}

        if result.multi_hand_landmarks:
            for hand_lm in result.multi_hand_landmarks:
                lm = hand_lm.landmark[8]
                fx = int(lm.x * screen_w)
                fy = int(lm.y * screen_h)

                smooth_x = int(alpha * fx + (1-alpha) * smooth_x)
                smooth_y = int(alpha * fy + (1-alpha) * smooth_y)

                current_key = get_hovered_key(smooth_x, smooth_y,
                                              key_positions)

                if current_key:
                    if current_key == hover_key:
                        elapsed = time.time() - hover_start
                        progress_map[current_key] = min(
                            elapsed / DWELL_TIME, 1.0)

                        if elapsed >= DWELL_TIME and last_pressed != current_key:
                            if current_key == "BS":
                                typed_text = typed_text[:-1]
                            elif current_key == "SP":
                                typed_text += " "
                            else:
                                typed_text += current_key
                            last_pressed = current_key
                            print(f"✅ Key Pressed: {current_key}")
                            print(f"📝 Typed: {typed_text}")
                    else:
                        hover_key    = current_key
                        hover_start  = time.time()
                        last_pressed = None
                else:
                    hover_key    = None
                    last_pressed = None
        else:
            hover_key    = None
            last_pressed = None

        draw_text_box(frame, typed_text, screen_w, screen_h)
        draw_status(frame, current_state, screen_w, screen_h)
        draw_keyboard_modern(frame, key_positions,
                             active_key=hover_key,
                             progress_map=progress_map)

        if result.multi_hand_landmarks:
            for hand_lm in result.multi_hand_landmarks:
                mp_draw.draw_landmarks(
                    frame, hand_lm, mp_hands.HAND_CONNECTIONS,
                    mp_draw.DrawingSpec(color=(0,255,0),
                                        thickness=2, circle_radius=3),
                    mp_draw.DrawingSpec(color=(255,255,255), thickness=2)
                )
            cv2.circle(frame, (smooth_x, smooth_y), 16, (0,200,255), -1)
            cv2.circle(frame, (smooth_x, smooth_y), 16, (255,255,255), 2)
            cv2.circle(frame, (smooth_x, smooth_y),  4, (255,255,255), -1)

        # ── Encode frame for streaming ──
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' +
               frame_bytes + b'\r\n')

# ── Get typed text ────────────────────────────────────────────
def get_typed_text():
    return typed_text

# ── Clear typed text ──────────────────────────────────────────
def clear_typed_text():
    global typed_text
    typed_text = ""