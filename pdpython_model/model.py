from mesa import Model
from mesa.space import SingleGrid
from mesa.time import BaseScheduler, RandomActivation, SimultaneousActivation
from pdpython_model.agents import PDAgent

from mesa.datacollection import DataCollector
import time
import csv


class PDModel(Model):

    schedule_types = {"Sequential": BaseScheduler,
                     "Random": RandomActivation,
                     "Simultaneous": SimultaneousActivation}

    def __init__(self, height=8, width=8,
                 number_of_agents=2,
                 schedule_type="Simultaneous",
                 rounds=1,):


        # Model Parameters
        self.height = height
        self.width = width
        self.number_of_agents = number_of_agents
        self.step_count = 0
        self.exp_n = 'trial zero'
        self.filename = ('%s model output.csv' % (self.exp_n), "a")
        self.schedule_type = schedule_type
        self.payoffs = {("C", "C"): 3,
                        ("C", "D"): 0,
                        ("D", "C"): 5,
                        ("D", "D"): 2}


        # Model Functions
        self.schedule = self.schedule_types[self.schedule_type](self)
        self.grid = SingleGrid(self.height, self.width, torus=True)

        # Find list of empty cells
        self.coordinates = [(x, y) for x in range(self.width) for y in range(self.height)]

        self.agentIDs = list(range(1, (number_of_agents + 1)))

        self.datacollector = DataCollector({
            "Cooperating_Agents":
                lambda m: len([a for a in m.schedule.agents if a.common_move == "C"])
        })
        self.cooperating_agents = lambda m: len([a for a in m.schedule.agents if a.common_move == "C"])

        # ----- Storage -----
        self.agents_cooperating = 0
        self.agents_defecting = 0
        self.number_of_defects = 0
        self.number_of_coops = 0
        self.coops_utility = 0
        self.defects_utility = 0

        self.make_agents()
        self.running = True
        self.datacollector.collect(self)

    def output_data(self, steptime):
        with open('{}.csv'.format(self.filename), 'a', newline='') as csvfile:
            fieldnames = ['stepcount', 'steptime', 'cooperating', 'defecting', 'coop total', 'defect total', 'coop total utility',
                          'defect total utility']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if self.step_count == 0 or 1:
                writer.writeheader()
                writer.writerow({'stepcount': self.step_count, 'steptime': steptime, 'cooperating': self.agents_cooperating, 'defecting': self.agents_defecting,
                             'coop total': self.number_of_coops, 'defect total': self.number_of_defects,
                             'coop total utility': self.coops_utility, 'defect total utility': self.defects_utility})
            else:
                writer.writerow({'stepcount': self.step_count, 'steptime': steptime, 'cooperating': self.agents_cooperating,
                                 'defecting': self.agents_defecting,
                                 'coop total': self.number_of_coops, 'defect total': self.number_of_defects,
                                 'coop total utility': self.coops_utility,
                                 'defect total utility': self.defects_utility})


        # take in how many agents are cooperating, how many are defecting, and how many are 'equal'
        # how many co-operations and defections occurred this round TOTAL
        # make sure to reset these values to zero at the end of each step - AFTER WE OUTPUT THE DATA TO FILE

    def reset_values(self):
        self.agents_defecting = 0
        self.agents_cooperating = 0
        self.number_of_defects = 0
        self.number_of_coops = 0
        # don't want to reset the total of utility because - CRUCIALLY - utility will never decrease, it will only +0
        # at minimum

    def make_agents(self):
        for i in range(self.number_of_agents):
            x, y = self.coordinates.pop(0)
            # print("x, y:", x, y)
            # x, y = self.grid.find_empty()
            pdagent = PDAgent((x, y), self, True)
            self.grid.place_agent(pdagent, (x, y))
            self.schedule.add(pdagent)

    def step(self):
        start = time.time()
        self.schedule.step()
        self.step_count += 1
        print("Step:", self.step_count)
        end = time.time()
        steptime = end - start
        self.output_data(steptime)
        self.reset_values()

    def run_model(self, rounds=200):
        for i in range(rounds):
            self.step()

