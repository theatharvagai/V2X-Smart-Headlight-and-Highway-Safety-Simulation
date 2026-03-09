# 🚗⚡ V2X Smart Highway Simulation System (v5.0)

### 🌐 AI + V2X + Computer Vision + Modern UI Ecosystem

<p align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Orbitron&size=30&duration=3000&color=00F5FF&center=true&vCenter=true&width=1000&lines=V2X+Smart+Highway+v5.0;Connected+Vehicle+Ecosystem;Glassmorphism+UI+Dashboard;Real-Time+V2X+Signal+Pulses" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Version-5.0-blue?style=for-the-badge" />
  <img src="https://img.shields.io/badge/UI-Modern%20HUD-cyan?style=for-the-badge" />
  <img src="https://img.shields.io/badge/AI-Drowsiness%20Detection-green?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Protocol-MQTT-orange?style=for-the-badge" />
</p>

---

# 🌍 Overview

The **V2X Smart Highway Simulation System v5.0** is an advanced, real-time connected vehicle ecosystem. It simulates a cooperative smart transportation network where multiple vehicle nodes communicate over MQTT to share critical safety data and telemetry.

This version introduces a **Modern HUD Experience**, featuring glassmorphism design elements, real-time V2X signal visualization, and enhanced AI-driven safety protocols.

---

# 🎥 Project Demo (Latest UI)

<p align="center">
  <img src="assets/dashboard.png" width="300" alt="Modern Dashboard"/>
  <img src="assets/navigation.png" width="300" alt="Nav System"/>
  <img src="assets/drowsy.png" width="300" alt="AI Safety"/>
</p>

<p align="center">
  <sub>📊 Glassmorphism Dashboard • 📡 V2X Signal Pulses • 🚑 Emergency HUD Alerts</sub>
</p>

---

# 🚀 New in Version 5.0 (Modernization Pass)

*   **📡 V2X Signal Visualization:** Real-time expanding pulse animations from vehicles to represent active data exchange.
*   **🎨 Glassmorphism UI:** Semi-transparent, blurred dashboard panels and alert boxes for a high-tech cockpit feel.
*   **🏎️ Role-Based Color Coding:** 
    *   🔵 **Blue:** Your Vehicle (Player)
    *   🔴 **Red:** Other Connected Vehicles
    *   🟠 **Yellow/Orange:** Emergency Vehicles (Ambulances)
*   **🚨 Enhanced HUD Alerts:** High-visibility pulsing alerts for **EMERGENCY BRAKING** and **VEHICLE AHEAD**.
*   **🛣️ Service Lane Overlay:** Clear, high-impact "SERVICE LANE" text blitted directly on the infrastructure with smart opacity.
*   **📈 Visual Speed Gauge:** Modern progress-bar style gauge replacing static text for real-time velocity monitoring.

---

# 🔥 Core Features

## 🚗 Distributed V2X Networking
*   **Multi-Node Sync:** Run on different systems to see real-time interaction.
*   **Low Latency:** Optimized MQTT broadcasting for sub-100ms telemetry updates.
*   **V2V & V2I:** Cooperative collision avoidance and smart streetlight response.

## 🧠 AI Safety Intelligence
*   **Computer Vision:** Real-time drowsiness detection using OpenCV.
*   **Auto-Pilot Response:** Automatic redirection to the Service Lane and emergency stopping when fatigue is detected.
*   **Adaptive Headlights:** AI-driven High/Low beam switching based on oncoming V2X data to prevent glare.

## 🛣️ Intelligent Infrastructure
*   **5-Lane Architecture:** 
    *   Lane 0: Incoming/Opposite Traffic
    *   Lane 1-3: Forward Traffic
    *   Lane 4: **SERVICE LANE** (Emergency & Drowsy Parking)
*   **Smart Streetlights:** Dynamically activate only when vehicles are nearby to conserve energy.

---

# 🛠️ Tech Stack

| Category             | Technology                                  |
| -------------------- | ------------------------------------------- |
| Language             | 🐍 Python 3.10+                             |
| Graphics Engine      | 🎮 Pygame (Modern Hardware Accel)           |
| AI & CV              | 🧠 OpenCV + NumPy                           |
| Networking           | 📡 MQTT (EMQX Cloud Broker)                 |
| UI Design            | ✨ Glassmorphism & HUD Principles           |

---

# 🎮 Controls & Interaction

| Control             | Function                   |
| ------------------- | -------------------------- |
| **Steer Buttons**   | Shift between 5 dynamic lanes |
| **Speed Gauges**    | Adjust target cruise speed |
| **X Key**           | Force-trigger Drowsiness (Simulated) |
| **🚑 Call AMB**     | Spawn an intelligent Emergency Vehicle |
| **🗺️ Map Interaction** | Click to Expand or inject obstacles |

---

# ⚙️ Quick Start

```bash
# 1. Install Dependencies
pip install pygame opencv-python numpy paho-mqtt

# 2. Launch Simulation
python v2x_unified_complete.py
```

---

# 👨‍💻 Author

**Atharva Gai**
M.Tech CSE — VIT Vellore
*Specializing in Intelligent Transportation & Distributed V2X Systems*

🔗 [GitHub](https://github.com/theatharvagai) • [LinkedIn](https://linkedin.com/in/atharvagai)

---

# ⭐ Support the Research
If you find this V2X framework useful for your research or project, please consider giving it a star!
