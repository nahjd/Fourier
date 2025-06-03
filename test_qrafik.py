import numpy as np
import matplotlib.pyplot as plt

# Parametrlər (istədiyin kimi dəyişə bilərsən)
a0 = 1
a = [2, -0.5]   # a1, a2
b = [1, 0.5]    # b1, b2
N = len(a)

# X oxu üçün nöqtələr (0-dan 2π-yə)
x = np.linspace(0, 2 * np.pi, 1000)
y = np.full_like(x, a0)

# Siqnalı hesablayırıq
for n in range(1, N + 1):
    y += a[n - 1] * np.cos(n * x) + b[n - 1] * np.sin(n * x)

# Max və Min nöqtələri
max_val = np.max(y)
min_val = np.min(y)

print(f"Max qiymət: {max_val}")
print(f"Min qiymət: {min_val}")

# Fayla yaz
with open("signal.txt", "w") as f:
    for xi, yi in zip(x, y):
        f.write(f"{xi:.4f}, {yi:.4f}\n")

# Qrafiki göstər
plt.plot(x, y, label="Fourier Siqnalı")
plt.title("Fourier Qrafiki")
plt.xlabel("x")
plt.ylabel("f(x)")
plt.grid(True)
plt.legend()
plt.show()
