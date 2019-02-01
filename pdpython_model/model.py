from mesa import Model
from mesa.space import SingleGrid
from mesa.time import BaseScheduler, RandomActivation, SimultaneousActivation
from pdpython_model.agents import PDAgent

from mesa.datacollection import DataCollector

class PDModel(Model):

    schedule_types = {"Sequential": BaseScheduler,
                     "Random": RandomActivation,
                     "Simultaneous": SimultaneousActivation}

    def __init__(self, height=5, width=5,
                 number_of_agents=2,
                 schedule_type="Simultaneous",
                 rounds=1,):


        # Model Parameters
        self.height = height
        self.width = width
        self.number_of_agents = number_of_agents
        self.step_count = 0
        self.schedule_type = schedule_type
        self.payoffs = {("C", "C"): 3,
                        ("C", "D"): 0,
                        ("D", "C"): 5,
                        ("D", "D"): 2}

        # Model Functions
        self.schedule = self.schedule_types[self.schedule_type](self)
        self.grid = SingleGrid(self.height, self.width, torus=True)

        self.make_agents()
        self.running = True

    def make_agents(self):
        for i in range(self.number_of_agents):
            x, y = self.grid.find_empty()
            pdagent = PDAgent((x, y), self, True)
            self.grid.place_agent(pdagent, (x, y))
            self.schedule.add(pdagent)

    def step(self):
        self.schedule.step()
        self.step_count += 1

    def run_model(self, rounds=200):
        for i in range(rounds):
            self.step()

