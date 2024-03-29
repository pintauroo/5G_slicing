import pandas as pd
import matplotlib.pyplot as plt

# Define the packet size ranges
# packet_ranges = [(100, 1000), (1000, 5000), (5000, 10000)]
packet_ranges = [(100, 10000)]

csv_files = [
    "/home/andrea/projects/5G_slicing/RR_flows_100q.csv",
    "/home/andrea/projects/5G_slicing/PF_flows_100q.csv"
]

# Loop through each packet size range
for packet_range in packet_ranges:
    plt.figure(figsize=(8, 6))
    
    for csv_file in csv_files:
        data = pd.read_csv(csv_file)
        
        data_filtered = data[(data['Num_Packets'] > packet_range[0]) & (data['Num_Packets'] <= packet_range[1])]
        
        # Calculate the actual completion time as a difference between Completion_Time and Start_Time
        data_filtered['Actual_Completion_Time'] = data_filtered['Completion_Time'] - data_filtered['Start_Time']
        
        data_filtered = data_filtered.sort_values(by="Actual_Completion_Time")
        
        data_filtered["CDF"] = data_filtered["Actual_Completion_Time"].rank(method='average', pct=True)
        
        plt.plot(data_filtered["Actual_Completion_Time"], data_filtered["CDF"], marker='o', linestyle='-', label=f"CDF of {csv_file.split('/')[-1]} in range {packet_range}")
    
    plt.title(f'CDF of Actual Completion Time for Packet Size {packet_range}')
    plt.xlabel('Actual Completion Time')
    plt.ylabel('CDF')
    plt.grid(True)
    plt.legend()
    
    plt.savefig(f'flows_cdf_{packet_range[0]}_{packet_range[1]}.png')
