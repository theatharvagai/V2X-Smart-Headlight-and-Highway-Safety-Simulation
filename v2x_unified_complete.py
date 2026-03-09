import pygame
import random
import time
import json
import os
import threading
import math
import cv2
import numpy as np
import paho.mqtt.client as mqtt

# ==========================================
# 0. INITIALIZATION & PATH FIX
# ==========================================
try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except:
    pass

# ==========================================
# 1. CONFIGURATION
# ==========================================
class AppConfig:
    BROKER = "broker.emqx.io"
    PORT = 1883
    TOPIC_VEHICLE = "v2x/hackathon/unified/cars"
    
    # Defaults (Now dynamic)
    SCREEN_WIDTH = 1400
    SCREEN_HEIGHT = 900
    FPS = 60

    LANE_HEIGHT = 100
    LANE_COUNT = 5
    INCOMING_LANE_INDEX = 0
    SERVICE_LANE_INDEX = 4
    ROAD_Y = 220
    TOTAL_LENGTH = 2000
    
    MAX_SPEED_KMH = 250 
    MAX_SPEED_MS = MAX_SPEED_KMH / 3.6
    ACCEL = 10
    BRAKE = 25
    LANE_CHANGE_SPEED = 2.0
    
    # INCREASED SAFETY DISTANCES
    SAFE_DIST = 300  # Previously 150
    CRITICAL_DIST = 120 # Previously 60
    AMBULANCE_DIST = 400
    GHOST_TIMEOUT = 3.0
    DROWSY_TIME_THRESHOLD = 2.0
    
    # BRIGHTER COLORS for visibility
    C_BG = (22, 24, 30)
    C_ROAD = (40, 42, 50)
    C_LINE = (160, 160, 175)
    C_LINE_YELLOW = (220, 180, 40)
    C_PANEL = (30, 33, 40)
    C_ACCENT = (0, 200, 255)
    C_NAV_BG = (35, 38, 48)
    C_NAV_FULL_BG = (15, 17, 22)
    C_ROUTE_ACTIVE = (0, 255, 150)
    C_ROUTE_BLOCKED = (220, 50, 50)
    C_ROUTE_IDLE = (90, 95, 110)

# ==========================================
# 2. UTILS
# ==========================================
def draw_glass_panel(screen, rect, color, alpha=180, radius=12):
    s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(s, (*color, alpha), (0, 0, rect.width, rect.height), border_radius=radius)
    pygame.draw.rect(s, (255, 255, 255, 40), (0, 0, rect.width, rect.height), 2, border_radius=radius)
    screen.blit(s, rect.topleft)

# ==========================================
# 3. DROWSINESS DETECTION
# ==========================================
class DrowsinessDetector:
    def __init__(self, useCamera=True):
        self.isDrowsy = False
        self.noFaceStartTime = None
        self.isRunning = True
        self.currentFrame = None
        self.useCamera = useCamera
        self.lock = threading.Lock()
        if not self.useCamera: return
            
        self.faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.thread = threading.Thread(target=self._detectionLoop, daemon=True)
        self.thread.start()

    def _detectionLoop(self):
        try:
            cap = cv2.VideoCapture(0) 
            while self.isRunning and cap.isOpened():
                success, frame = cap.read()
                if not success: continue
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.faceCascade.detectMultiScale(gray, 1.1, 4)
                if len(faces) == 0:
                    if self.noFaceStartTime is None: self.noFaceStartTime = time.time()
                    elif time.time() - self.noFaceStartTime > AppConfig.DROWSY_TIME_THRESHOLD: self.isDrowsy = True
                else:
                    self.noFaceStartTime = None
                    self.isDrowsy = False
                for (x, y, w, h) in faces: cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                with self.lock:
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    self.currentFrame = np.rot90(rgb)
                time.sleep(0.05)
            cap.release()
        except: self.useCamera = False

    def getFrame(self):
        with self.lock:
            if self.currentFrame is not None:
                surf = pygame.surfarray.make_surface(self.currentFrame)
                return pygame.transform.flip(surf, True, False)
        return None

    def stopDetector(self): self.isRunning = False

# ==========================================
# 3. NAVIGATION SYSTEM
# ==========================================
class NavigationSystem:
    def __init__(self):
        self.width, self.height = 260, 180
        self.x, self.y = 20, 20
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.isFullScreen = False
        self.totalDist = 5000
        self.destinationDist = self.totalDist
        self.fontS = pygame.font.SysFont("Verdana", 12, bold=True)
        self.fontB = pygame.font.SysFont("Verdana", 16, bold=True)
        self.fontXL = pygame.font.SysFont("Verdana", 28, bold=True)
        start, end = (150, 700), (1250, 200)
        self.routes = {
            "main": {"points": [start, (700, 450), end], "status": "active", "name": "Main", "length": 1.0},
            "top": {"points": [start, (400, 350), (1000, 180), end], "status": "idle", "name": "North", "length": 1.4},
            "bottom": {"points": [start, (450, 750), (900, 680), end], "status": "idle", "name": "South", "length": 1.2}
        }
        self.currentRouteKey = "main"
        self.obstacles = []

    def resetObstacles(self):
        self.obstacles = []
        for k in self.routes: self.routes[k]["status"] = "idle"
        self.selectBestRoute()

    def selectBestRoute(self):
        newKey = "main"
        if self.routes["main"]["status"] == "blocked":
            newKey = "bottom" if self.routes["bottom"]["status"] != "blocked" else "top"
        self.currentRouteKey = newKey
        for k in self.routes:
            if self.routes[k]["status"] != "blocked": self.routes[k]["status"] = "active" if k == newKey else "idle"

    def handleMapClick(self, pos):
        if not self.isFullScreen: return
        self.obstacles.append(pos)
        self.routes[self.currentRouteKey]["status"] = "blocked"
        self.selectBestRoute()

    def updateNav(self, dt, speed):
        self.destinationDist -= speed * dt
        if self.destinationDist <= 0: self.destinationDist = self.totalDist

    def toggleView(self): self.isFullScreen = not self.isFullScreen

    def drawMiniMap(self, screen, hasImage=False):
        if not hasImage:
            pygame.draw.rect(screen, AppConfig.C_NAV_BG, self.rect, border_radius=12)
        pygame.draw.rect(screen, (80, 80, 95), self.rect, 2, border_radius=12)
        screen.blit(self.fontB.render("V2X Nav", True, (255, 255, 255)), (self.x + 15, self.y + 10))
        status = self.fontXL.render("ACTIVE", True, (80, 255, 120))
        screen.blit(status, (self.x + 25, self.y + 50))
        if self.currentRouteKey:
            screen.blit(self.fontS.render(f"Via: {self.routes[self.currentRouteKey]['name']}", True, (200, 200, 210)), (self.x + 20, self.y + 105))

    def drawFullMap(self, screen):
        screen.fill(AppConfig.C_NAV_FULL_BG)
        for key, route in self.routes.items():
            col = AppConfig.C_ROUTE_ACTIVE if route["status"] == "active" else AppConfig.C_ROUTE_IDLE
            if route["status"] == "blocked": col = AppConfig.C_ROUTE_BLOCKED
            if len(route["points"]) >= 2: pygame.draw.lines(screen, col, False, route["points"], 8 if route["status"]=="active" else 4)

# ==========================================
# 4. BUTTON CLASS
# ==========================================
class AppButton:
    def __init__(self, x, y, w, h, text, color=(50, 55, 65), cb=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.cb = cb
        self.isHovered = False

    def draw(self, screen, font):
        col = (min(self.color[0]+30, 255), min(self.color[1]+30, 255), min(self.color[2]+30, 255)) if self.isHovered else self.color
        pygame.draw.rect(screen, col, self.rect, border_radius=8)
        pygame.draw.rect(screen, (100, 100, 120), self.rect, 1, border_radius=8)
        txt = font.render(self.text, True, (240, 240, 250))
        screen.blit(txt, (self.rect.centerx - txt.get_width()//2, self.rect.centery - txt.get_height()//2))

    def checkClick(self, pos):
        if self.rect.collidepoint(pos) and self.cb: self.cb()

# ==========================================
# 5. VEHICLE CLASS
# ==========================================
class SmartVehicle:
    def __init__(self, uid, isEmergency=False, direction=1):
        self.id = uid
        self.isEmergency = isEmergency
        self.direction = direction
        self.lane = 1 if not isEmergency else 2
        if direction == -1: self.lane = AppConfig.INCOMING_LANE_INDEX
        self.visualLane = float(self.lane)
        self.x = 0 if direction == 1 else AppConfig.TOTAL_LENGTH
        self.speed = 15
        self.userTargetSpeed = 15
        self.targetSpeed = 15
        self.color = (255, 200, 0) if isEmergency else (random.randint(80, 220), random.randint(80, 220), 255)
        self.isBraking = False
        self.warningAhead = False
        self.isDrowsy = False
        self.headlightMode = "high"
        self.lastUpdate = time.time()
        self.laneChangeCooldown = 0
        self.pulseTimer = 0.0

    def updatePhysics(self, dt, allVehicles, isMeDrowsy=False):
        self.pulseTimer = (self.pulseTimer + dt) % 1.5
        distToAhead = float('inf')
        speedAhead = None
        oncomingDetected = False
        for other in allVehicles.values():
            if other.id == self.id: continue
            if other.direction != self.direction:
                rel_x = (other.x - self.x) if self.direction == 1 else (self.x - other.x)
                if rel_x < -AppConfig.TOTAL_LENGTH / 2: rel_x += AppConfig.TOTAL_LENGTH
                if rel_x > AppConfig.TOTAL_LENGTH / 2: rel_x -= AppConfig.TOTAL_LENGTH
                if 0 < rel_x < 600: oncomingDetected = True
                continue
            if other.lane == self.lane:
                dAhead = (other.x - self.x) if self.direction == 1 else (self.x - other.x)
                if dAhead < 0: dAhead += AppConfig.TOTAL_LENGTH
                if dAhead < distToAhead:
                    distToAhead = dAhead
                    speedAhead = other.speed

        self.headlightMode = "low" if oncomingDetected else "high"
        self.isBraking = False
        self.warningAhead = False
        
        if isMeDrowsy and self.direction == 1:
            self.isDrowsy = True
            if self.lane != AppConfig.SERVICE_LANE_INDEX:
                if self.laneChangeCooldown <= 0: self.lane += 1; self.laneChangeCooldown = 1.0
            else: self.targetSpeed = 0; self.isBraking = True
        elif distToAhead < AppConfig.CRITICAL_DIST: 
            self.targetSpeed = 0; self.isBraking = True; self.warningAhead = True
        elif distToAhead < AppConfig.SAFE_DIST: 
            self.targetSpeed = (speedAhead or 5) * 0.8; self.isBraking = True; self.warningAhead = True
        else: self.targetSpeed = self.userTargetSpeed

        if self.speed < self.targetSpeed: self.speed += AppConfig.ACCEL * dt
        elif self.speed > self.targetSpeed: self.speed -= AppConfig.BRAKE * dt
        self.speed = max(0, min(self.speed, AppConfig.MAX_SPEED_MS))
        self.x += (self.speed * self.direction) * dt
        if self.x > AppConfig.TOTAL_LENGTH: self.x = 0
        elif self.x < 0: self.x = AppConfig.TOTAL_LENGTH
        self.laneChangeCooldown -= dt

    def draw(self, screen, images, font, w, isMe=False):
        vx = (self.x / AppConfig.TOTAL_LENGTH) * w
        vy = AppConfig.ROAD_Y + (self.visualLane * AppConfig.LANE_HEIGHT) + 22
        
        # Color refinement: Player=Blue, Ambulance=Yellow, Others=Red
        draw_color = (0, 150, 255) if isMe else ((255, 180, 0) if self.isEmergency else (240, 60, 60))
        
        # 1. Soft Shadow
        shadow_rect = pygame.Rect(vx+5, vy+45, 100, 15)
        pygame.draw.ellipse(screen, (0, 0, 0, 80), shadow_rect)

        # 2. V2X Signal Pulse (Reduced opacity: 120 max)
        if self.pulseTimer < 0.8:
            r = int(50 + self.pulseTimer * 100)
            alpha = int(120 * (1 - self.pulseTimer / 0.8))
            s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*draw_color, alpha), (r, r), r, 2)
            screen.blit(s, (vx + 55 - r, vy + 27 - r))

        # 3. Headlights
        bl, bw = (350 if self.headlightMode=="high" else 120), (80 if self.headlightMode=="high" else 40)
        headlight_surf = pygame.Surface((bl, bw*2), pygame.SRCALPHA)
        pts = [(0, bw), (bl, 0), (bl, bw*2), (0, bw)] if self.direction == 1 else [(bl, bw), (0, 0), (0, bw*2), (bl, bw)]
        pygame.draw.polygon(headlight_surf, (255, 255, 200, 60), pts)
        screen.blit(headlight_surf, (vx+100 if self.direction==1 else vx-bl+10, vy-bw+27))

        # 4. Vehicle Body
        img_key = 'me' if isMe else ('amb' if self.isEmergency else 'other')
        if images and img_key in images:
            img = images[img_key]
            if self.direction == -1: img = pygame.transform.flip(img, True, False)
            screen.blit(img, (vx, vy))
        else:
            pygame.draw.rect(screen, draw_color, (vx, vy, 110, 55), border_radius=10)
            pygame.draw.rect(screen, (255, 255, 255, 100), (vx, vy, 110, 55), 2, border_radius=10)

        # 5. Labels (Moved closer: -15 instead of -25)
        lbl = font.render(f"{self.id} {int(self.speed*3.6)}km/h", True, (255, 255, 255))
        screen.blit(lbl, (vx + 55 - lbl.get_width()//2, vy - 15))

    def updateVisuals(self, dt):
        diff = self.lane - self.visualLane
        if abs(diff) > 0.01: self.visualLane += (1 if diff > 0 else -1) * AppConfig.LANE_CHANGE_SPEED * dt
        else: self.visualLane = float(self.lane)

    def toJSON(self):
        return json.dumps({"id":self.id, "lane":self.lane, "x":self.x, "spd":self.speed, "emb":self.isEmergency, "dir":self.direction, "col":self.color, "drw":self.isDrowsy, "brk":self.isBraking, "hdm":self.headlightMode})

    @staticmethod
    def fromJSON(payload):
        try:
            d = json.loads(payload)
            v = SmartVehicle(d['id'], d['emb'], d.get('dir', 1))
            v.lane=d['lane']; v.x=d['x']; v.speed=d['spd']; v.color=tuple(d['col']); v.isDrowsy=d.get('drw', False); v.isBraking=d.get('brk', False); v.headlightMode=d.get('hdm', 'high'); v.visualLane=float(v.lane); v.lastUpdate=time.time()
            return v
        except: return None

# ==========================================
# 6. MAIN APP
# ==========================================
class V2XUnifiedApp:
    def __init__(self, uid, useCamera=True):
        print(f"Initializing V2X App for {uid}...")
        pygame.init()
        try:
            pygame.font.init()
        except:
            print("Warning: Font system initialization failed.")
            
        self.screen = pygame.display.set_mode((AppConfig.SCREEN_WIDTH, AppConfig.SCREEN_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption(f"V2X Smart Highway - {uid}")
        
        # Show a quick loading screen so it's not black
        self.screen.fill((30, 35, 45))
        loading_font = pygame.font.SysFont("Arial", 24)
        loading_text = loading_font.render(f"Loading V2X Ecosystem: {uid}...", True, (200, 200, 200))
        self.screen.blit(loading_text, (AppConfig.SCREEN_WIDTH//2 - 150, AppConfig.SCREEN_HEIGHT//2))
        pygame.display.flip()

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Verdana", 14, bold=True)
        self.bigFont = pygame.font.SysFont("Verdana", 24, bold=True)
        self.alertFont = pygame.font.SysFont("Verdana", 32, bold=True)
        
        self.myVehicle = SmartVehicle(uid)
        self.vehicles = {uid: self.myVehicle}
        self.ownedVids = {uid}
        
        print("Loading assets...")
        self.images = self.loadAssets()
        
        print("Starting safety systems...")
        self.detector = DrowsinessDetector(useCamera)
        self.navSystem = NavigationSystem()
        self.networkTick = 0
        self.streetLights = [{"x": x, "isOn": False} for x in range(0, AppConfig.TOTAL_LENGTH, 200)]
        self.manualDrowsy = False
        
        self.update_layout()
        
        print("Connecting to V2X Network...")
        try:
            # Fallback for different paho-mqtt versions
            try:
                self.client = mqtt.Client(client_id=f"{uid}_{random.randint(1000, 9999)}", callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
            except (AttributeError, TypeError):
                # Older paho-mqtt version
                self.client = mqtt.Client(client_id=f"{uid}_{random.randint(1000, 9999)}")
            
            self.client.on_message = self.onMsg
            threading.Thread(target=self._connectMQTT, daemon=True).start()
        except Exception as e:
            print(f"Network initialization error: {e}")

    def _connectMQTT(self):
        try:
            self.client.connect(AppConfig.BROKER, AppConfig.PORT, keepalive=60)
            self.client.subscribe(AppConfig.TOPIC_VEHICLE)
            self.client.loop_start()
            print("V2X Network Connected Successfully.")
        except Exception as e:
            print(f"V2X Network Offline (Broker unreachable): {e}")

    def update_layout(self):
        w, h = self.screen.get_size()
        AppConfig.SCREEN_WIDTH, AppConfig.SCREEN_HEIGHT = w, h
        
        if hasattr(self, 'images') and self.images and 'dash' in self.images:
            try:
                self.images['dash'] = pygame.transform.scale(self.images['dash'], (w, 220))
            except: pass

        cx = w // 2 - 350
        y = 30
        self.buttons = [
            AppButton(cx, y, 115, 32, "SteerLeft", cb=lambda: self.changeLane(-1)),
            AppButton(cx + 125, y, 115, 32, "SteerRight", cb=lambda: self.changeLane(1)),
            AppButton(cx, y + 40, 115, 32, "SpeedDown", color=(90, 45, 45), cb=lambda: self.chgSpeed(-5)),
            AppButton(cx + 125, y + 40, 115, 32, "SpeedUp", color=(45, 90, 45), cb=lambda: self.chgSpeed(5)),
            AppButton(cx + 260, y, 220, 32, "CallAmbulance", color=(160, 35, 35), cb=self.spawnAmbulance),
            AppButton(cx + 260, y + 40, 220, 32, "CallIncoming", color=(35, 35, 140), cb=self.spawnIncoming),
            AppButton(cx + 490, y + 15, 180, 45, "0 KM/H", color=(20, 100, 80))
        ]
        self.btnBack = AppButton(w - 220, h - 80, 200, 60, "Back", cb=self.navSystem.toggleView)

    def loadAssets(self):
        imgs = {}
        try:
            sz = (110, 55)
            # Try to load images with absolute paths to be safe
            base_path = os.path.dirname(os.path.abspath(__file__))
            assets_dir = os.path.join(base_path, "assets")
            
            def load_and_scale(name, size):
                p = os.path.join(assets_dir, name)
                if os.path.exists(p):
                    return pygame.transform.scale(pygame.image.load(p).convert_alpha(), size)
                return None

            imgs['me'] = load_and_scale("car_blue.png", sz)
            imgs['other'] = load_and_scale("car_red.png", sz)
            imgs['amb'] = load_and_scale("ambulance.png", sz)
            imgs['dash'] = load_and_scale("dashboard.png", (AppConfig.SCREEN_WIDTH, 220))
            imgs['nav'] = load_and_scale("navigation.png", (260, 180))
            
            # Remove None values
            imgs = {k: v for k, v in imgs.items() if v is not None}
        except Exception as e:
            print(f"Error loading assets: {e}")
        return imgs

    def changeLane(self, d):
        n = self.myVehicle.lane + d
        if 0 < n < AppConfig.LANE_COUNT: self.myVehicle.lane = n

    def chgSpeed(self, d): self.myVehicle.userTargetSpeed = max(0, min(self.myVehicle.userTargetSpeed + d, AppConfig.MAX_SPEED_MS))

    def spawnAmbulance(self):
        if "AMB-1" not in self.vehicles: v = SmartVehicle("AMB-1", True); self.vehicles["AMB-1"] = v; self.ownedVids.add("AMB-1")

    def spawnIncoming(self):
        iid = f"INC-{random.randint(100, 999)}"
        v = SmartVehicle(iid, False, -1); self.vehicles[iid] = v; self.ownedVids.add(iid)

    def onMsg(self, c, u, m):
        try:
            d = json.loads(m.payload.decode())
            if d['id'] not in self.ownedVids:
                if d['id'] not in self.vehicles: self.vehicles[d['id']] = SmartVehicle.fromJSON(m.payload.decode())
                else:
                    v = self.vehicles[d['id']]; v.lane=d['lane']; v.speed=d['spd']; v.direction=d.get('dir', 1); v.isEmergency=d['emb']; v.isDrowsy=d.get('drw', False); v.isBraking=d.get('brk', False); v.headlightMode=d.get('hdm', 'high'); v.lastUpdate=time.time()
                    if abs(v.x - d['x']) > 50: v.x = d['x']
        except: pass

    def drawSimulation(self):
        w, h = self.screen.get_size()
        self.screen.fill(AppConfig.C_BG)
        
        # 1. Dashboard Panel (Glassmorphism)
        draw_glass_panel(self.screen, pygame.Rect(0, 0, w, AppConfig.ROAD_Y), AppConfig.C_PANEL, 200, 0)

        # 2. Road & Lanes
        roadH = AppConfig.LANE_HEIGHT * AppConfig.LANE_COUNT
        pygame.draw.rect(self.screen, AppConfig.C_ROAD, (0, AppConfig.ROAD_Y, w, roadH))
        for i in range(AppConfig.LANE_COUNT + 1):
            y = AppConfig.ROAD_Y + i * AppConfig.LANE_HEIGHT
            if i == AppConfig.INCOMING_LANE_INDEX + 1:
                pygame.draw.line(self.screen, AppConfig.C_LINE_YELLOW, (0, y-3), (w, y-3), 4)
                pygame.draw.line(self.screen, AppConfig.C_LINE_YELLOW, (0, y+3), (w, y+3), 4)
            elif i == 0 or i == AppConfig.LANE_COUNT: pygame.draw.line(self.screen, AppConfig.C_LINE, (0, y), (w, y), 3)
            else:
                for x in range(0, w, 40): pygame.draw.line(self.screen, AppConfig.C_LINE, (x, y), (x+20, y), 2)
        
        # 3. Streetlights
        for light in self.streetLights:
            light["isOn"] = any(abs(v.x - light["x"]) < 400 for v in self.vehicles.values())
            lx = (light["x"] / AppConfig.TOTAL_LENGTH) * w
            lCol = (255, 255, 255) if light["isOn"] else (50, 50, 60)
            if light["isOn"]: # Bloom effect
                for r in range(12, 4, -2): pygame.draw.circle(self.screen, (*lCol, 50), (int(lx), AppConfig.ROAD_Y - 20), r)
            pygame.draw.circle(self.screen, lCol, (int(lx), AppConfig.ROAD_Y - 20), 6)
            pygame.draw.circle(self.screen, lCol, (int(lx), AppConfig.ROAD_Y + roadH + 20), 6)

        # 3.5 Service Lane Text Overlay (20% opacity)
        sl_y = AppConfig.ROAD_Y + (AppConfig.SERVICE_LANE_INDEX * AppConfig.LANE_HEIGHT) + AppConfig.LANE_HEIGHT//2
        sl_surf = self.bigFont.render("SERVICE LANE", True, (255, 255, 255))
        sl_surf.set_alpha(51) # 20% of 255
        for sx in range(200, w, 800):
            self.screen.blit(sl_surf, (sx, sl_y - sl_surf.get_height()//2))

        # 4. Vehicles
        for v in self.vehicles.values():
            v.draw(self.screen, self.images, self.font, w, isMe=(v.id == self.myVehicle.id))

        # 5. Dashboard UI
        for b in self.buttons[:-1]: b.draw(self.screen, self.font)
        
        # Speed Gauge (Replacing last button)
        gauge_rect = self.buttons[-1].rect
        pygame.draw.rect(self.screen, (20, 25, 30), gauge_rect, border_radius=8)
        speed_pct = self.myVehicle.speed / AppConfig.MAX_SPEED_MS
        fill_w = int((gauge_rect.width - 10) * speed_pct)
        pygame.draw.rect(self.screen, (0, 200, 255), (gauge_rect.x+5, gauge_rect.y+5, fill_w, gauge_rect.height-10), border_radius=4)
        spd_txt = self.font.render(f"{int(self.myVehicle.speed * 3.6)} KM/H", True, (255, 255, 255))
        self.screen.blit(spd_txt, (gauge_rect.centerx - spd_txt.get_width()//2, gauge_rect.centery - spd_txt.get_height()//2))

        # 6. HUD ALERTS
        blink = pygame.time.get_ticks() % 600 < 300
        if self.myVehicle.isBraking and blink:
            alert_rect = pygame.Rect(w//2 - 150, 120, 300, 50)
            draw_glass_panel(self.screen, alert_rect, (180, 20, 20), 180)
            txt = self.alertFont.render("EMERGENCY BRAKE", True, (255, 255, 255))
            self.screen.blit(txt, (alert_rect.centerx - txt.get_width()//2, alert_rect.centery - txt.get_height()//2))
        
        if self.myVehicle.warningAhead and not self.myVehicle.isBraking:
            box = pygame.Rect(w//2 - 120, 180, 240, 35)
            draw_glass_panel(self.screen, box, (200, 100, 0), 180)
            txt = self.font.render("! VEHICLE AHEAD !", True, (255, 255, 255))
            self.screen.blit(txt, (box.centerx - txt.get_width()//2, box.centery - txt.get_height()//2))

        # 7. Safety Systems Panels
        frame = self.detector.getFrame()
        if frame:
            cam_rect = pygame.Rect(w - 250, 20, 220, 160)
            draw_glass_panel(self.screen, cam_rect, (0, 0, 0), 255, 12)
            f = pygame.transform.scale(frame, (216, 156))
            self.screen.blit(f, (w - 248, 22))
            if self.detector.isDrowsy:
                pygame.draw.rect(self.screen, (255, 0, 0), cam_rect, 4, border_radius=12)
                if blink:
                    dr_txt = self.font.render("DROWSINESS DETECTED", True, (255, 100, 100))
                    self.screen.blit(dr_txt, (cam_rect.centerx - dr_txt.get_width()//2, cam_rect.bottom + 5))
        
        # MiniMap
        self.navSystem.drawMiniMap(self.screen, hasImage=False)
    def run(self):
        while True:
            dt = self.clock.tick(AppConfig.FPS) / 1000.0
            mx, my = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return
                if event.type == pygame.VIDEORESIZE: self.update_layout()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_x: self.manualDrowsy = not self.manualDrowsy
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.navSystem.isFullScreen: self.navSystem.toggleView()
                    else:
                        for b in self.buttons: b.checkClick((mx, my))
                        if self.navSystem.rect.collidepoint((mx, my)): self.navSystem.toggleView()
            for b in self.buttons: b.isHovered = b.rect.collidepoint((mx, my))
            self.btnBack.isHovered = self.btnBack.rect.collidepoint((mx, my))
            
            self.networkTick += dt
            doPub = (self.networkTick >= 0.06)
            if doPub: self.networkTick = 0
            for vid in list(self.vehicles.keys()):
                v = self.vehicles[vid]
                if vid in self.ownedVids:
                    v.updatePhysics(dt, self.vehicles, isMeDrowsy=(self.detector.isDrowsy or self.manualDrowsy if vid == self.myVehicle.id else False))
                    if doPub: self.client.publish(AppConfig.TOPIC_VEHICLE, v.toJSON())
                else:
                    v.x += (v.speed * v.direction) * dt
                    if v.x > AppConfig.TOTAL_LENGTH: v.x = 0
                    elif v.x < 0: v.x = AppConfig.TOTAL_LENGTH
                v.updateVisuals(dt)
            self.navSystem.updateNav(dt, self.myVehicle.speed)
            now = time.time()
            ghosts = [vid for vid, v in self.vehicles.items() if vid not in self.ownedVids and (now - v.lastUpdate > 3.0)]
            for vid in ghosts: del self.vehicles[vid]
            if self.navSystem.isFullScreen:
                self.navSystem.drawFullMap(self.screen)
                self.btnBack.draw(self.screen, self.font)
            else: self.drawSimulation()
            pygame.display.flip()

if __name__ == "__main__":
    try:
        uid = input("Vehicle ID: ").strip().upper() or "CAR1"
        cam = input("Use Camera? (Y/N): ").strip().upper() == "Y"
        app = V2XUnifiedApp(uid, cam)
        app.run()
    except Exception as e:
        import traceback; traceback.print_exc()
        input("Press Enter...")
