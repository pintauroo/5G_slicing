import csv
import random
import math
import numpy as np
import traffic

class Queue:
    def __init__(self, id):
        self.id = id
        self.packets = 0  # Total packets in the queue
        self.flows = []  # Flows assigned to this queue
        self.flows_packets = []  # List to store packets (by flow ID)
        self.buffer_size = 256
        
        

class Flow:
    def __init__(self, id: int, num_packets: int, start_time: int):
        self.id = id
        self.num_packets_tot = num_packets
        self.num_packets = num_packets
        self.start_time = start_time
        self.completion_time = None
        self.inflight = 0
        self.cwnd = 2
        self.dropped = 0
        self.flow_dropped = 0
    
    def ack(self, num_packets, time):
        self.num_packets -= num_packets
        self.num_packets += self.dropped
        self.inflight = 0

        if self.num_packets <= 0 and self.completion_time==None and self.inflight <=0:
            self.completion_time = time
            print(f'Flow {self.id} completed at time {time}')
            return True
        return False

    def send(self):
        if self.dropped == 0:
            self.cwnd += 10
        else:
            self.dropped = 0
            self.cwnd = max(2, int(self.cwnd/2))

        self.inflight = min(self.cwnd, self.num_packets)

        return self.inflight
    
    def drop_pkts(self, dropped):
        self.dropped = dropped
        self.flow_dropped += dropped

class BaseStation:
    def __init__(self, num_prbs: int, num_queues: int, scheduling: str):
        self.queues = [Queue(id) for id in range(num_queues)]  # Assume 3 queues
        self.time = 0
        #self.prb_data_capacity = prb_data_capacity
        self.total_num_prbs = num_prbs
        self.completed_flows = []
        self.prb_allocations = []
        self.buffer_size = []
        self.cqi = []
        self.prb_used = []
        self.time_stamp = []
        self.scheduling = scheduling
        self.packet_loss = 0
        self.dropped_packets = []

    def add_flow(self, flow: Flow, queue_index: int):
        self.queues[queue_index].flows.append(flow)

    def fill_queues(self):
        print('\n----FILL----')
        for queue in self.queues:
            self.time +=1
            for flow in queue.flows:

                if self.time >= flow.start_time and flow.num_packets > 0 and flow.completion_time is None:
                    added_packets = flow.send()
                    dropped = 0

                    if queue.packets + added_packets <= queue.buffer_size:

                    
                        queue.packets += added_packets

                        queue.flows_packets.extend([flow.id] *added_packets)

                        print(queue.flows_packets)
                    else:
                        dropped = (queue.packets + added_packets) - queue.buffer_size

                        self.packet_loss += dropped

                        self.dropped_packets.append(dropped)

                    

                        

                        queue.packets = queue.buffer_size

                        flow.drop_pkts(dropped)


                    #queue.flows_packets.extend([flow.id] * added_packets)
                    print(f'Flow {flow.id} added {added_packets} packets to Queue {queue.id}, dropped: {dropped}, flow packets: {flow.num_packets}')


    def bs_data_rate(self,cqi):
        slots_per_frame = 1600
        cqi_factors = [0.1523, 0.1523, 0.3770, 0.8770, 1.4766, 1.9141, 2.4063, 2.7305, 3.3223, 3.9023, 4.5234, 5.1152, 5.5547, 6.2266, 6.9141, 7.4063]
        Tbsize = 132 * cqi_factors[int(cqi)]
        Tbsize = math.floor(Tbsize)
        rate = int(Tbsize) * int(slots_per_frame)
        return int(rate / (1500 * 8) ) # packet/s



    def drain_sched_PF(self):
        print('-----DRAIN------ \n')
        
        self.prbs_allocations = self.slicing()  # Slicing

        packets_transmitted = [0] * len(self.queues)

        for i, queue in enumerate(self.queues):
            if queue.packets > 0:
                
                packets_to_tx = min(queue.packets, self.bs_data_rate(self.cqi[i]) * self.prbs_allocations[i])

                print('capacity: ',queue.packets,self.bs_data_rate(self.cqi[i]) * self.prbs_allocations[i])

                packets_transmitted[i] = packets_to_tx

                #print(queue.packets)

                flow_priorities = self.PF_scheduler_app_aware(queue, self.bs_data_rate(self.cqi[i]))
                #flow_priorities = self.PF_scheduler(queue, self.bs_data_rate(self.cqi[i]))


                
                for flow_id  in flow_priorities:
                    prb_ratio = self.prb_allocations[i] / self.total_num_prbs

                    print('prb_ratio: ',prb_ratio)

                    flow = next((f for f in queue.flows if f.id == flow_id), None)
                    if (flow and packets_to_tx > 0):
                        packets_from_flow = min(packets_to_tx, flow.num_packets)
                        #print(packets_to_tx, flow.num_packets, flow.inflight)
                        acked = flow.ack(packets_from_flow, self.time)
                        # packets_to_tx -= packets_from_flow
                        #queue.packets -= packets_from_flow

                        #add_buffer_bloat penalty
                        bb_penalty = int(queue.buffer_size * 0.1)
                        self.time += bb_penalty


            

                        if acked and flow not in self.completed_flows:
                            self.completed_flows.append(flow)

                        if packets_to_tx <= 0:
                            break
                
                queue.packets -= packets_transmitted[i]

                print(f'Queue {queue.id} drained {packets_transmitted[i]} packets, remaining packets: {queue.packets}')
            self.time += 1
    
    
    def drain_sched_RR(self):
        print('-----DRAIN------ \n')
        
        self.prbs_allocations = self.slicing()  # Example slicing function output

        packets_transmitted = [0] * len(self.queues)

        for i, queue in enumerate(self.queues):
            if queue.packets > 0:
                
                packets_to_tx = min(queue.packets, self.bs_data_rate(self.cqi[i]) * self.prbs_allocations[i])

                print(self.bs_data_rate(self.cqi[i]) * self.prbs_allocations[i])

                packets_transmitted[i] = packets_to_tx

                print(queue.packets)

                flow_priorities = self.RR_scehduler(queue)
                
                for flow_id, _ in flow_priorities:
                    

                    flow = next((f for f in queue.flows if f.id == flow_id), None)
                    if flow:
                        packets_from_flow = min(packets_to_tx, flow.num_packets)
                        acked = flow.ack(packets_from_flow, self.time)
                        #packets_to_tx -= packets_from_flow
                        #queue.packets -= packets_from_flow
                        bb_penalty = int(queue.buffer_size * 0.1)
                        self.time += bb_penalty


            

                        if acked and flow not in self.completed_flows:
                            self.completed_flows.append(flow)

                        if packets_to_tx <= 0:
                            break
                    self.time +=1
                queue.packets -= packets_transmitted[i]

                print(f'Queue {queue.id} drained {packets_transmitted[i]} packets, remaining packets: {queue.packets}, ')





    
    

    



    def PF_scheduler(self, queue, data_rate):       
        flow_priorities = []
        priority_metric = []
        for flow in queue.flows:
            if flow.num_packets > 0 and flow.inflight > 0:
                priority = flow.num_packets / data_rate
                priority_metric.append(priority)
                flow_priorities.append((flow.id, priority))
        sorted_flows = sorted(flow_priorities, key=lambda x: x[1], reverse=True)
        sorted_flows = [flow_id for flow_id, _ in sorted_flows]
        return sorted_flows
    
    def PF_scheduler_app_aware(self, queue, data_rate):       
        flow_priorities = []
        priority_metric = []
        for flow in queue.flows:
            if flow.num_packets > 0 and flow.inflight > 0:
                priority = flow.dropped / flow.num_packets
                priority_metric.append(priority)
                flow_priorities.append((flow.id, priority))
        sorted_flows = sorted(flow_priorities, key=lambda x: x[1], reverse=True)
        sorted_flows = [flow_id for flow_id, _ in sorted_flows]
        return sorted_flows

    def RR_scehduler(self, queue):
        flow_priorities = []
        for flow in queue.flows:
            if flow.num_packets > 0 and flow.inflight > 0 and flow.completion_time is None:
                flow_priorities.append((flow.id, flow.id))
        sorted_flows = sorted(flow_priorities, key=lambda x: x[1], reverse=False)
        print('sorted_flows :', sorted_flows)
        return sorted_flows
    
    def propotional_slicing(self, prbs_to_slice):
        total_packets = sum(queue.packets for queue in self.queues)
        # check how many packets each flow in that queue has left
        # cwnd
        prbs_allocation = [0] * len(self.queues)
        #print(prbs_allocation)
        if total_packets > 0:
            for i, queue in enumerate(self.queues):
                proportion = queue.packets / total_packets
                prbs_allocation[i] = int(proportion * prbs_to_slice)
                #print(prbs_allocation[i])
 
        return prbs_allocation
    

        
    def slicing(self):

        #self.prb_allocations = self.propotional_slicing(self.total_num_prbs)
        self.prb_allocations = [10, 20, 30]
        self.prb_used.append(self.prb_allocations)
        return self.prb_allocations

 

    def simulate_time_step(self):
        self.cqi = [random.randint(1,15) for _ in range(len(self.queues))]  # place holder for actual channel condition function
        #self.cqi = [15 for _ in range(len(self.queues))]  # place holder for actual channel condition function
        self.time += 1
        self.fill_queues()
        #drain the queue accordin to different sched algorithm
        if self.scheduling == 'RR':
            self.drain_sched_RR()
        
        elif self.scheduling == 'PF':
            self.drain_sched_PF()
        
        print('total dropped packets :', self.packet_loss)
        print(self.dropped_packets)

    

    def simulate(self, num_steps: int):

        for _ in range(num_steps):
            print('-' * 20)
            print(f'Time Step: {self.time}')

            self.time_stamp.append(self.time)

            if len(self.completed_flows) == len(flows_list):
                break

            if self.time > num_steps:
                break

            self.simulate_time_step()

            completion_times = [(flow.id, flow.start_time, flow.completion_time, flow.dropped) for flow in self.completed_flows]
            #print('completed:', completion_times)
            

           

        return completion_times

    def write_prb_allocations_to_csv(self, filename):
        with open(filename, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            time_step = self.time_stamp
            csvwriter.writerow(['Time Step'] + [f'Queue {i} PRBs' for i in range(len(self.queues))])
            for i in range(len(self.prb_used)):
                csvwriter.writerow([i] + self.prb_used[i])
               

# Set up the simulation parameters
execution_time = 10000
flows_number = 10

num_queues =3 

scheduling = "PF"
scheduling = "RR"
base_station = BaseStation(num_prbs=50, num_queues=num_queues, scheduling= scheduling)

# Generate random flows and associate them with queues

#random_flows = [Flow(id=i, num_packets=1500, start_time=random.randint(0, 10)) for i in range(flows_number)]

#random_flows = [Flow(id=i, num_packets=1500, start_time=0) for i in range(flows_number)]

##########################################################################################################################
'''
flow id 
'''


flows_list = [Flow(id=0, num_packets= 10000, start_time=0 ),
               Flow(id=1, num_packets=9000, start_time=0 ),
               Flow(id=2, num_packets=8000, start_time=0 ),
               Flow(id=3, num_packets=4000, start_time=0 ),
               Flow(id=4, num_packets=2500, start_time=0 ),
               Flow(id=5, num_packets=2500, start_time=0 ),
               Flow(id=6, num_packets=1500, start_time=0 ),
               Flow(id=7, num_packets=800, start_time=0 ),
               Flow(id=8, num_packets=700, start_time=0 ),
               Flow(id=9, num_packets=500, start_time=0 ),
               ]

#flows_list = [Flow(id=0, num_packets=2500, start_time=0)]




# def generate_flows(num_flows: int, min_packets=10, max_packets=100, lambda_inv=100):
#     flows_list = []
#     current_time = 0  # Initialize current time

#     for flow_id in range(num_flows):
#         # Use a more complex function for num_packets to ensure variability and non-linearity
#         num_packets = int(min_packets + (math.sin(flow_id) + math.sin(flow_id**2 / 30)) * (max_packets - min_packets) / 2)

#         # Ensure num_packets does not exceed max_packets
#         num_packets = max(min(num_packets, max_packets), min_packets)

#         # Simulate deterministic "Poissonian-like" arrival times with added variability
#         interval = lambda_inv + math.sin(flow_id) * lambda_inv / 2
#         current_time += interval

#         flow = Flow(id=flow_id, num_packets=num_packets, start_time=int(current_time))
#         flows_list.append(flow)

#     return flows_list


# flows_list = generate_flows(num_flows=flows_number, min_packets=1000, max_packets=10000, lambda_inv=100)

for i, flow in enumerate(flows_list):
    #base_station.add_flow(flow, i)

    if num_queues == 1:
        base_station.add_flow(flow, 0)

    else:
        if flow.num_packets<1000:
            base_station.add_flow(flow, 0)

        elif flow.num_packets<5000 and flow.num_packets>1000:
            base_station.add_flow(flow, 1)

        else:
            base_station.add_flow(flow, 2)

    queue_index = i % len(base_station.queues)
    print('flow:'+str(i), 'on queue:'+str(queue_index))
    base_station.add_flow(flow, queue_index)

# Run the simulation
completion_times = base_station.simulate(execution_time)

# After simulation, write PRB allocations to CSV
csv_filename = 'prb_allocations.csv'
base_station.write_prb_allocations_to_csv(csv_filename)

# print("Flow completion times:", completion_times)


# Write the flows to a CSV file
csv_filename = scheduling + "_flows_"+str(num_queues)+"q.csv"
with open(csv_filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["ID", "Num_Packets", "Num_Packets_Left", "Start_Time", "Completion_Time", "Inflight", "Dropped"])
    for flow in flows_list:
        writer.writerow([flow.id, flow.num_packets_tot, flow.num_packets, flow.start_time, flow.completion_time, flow.inflight, flow.flow_dropped])

