
from scipy.stats import norm
import numpy as np

data_start = 0
data_end = 15
data_points = 32
data = np.linspace(data_start, data_end, data_points)
mean = np.mean(data)
std = np.std(data)
t = [norm.pdf(i, loc=mean, scale=std) for i in range(0,16) ]

def calculate_normal(day):
    return t[day]
