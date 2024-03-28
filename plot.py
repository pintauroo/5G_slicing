import pandas as pd
import matplotlib.pyplot as plt

# Define the packet size ranges
packet_ranges = [(100, 1000), (1000, 5000), (5000, 10000)]

# List of paths to your CSV files
csv_files = [
    "/home/andrea/projects/5G_slicing/flows_1q.csv",
    "/home/andrea/projects/5G_slicing/flows_3q.csv",
    # "/home/andrea/projects/5G_slicing/flows_2q.csv"
    # Add more CSV file paths as needed
]

# Loop through each packet size range
for packet_range in packet_ranges:
    # Initialize the plot for the current range
    plt.figure(figsize=(8, 6))
    
    # Loop through each CSV file
    for csv_file in csv_files:
        # Load the CSV data
        data = pd.read_csv(csv_file)
        
        # Filter data for the current packet size range
        data_filtered = data[(data['Num_Packets'] > packet_range[0]) & (data['Num_Packets'] <= packet_range[1])]
        
        # Calculate the actual completion time as a difference between Completion_Time and Start_Time
        data_filtered['Actual_Completion_Time'] = data_filtered['Completion_Time'] - data_filtered['Start_Time']
        
        # Sort the DataFrame based on the Actual_Completion_Time
        data_filtered = data_filtered.sort_values(by="Actual_Completion_Time")
        
        # Calculate the CDF for the Actual_Completion_Time
        data_filtered["CDF"] = data_filtered["Actual_Completion_Time"].rank(method='average', pct=True)
        
        # Plot the CDF with a label for the legend
        plt.plot(data_filtered["Actual_Completion_Time"], data_filtered["CDF"], marker='o', linestyle='-', label=f"CDF of {csv_file.split('/')[-1]} in range {packet_range}")
    
    # Customize the plot
    plt.title(f'CDF of Actual Completion Time for Packet Size {packet_range}')
    plt.xlabel('Actual Completion Time')
    plt.ylabel('CDF')
    plt.grid(True)
    plt.legend()  # Show the legend to differentiate between CSV files
    
    # Save the plot to a file
    plt.savefig(f'flows_cdf_{packet_range[0]}_{packet_range[1]}.png')
