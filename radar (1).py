import tkinter as tk
import serial
import math
import time
import threading
from collections import deque

# ═══════════════════════════════════════════════════
#   SETTINGS — change as needed
# ═══════════════════════════════════════════════════
PORT     = "COM3"    # your COM port
BAUD     = 9600
MAX_DIST = 50        # cm — maximum detection range
# ═══════════════════════════════════════════════════

WIDTH    = 900
HEIGHT   = 620
CX       = WIDTH // 2
CY       = HEIGHT - 40
RADIUS   = 530
FPS      = 60

# Colors
BG           = "#050d05"
GRID_DIM     = "#0a2a0a"
GRID_MED     = "#0d400d"
GREEN_BRIGHT = "#00ff66"
GREEN_MED    = "#00cc44"
GREEN_DIM    = "#007722"
SCAN_GLOW    = "#00ff88"
RED_HOT      = "#ff2244"
RED_WARM     = "#ff6644"
RED_FADE     = "#441100"
WHITE        = "#e8ffe8"
AMBER        = "#ffcc00"
PANEL_BG     = "#020f02"
PANEL_BORDER = "#1a5a1a"

current_angle = 0
current_dist  = 999
detections = deque(maxlen=200)  # stores (angle, distance, timestamp)
lock = threading.Lock()

# ─────────────────────────────────────────────────
def polar_to_xy(angle, dist_cm):
    """Convert angle and distance to screen XY coordinates."""
    rad = math.radians(angle)
    dist_px = (min(dist_cm, MAX_DIST) / MAX_DIST) * RADIUS
    x = CX + math.cos(math.pi - rad) * dist_px
    y = CY - math.sin(rad) * dist_px
    return int(x), int(y)

def hex_blend(c1, c2, t):
    """Blend between two hex colors. t=0 returns c1, t=1 returns c2."""
    r1,g1,b1 = int(c1[1:3],16), int(c1[3:5],16), int(c1[5:7],16)
    r2,g2,b2 = int(c2[1:3],16), int(c2[3:5],16), int(c2[5:7],16)
    r = int(r1 + (r2-r1)*t)
    g = int(g1 + (g2-g1)*t)
    b = int(b1 + (b2-b1)*t)
    return f"#{r:02x}{g:02x}{b:02x}"

# ─────────────────────────────────────────────────
def draw_radar():
    canvas.delete("all")
    now = time.time()

    # Background gradient (simulated with concentric circles)
    for i in range(12, 0, -1):
        r = int(RADIUS * i / 12)
        shade = int(8 + i * 1.2)
        color = f"#00{shade:02x}00"
        canvas.create_oval(CX-r, CY-r, CX+r, CY+r,
                           outline="", fill=color)
    # Cover the bottom half with black (only show semicircle)
    canvas.create_rectangle(0, CY, WIDTH, HEIGHT+10, fill=BG, outline="")

    # Grid — distance rings
    ring_distances = [int(MAX_DIST * i / 4) for i in range(1, 5)]
    for d in ring_distances:
        r = int((d / MAX_DIST) * RADIUS)
        canvas.create_arc(CX-r, CY-r, CX+r, CY+r,
                          start=0, extent=180, style="arc",
                          outline=GRID_MED, width=1)
        # Distance labels on both sides
        canvas.create_text(CX + r + 4, CY - 8,
                           text=f"{d}cm", fill=GREEN_DIM,
                           font=("Courier New", 8, "bold"), anchor="w")
        canvas.create_text(CX - r - 4, CY - 8,
                           text=f"{d}cm", fill=GREEN_DIM,
                           font=("Courier New", 8, "bold"), anchor="e")

    # Grid — angle lines
    for a in range(0, 181, 15):
        rad = math.radians(a)
        ex = CX + math.cos(math.pi - rad) * RADIUS
        ey = CY - math.sin(rad) * RADIUS
        color = GRID_MED if a % 30 == 0 else GRID_DIM
        canvas.create_line(CX, CY, int(ex), int(ey), fill=color, width=1)
        if a % 30 == 0:
            lx = CX + math.cos(math.pi - rad) * (RADIUS + 22)
            ly = CY - math.sin(rad) * (RADIUS + 22)
            canvas.create_text(int(lx), int(ly), text=f"{a}°",
                               fill=GREEN_MED, font=("Courier New", 9, "bold"))

    # Baseline (horizontal line)
    canvas.create_line(CX - RADIUS - 10, CY, CX + RADIUS + 10, CY,
                       fill=GRID_MED, width=1)

    # Detection trail — group nearby angles into line segments
    with lock:
        dets_copy = list(detections)

    segments = []
    segment = []
    for a, d, t in dets_copy:
        age = now - t
        if age > 8:
            continue
        if segment:
            prev_a = segment[-1][0]
            if abs(a - prev_a) > 10:  # new object if angle gap is large
                segments.append(segment)
                segment = []
        segment.append((a, d, t))
    if segment:
        segments.append(segment)

    for seg in segments:
        # Draw lines between consecutive detection points
        for i in range(len(seg) - 1):
            a1, d1, t1 = seg[i]
            a2, d2, t2 = seg[i+1]
            age = now - t1
            fade = 1 - (age / 8)
            x1, y1 = polar_to_xy(a1, d1)
            x2, y2 = polar_to_xy(a2, d2)
            if fade > 0.7:
                color = RED_HOT
                width = 3
            elif fade > 0.4:
                color = RED_WARM
                width = 2
            else:
                color = hex_blend(RED_FADE, RED_WARM, fade / 0.4)
                width = 1
            canvas.create_line(x1, y1, x2, y2,
                               fill=color, width=width, capstyle="round")
        # Dot at the tip of the line (head of detection)
        a, d, t = seg[-1]
        age = now - t
        if age < 4:
            x, y = polar_to_xy(a, d)
            canvas.create_oval(x-5, y-5, x+5, y+5,
                               fill=RED_HOT, outline=WHITE, width=1)

    # Scanner glow effect (multiple layers)
    glow_layers = [
        (25, GRID_DIM,    1),
        (18, GREEN_DIM,   1),
        (12, GREEN_DIM,   1),
        (7,  GREEN_MED,   1),
        (3,  GREEN_BRIGHT,1),
        (0,  SCAN_GLOW,   2),
    ]
    for offset, color, width in glow_layers:
        a = current_angle - offset
        if a < 0:
            continue
        rad = math.radians(a)
        ex = CX + math.cos(math.pi - rad) * RADIUS
        ey = CY - math.sin(rad) * RADIUS
        canvas.create_line(CX, CY, int(ex), int(ey), fill=color, width=width)

    # Glowing tip at end of scanner line
    rad = math.radians(current_angle)
    tip_x = CX + math.cos(math.pi - rad) * RADIUS
    tip_y = CY - math.sin(rad) * RADIUS
    canvas.create_oval(int(tip_x)-4, int(tip_y)-4,
                       int(tip_x)+4, int(tip_y)+4,
                       fill=SCAN_GLOW, outline="")

    # Center dot
    canvas.create_oval(CX-6, CY-6, CX+6, CY+6,
                       fill=GREEN_BRIGHT, outline=SCAN_GLOW, width=2)

    # Current detection highlight
    with lock:
        a_now = current_angle
        d_now = current_dist

    if d_now < MAX_DIST:
        x, y = polar_to_xy(a_now, d_now)
        # Glow halo around detected point
        for size, alpha in [(20, GRID_DIM), (14, "#330000"), (9, "#880000")]:
            canvas.create_oval(x-size, y-size, x+size, y+size,
                               fill=alpha, outline="")
        canvas.create_oval(x-7, y-7, x+7, y+7,
                           fill=RED_HOT, outline=WHITE, width=1)
        # Dashed line from center to object
        canvas.create_line(CX, CY, x, y,
                           fill="#ff2244", width=1, dash=(4,4))
        # Distance label box
        canvas.create_rectangle(x+12, y-14, x+80, y+14,
                                 fill="#001100", outline=GREEN_DIM)
        canvas.create_text(x+46, y,
                           text=f"{d_now} cm", fill=RED_HOT,
                           font=("Courier New", 10, "bold"))

    # Info panel (top left)
    panel_w = 220
    canvas.create_rectangle(8, 8, panel_w, 130,
                             fill=PANEL_BG, outline=PANEL_BORDER, width=1)

    status_color = RED_HOT if d_now < MAX_DIST else GREEN_MED
    status_text  = "◉ DETECTED" if d_now < MAX_DIST else "○ SCANNING"

    canvas.create_text(20, 24, anchor="w",
                       text="■ ARDUINO RADAR v2",
                       fill=GREEN_BRIGHT, font=("Courier New", 11, "bold"))
    canvas.create_line(14, 36, panel_w-8, 36, fill=PANEL_BORDER)
    canvas.create_text(20, 50, anchor="w",
                       text=f"ANGLE   : {a_now:>5}°",
                       fill=WHITE, font=("Courier New", 10))
    canvas.create_text(20, 68, anchor="w",
                       text=f"DIST    : {d_now if d_now < MAX_DIST else '---':>5}{'cm' if d_now < MAX_DIST else '  '}",
                       fill=WHITE, font=("Courier New", 10))
    canvas.create_text(20, 86, anchor="w",
                       text=f"RANGE   : {MAX_DIST:>5} cm",
                       fill=GREEN_DIM, font=("Courier New", 10))
    canvas.create_text(20, 104, anchor="w",
                       text=f"PORT    :  {PORT}",
                       fill=GREEN_DIM, font=("Courier New", 10))
    canvas.create_line(14, 116, panel_w-8, 116, fill=PANEL_BORDER)
    canvas.create_text(20, 125, anchor="w",
                       text=status_text, fill=status_color,
                       font=("Courier New", 10, "bold"))

    # Title at top center
    canvas.create_text(CX, 22, text="◈  RADAR MONITOR  ◈",
                       fill=GREEN_DIM, font=("Courier New", 13, "bold"))

    root.after(1000 // FPS, draw_radar)

# ─────────────────────────────────────────────────
def read_serial():
    """Read angle and distance from Arduino over serial port."""
    global current_angle, current_dist
    while True:
        try:
            if ser.in_waiting > 0:
                line = ser.readline().decode("utf-8").strip()
                parts = line.split(",")
                if len(parts) == 2:
                    a = int(parts[0])
                    d = int(parts[1])
                    with lock:
                        current_angle = a
                        current_dist  = d
                        if d < MAX_DIST:
                            detections.append((a, d, time.time()))
        except:
            pass

# ─────────────────────────────────────────────────
# Connect to Arduino
try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    time.sleep(2)  # wait for Arduino to initialize
    print(f"Connected to {PORT}")
except Exception as e:
    print(f"Cannot connect to {PORT}")
    print(f"Check your port in Arduino IDE → Tools → Port")
    print(f"Error: {e}")
    exit()

# Window setup
root = tk.Tk()
root.title("Arduino Radar Monitor")
root.configure(bg=BG)
root.resizable(False, False)

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT,
                   bg=BG, highlightthickness=0)
canvas.pack()

# Start serial reading in a background thread
t = threading.Thread(target=read_serial, daemon=True)
t.start()

draw_radar()
root.mainloop()
ser.close()
