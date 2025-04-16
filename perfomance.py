import matplotlib.pyplot as plt
import numpy as np


# Data for the Intent Recognition Accuracy
categories_accuracy = ['Intent Recognition Accuracy (%)']
values_accuracy = [88]

# Set up the figure and axis for intent recognition accuracy
fig, ax = plt.subplots(figsize=(6, 6))

# Create the bar chart for intent recognition accuracy
bars = ax.bar(categories_accuracy, values_accuracy, color=['lightgreen'])

# Add value labels on top of the bar
for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, yval + 1, round(yval, 2), ha='center', va='bottom', fontsize=10)

# Set chart title and labels
ax.set_title('Healthcare Chatbot Intent Recognition Accuracy', fontsize=16, fontweight='bold')
ax.set_ylabel('Accuracy (%)', fontsize=12)

# Adjust y-axis to make space for labels
plt.ylim(0, max(values_accuracy) + 10)

# Display the graph for intent recognition accuracy
plt.tight_layout()
plt.show()
