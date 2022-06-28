import numpy as np
from scipy.integrate import odeint
from VerletPython import acceleration

def ode(y, t, m):
    r = y[:y.shape[0] // 2]
    v = y[y.shape[0] // 2:]
    dydt = np.concatenate((v, acceleration(m, r.reshape((-1, 2))).flatten()))
    return dydt

def OdeintSolver(m, r, v, T, k):
    t = np.linspace(0, T, k)
    sol = odeint(ode, np.concatenate((r.flatten(), v.flatten())), t, args = (m, )).transpose()
    return sol[:sol.shape[0] // 2,:].reshape((-1, 2, k)), sol[sol.shape[0] // 2:,:].reshape((-1, 2, k))