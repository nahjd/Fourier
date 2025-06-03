import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import sys


def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def load_signal_file():
    try:
        signal_path = os.path.join(get_base_path(), "signal.txt")
        with open(signal_path, "r") as f:
            lines = f.readlines()[1:]  # skip header
            x_vals, y_vals = [], []
            for line in lines:
                t_val, y_val = map(float, line.strip().split(','))
                x_vals.append(t_val)
                y_vals.append(y_val)
        return np.array(x_vals), np.array(y_vals)
    except Exception as e:
        messagebox.showerror("Xəta", f"Fayl oxunarkən xəta baş verdi:\n\n{e}")
        return None, None



def calculate_fourier(x, y, omega_0, nmax=10):
    T = x[-1] - x[0]
    a0 = (2 / T) * np.trapz(y, x)
    an = []
    bn = []
    for n in range(1, nmax + 1):
        cos_term = np.cos(n * omega_0 * x)
        sin_term = np.sin(n * omega_0 * x)
        a_n = (2 / T) * np.trapz(y * cos_term, x)
        b_n = (2 / T) * np.trapz(y * sin_term, x)
        an.append(a_n)
        bn.append(b_n)
    return a0, an, bn


def reconstruct_signal(x, a0, an, bn, omega_0):
    y_approx = np.full_like(x, a0 / 2)
    for n in range(1, len(an) + 1):
        y_approx += an[n - 1] * np.cos(n * omega_0 * x) + bn[n - 1] * np.sin(n * omega_0 * x)
    return y_approx


def show_plot(x, y_original, y_approx):
    fig = plt.Figure(figsize=(6, 4), dpi=100)
    ax = fig.add_subplot(111)
    ax.plot(x, y_original, label="Orijinal Siqnal")
    ax.plot(x, y_approx, label="Fourier Təqribi", linestyle="--")
    ax.set_title("Harmonik Siqnal")
    ax.set_xlabel("x")
    ax.set_ylabel("f(x)")
    ax.grid(True)
    ax.legend()

    if hasattr(show_plot, 'canvas') and show_plot.canvas:
        show_plot.canvas.get_tk_widget().destroy()

    show_plot.canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    show_plot.canvas.draw()
    show_plot.canvas.get_tk_widget().pack()


def on_omega_change(*args):
    omega_str = omega_var.get()
    if not omega_str:
        result_label.config(text="Omega₀ daxil edin.")
        return
    try:
        omega_0 = float(omega_str)
        if omega_0 <= 0:
            raise ValueError("Omega₀ müsbət olmalıdır.")
    except Exception as e:
        result_label.config(text=f"Xəta: {e}")
        return

    x, y = load_signal_file()
    if x is None or y is None:
        result_label.config(text="Siqnal faylı oxunmadı.")
        return

    a0, an, bn = calculate_fourier(x, y, omega_0)
    text = f"a₀ = {a0:.6f}\n"
    for i in range(len(an)):
        text += f"a{i+1} = {an[i]:.6f},  b{i+1} = {bn[i]:.6f}\n"
    result_label.config(text=text)

    y_approx = reconstruct_signal(x, a0, an, bn, omega_0)
    show_plot(x, y, y_approx)


def create_gui():
    global omega_var, result_label, plot_frame

    window = tk.Tk()
    window.title("Furye Analizi, Proqramcı: Nahid Məmmədov")

    # Yeni label hissəsi (iki hissəyə bölünmüş)
    frame_label = tk.Frame(window)
    frame_label.pack(pady=5)

    label_bold = tk.Label(frame_label, text="Omega₀", font=("Arial", 12, "bold"))
    label_bold.pack(side="left")

    label_normal = tk.Label(frame_label, text=" dəyərini daxil edin:", font=("Arial", 12))
    label_normal.pack(side="left")

    omega_var = tk.StringVar()
    omega_var.trace_add("write", on_omega_change)
    omega_entry = ttk.Entry(window, textvariable=omega_var)
    omega_entry.pack(pady=5)

    result_label = tk.Label(window, text="Nəticələr burada göstəriləcək", font=("Arial", 12), justify="left")
    result_label.pack(pady=10)

    plot_frame = tk.Frame(window)
    plot_frame.pack(pady=10)

    window.mainloop()


if __name__ == "__main__":
    create_gui()
