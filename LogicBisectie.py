import sympy as sp
import numpy as np
import pandas as pd
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from sympy import sympify, symbols
from sympy import lambdify

def transforma_functie(f_str):
    try:
     x= symbols('x')
     temp=sympify(f_str)
     f= lambdify(x,temp,'numpy')
     return f
    except Exception:
     return None
        

















'''p=transforma_functie("x**2")
print(p(10))'''