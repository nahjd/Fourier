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
        return os.path.dirname(sys.executable)  # Folder where the .exe lives
    else:
        return os.path.dirname(os.path.abspath(__file__))  # Folder where .py is

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

        self.settings_file_path = get_settings_file_path()
        Label(root, text="Simulator", font=("Helvetica", 16)).grid(row=0, columnspan=4, pady=20, padx=10, sticky=W)

        Label(root, text="a0:", font=("Arial", 11, "bold")).grid(row=1, column=0, sticky=W, padx=10)
        self.a0_entry = Entry(root)
        self.a0_entry.insert(0, "0")
        self.a0_entry.grid(row=1, column=1)

        Label(root, text="ω0:", font=("Arial", 11, "bold")).grid(row=2, column=0, sticky=W, padx=10)
        self.w0_entry = Entry(root)
        self.w0_entry.insert(0, "1")
        self.w0_entry.grid(row=2, column=1)

        Label(root, text="n_max:", font=("Arial", 11, "bold")).grid(row=3, column=0, sticky=W, padx=10)
        self.n_max_var = StringVar()
        self.n_max_var.trace_add("write", self.update_entries_live)
        self.n_max_entry = Entry(root, textvariable=self.n_max_var)
        self.n_max_entry.insert(0, "1")
        self.n_max_entry.grid(row=3, column=1)

        Label(root, text="N:", font=("Arial", 11, "bold")).grid(row=4, column=0, sticky=W, padx=10)
        self.n_var = StringVar()
        self.n_entry = Entry(root, textvariable=self.n_var)
        self.n_entry.insert(0, "1000")
        self.n_entry.grid(row=4, column=1)

        self.a_entries = []
        self.b_entries = []
        self.labels = []

        Label(root, text="").grid(row=99, column=0, pady=10)
        self.plot_frame = Frame(root)
        self.plot_frame.grid(row=100, column=0, columnspan=4)

        self.canvas = None

        # ✅ Set signal file path at startup
        self.signal_file_path = get_signal_file_path()

        self.a0_entry.bind("<KeyRelease>", lambda e: self.safe_calculate())
        self.w0_entry.bind("<KeyRelease>", lambda e: self.safe_calculate())
        self.n_entry.bind("<KeyRelease>", lambda e: self.safe_calculate())

        

        self.load_settings()
        self.safe_calculate()

    def safe_calculate(self):
        try:
            self.calculate_fourier()
        except Exception:
            pass  # İstifadəçi daxil edərkən error çıxmasın

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
                self.a_entries[i].grid(row=row, column=1)
                self.b_entries[i].grid(row=row, column=3)
                self.labels[i * 2].grid(row=row, column=0)
                self.labels[i * 2 + 1].grid(row=row, column=2)
            else:
                a_label = Label(self.root, text=f"a{i + 1}:", font=("Arial", 11, "bold"))
                a_label.grid(row=row, column=0, padx=10)
                a_entry = Entry(self.root)
                a_entry.insert(0, "0")
                a_entry.grid(row=row, column=1)
                a_entry.bind("<KeyRelease>", lambda e: self.safe_calculate())

                b_label = Label(self.root, text=f"b{i + 1}:", font=("Arial", 11, "bold"))
                b_label.grid(row=row, column=2, padx=10)
                b_entry = Entry(self.root)
                b_entry.insert(0, "0")
                b_entry.grid(row=row, column=3)
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

        # ✅ Write to shared signal.txt
        with open(self.signal_file_path, "w") as f:
            f.write("t, X(t)\n")
            for xi, yi in zip(x, y):
                f.write(f"{xi:.6f}, {yi:.6f}\n")

        self.plot_fourier(x, y)

        self.save_settings()


    def plot_fourier(self, x, y):
        fig = plt.Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(x, y, label="Harmonik Siqnal")
        ax.set_title("Harmonik Siqnal")
        ax.set_xlabel("x")
        ax.set_ylabel("f(x)")
        ax.grid(True)
        ax.legend()

        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()


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
            "n_max": int(self.n_max_entry.get()),
            "N": int(self.n_entry.get()),
            "a": [float(e.get()) for e in self.a_entries[:n_max]],
            "b": [float(e.get()) for e in self.b_entries[:n_max]],

             }
            with open(self.settings_file_path, "w") as f:
                 json.dump(data, f, indent=4)
        except Exception as e:
              print("Ayarlar saxlanılarkən xəta:", e)



if __name__ == '__main__':
    root = Tk()
    app = FourierApp(root)
    root.mainloop()
