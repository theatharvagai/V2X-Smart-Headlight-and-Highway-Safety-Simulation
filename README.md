# 🚀 V2X Drowsiness Detection & Autonomous Takeover

🏆 **Hackathon Winner** • 👁️ **Computer Vision** • 📡 **V2X Communication (MQTT)** • 🤖 **Autonomous Safety System**

---

## 🏆 Hackathon Winner! 🏆

This project was conceived and built in **under 24 hours** for a hackathon at **SENSE school, VIT Vellore**. Our team is proud to have secured **first place among 60 competing teams** for this innovative approach to road safety.

---

## 📌 Project Overview

This is a proof-of-concept system that combines **real-time driver drowsiness detection** with a **Vehicle-to-Everything (V2X) communication network**.

The system uses a webcam to monitor the driver's eyes. If signs of drowsiness are detected, it triggers an **autonomous safety protocol**:
1.  The vehicle broadcasts a "DROWSY" alert to all other vehicles on the road via the V2X network.
2.  It initiates an **autonomous takeover**, safely maneuvering the car into a slow lane.
3.  The vehicle then brakes gently until it comes to a complete, safe stop.

A live `matplotlib` dashboard visualizes both the driver's camera feed and a map of all connected vehicles in the simulation.



---

## ⚙️ How It Works

1.  **👁️ Driver Monitoring:** `OpenCV` captures the video feed, and `dlib` detects the driver's face and facial landmarks. The system calculates the **Eye Aspect Ratio (EAR)** in real-time.
2.  **😴 Drowsiness Logic:** If the EAR drops below a set threshold for a specific duration, the system flags the driver as drowsy.
3.  **📡 V2X Communication:** Each instance of the script acts as a vehicle. They all connect to a public **MQTT broker**, broadcasting their ID, position, speed, and status (e.g., "OK" or "DROWSY").
4.  **🤖 Autonomous Takeover:** A state machine manages the vehicle's mode. Upon detecting drowsiness, it transitions from `MANUAL_DRIVING` to `AUTONOMOUS_TAKEOVER`, initiating the lane change and braking sequence.

---

## 🛠️ Technologies Used

* **💻 Python**
* **📦 OpenCV:** For webcam capture and image processing.
* **🧠 Dlib:** For state-of-the-art face and facial landmark detection.
* **📡 Paho-MQTT:** For V2X communication protocol.
* **📊 Matplotlib & NumPy:** For creating the live visualization dashboard.
* **🔬 SciPy:** For calculating Euclidean distance for the EAR.

---

## 🚀 Setup & Installation

1.  **Clone the Repository**
    ```sh
    git clone [https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git)
    cd YOUR_REPO_NAME
    ```

2.  **Create and Activate a Virtual Environment**
    ```sh
    python -m venv venv
    # On macOS/Linux: source venv/bin/activate
    # On Windows: .\\venv\\Scripts\\activate
    ```

3.  **Install Dependencies**
    ```sh
    pip install opencv-python dlib scipy paho-mqtt matplotlib numpy
    ```

4.  **Download the Dlib Shape Predictor Model**
    This project requires the pre-trained facial landmark model.

    * **Source:** The model is provided by the dlib library.
    * **Direct Download Link:** [**shape_predictor_68_face_landmarks.dat.bz2**](http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2)
    * **Instructions:** Download the file from the link above, unzip it, and place the resulting `shape_predictor_68_face_landmarks.dat` file in the root directory of your project.

---

## ▶️ How to Run the Simulation

To see the V2X network in action, you need to run at least two instances of the script.

1.  **Open a new terminal** for each vehicle you want to simulate.
2.  In each terminal, activate the virtual environment and run the script:
    ```sh
    python your_script_name.py
    ```
3.  The script will prompt you to enter a **UNIQUE Vehicle ID** (e.g., `CAR1`) and a target speed.
4.  A `matplotlib` window will pop up for each vehicle, showing its own perspective and the position of other vehicles on the map. To test the autonomous takeover, cover the camera or close your eyes for a few seconds!
