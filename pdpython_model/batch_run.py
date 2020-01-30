from mesa import Model
from mesa.space import SingleGrid
from mesa.time import BaseScheduler, RandomActivation, SimultaneousActivation
from pdpython_model.agents import PDAgent

from mesa.datacollection import DataCollector
from mesa.batchrunner import BatchRunner
import random
import time
import csv
import numpy as np
import pandas as pd
import sys


def get_num_coop_agents(model):
    """ return number of cooperations"""

    agent_cooperations = [a.number_of_c for a in model.schedule.agents]
    # print("hey", agent_cooperations)
    agent_cooperations = np.sum(agent_cooperations)
    # print("lol", agent_cooperations.item())
    return agent_cooperations.item()

def get_num_defect_agents(model):
    """ return number of defections"""

    agent_defections = [a.number_of_d for a in model.schedule.agents]
    # print("hey", agent_defections)
    agent_defections = np.sum(agent_defections)
    # print("lol", agent_defections.item())
    return agent_defections.item()

def get_cooperators(model):
    C_count = 0

    agent_behav_types = [a.common_move for a in model.schedule.agents]
    for i in agent_behav_types:
        current_agent = i

        if current_agent == "C":
            C_count += 1

    return C_count


def get_defectors(model):
    D_count = 0

    agent_behav_types = [a.common_move for a in model.schedule.agents]
    for i in agent_behav_types:
        current_agent = i

        if current_agent == "D":
            D_count += 1

    return D_count

def get_tft_performance(model):
    """ For acquiring the sum total performance of a strategy"""

    # get the list of agent
    strategy = [a.strategy for a in model.schedule.agents]
    # get the list of agent performances
    scores = [a.score for a in model.schedule.agents]
    # for each in that list, when strategy = x y z, sum their number to a value
    agent_scores = []
    for i in strategy:
            if i == "TFT":
                indices = strategy.index(i)
                agent = scores[indices]
                agent_scores.append(agent)

    # if sum(agent_scores) != 0:
        # print("tft scored", sum(agent_scores))
    return sum(agent_scores)

def get_tft_cooperations(model):
    """ For acquiring the sum total cooperations of a strategy"""

    # get the list of agent
    strategy = [a.strategy for a in model.schedule.agents]
    # get the list of agent performances
    coops = [a.number_of_c for a in model.schedule.agents]
    # for each in that list, when strategy = x y z, sum their number to a value
    agent_coops = []
    for i in strategy:
            if i == "TFT":
                indices = strategy.index(i)
                agent = coops[indices]
                agent_coops.append(agent)

    # if sum(agent_coops) != 0:
        # print("tft cooped", sum(agent_coops))
    return sum(agent_coops)

def get_vpp_performance(model):
    """ For acquiring the sum total performance of a strategy"""

    # get the list of agent
    strategy = [a.strategy for a in model.schedule.agents]
    # get the list of agent performances
    scores = [a.score for a in model.schedule.agents]
    # for each in that list, when strategy = x y z, sum their number to a value
    agent_scores = []
    for i in strategy:
            if i == "VPP":
                indices = strategy.index(i)
                agent = scores[indices]
                agent_scores.append(agent)

    # if sum(agent_scores) != 0:
        # print("vpp scored", sum(agent_scores))
    return sum(agent_scores)

def get_vpp_cooperations(model):
    """ For acquiring the sum total cooperations of a strategy"""

    # get the list of agent
    strategy = [a.strategy for a in model.schedule.agents]
    # get the list of agent performances
    coops = [a.number_of_c for a in model.schedule.agents]
    # for each in that list, when strategy = x y z, sum their number to a value
    agent_coops = []
    for i in strategy:
            if i == "VPP":
                indices = strategy.index(i)
                agent = coops[indices]
                agent_coops.append(agent)

    # if sum(agent_coops) != 0:
        # print("vpp cooped", sum(agent_coops))
    return sum(agent_coops)

def get_wsls_performance(model):
    """ For acquiring the sum total performance of a strategy"""

    # get the list of agent
    strategy = [a.strategy for a in model.schedule.agents]
    # get the list of agent performances
    scores = [a.score for a in model.schedule.agents]
    # for each in that list, when strategy = x y z, sum their number to a value
    agent_scores = []
    for i in strategy:
            if i == "WSLS":
                indices = strategy.index(i)
                agent = scores[indices]
                agent_scores.append(agent)

    # if sum(agent_scores) != 0:
        # print("wsls scored", sum(agent_scores))
    return sum(agent_scores)

def get_wsls_cooperations(model):
    """ For acquiring the sum total cooperations of a strategy"""

    # get the list of agent
    strategy = [a.strategy for a in model.schedule.agents]
    # get the list of agent performances
    coops = [a.number_of_c for a in model.schedule.agents]
    # for each in that list, when strategy = x y z, sum their number to a value
    agent_coops = []
    for i in strategy:
            if i == "WSLS":
                indices = strategy.index(i)
                agent = coops[indices]
                agent_coops.append(agent)

    # if sum(agent_coops) != 0:
        # print("wsls cooped", sum(agent_coops))
    return sum(agent_coops)

def track_params(model):
    return (model.number_of_agents,
            model.gamma,
            #model.learning_rate
            model.init_ppD,
            )


class PDModel(Model):

    schedule_types = {"Sequential": BaseScheduler,
                     "Random": RandomActivation,
                     "Simultaneous": SimultaneousActivation}

    def __init__(self, height=8, width=8,
                 number_of_agents=64,
                 schedule_type="Simultaneous",
                 rounds=250,
                 collect_data=True,
                 agent_printing=False,
                 randspawn=True,
                 DD=1,
                 CC=1.5,
                 CD=-2,
                 DC=2,
                 simplified_payoffs=False,
                 b=0,
                 c=0,
                 learning_rate = 1,
                 gamma = 0.015,
                 init_ppD = 0.1):

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
        self.gamma = gamma
        self.init_ppD = init_ppD
        self.learning_rate = learning_rate
        self.simplified_payoffs = simplified_payoffs
        self.rounds = rounds
        self.randspawn = randspawn
        self.exp_n = 'scale2_wsls_8x8_no_25'
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
        self.agent_list = []

        # Model Functions
        self.schedule = self.schedule_types[self.schedule_type](self)
        self.grid = SingleGrid(self.height, self.width, torus=True)

        # Find list of empty cells
        self.coordinates = [(x, y) for x in range(self.width) for y in range(self.height)]

        self.agentIDs = list(range(1, (number_of_agents + 1)))


        # ----- Storage -----
        self.agents_cooperating = 0
        self.agents_defecting = 0
        self.number_of_defects = 0
        self.number_of_coops = 0
        self.coops_utility = 0
        self.defects_utility = 0


        self.datacollector = DataCollector(model_reporters={
            "Cooperations": get_num_coop_agents,
            "Defections": get_num_defect_agents,
            "Cooperators": get_cooperators,
            "Defectors": get_defectors,
            "TFT Performance": get_tft_performance,
            "TFT Cooperations": get_tft_cooperations,
            "VPP Performance": get_vpp_performance,
            "VPP Cooperations": get_vpp_cooperations,
            "WSLS Performance": get_wsls_performance,
            "WSLS Cooperations": get_wsls_cooperations,
            "Model Params": track_params,
            },
            agent_reporters={
                 "Cooperations": lambda x: x.number_of_c,
                 "Defections": lambda x: x.number_of_d
                })

        self.make_agents()
        self.running = True
        self.datacollector.collect(self)



    def output_data(self, steptime):
        with open('{}.csv'.format(self.filename), 'a', newline='') as csvfile:
            fieldnames = ['n agents', 'stepcount', 'steptime', 'cooperating', 'defecting', 'coop total', 'defect total',]

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if self.step_count == 1:
                writer.writeheader()
            writer.writerow({'n agents': self.number_of_agents, 'stepcount': self.step_count, 'steptime': steptime, 'cooperating': self.agents_cooperating, 'defecting': self.agents_defecting,
                             'coop total': self.number_of_coops, 'defect total': self.number_of_defects,
                             })

        # with open('{} agent strategies.csv'.format(self.filename), 'a', newline='') as csvfile:
        #     fieldnames = ['stepcount', 'agent_strategy']
        #
        #     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        #
        #     if self.step_count == 1:
        #         writer.writeheader()
        #     writer.writerow({'stepcount': self.step_count, 'agent_strategy': self.agent_list})



    def reset_values(self):
        # self.agents_defecting = 0
        # self.agents_cooperating = 0
        # self.number_of_defects = 0
        self.number_of_NULL = 0  # should be coops

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
        self.datacollector.collect(self)
        self.reset_values()

        # if self.step_count >= self.rounds:
            # sys.exit()  # Do we need it to kill itself?

    def run_model(self, rounds=200):
        for i in range(self.rounds):
            self.step()


# parameter lists for each parameter to be tested in batch run
br_params = {"number_of_agents": [16,# 32, 64
                                  ],
            "gamma": [0.001, #0.01, 0.015, 0.02
                      ],
            #model.learning_rate
            "init_ppD": [0.1]}

br = BatchRunner(PDModel,
                 br_params,
                 iterations=1,
                 max_steps=250,
                 model_reporters={"Data Collector": lambda m: m.datacollector})

if __name__ == '__main__':
    br.run_all()
    br_df = br.get_model_vars_dataframe()
    br_step_data = pd.DataFrame()
    for i in range(len(br_df["Data Collector"])):
        if isinstance(br_df["Data Collector"][i], DataCollector):
            i_run_data = br_df["Data Collector"][i].get_model_vars_dataframe()
            br_step_data = br_step_data.append(i_run_data, ignore_index=True)
    br_step_data.to_csv("PDModel_Step_Data.csv")

