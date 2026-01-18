import os, sys, time, socket, base64, threading
import tkinter as tk
from tkinter import messagebox, ttk
import pyautogui, cv2, numpy as np
import winreg as reg
from flask import Flask
from flask_socketio import SocketIO

# --- إعدادات الحماية والنسخة النهائية ---
APP_NAME = "Mida Interactive Ultimate"
SERIAL_KEY = "MIDA-2026-PRO-99"

def check_activation():
    try:
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, r"Software\MidaUltimate", 0, reg.KEY_READ)
        status, _ = reg.QueryValueEx(key, "Activated")
        return status == "YES"
    except: return False

def do_activate(code, root):
    if code == SERIAL_KEY:
        reg.CreateKey(reg.HKEY_CURRENT_USER, r"Software\MidaUltimate")
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, r"Software\MidaUltimate", 0, reg.KEY_ALL_ACCESS)
        reg.SetValueEx(key, "Activated", 0, reg.REG_SZ, "YES")
        messagebox.showinfo("Mida", "تم التفعيل بنجاح! سيتم تشغيل السيرفر الآن.")
        root.destroy()
        # تشغيل السيرفر مباشرة بعد التفعيل
        threading.Thread(target=start_mida_server).start()
    else:
        messagebox.showerror("خطأ", "السيريال غير صحيح")

# --- واجهة السيت أب الاحترافية ---
class ProfessionalSetup:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(APP_NAME)
        self.root.geometry("500x350")
        self.root.configure(bg="#1e1e1e")
        
        frame = tk.Frame(self.root, bg="#2d2d2d", bd=2)
        frame.place(relx=0.5, rely=0.5, anchor="center", width=450, height=300)
        
        tk.Label(frame, text="MIDA INTERACTIVE", fg="#00ffcc", bg="#2d2d2d", font=("Segoe UI", 20, "bold")).pack(pady=20)
        tk.Label(frame, text="أدخل مفتاح المنتج للتثبيت:", fg="white", bg="#2d2d2d").pack()
        
        self.ent = tk.Entry(frame, font=("Consolas", 14), justify="center", bg="#3d3d3d", fg="white", bd=0)
        self.ent.pack(pady=15, padx=30, fill="x")
        
        btn = tk.Button(frame, text="تفعيل وتثبيت النسخة", command=lambda: do_activate(self.ent.get(), self.root),
                        bg="#00ffcc", fg="#1e1e1e", font=("Segoe UI", 12, "bold"), relief="flat")
        btn.pack(pady=20, ipadx=30)
        self.root.mainloop()

# --- قسم السيرفر وبث الشاشة (تم التعديل ليعمل في المحاكي) ---
app = Flask(__name__)
# وضعنا async_mode='threading' لحل مشكلة الصورة الأخيرة
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

def broadcast_screen():
    while True:
        try:
            screen = pyautogui.screenshot()
            frame = np.array(screen)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (800, 450)) # ضغط ذكي
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 45])
            encoded = base64.b64encode(buffer).decode('utf-8')
            socketio.emit('screen_frame', {'image': encoded})
            time.sleep(0.07) # ضبط الـ Delay لثبات البث
        except: continue

def start_mida_server():
    print("Mida Server is Live on Port 5000...")
    socketio.start_background_task(broadcast_screen)
    socketio.run(app, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    if not check_activation():
        ProfessionalSetup()
    else:
        start_mida_server()
