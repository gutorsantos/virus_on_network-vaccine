
from scipy.stats import norm
import numpy as np

data_start = 0
data_end = 15
data_points = 15
data = np.linspace(data_start, data_end, data_points)
  
mean = np.mean(data)
std = np.std(data)
  
probability_pdf = norm.pdf(7.5, loc=mean, scale=std)
print(probability_pdf)

# sum = 0
# for i in range(0, 16):
#     sum += norm.pdf(i, loc=mean, scale=std)

r = 1
i = 1
while(r > probability_pdf*0.2):
    i += 1
    r = np.random.random()
    print(i, '|', r, probability_pdf*0.9)

