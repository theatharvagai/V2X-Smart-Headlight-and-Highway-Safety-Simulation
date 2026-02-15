# 🚗 V2X Smart Highway Simulation System

### AI + V2X + Computer Vision + Intelligent Infrastructure  
A Real-Time Connected Vehicle Ecosystem for Smart Transportation 🚦

---

## 🌍 Overview
This project is a real-time V2X (Vehicle-to-Everything) Smart Highway Simulation where multiple computers act as intelligent vehicles communicating over MQTT to form a cooperative transportation network.

Each node (computer) behaves like a connected vehicle and continuously shares:
- Position 📍  
- Speed 🚗  
- Lane 🛣️  
- Safety Alerts ⚠️  

All vehicle data is visualized on a live interactive dashboard with AI safety features, intelligent navigation, and smart infrastructure integration.

---

## 🖼️ Project Demo (Live Screenshots)

<p align="center">
  <img src="assets/dashboard.png" width="260"/>
  <img src="assets/navigation.png" width="260"/>
  <img src="assets/drowsy.png" width="260"/>
</p>

<p align="center">
  <sub>V2X Dashboard • Live Navigation System • Drowsiness Detection & Service Lane Parking</sub>
</p>

---

## 🎯 Key Highlights
- Real-Time V2V Communication using MQTT  
- AI-Based Driver Drowsiness Detection (OpenCV)  
- Emergency Vehicle Priority System 🚑  
- Bidirectional Highway Traffic Simulation  
- Adaptive High/Low Beam Headlight Control  
- Smart Street Lighting (V2I Infrastructure)  
- Dynamic Route Navigation with Obstacles  
- Interactive Real-Time Simulation Dashboard  

---

## 🧠 Core Features

### 🚗 V2X Communication System
- Distributed vehicle nodes using MQTT protocol  
- Real-time sharing of telemetry (speed, lane, position, alerts)  
- Multi-computer synchronized simulation  
- Cooperative collision avoidance logic  

### 😴 AI Driver Drowsiness Detection
- Camera-based face detection using OpenCV  
- Detects driver inactivity and drowsiness in real-time  
- Automatic service-lane parking when drowsy  
- Global alert broadcast to all nearby vehicles  

### 🚑 Emergency Vehicle Intelligence
- One-click ambulance spawning system  
- Automatic lane yielding by surrounding vehicles  
- Priority traffic behavior using V2X communication  
- Real-time emergency alert broadcasting  

### 🛣️ Smart Highway Simulation
- 4-Lane Highway Architecture:
  - Lane 0–1 → Forward Traffic  
  - Lane 2 → Opposite Traffic  
  - Lane 3 → Service Lane (Drowsy Parking)  
- Smooth lane change physics  
- Collision avoidance with safe distance logic  
- Adaptive braking and speed control  

### 🔦 Adaptive Headlight System (India-Focused Innovation)
- Detects oncoming vehicles in opposite lane within range  
- Automatically switches High Beam → Low Beam  
- Restores High Beam after vehicles pass  
- Reduces night glare accidents on highways  

### 💡 Intelligent Street Light Infrastructure (V2I)
- Street lights activate only 500m ahead of vehicles  
- Infrastructure responds dynamically to vehicle telemetry  
- Energy-efficient smart lighting system  
- Demonstrates Vehicle-to-Infrastructure (V2I) concept  

### 🗺️ Advanced Navigation & Routing System
- Google Maps-style live route visualization  
- Dynamic rerouting with obstacle injection  
- Real-time ETA calculation  
- Interactive full-screen navigation mode  

---

## 🧩 System Architecture
```
Multiple Vehicle Nodes (Computers)
            │
            ▼
        MQTT Broker
            │
     ┌──────┼────────┐
     │      │        │
    V2V    V2I   Emergency Alerts
     │      │        │
     └────► Real-Time Simulation Engine
            + AI Safety + Navigation
```

---

## 🛠️ Tech Stack
Programming Language:
- Python 3  

Simulation & Visualization:
- Pygame  
- NumPy  

AI & Computer Vision:
- OpenCV (Drowsiness Detection)  
- Haar Cascade Face Detection  

Networking (V2X Communication):
- MQTT (paho-mqtt)  
- EMQX Public Broker  
- Distributed Node Architecture  

Concept Domains:
- V2X (Vehicle-to-Everything)  
- Intelligent Transportation Systems (ITS)  
- Smart Infrastructure  
- Real-Time Simulation Systems  

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/v2x-smart-highway.git
cd v2x-smart-highway
```

### 2. Install Dependencies
```bash
pip install pygame opencv-python numpy paho-mqtt
```

### 3. Run the Simulation
```bash
python v2x_unified_complete.py
```

Run the program on multiple systems and enter different Vehicle IDs (CAR1, CAR2, etc.) to simulate real V2X communication.

---

## 🎮 Controls
| Control | Function |
|--------|----------|
| Left / Right Buttons | Change Lane |
| Faster / Slower | Adjust Speed |
| X Key | Toggle Drowsiness Mode |
| Call Ambulance Button | Spawn Emergency Vehicle |
| Click Map Panel | Expand Navigation View |
| Click Routes | Add Obstacles & Trigger Rerouting |

---

## 🧪 Real-World Applications
- Intelligent Transportation Systems (ITS)  
- Smart Cities & Mobility Research  
- Autonomous Vehicle Simulation  
- Emergency Response Optimization  
- Highway Safety Systems  
- Energy-Efficient Smart Infrastructure  
- V2X Communication Research  

---

## 🏆 Hackathon Innovation Value
This project demonstrates:
- Distributed Systems Engineering  
- Real-Time Simulation Design  
- AI + Computer Vision Integration  
- V2X Communication Architecture  
- Intelligent Infrastructure Modeling  

---

## 👨‍💻 Author
Atharva Gai  
M.Tech CSE — VIT Vellore  
AI • Computer Vision • Intelligent Systems • V2X Research  

GitHub: https://github.com/theatharvagai  
LinkedIn: https://linkedin.com/in/atharvagai  

---

⭐ If you like this project, consider giving it a star to support intelligent transportation research!
