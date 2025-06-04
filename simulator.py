import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import json
from tkinter import *
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def get_signal_file_path():
    return os.path.join(get_base_path(), "signal.txt")

def get_settings_file_path():
    return os.path.join(get_base_path(), "settings.json")

def format_number(value):
    return str(int(value)) if float(value).is_integer() else str(value)

class FourierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulator, Proqramcı: Nahid Məmmədov")
        self.root.configure(bg="#2e2e2e")

        self.settings_file_path = get_settings_file_path()

        main_frame = Frame(root, bg="#2e2e2e")
        main_frame.pack(fill=BOTH, expand=True)

        left_frame = Frame(main_frame, bg="#2e2e2e")
        left_frame.pack(side=LEFT, fill=Y, expand=False)

        right_frame = Frame(main_frame, bg="#2e2e2e")
        right_frame.pack(side=RIGHT, fill=BOTH, expand=True)

        canvas = Canvas(left_frame, bg="#2e2e2e", highlightthickness=0)
        scrollbar = Scrollbar(left_frame, orient=VERTICAL, command=canvas.yview)
        self.scrollable_frame = Frame(canvas, bg="#2e2e2e")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=LEFT, fill=Y, expand=False)
        scrollbar.pack(side=RIGHT, fill=Y)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        label_font = ("Arial", 12, "bold")
        entry_font = ("Arial", 12)

        Label(self.scrollable_frame, text="Simulator", font=("Helvetica", 18, "bold"),
              bg="#2e2e2e", fg="white").grid(row=0, columnspan=4, pady=10, padx=10, sticky=W)

        def add_labeled_entry(row, text, var=None, default="0"):
            Label(self.scrollable_frame, text=text, font=label_font,
                  bg="#2e2e2e", fg="white").grid(row=row, column=0, sticky=W, padx=10, pady=2)
            entry = Entry(self.scrollable_frame, font=entry_font, bg="#444", fg="white",
                          insertbackground='white', textvariable=var)
            entry.insert(0, default)
            entry.grid(row=row, column=1, columnspan=3, sticky=W+E, pady=2)
            return entry

        self.a0_entry = add_labeled_entry(1, "a0:", default="0")
        self.w0_entry = add_labeled_entry(2, "ω0:", default="1")
        self.n_max_var = StringVar()
        self.n_max_var.trace_add("write", self.update_entries_live)
        self.n_max_entry = add_labeled_entry(3, "n_max:", self.n_max_var, default="1")
        self.n_var = StringVar()
        self.n_entry = add_labeled_entry(4, "N:", self.n_var, default="1000")

        self.a_entries = []
        self.b_entries = []
        self.labels = []

        self.plot_frame = Frame(right_frame, bg="#2e2e2e")
        self.plot_frame.pack(fill=BOTH, expand=True)

        self.canvas = None
        self.signal_file_path = get_signal_file_path()

        for entry in [self.a0_entry, self.w0_entry, self.n_entry]:
            entry.bind("<KeyRelease>", lambda e: self.safe_calculate())

        self.load_settings()
        self.safe_calculate()

    def safe_calculate(self):
        try:
            self.calculate_fourier()
        except Exception:
            pass

    def update_entries_live(self, *args):
        value = self.n_max_var.get()
        if value.isdigit():
            self.add_entries(int(value))
            self.safe_calculate()

    def add_entries(self, n_max):
        max_current = len(self.a_entries)
        row = 6

        for i in range(n_max):
            if i < max_current:
                self.a_entries[i].grid(row=row, column=1, sticky=W)
                self.b_entries[i].grid(row=row, column=3, sticky=W)
                self.labels[i * 2].grid(row=row, column=0, sticky=W, padx=10)
                self.labels[i * 2 + 1].grid(row=row, column=2, sticky=W, padx=10)
            else:
                a_label = Label(self.scrollable_frame, text=f"a{i + 1}:", font=("Arial", 11, "bold"),
                                bg="#2e2e2e", fg="white")
                a_label.grid(row=row, column=0, padx=10, sticky=W)
                a_entry = Entry(self.scrollable_frame, font=("Arial", 11), bg="#444", fg="white", insertbackground='white', width=10)
                a_entry.insert(0, "0")
                a_entry.grid(row=row, column=1, sticky=W)
                a_entry.bind("<KeyRelease>", lambda e: self.safe_calculate())

                b_label = Label(self.scrollable_frame, text=f"b{i + 1}:", font=("Arial", 11, "bold"),
                                bg="#2e2e2e", fg="white")
                b_label.grid(row=row, column=2, padx=10, sticky=W)
                b_entry = Entry(self.scrollable_frame, font=("Arial", 11), bg="#444", fg="white", insertbackground='white', width=10)
                b_entry.insert(0, "0")
                b_entry.grid(row=row, column=3, sticky=W)
                b_entry.bind("<KeyRelease>", lambda e: self.safe_calculate())

                self.a_entries.append(a_entry)
                self.b_entries.append(b_entry)
                self.labels.extend([a_label, b_label])
            row += 1

        for i in range(n_max, max_current):
            self.a_entries[i].grid_remove()
            self.b_entries[i].grid_remove()
            self.labels[i * 2].grid_remove()
            self.labels[i * 2 + 1].grid_remove()

    def calculate_fourier(self):
        a0 = float(self.a0_entry.get())
        w0 = float(self.w0_entry.get())
        n_max = int(self.n_max_entry.get())
        N = int(self.n_entry.get())

        if N < 10:
            messagebox.showerror("Xəta", "N dəyəri çox kiçikdir, ən azı 10 olmalıdır.")
            return
        if n_max < 1:
            messagebox.showerror("Xəta", "n_max ən azı 1 olmalıdır.")
            return

        if n_max > len(self.a_entries):
            self.add_entries(n_max)

        a = [float(e.get()) for e in self.a_entries[:n_max]]
        b = [float(e.get()) for e in self.b_entries[:n_max]]

        x = np.linspace(0, 2 * np.pi, N)
        y = np.full_like(x, a0 / 2)

        for n in range(1, n_max + 1):
            y += a[n - 1] * np.cos(n * w0 * x) + b[n - 1] * np.sin(n * w0 * x)

        if np.max(np.abs(y)) > 1e4:
            messagebox.showerror("Xəta", "Siqnal çox böyükdür.")
            return

        with open(self.signal_file_path, "w") as f:
            f.write("t, X(t)\n")
            for xi, yi in zip(x, y):
                f.write(f"{xi:.6f}, {yi:.6f}\n")

        self.plot_fourier(x, y)
        self.save_settings()

    def plot_fourier(self, x, y):
        fig = plt.Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(x, y, color='cyan')
        ax.set_facecolor("#1e1e1e")
        fig.patch.set_facecolor('#2e2e2e')
        ax.set_title(" Siqnal", color='white')
        ax.set_xlabel("x", color='white')
        ax.set_ylabel("f(x)", color='white')
        ax.tick_params(colors='white')
        ax.grid(True, color='gray')
        # ax.legend(facecolor="#2e2e2e", edgecolor="gray", labelcolor="white")

        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=True)

    def load_settings(self):
        if os.path.exists(self.settings_file_path):
            try:
                with open(self.settings_file_path, "r") as f:
                    data = json.load(f)

                self.a0_entry.delete(0, END)
                self.a0_entry.insert(0, format_number(data.get("a0", 0)))
                self.w0_entry.delete(0, END)
                self.w0_entry.insert(0, format_number(data.get("w0", "1")))

                self.n_max_var.set(format_number(data.get("n_max", "1")))
                self.n_var.set(format_number(data.get("N", "1000")))

                a_list = data.get("a", [])
                b_list = data.get("b", [])
                self.add_entries(len(a_list))

                for i, val in enumerate(a_list):
                    self.a_entries[i].delete(0, END)
                    self.a_entries[i].insert(0, format_number(val))

                for i, val in enumerate(b_list):
                    self.b_entries[i].delete(0, END)
                    self.b_entries[i].insert(0, format_number(val))

            except Exception as e:
                print("Ayarlar yüklənərkən xəta:", e)

    def save_settings(self):
        try:
            n_max = int(self.n_max_entry.get())
            data = {
                "a0": float(self.a0_entry.get()),
                "w0": float(self.w0_entry.get()),
                "n_max": n_max,
                "N": int(self.n_entry.get()),
                "a": [float(e.get()) for e in self.a_entries[:n_max]],
                "b": [float(e.get()) for e in self.b_entries[:n_max]]
            }
            with open(self.settings_file_path, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print("Ayarlar saxlanarkən xəta:", e)

if __name__ == "__main__":
    root = Tk()
    app = FourierApp(root)
    root.mainloop()
