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
        self.buffer_size = 20
        

class Flow:
    def __init__(self, id: int, num_packets: int, start_time: int):
        self.id = id
        self.num_packets = num_packets
        self.start_time = start_time
        self.completion_time = None
        self.inflight = 0
    
    def ack(self, num_packets, time):
        self.num_packets -= num_packets
        self.inflight = 0
    
        if self.num_packets <= 0 and self.completion_time==None:
            self.completion_time = time
            print(f'Flow {self.id} completed at time {time}')
            return True
        return False

    def send(self):
        self.inflight = min(self.inflight + random.randint(1, 20), self.num_packets)
        print('sending: ', self.inflight)
        return self.inflight
    
    def drop_pkts(self, inflight):
        self.inflight = inflight

class BaseStation:
    def __init__(self, num_prbs: int):
        self.queues = [Queue(id) for id in range(3)]  # Assume 3 queues
        self.time = 0
        #self.prb_data_capacity = prb_data_capacity
        self.total_num_prbs = num_prbs
        self.completed_flows = []
        self.prb_allocations = []
        self.buffer_size = []
        self.cqi = []
        self.prb_used = []
        self.time_stamp = []

    def add_flow(self, flow: Flow, queue_index: int):
        self.queues[queue_index].flows.append(flow)

    def fill_queues(self):
        print('\n----FILL----')
        for queue in self.queues:
            for flow in queue.flows:
                if self.time >= flow.start_time and flow.num_packets > 0 and flow.completion_time is None:
                    added_packets = flow.send()
                    queue.packets += added_packets
                    #queue.flows_packets.extend([flow.id] * added_packets)
                    print(f'Flow {flow.id} added {added_packets} packets to Queue {queue.id}')

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

                flow_priorities = self.PF_scheduler(queue, self.bs_data_rate(self.cqi[i]))


                
                for flow_id, _ in flow_priorities:
                    prb_ratio = self.prb_allocations[i] * int(_)

                    print('prb_ratio: ',prb_ratio)

                    flow = next((f for f in queue.flows if f.id == flow_id), None)
                    if (flow and packets_to_tx > 0):
                        packets_from_flow = min(packets_to_tx, flow.num_packets)
                        #print(packets_to_tx, flow.num_packets, flow.inflight)
                        acked = flow.ack(packets_from_flow, self.time)
                        # packets_to_tx -= packets_from_flow
                        #queue.packets -= packets_from_flow


            

                        if acked and flow not in self.completed_flows:
                            self.completed_flows.append(flow)

                        if packets_to_tx <= 0:
                            break
                
                queue.packets -= packets_transmitted[i]

                print(f'Queue {queue.id} drained {packets_transmitted[i]} packets, remaining packets: {queue.packets}')
    
    
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
                    prb_ratio = 1

                    flow = next((f for f in queue.flows if f.id == flow_id), None)
                    if flow:
                        packets_from_flow = min(packets_to_tx, flow.num_packets)
                        acked = flow.ack(packets_from_flow, self.time)
                        #packets_to_tx -= packets_from_flow
                        #queue.packets -= packets_from_flow


            

                        if acked and flow not in self.completed_flows:
                            self.completed_flows.append(flow)

                        if packets_to_tx <= 0:
                            break
                    # self.time +=1
                queue.packets -= packets_transmitted[i]

                print(f'Queue {queue.id} drained {packets_transmitted[i]} packets, remaining packets: {queue.packets}')





    def drain_sched_max_throughput(self):

        self.prb_allocations = self.slicing(self.total_num_prbs)

        q_index = np.argmin(self.cqi)

        queue = self.queues[q_index]

        if queue.packets > 0:

            packets_to_tx = min(queue.packets, self.bs_data_rate(self.cqi[i]) * self.prbs_allocations[i])
    

    



    def PF_scheduler(self, queue, data_rate):       
        flow_priorities = []
        priority_metric = []
        for flow in queue.flows:
            if flow.num_packets > 0 and flow.inflight > 0:
                priority = flow.num_packets / data_rate
                priority_metric.append(priority)
                flow_priorities.append((flow.id, priority))
        sorted_flows = sorted(flow_priorities, key=lambda x: x[1], reverse=True)
        return sorted_flows

    def RR_scehduler(self, queue):
        flow_priorities = []
        for flow in queue.flows:
            if flow.num_packets > 0 and flow.inflight > 0:
                flow_priorities.append((flow.id, flow.id))
        sorted_flows = sorted(flow_priorities, key=lambda x: x[1], reverse=True)
        print('sorted_flows :', sorted_flows)
        return sorted_flows
    
    def propotional_slicing(self, prbs_to_slice):
        total_packets = sum(queue.packets for queue in self.queues)
        prbs_allocation = [0] * len(self.queues)
        #print(prbs_allocation)
        if total_packets > 0:
            for i, queue in enumerate(self.queues):
                proportion = queue.packets / total_packets
                prbs_allocation[i] = int(proportion * prbs_to_slice)
                #print(prbs_allocation[i])
 
        return prbs_allocation
    

    def dynamic_slicing(self, prbs_to_slice):

        total_packets = sum(queue.packets for queue in self.queues)
        
        prbs_allocation = [0] * len(self.queues)

        if total_packets > 0:
            for i, queue in enumerate(self.queues):
                proportion = queue.packets / total_packets
                cqi = self.cqi[i]

                normalized_cqi = (15 - cqi) / 14

                #75% priority to BUFFER  and 25% to cqi
                prbs_allocation[i] = int(0.75 * proportion * prbs_to_slice +  0.25 * prbs_to_slice * normalized_cqi)
        
        return prbs_allocation

        
    def slicing(self):
        #place holder for slicing algorithm       
        self.prb_allocations = self.propotional_slicing(self.total_num_prbs)
        self.prb_used.append(self.prb_allocations)
        return self.prb_allocations

 

    def simulate_time_step(self):
        self.cqi = [random.randint(1,5) for _ in range(3)]  # place holder for actual channel condition function
        self.time += 1
        self.fill_queues()
        #drain the queue accordin to different sched algorithm
        self.drain_sched_PF()
        #$self.drain_sched_RR()

    

    def simulate(self, num_steps: int):

        for _ in range(num_steps):
            print('-' * 20)
            print(f'Time Step: {self.time}')

            self.time_stamp.append(self.time)

            if len(self.completed_flows) == len(flow_list):
                break

            if self.time > num_steps:
                break

            self.simulate_time_step()

            completion_times = [(flow.id, flow.start_time, flow.completion_time) for flow in self.completed_flows]
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
execution_time = 100000
flows_number = 10
base_station = BaseStation(num_prbs=50)

# Generate random flows and associate them with queues

#random_flows = [Flow(id=i, num_packets=1500, start_time=random.randint(0, 10)) for i in range(flows_number)]

#random_flows = [Flow(id=i, num_packets=1500, start_time=0) for i in range(flows_number)]

##########################################################################################################################
'''
flow id 


'''


flow_list = [Flow(id=0, num_packets=2500, start_time=0 ),
               Flow(id=1, num_packets=2500, start_time=0 ),
               Flow(id=2, num_packets=250000, start_time=0 ),
               Flow(id=3, num_packets=10000, start_time=0 ),
               Flow(id=4, num_packets=250000, start_time=0 ),
               Flow(id=5, num_packets=150000, start_time=0 ),
               Flow(id=6, num_packets=50000, start_time=0 ),
               Flow(id=7, num_packets=50000, start_time=0 ),
               Flow(id=8, num_packets=10000, start_time=0 ),
               Flow(id=9, num_packets=15000, start_time=0 ),
               ]



#random_flows = [Flow(id=i, num_packets=np.random.poisson(100000), start_time=random.randint(0, 10)) for i in range(flows_number)]


for i, flow in enumerate(flow_list):
    queue_index = i % len(base_station.queues)
    print('flow:'+str(i), 'on queue:'+str(queue_index))
    base_station.add_flow(flow, queue_index)

# Run the simulation
completion_times = base_station.simulate(execution_time)

# After simulation, write PRB allocations to CSV
csv_filename = 'prb_allocations.csv'
base_station.write_prb_allocations_to_csv(csv_filename)

print("Flow completion times:", completion_times)
