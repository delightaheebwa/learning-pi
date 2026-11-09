"""
Phase 1 L08 — Optimization (Gradient Descent Family)
Race three optimizers on the Rosenbrock benchmark:
  vanilla GD, SGD with Momentum, Adam.

Rosenbrock: f(x,y) = (1-x)^2 + 100*(y - x^2)^2    minimum at (1, 1)
Gradient:
  df/dx = -2*(1-x) - 400*x*(y - x^2)
  df/dy = 200*(y - x^2)
"""

import numpy as np


def rosenbrock(w):
    x, y = w[0], w[1]
    return (1 - x) ** 2 + 100 * (y - x ** 2) ** 2


def rosenbrock_grad(w):
    x, y = w[0], w[1]
    dx = -2 * (1 - x) - 400 * x * (y - x ** 2)
    dy = 200 * (y - x ** 2)
    return np.array([dx, dy])


class GradientDescent:
    def __init__(self, lr=0.001):
        self.lr = lr

    def step(self, w, grad):
        return w - self.lr * grad


class SGDMomentum:
    def __init__(self, lr=0.001, beta=0.9):
        self.lr, self.beta = lr, beta
        self.v = 0.0

    def step(self, w, grad):
        self.v = self.beta * self.v + grad          # raw velocity accumulation
        return w - self.lr * self.v


class Adam:
    def __init__(self, lr=0.001, beta1=0.9, beta2=0.999, eps=1e-8):
        self.lr, self.beta1, self.beta2, self.eps = lr, beta1, beta2, eps
        self.m = 0.0
        self.v = 0.0
        self.t = 0

    def step(self, w, grad):
        self.t += 1
        self.m = self.beta1 * self.m + (1 - self.beta1) * grad   # first moment (mean of grad)
        self.v = self.beta2 * self.v + (1 - self.beta2) * grad ** 2  # second moment (mean of grad^2)
        m_hat = self.m / (1 - self.beta1 ** self.t)             # bias correction
        v_hat = self.v / (1 - self.beta2 ** self.t)
        return w - self.lr * (m_hat / (np.sqrt(v_hat) + self.eps))


def run(optimizer, start, iters=20000, tol=1e-6):
    w = np.array(start, dtype=float)
    loss = rosenbrock(w)
    history = [loss]
    converged_at = None
    for i in range(iters):
        g = rosenbrock_grad(w)
        w = optimizer.step(w, g)
        loss = rosenbrock(w)
        history.append(loss)
        if converged_at is None and loss < tol:
            converged_at = i + 1
    return w, history, converged_at


if __name__ == "__main__":
    start = [-1.0, 1.0]   # same start used in the paper practice (CP1)

    configs = {
        "Vanilla GD":   GradientDescent(lr=0.0005),
        "SGD Momentum": SGDMomentum(lr=0.0005, beta=0.9),
        "Adam":         Adam(lr=0.001),
    }

    print(f"{'optimizer':<14} {'final w':<22} {'final loss':>12}  {'converged @':>12}")
    print("-" * 64)
    for name, opt in configs.items():
        w, hist, conv = run(opt, start)
        w_fmt = f"({w[0]:.4f}, {w[1]:.4f})"
        conv_fmt = str(conv) if conv is not None else "NOT converged"
        print(f"{name:<14} {w_fmt:<22} {hist[-1]:>12.3e}  {conv_fmt:>12}")

    # Trace first few + last loss for each, to show convergence speed difference
    print("\nLoss trajectory (first 5 iters, then landmarks):")
    for name, opt in configs.items():
        w = np.array(start, dtype=float)
        h = [rosenbrock(w)]
        for i in range(20000):
            w = opt.step(w, rosenbrock_grad(w))
            h.append(rosenbrock(w))
        marks = [0, 1, 2, 3, 4, 10, 50, 100, 500, 1000, 5000, 10000, 20000]
        out = "  ".join(f"t{m}={h[m]:.2e}" for m in marks if m < len(h))
        print(f"{name:<14} {out}")
