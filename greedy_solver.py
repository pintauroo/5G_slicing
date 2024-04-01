from scipy import stats 

class Configuration:
    def __init__(self, prb_allocation, average_completion_time):
        self.prb_allocation = prb_allocation
        self.average_completion_time = average_completion_time

def greedy_algorithm(configurations):
    sorted_configurations = sorted(configurations, key=lambda x: x.average_completion_time)
    
    optimal_solution = sorted_configurations[0] 
    

    for config in sorted_configurations[1:]:
        if config.average_completion_time < optimal_solution.average_completion_time:
            optimal_solution = config
    
    return optimal_solution

# Example usage
configurations = [
    Configuration(prb_allocation=[10,20,20], average_completion_time=1413),
    Configuration(prb_allocation=[30,15,5], average_completion_time=1427),
    Configuration(prb_allocation=[10,20,30], average_completion_time=1668),
    Configuration(prb_allocation=[30,19,1], average_completion_time=1541),
    Configuration(prb_allocation=[15,15,20], average_completion_time=1456),
    Configuration(prb_allocation=[5,40,5], average_completion_time=1422),
    Configuration(prb_allocation=[5,5,45], average_completion_time=1450)
]

# Find the optimal solution using greedy algorithm
optimal_solution = greedy_algorithm(configurations)

# Output the optimal solution
print("Optimal Configuration - PRB Allocation:", optimal_solution.prb_allocation, "Average Completion Time:", optimal_solution.average_completion_time)




# fct= [1413
# ,1427
# ,1668
# ,1541
# ,1456
# ,1422
# ,1450]

# pkt_loss = [2876, 3466, 3630, 2675, 4890, 3043, 3155, 3960]


# pkt_loss_zscore = stats.zscore(pkt_loss)
# fct_zscore = stats.zscore(fct)

# utility=[]

# for i in fct_zscore:
#     utility[i] = (0.8 * fct_zscore[i] ) + (0.2 * pkt_loss_zscore[i])

# print(utility)

