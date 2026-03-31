import os
import telebot
import logging
import dotenv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import cv2  # <--- NEW: The Computer Vision Library

dotenv.load_dotenv('.env')
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

if not CHAT_ID or not BOT_TOKEN:
    raise ValueError("CRITICAL ERROR: Values not imported from .env")

bot = telebot.TeleBot(BOT_TOKEN)

logging.basicConfig(
    filename='File_LOG.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# --- EVIDENCE LOCKER SETUP ---
EVIDENCE_DIR = "evidence_locker"
if not os.path.exists(EVIDENCE_DIR):
    os.makedirs(EVIDENCE_DIR)
    print(f"[+] Created local offline storage: {EVIDENCE_DIR}")

class Event_Handler(FileSystemEventHandler):
    
    def is_valid_file(self, filepath):
        filename = os.path.basename(filepath)
        return not filename.startswith('.')

    # --- UPGRADED WEBCAM TRAP (Offline Capable) ---
    def capture_intruder(self):
        try:
            logging.info("Intruder detected. Initializing webcam...")
            cap = cv2.VideoCapture(0) 
            
            if not cap.isOpened():
                logging.error("Webcam blocked! macOS denied permission or camera in use.")
                return None

            time.sleep(1.5) 
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                # Generate a unique filename based on the exact second it was taken
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                photo_filename = f"intruder_{timestamp}.jpg"
                photo_path = os.path.join(EVIDENCE_DIR, photo_filename)
                
                # Save it permanently to the Mac
                cv2.imwrite(photo_path, frame)
                logging.info(f"SUCCESS: Offline snapshot secured at {photo_path}")
                
                return photo_path # Hand the path back to the alert function
            else:
                logging.error("Webcam fired, but screen was black.")
                return None
                
        except Exception as e:
            logging.error(f"Critical Webcam Engine Failure: {e}")
            return None

    # --- YOUR EXISTING EVENTS ---
    def on_modified(self, event):
        if not event.is_directory and self.is_valid_file(event.src_path):
            logging.info(f"File modified : {event.src_path}")
            self.SendAlert("File modified", event.src_path)
        return super().on_modified(event)
        
    def on_created(self, event):
        if self.is_valid_file(event.src_path):
            item_type = "Folder" if event.is_directory else "File"
            logging.info(f"{item_type} created : {event.src_path}")
            self.SendAlert(f"{item_type} created", event.src_path)
        return super().on_created(event)
        
    def on_deleted(self, event):
        if self.is_valid_file(event.src_path):
            item_type = "Folder" if event.is_directory else "File"
            logging.info(f"{item_type} deleted : {event.src_path}")
            self.SendAlert(f"{item_type} deleted", event.src_path)
        return super().on_deleted(event)
        
    def on_moved(self, event):
        if self.is_valid_file(event.src_path):
            item_type = "Folder" if event.is_directory else "File"
            logging.info(f"{item_type} renamed from {event.src_path} to {event.dest_path}")
            self.SendAlert(f"{item_type} renamed", event.dest_path)
        return super().on_moved(event)

    # --- UPGRADED TELEMETRY (With Offline Survival) ---
    def SendAlert(self, action, path):
        # 1. Secure the evidence locally FIRST
        photo_path = self.capture_intruder()

        # 2. Try to sync to the cloud (Telegram)
        try:
            mssg = f"🚨 **ALERT!**\nAction: {action}\nPath: `{path}`"
            bot.send_message(CHAT_ID, mssg, parse_mode="Markdown")

            # If we got a photo, upload it
            if photo_path:
                with open(photo_path, "rb") as photo:
                    bot.send_photo(CHAT_ID, photo, caption="📸 **INTRUDER CAPTURED**", parse_mode="Markdown")
            
            # NOTE: We no longer delete the photo! It stays in the evidence_locker.

        except Exception as e:
            # If Wi-Fi is off, Telegram will crash here. We catch it and keep the script alive.
            logging.warning(f"OFFLINE MODE: Could not send Telegram alert. Evidence safely stored locally. Error: {e}")
            print("[!] Wi-Fi offline. Alert and photo saved to local evidence locker.")


if __name__ == '__main__':
    target_folder = '/Users/benhursanthosh/Desktop/confidential'
    event_handler = Event_Handler()
    observer = Observer()
    observer.schedule(event_handler, target_folder, recursive=True)
    observer.start()
    
    print(f"Active! I am watching {target_folder}")
    bot.send_message(CHAT_ID, "🟢 **Sentinel System Online.** Monitoring local file system.", parse_mode="Markdown")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nShutting Down :)")
    observer.join()