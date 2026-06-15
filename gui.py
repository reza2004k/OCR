import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import requests
from PIL import Image, ImageTk
import io
import json

class OCRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("سامانه هوشمند OCR فارسی")
        self.root.geometry("700x600")
        
        self.image_path = None
        self.server_url = "http://127.0.0.1:5000/ocr"
        
        # دکمه انتخاب عکس
        self.btn_select = tk.Button(root, text="۱. انتخاب تصویر", command=self.select_image, font=("Tahoma", 10))
        self.btn_select.pack(pady=10)
        
        # نمایش پیش‌نمایش عکس
        self.lbl_image = tk.Label(root, text="تصویری انتخاب نشده است")
        self.lbl_image.pack(pady=10)
        
        # دکمه ارسال به سرور
        self.btn_send = tk.Button(root, text="۲. پردازش و استخراج متن (OCR)", command=self.send_to_server, font=("Tahoma", 10), bg="green", fg="white")
        self.btn_send.pack(pady=10)
        
        # کادر نمایش خروجی JSON
        self.lbl_result = tk.Label(root, text="خروجی JSON:", font=("Tahoma", 10))
        self.lbl_result.pack(anchor="w", padx=20)
        
        self.txt_result = scrolledtext.ScrolledText(root, width=80, height=15, font=("Courier New", 10))
        self.txt_result.pack(pady=10, padx=20)

    def select_image(self):
        # باز کردن دیالوگ انتخاب فایل
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")])
        if file_path:
            self.image_path = file_path
            # نمایش پیش‌نمایش کوچک از عکس در محیط برنامه
            img = Image.open(file_path)
            img.thumbnail((200, 200))
            img_tk = ImageTk.PhotoImage(img)
            self.lbl_image.config(image=img_tk, text="")
            self.lbl_image.image = img_tk

    def send_to_server(self):
        if not self.image_path:
            messagebox.showwarning("خطا", "لطفاً ابتدا یک تصویر انتخاب کنید.")
            return
            
        self.txt_result.delete(1.0, tk.END)
        self.txt_result.insert(tk.END, "... در حال پردازش و ارتباط با سرور ...")
        self.root.update_idletasks()
        
        try:
            # ارسال فایل به صورت POST Multipart به وب‌سایت واسط
            with open(self.image_path, 'rb') as f:
                files = {'image': f}
                response = requests.post(self.server_url, files=files)
                
            if response.status_code == 200:
                # مرتب‌سازی و زیباسازی JSON دریافتی جهت نمایش
                json_data = response.json()
                formatted_json = json.dumps(json_data, indent=4, ensure_ascii=False)
                
                self.txt_result.delete(1.0, tk.END)
                self.txt_result.insert(tk.END, formatted_json)
            else:
                self.txt_result.delete(1.0, tk.END)
                messagebox.showerror("خطای سرور", f"خطا از سمت وب‌سایت: {response.text}")
                
        except requests.exceptions.ConnectionError:
            self.txt_result.delete(1.0, tk.END)
            messagebox.showerror("خطای ارتباط", "ارتباط با وب‌سایت واسط برقرار نشد. آیا سرور روشن است؟")
        except Exception as e:
            self.txt_result.delete(1.0, tk.END)
            messagebox.showerror("خطا", f"رخداد خطای غیرمنتظره: {str(e)}")

if __name__ == '__main__':
    root = tk.Tk()
    app = OCRApp(root)
    root.mainloop()