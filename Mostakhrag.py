import os, sys, time, socket, base64, threading
import tkinter as tk
from tkinter import messagebox
import pyautogui, cv2, numpy as np
import winreg as reg
from flask import Flask
from flask_socketio import SocketIO

# --- بيانات النظام ---
APP_TITLE = "Mida Interactive Ultimate"
SECRET_KEY = "MIDA-2026-PRO-99"

# دالة التفعيل (تعمل في المحاكي)
def check_activation():
    try:
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, r"Software\MidaPro", 0, reg.KEY_READ)
        val, _ = reg.QueryValueEx(key, "Status")
        return val == "Activated"
    except: return False

def start_activation(entry_val, window):
    if entry_val == SECRET_KEY:
        reg.CreateKey(reg.HKEY_CURRENT_USER, r"Software\MidaPro")
        k = reg.OpenKey(reg.HKEY_CURRENT_USER, r"Software\MidaPro", 0, reg.KEY_ALL_ACCESS)
        reg.SetValueEx(k, "Status", 0, reg.REG_SZ, "Activated")
        messagebox.showinfo("Mida", "تم تفعيل النظام بنجاح!")
        window.destroy()
        # تشغيل السيرفر
        threading.Thread(target=run_mida_server, daemon=True).start()
    else:
        messagebox.showerror("خطأ", "المفتاح غير صحيح")

# --- واجهة سيت أب احترافية ---
class ProfessionalUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(APP_TITLE)
        self.root.geometry("450x300")
        self.root.configure(bg="#212121")
        
        tk.Label(self.root, text="MIDA INTERACTIVE", fg="#00E676", bg="#212121", font=("Arial", 22, "bold")).pack(pady=25)
        tk.Label(self.root, text="أدخل مفتاح التفعيل للبدء:", fg="white", bg="#212121").pack()
        
        self.key_entry = tk.Entry(self.root, font=("Arial", 14), justify="center", bg="#333", fg="white", bd=0)
        self.key_entry.pack(pady=15, padx=40, fill="x")
        
        btn = tk.Button(self.root, text="تفعيل الآن", bg="#00E676", fg="black", font=("Arial", 12, "bold"), 
                        command=lambda: start_activation(self.key_entry.get(), self.root))
        btn.pack(pady=20, ipadx=40)
        self.root.mainloop()

# --- قسم السيرفر (حل مشكلة async_mode) ---
app = Flask(__name__)
# استخدمنا threading كوضع افتراضي عشان يشتغل في أي محاكي
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

def capture_and_stream():
    while True:
        try:
            shot = pyautogui.screenshot()
            frame = np.array(shot)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (800, 450)) # جودة ممتازة وسرعة
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
            b64 = base64.b64encode(buffer).decode('utf-8')
            socketio.emit('screen_frame', {'image': b64})
            time.sleep(0.05)
        except: continue

def run_mida_server():
    socketio.start_background_task(capture_and_stream)
    socketio.run(app, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    if check_activation():
        run_mida_server()
    else:
        ProfessionalUI()
          
