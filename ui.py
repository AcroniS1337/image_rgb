import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import cv2
import numpy as np
from PIL import Image, ImageTk
import os

from image_editor import ImageEditor


class AppUI:

    def __init__(self, root: tk.Tk):
        self.root = root
        self.image_core = ImageEditor()
        self.photo_image = None

        self._configure_window()
        self._apply_styles()
        self._build_layout()

    def _configure_window(self):
        self.root.geometry("1100x750")
        self.root.configure(bg="#1e1e2e")

    def _apply_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 10), padding=6,
                        background="#313244", foreground="#cdd6f4",
                        borderwidth=0, focusthickness=0)
        style.map("TButton",
                  background=[("active", "#45475a"), ("pressed", "#585b70")])
        style.configure("TLabel", background="#1e1e2e", foreground="#cdd6f4",
                        font=("Segoe UI", 10))

    def _build_layout(self):
        left_panel = self._build_left_panel()
        self._build_right_panel()

    def _build_left_panel(self) -> tk.Frame:
        left = tk.Frame(self.root, bg="#181825", width=240)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 5), pady=10)
        left.pack_propagate(False)

        tk.Label(left, bg="#181825",
                 fg="#cba6f7", font=("Segoe UI", 14, "bold")).pack(pady=(16, 8))

        self._build_load_section(left)
        self._build_channels_section(left)
        self._build_variant_section(left)
        self._build_utility_buttons(left)

        return left

    def _build_load_section(self, parent: tk.Frame):
        self._section(parent, "", [
            ("Открыть файл",          self._on_load_file),
            ("Сделать снимок с камеры", self._on_capture_webcam),
        ])

    def _build_channels_section(self, parent: tk.Frame):
        self._section(parent, "", [
            ("Красный канал", lambda: self._on_show_channel("R")),
            ("Зелёный канал", lambda: self._on_show_channel("G")),
            ("Синий канал", lambda: self._on_show_channel("B")),
        ])

    def _build_variant_section(self, parent: tk.Frame):
        self._section(parent, "", [
            ("Изменить размер",         self._on_resize),
            ("Добавить границы",        self._on_add_border),
            ("Нарисовать прямоугольник", self._on_draw_rectangle),
        ])

    def _build_utility_buttons(self, parent: tk.Frame):
        ttk.Button(parent, text="Сбросить",
                   command=self._on_reset).pack(fill=tk.X, padx=12, pady=(16, 4))
        ttk.Button(parent, text="Сохранить",
                   command=self._on_save).pack(fill=tk.X, padx=12, pady=4)

    def _build_right_panel(self):
        right = tk.Frame(self.root, bg="#1e1e2e")
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True,
                   padx=(5, 10), pady=10)

        self._build_status_bar(right)
        self._build_canvas(right)

    def _build_status_bar(self, parent: tk.Frame):
        self.status_var = tk.StringVar(
            value="Загрузите изображение для начала работы.")
        self.status_label = tk.Label(
            parent, textvariable=self.status_var,
            bg="#181825", fg="#a6e3a1",
            font=("Segoe UI", 9), anchor="w", padx=10)
        self.status_label.pack(fill=tk.X, pady=(0, 6))

    def _build_canvas(self, parent: tk.Frame):
        canvas_frame = tk.Frame(parent, bg="#11111b")
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(canvas_frame, bg="#11111b",
                                highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", lambda e: self._redraw())

    def _section(self, parent: tk.Frame, title: str, buttons: list):
        for label, cmd in buttons:
            ttk.Button(parent, text=label, command=cmd).pack(
                fill=tk.X, padx=12, pady=2)

    def _set_status(self, msg: str, color: str = "#a6e3a1"):
        self.status_var.set(msg)
        self.status_label.configure(fg=color)

    def _require_image(self) -> bool:
        if not self.image_core.has_image():
            messagebox.showwarning("Нет изображения",
                                   "Сначала загрузите или снимите изображение.")
            return False
        return True

    def _display(self, bgr_img: np.ndarray):
        rgb = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb)

        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        if cw < 2 or ch < 2:
            cw, ch = 800, 600

        ih, iw = bgr_img.shape[:2]
        scale = min(cw / iw, ch / ih, 1.0)
        new_w = max(1, int(iw * scale))
        new_h = max(1, int(ih * scale))
        pil_img = pil_img.resize((new_w, new_h), Image.LANCZOS)

        self.photo_image = ImageTk.PhotoImage(pil_img)
        self.canvas.delete("all")
        self.canvas.create_image(cw // 2, ch // 2, anchor=tk.CENTER,
                                 image=self.photo_image)

    def _redraw(self):
        if self.image_core.has_image():
            self._display(self.image_core.current)

    def _ask_int(self, title: str, prompt: str,
                 minval: int = 1, maxval: int = 10000,
                 initial: int | None = None) -> int | None:
        return simpledialog.askinteger(title, prompt,
                                       minvalue=minval, maxvalue=maxval,
                                       initialvalue=initial,
                                       parent=self.root)

    def _on_load_file(self):
        path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[("Images", "*.png *.jpg *.jpeg")])
        if not path:
            return
        try:
            img = self.image_core.load_from_file(path)
            self._display(img)
            h, w = img.shape[:2]
            self._set_status(
                f"Загружено: {os.path.basename(path)}  ({w}×{h} px)")
        except Exception as e:
            messagebox.showerror("Ошибка загрузки", str(e))
            self._set_status("Ошибка загрузки файла.", "#f38ba8")

    def _on_capture_webcam(self):
        try:
            cap = self.image_core.capture_from_webcam()
        except RuntimeError as e:
            messagebox.showerror(
                "Камера недоступна",
                str(e) + "\n\nВозможные решения:\n"
                "1) Убедитесь, что камера не занята другим приложением.\n"
                "2) Проверьте права доступа в настройках ОС.\n"
                "3) Проверьте подключена ли камера к компьютеру\ноутубку")
            self._set_status("Веб-камера недоступна.", "#f38ba8")
            return
        self._open_webcam_window(cap)

    def _open_webcam_window(self, cap: cv2.VideoCapture):
        win = tk.Toplevel(self.root)
        win.title("Предпросмотр — нажмите «Снять»")
        win.configure(bg="#1e1e2e")
        win.resizable(False, False)

        lbl = tk.Label(win, bg="#11111b")
        lbl.pack(padx=10, pady=10)

        state = {"running": True, "last_frame": None}

        def update():
            if not state["running"]:
                return
            ret, frame = cap.read()
            if ret:
                state["last_frame"] = frame
                rgb = cv2.cvtColor(
                    cv2.resize(frame, (640, 480)), cv2.COLOR_BGR2RGB)
                ph = ImageTk.PhotoImage(Image.fromarray(rgb))
                lbl.configure(image=ph)
                lbl.image = ph
            win.after(30, update)

        def take_photo():
            state["running"] = False
            cap.release()
            frame = state["last_frame"]
            if frame is not None:
                self.image_core.set_image(frame)
                self._display(self.image_core.current)
                h, w = frame.shape[:2]
                self._set_status(f"Снимок сделан ({w}×{h} px)")
            win.destroy()

        def on_close():
            state["running"] = False
            cap.release()
            win.destroy()

        tk.Button(win, text="📷  Снять", bg="#89b4fa", fg="#1e1e2e",
                  font=("Segoe UI", 11, "bold"), command=take_photo,
                  padx=20, pady=6).pack(pady=(0, 10))
        win.protocol("WM_DELETE_WINDOW", on_close)
        update()

    def _on_show_channel(self, channel: str):
        if not self._require_image():
            return
        try:
            result = self.image_core.extract_channel(channel)
            self._display(result)
            names = {"R": "красный", "G": "зелёный", "B": "синий"}
            self._set_status(f"Показан {names[channel]} канал.")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _on_resize(self):
        if not self._require_image():
            return
        h, w = self.image_core.current.shape[:2]
        new_w = self._ask_int("Ширина", "Новая ширина (px):", 1, 8000, w)
        if new_w is None:
            return
        new_h = self._ask_int("Высота", "Новая высота (px):", 1, 8000, h)
        if new_h is None:
            return
        try:
            result = self.image_core.resize(new_w, new_h)
            self._display(result)
            self._set_status(f"Размер изменён: {new_w}×{new_h} px.")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _on_add_border(self):
        if not self._require_image():
            return
        size = self._ask_int("Граница", "Размер границ (px):", 1, 500, 20)
        if size is None:
            return
        try:
            result = self.image_core.add_border(size)
            self._display(result)
            self._set_status(f"Добавлены границы {size} px.")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _on_draw_rectangle(self):
        if not self._require_image():
            return
        ih, iw = self.image_core.current.shape[:2]
        x1 = self._ask_int("Прямоугольник", f"X1 (0–{iw}):", 0, iw - 1, 10)
        if x1 is None:
            return
        y1 = self._ask_int("Прямоугольник", f"Y1 (0–{ih}):", 0, ih - 1, 10)
        if y1 is None:
            return
        x2 = self._ask_int(
            "Прямоугольник", f"X2 ({x1+1}–{iw}):", x1 + 1, iw, iw - 10)
        if x2 is None:
            return
        y2 = self._ask_int(
            "Прямоугольник", f"Y2 ({y1+1}–{ih}):", y1 + 1, ih, ih - 10)
        if y2 is None:
            return
        t = self._ask_int(
            "Прямоугольник", "Толщина (px, -1 = заливка):", -1, 50, 2)
        if t is None:
            return
        try:
            result = self.image_core.draw_rectangle(x1, y1, x2, y2, t)
            self._display(result)
            self._set_status(
                f"Прямоугольник ({x1},{y1})–({x2},{y2}), толщина={t}.")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _on_reset(self):
        result = self.image_core.reset()
        if result is None:
            messagebox.showwarning(
                "Нет изображения", "Оригинал ещё не загружен.")
            return
        self._display(result)
        self._set_status("Изображение сброшено к оригиналу.")

    def _on_save(self):
        if not self._require_image():
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg")])
        if not path:
            return
        try:
            self.image_core.save(path)
            self._set_status(f"Сохранено: {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", str(e))
            self._set_status("Ошибка при сохранении.", "#f38ba8")
