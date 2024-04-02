
import matplotlib.pyplot as plt
import pandas as pd


fontsize = 15
# Packet loss percentages for each configuration and specific flows
pf = [6.48, 11.16, 1.00]
rr = [5.26, 7.40, 0.506]
opt = [4.12, 3.82, 0.05]  # Correcting a typo in the original data for readability

# Labels for the configurations
configurations = ['PF', 'RR', 'Optimal']

# Flow IDs for labeling
flows = ['Flow 1', 'Flow 4', 'Flow 9']



# Creating a DataFrame for easier plotting
df_losses = pd.DataFrame({'PF': pf, 'RR': rr, 'Optimal': opt}, index=flows)

# Plotting
ax = df_losses.plot(kind='bar', figsize=(20, 10), width=0.8, color=['skyblue', 'lightgreen', 'salmon'], edgecolor='black')

# Customizing the plot
plt.title('Packet Loss Percentage by Configuration',
fontsize = 25)
plt.ylabel('Packet Loss Percentage (%)' , 
fontsize = 25)
plt.xlabel('Flow ID',
fontsize = 25)
plt.xticks(rotation=45,
fontsize = 25)

plt.yticks(
fontsize = 25)
plt.legend(title='Configuration',
fontsize = 25)

# Adding patterns to the bars for distinguishability
bars = ax.patches
patterns = ['/', '\\', '+']  # Different patterns for each configuration
for bar, pattern in zip(bars, patterns * len(flows)):
    bar.set_hatch(pattern)
plt.savefig('pkt_loss.png',dpi=900)
plt.show()
