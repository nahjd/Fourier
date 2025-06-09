import customtkinter as ctk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.integrate import trapezoid
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
        if not os.path.exists(signal_path):
            messagebox.showerror("Xəta", "signal.txt faylı mövcud deyil!")
            return None, None

        with open(signal_path, "r") as f:
            lines = f.readlines()
            if lines[0].startswith("t") or lines[0].startswith("#"):
                lines = lines[1:]

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
    a0 = (2 / T) * np.trapezoid(y, x)
    an = []
    bn = []
    for n in range(1, nmax + 1):
        cos_term = np.cos(n * omega_0 * x)
        sin_term = np.sin(n * omega_0 * x)
        a_n = (2 / T) * np.trapezoid(y * cos_term, x)
        b_n = (2 / T) * np.trapezoid(y * sin_term, x)
        an.append(a_n)
        bn.append(b_n)
    return a0, an, bn


def reconstruct_signal(x, a0, an, bn, omega_0):
    y_approx = np.full_like(x, a0 / 2)
    for n in range(1, len(an) + 1):
        y_approx += an[n - 1] * np.cos(n * omega_0 * x) + bn[n - 1] * np.sin(n * omega_0 * x)
    return y_approx


def show_plot(x, y_original, y_approx):
    fig = plt.Figure(figsize=(7, 5.2), dpi=100)
    ax = fig.add_subplot(111)
    ax.plot(x, y_original, label="Orijinal Siqnal", color="blue", linewidth=2)
    ax.plot(x, y_approx, label="Fourier Təqribi", linestyle="--", color="orange", linewidth=2)
    ax.set_title(" Siqnal", fontsize=14)
    ax.set_xlabel("x")
    ax.set_ylabel("f(x)")
    ax.grid(True)
    ax.legend()

    if hasattr(show_plot, 'canvas') and show_plot.canvas:
        show_plot.canvas.get_tk_widget().destroy()

    show_plot.canvas = FigureCanvasTkAgg(fig, master=right_frame)
    show_plot.canvas.draw()
    show_plot.canvas.get_tk_widget().pack(fill="both", expand=True)


def on_omega_change(*args):
    omega_str = omega_var.get()
    nmax_str = nmax_var.get()
    if omega_str.strip() == "" or nmax_str.strip() == "":
        return

    try:
        omega_0 = float(omega_str)
        if omega_0 < 0:
            raise ValueError
    except:
        messagebox.showerror("Xəta", "Omega₀ müsbət ədəddən ibarət olmalıdır!")
        return

    try:
        nmax = int(nmax_str)
        if nmax <= 0:
            raise ValueError
    except:
        messagebox.showerror("Xəta", "Əmsal sayı (n) müsbət tam ədəd olmalıdır!")
        return

    x, y = load_signal_file()
    if x is None or y is None:
        return

    a0, an, bn = calculate_fourier(x, y, omega_0, nmax)
    table.delete(*table.get_children())
    table.insert("", "end", values=("a₀/2", f"{a0 / 2:.6f}", "-"))
    for i in range(len(an)):
        table.insert("", "end", values=(f"{i+1}", f"{an[i]:.6f}", f"{bn[i]:.6f}"))

    y_approx = reconstruct_signal(x, a0, an, bn, omega_0)
    show_plot(x, y, y_approx)


def create_gui():
    global omega_var, nmax_var, table, right_frame

    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    window = ctk.CTk()
    window.title("Fourier Analizi, Proqramçı: Nahid Məmmədov")
    window.geometry("1100x650")

    top_frame = ctk.CTkFrame(window)
    top_frame.pack(pady=10, fill="x")

    omega_label = ctk.CTkLabel(top_frame, text="Omega₀ dəyəri:", font=("Arial", 16))
    omega_label.pack(side="left", padx=(10, 2))

    omega_var = ctk.StringVar()
    omega_var.trace_add("write", on_omega_change)

    omega_entry = ctk.CTkEntry(top_frame, textvariable=omega_var, width=100, font=("Arial", 16))
    omega_entry.pack(side="left")

    n_label = ctk.CTkLabel(top_frame, text="Əmsal sayı (n):", font=("Arial", 16))
    n_label.pack(side="left", padx=(20, 2))

    nmax_var = ctk.StringVar(value="10")
    nmax_entry = ctk.CTkEntry(top_frame, textvariable=nmax_var, width=60, font=("Arial", 16))
    nmax_entry.pack(side="left")

    content_frame = ctk.CTkFrame(window)
    content_frame.pack(fill="both", expand=True, padx=10, pady=10)

    left_frame = ctk.CTkFrame(content_frame)
    left_frame.pack(side="left", fill="y", padx=10)

    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Arial", 14, "bold"))
    style.configure("Treeview", font=("Arial", 13), rowheight=28)

    table = ttk.Treeview(left_frame, columns=("n", "aₙ", "bₙ"), show="headings", height=22)
    table.heading("n", text="n")
    table.heading("aₙ", text="aₙ")
    table.heading("bₙ", text="bₙ")
    table.column("n", width=60, anchor="center")
    table.column("aₙ", width=120, anchor="center")
    table.column("bₙ", width=120, anchor="center")
    table.pack(padx=5, pady=5)

    right_frame = ctk.CTkFrame(content_frame)
    right_frame.pack(side="right", fill="both", expand=True)

    window.mainloop()


if __name__ == "__main__":
    create_gui()
