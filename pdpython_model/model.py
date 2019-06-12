from mesa import Model
from mesa.space import SingleGrid
from mesa.time import BaseScheduler, RandomActivation, SimultaneousActivation
from pdpython_model.agents import PDAgent

from mesa.datacollection import DataCollector
import random
import time
import csv
import sys


class PDModel(Model):

    schedule_types = {"Sequential": BaseScheduler,
                     "Random": RandomActivation,
                     "Simultaneous": SimultaneousActivation}

    def __init__(self, height=8, width=8,
                 number_of_agents=2,
                 schedule_type="Simultaneous",
                 rounds=100,
                 collect_data=False,
                 agent_printing=False,
                 randspawn=False,
                 DD=1,
                 CC=1.5,
                 CD=-2,
                 DC=2,
                 simplified_payoffs=False,
                 b=0,
                 c=0,):

        # ---------- Model Parameters --------
        self.height = height
        self.width = width
        self.number_of_agents = number_of_agents
        self.step_count = 0
        self.DD = DD
        self.CC = CC
        self.CD = CD
        self.DC = DC
        self.b = b
        self.c = c
        self.simplified_payoffs = simplified_payoffs
        self.rounds = rounds
        self.randspawn = randspawn
        self.exp_n = 'vpp_simp_base_variance5'
        self.filename = ('%s model output.csv' % (self.exp_n), "a")
        self.schedule_type = schedule_type
        if not self.simplified_payoffs:
            self.payoffs = {("C", "C"): self.CC,
                            ("C", "D"): self.CD,
                            ("D", "C"): self.DC,
                            ("D", "D"): self.DD}
        elif self.simplified_payoffs:
            self.payoffs = {("C", "C"): self.b - abs(self.c),
                            ("C", "D"): - abs(self.c),
                            ("D", "C"): self.c,
                            ("D", "D"): 0}

        self.collect_data = collect_data
        self.agent_printing = agent_printing

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
            fieldnames = ['n agents', 'stepcount', 'steptime', 'cooperating', 'defecting', 'coop total', 'defect total',]
            # 'coop total utility', 'defect total utility'
            # I mean, it would nice to see utility per strategy if strategies were fixed

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if self.step_count == 1:
                writer.writeheader()
            writer.writerow({'n agents': self.number_of_agents, 'stepcount': self.step_count, 'steptime': steptime, 'cooperating': self.agents_cooperating, 'defecting': self.agents_defecting,
                             'coop total': self.number_of_coops, 'defect total': self.number_of_defects,
                             })
            # 'coop total utility': self.coops_utility, 'defect total utility': self.defects_utility

            # WE ALSO WANNA OUTPUT HOW MANY AGENTS THERE ARE, HOW MANY AGENTS IN EACH STRATEGY

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
        if not self.randspawn:
            for i in range(self.number_of_agents):
                """This is for adding agents in sequentially."""
                x, y = self.coordinates.pop(0)
                # print("x, y:", x, y)
                # x, y = self.grid.find_empty()
                pdagent = PDAgent((x, y), self, True)
                self.grid.place_agent(pdagent, (x, y))
                self.schedule.add(pdagent)

        elif self.randspawn:
            """ This is for adding in agents randomly """
            for i in range(self.number_of_agents):
                x, y = self.coordinates.pop(random.randrange(len(self.coordinates)))
                # print("x, y:", x, y)
                # x, y = self.grid.find_empty()
                pdagent = PDAgent((x, y), self, True)
                self.grid.place_agent(pdagent, (x, y))
                self.schedule.add(pdagent)

    def step(self):
        start = time.time()
        self.schedule.step()
        self.step_count += 1
        # print("Step:", self.step_count)
        end = time.time()
        steptime = end - start
        if self.collect_data:
            self.output_data(steptime)
        self.reset_values()

        if self.step_count >= self.rounds:
            sys.exit()

    def run_model(self, rounds=200):
        for i in range(self.rounds):
            self.step()

