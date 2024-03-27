import numpy as np
import random 
import math


def possion_traffic():

    packets = np.random.poisson(100)

    return packets


def gaussian_traffic():
    packets = int(np.random.normal(100,50))

    return packets

def beta_traffic():

    packets = np.random.beta()

    return int(packets)

def expotential_traffic():

    packets = np.random.exponential(100)

    return int(packets)



