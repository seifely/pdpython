from mesa import Model
from mesa.time import BaseScheduler, RandomActivation, SimultaneousActivation
from mesa.space import SingleGrid # doesn't need to be multigrid as agent's aren't moving atop one another
from mesa.datacollection import DataCollector


class PDGrid(Model):

    nagents = 2
    payoffs = {}
    schedule_types = {"Sequential": BaseScheduler,
                      "Random": RandomActivation,
                      "Simultaneous": SimultaneousActivation}
    spatiality = False
    if not spatiality:
        height = nagents + 5
        width = nagents + 5
    elif spatiality:
        height = nagents
        width = nagents

    def __init__(self,
                 nagents,
                 height ,
                 width,
                 payoffs,
                 schedule_type="Sequential"):

        return
