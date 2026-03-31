# FIM_IA
A native macOS File Integrity Monitor featuring kernel-level FSEvents tracking, automated webcam capture, and Telegram alerts.

## 🎯 Core Objectives
* **File System Tracking:** Monitor file creation, modification, deletion, and movement within a confidential directory in real-time.
* **Webcam Capture:** Automatically capture visual evidence of an intruder using the device's native webcam upon any unauthorized file system event.
* **Offline Storage & Alerts:** Provide real-time alerts via Telegram, and save data locally to ensure no evidence is lost if the network disconnects.

## 💻 Tech Stack & Environment
* **Hardware Environment:** Apple M4 Chip, 16 GB RAM
* **Operating System:** macOS Tahoe (Version 26.2, Build 25C56)
* **Language & IDE:** Python 3 | Visual Studio Code (VS Code)
* **Core Libraries:**
  * `watchdog`: Native macOS FSEvents integration.
  * `opencv-python` (`cv2`): Webcam control and image capture.
  * `pyTelegramBotAPI` (`telebot`): Telegram integration and remote alerting.
  * `python-dotenv`: Secure local environment variable management.

## ⚙️ System Design & Architecture
* **The Sensor Engine:** Utilizes `watchdog.observers.Observer` to passively monitor the target directory. A custom `Event_Handler` class filters out hidden macOS files to reduce noise and triggers specific logic based on exact file system events (modified, created, deleted, moved).
* **Image Capture Logic:** Upon an event trigger, the system initializes the Mac's native webcam (`cv2.VideoCapture(0)`), implements a 1.5-second buffer for lens light adjustment, captures the frame, and saves a time-stamped JPEG to a local `evidence_locker`.
* **Network Failure Handling:** The alert system is wrapped in a strict error-handling block. If the Wi-Fi drops or the network is disconnected, the script logs the failure but stays active, ensuring the photographic evidence is safely stored on the local drive.

## 📊 Project Outcomes
The system successfully bridges OS-level event tracking with automated webcam captures, sending Telegram alerts to the administrator in under two seconds. The implementation of the `evidence_locker` ensures that local data is preserved, proving the script continues to function and store evidence even if the computer is disconnected from the internet.
