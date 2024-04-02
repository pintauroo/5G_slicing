

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
# Example completion time data for each flow (in milliseconds)
# flow_completion_times_optimal = [
#     [7239, 7712, 7510, 7451, 7234],
#     [8579, 8704, 8830, 8955, 9080],
#     [4513, 4638, 4763, 4888, 5013],
#     [4347, 4472, 4597, 4722, 4847],
#     [2108, 2233, 2358, 2483, 2608],
#     [4872, 4997, 5122, 5247, 5372],
#     [2073, 2198, 2323, 2448, 2573],
#     [855, 1105, 1355, 1605, 1855],
#     [4608, 4858, 5108, 5358, 5608],
#     [2454, 2704, 2954, 3204, 3454]
# ]


flow_completion_times_optimal_128 = [
    [6057, 6182, 6307, 6432, 6557],
    [6908, 7158, 7408, 7658, 7908],
    [3857, 4107, 4357, 4607, 4857],
    [3327, 3577, 3827, 4077, 4327],
    [1424, 1674, 1924, 2174, 2424],
    [2857, 3107, 3357, 3607, 3857],
    [1519, 1769, 2019, 2269, 2519],
    [914, 1164, 1414, 1664, 1914],
    [594, 844, 1094, 1344, 1594],
    [767, 1017, 1267, 1517, 1767]
    
]

# Example completion time data for each configuration and flow (in milliseconds)
pf_completion_times = [
    [6253, 6453, 6653, 7053, 7253],
    [7417, 6585, 6487, 7293, 6406],
    [7937, 7337, 7931, 7132, 7531],
    [4810, 3665, 5473, 4813, 4652],
    [3035, 2452, 3117, 2685, 3080],
    [4906, 4712, 4545, 4934, 4786],
    [3341, 2493, 2290, 3314, 2426],
    [2007, 2320, 597, 2025, 1915],
    [4408, 4707, 5789, 5075, 5660],
    [2439, 2244, 2542, 2048, 1980],

]

rr_completion_times = [
    [6926, 7809, 6789, 7540, 7457],
    [8353, 9066, 9737, 8085, 8447],
    [4377, 6009, 5135, 4194, 4859],
    [4705, 4712, 4747, 4130, 5154],
    [1191, 2542, 2224, 2443, 2605],
    [4769, 5886, 5367, 5043, 5560],
    [2463, 2687, 2764, 2353, 1511],
    [1903, 1398, 1932, 1632, 1921],
    [4861, 4711, 5109, 6238, 4671],
    [2429, 2920, 1996, 2691, 3632]
]


# Corrected approach for distinct visualization of each configuration within each flow

# Create a new figure
plt.figure(figsize=(20, 10))

# Setup positions and colors for each configuration
positions = range(1, 31)  # 10 flows * 3 configurations
box_colors = ['skyblue', 'lightgreen', 'salmon']
config_labels = ['Optimal', 'PF', 'RR']

# # Flatten the data lists to plot them in sequence
# data_flattened = [item for sublist in zip(flow_completion_times_optimal_128, pf_completion_times, rr_completion_times) for item in sublist]

# # Plot each set of data
# for i, (data, color) in enumerate(zip(data_flattened, box_colors * 10)):
#     plt.boxplot(data, positions=[positions[i]], widths=0.5, patch_artist=True, boxprops=dict(facecolor=color))

# # Customizing the plot
# plt.xticks([i * 3 + 1.5 for i in range(10)], [f'Flow {i+1}' for i in range(10)])
# plt.ylabel('Completion Time (ms)')
# plt.title('Comparison of Flow Completion Times Across Configurations')

# # Creating legend manually
# legend_patches = [Patch(facecolor=box_colors[i], label=config_labels[i]) for i in range(len(config_labels))]
# plt.legend(handles=legend_patches, loc='upper right')

# plt.grid(True, which='both', linestyle='--', linewidth=0.5)
# plt.show()

# Extracting specific flows for each configuration
selected_flows_optimal_128 = [flow_completion_times_optimal_128[i] for i in [0, 4, 9]]
selected_flows_pf = [pf_completion_times[i] for i in [0, 4, 9]]
selected_flows_rr = [rr_completion_times[i] for i in [0, 4, 9]]

# Flattening the selected lists for plotting
selected_data_flattened = [item for sublist in zip(selected_flows_optimal_128, selected_flows_pf, selected_flows_rr) for item in sublist]

# New positions for the selected flows
selected_positions = range(1, 10)  # 3 flows * 3 configurations


for i, (data, color) in enumerate(zip(selected_data_flattened, box_colors * 3)):
    plt.boxplot(data, positions=[selected_positions[i]], widths=0.6, patch_artist=True, boxprops=dict(facecolor=color))

# Adjusting plot labels and title for the selected flows
plt.xticks([i * 3 + 1.5 for i in [0, 1, 2]], ['Flow 1', 'Flow 5', 'Flow 10'],fontsize = 25)
plt.ylabel('Completion Time (ms)',fontsize = 15)
plt.title('Comparison of Flow Completion Times for Selected Flows Across Configurations',fontsize = 25)

# Adding the corrected legend
legend_patches_selected = [Patch(facecolor=box_colors[i], label=config_labels[i]) for i in range(len(config_labels))]
plt.legend(handles=legend_patches_selected, loc='upper right', fontsize = 25)

plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.savefig('box_plot', dpi=900)

plt.show()
