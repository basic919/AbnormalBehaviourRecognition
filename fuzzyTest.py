# https://nbviewer.jupyter.org/github/WeatherGod/scipy2013_talks/blob/master/talks/joshua_warner/scikit-fuzzy_demo.ipynb

import numpy as np
import skfuzzy as fuzz
import matplotlib.pyplot as plt


# Generate universe functions
temp = np.arange(30, 101, 1)
customers = np.arange(0, 36, 1)


# Membership functions for heat
t_hot = fuzz.trimf(temp, [65, 100, 100])
t_moderate = fuzz.trimf(temp, [30, 65, 100])
t_cool = fuzz.trapmf(temp, [20, 20, 30, 65])

# Membership functions for customers
c_crowded = fuzz.trimf(customers, [24, 35, 35])
c_busy = fuzz.trimf(customers, [0, 24, 35])
c_quiet = fuzz.trimf(customers, [0, 0, 24])


# Visualize membership functions for temperature
fig, ax = plt.subplots()

ax.plot(temp, t_hot, 'r', temp, t_moderate, 'm', temp, t_cool, 'b')
ax.set_ylabel('Fuzzy membership')
ax.set_xlabel('Temp (Fahrenheit)')
ax.set_ylim(-0.05, 1.05)
fig.show()

# Visualize membership functions for customers
fig, ax = plt.subplots()

ax.plot(customers, c_quiet, 'c', customers, c_busy, 'm', customers, c_crowded, 'ForestGreen')
ax.set_ylabel('Fuzzy membership')
ax.set_xlabel('Number of Customers')
ax.set_ylim(-0.05, 1.05)
fig.show()


# Fuzzy relation
R1 = fuzz.relation_product(t_hot, c_crowded)
R2 = fuzz.relation_product(t_moderate, c_busy)
R3 = fuzz.relation_product(t_cool, c_quiet)

# Combine fuzzy relations into aggregate relation
R_combined = np.fmax(R1, np.fmax(R2, R3))

# Visualize
plt.imshow(R_combined)
cbar = plt.colorbar()
cbar.set_label('Fuzzy membership')
plt.yticks([i * 10 for i in range(8)], [str(i * 10 + 30) for i in range(8)])
plt.ylabel('Temp')
plt.xlabel('Customers')
plt.show()


# Note R_combined is zero-indexed, but the universe variable temp starts at 30... not zero.
print(fuzz.defuzz(customers, R_combined[temp == 75], 'centroid'))


# Defuzzify to generate crisp solution
predicted_customers = np.zeros_like(temp)

for i in range(len(predicted_customers)):
    predicted_customers[i] = fuzz.defuzz(customers, R_combined[i, :], 'centroid')
print(predicted_customers)


# Number of customers on our hypothetical 75 degree day
plt.plot(temp, predicted_customers, 'k')
plt.vlines(75, 5, predicted_customers[temp == 75], color='DarkOrange', linestyle='dashed', lw=2)
plt.hlines(predicted_customers[temp == 75], 30, 75, color='DarkOrange', linestyle='dashed', lw=2)
plt.xlabel('Temperature')
plt.ylabel('Customers')
plt.show()

# Number of customers on our real Texas day: 96 degrees
plt.plot(temp, predicted_customers, 'k')
plt.vlines(96, 5, predicted_customers[temp == 96], color='DarkOrange', linestyle='dashed', lw=2)
plt.hlines(predicted_customers[temp == 96], 30, 96, color='DarkOrange', linestyle='dashed', lw=2)
plt.xlabel('Temperature')
plt.ylabel('Customers')
plt.show()
