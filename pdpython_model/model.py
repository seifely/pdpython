from mesa import Model
from mesa.space import SingleGrid
from mesa.time import BaseScheduler, RandomActivation, SimultaneousActivation
from pdpython_model.agents import PDAgent

from mesa.datacollection import DataCollector
import random
import time
import csv
import numpy as np
import sys
import os.path
import pickle


def get_num_coop_agents(model):
    """ return number of cooperations"""

    agent_cooperations = [a.number_of_c for a in model.schedule.agents]
    # print("hey", agent_cooperations)
    agent_cooperations = np.sum(agent_cooperations)
    # print("agent cooperations:", agent_cooperations.item())
    return agent_cooperations.item()

def get_num_defect_agents(model):
    """ return number of defections"""

    agent_defections = [a.number_of_d for a in model.schedule.agents]
    # print("hey", agent_defections)
    agent_defections = np.sum(agent_defections)
    # print("agent defections:", agent_defections.item())
    return agent_defections.item()

def get_cooperators(model):
    C_count = 0

    agent_behav_types = [a.common_move for a in model.schedule.agents]
    for i in agent_behav_types:
        current_agent = i

        if current_agent == ['C']:
            C_count += 1

    return C_count


def get_defectors(model):
    D_count = 0

    agent_behav_types = [a.common_move for a in model.schedule.agents]
    for i in agent_behav_types:
        current_agent = i

        if current_agent == ['D']:
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
    #     print("tft scored", sum(agent_scores))
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
    #     print("tft cooped", sum(agent_coops))
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
    #     print("vpp scored", sum(agent_scores))
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
    #     print("vpp cooped", sum(agent_coops))
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
    #     print("wsls scored", sum(agent_scores))
    return sum(agent_scores)

def get_iwsls_performance(model):
    """ For acquiring the sum total performance of a strategy"""

    # get the list of agent
    strategy = [a.strategy for a in model.schedule.agents]
    # get the list of agent performances
    scores = [a.score for a in model.schedule.agents]
    # for each in that list, when strategy = x y z, sum their number to a value
    agent_scores = []
    for i in strategy:
            if i == "iWSLS":
                indices = strategy.index(i)
                agent = scores[indices]
                agent_scores.append(agent)

    # if sum(agent_scores) != 0:
    #     print("iwsls scored", sum(agent_scores))
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
    #     print("wsls cooped", sum(agent_coops))
    return sum(agent_coops)

def get_iwsls_cooperations(model):
    """ For acquiring the sum total cooperations of a strategy"""

    # get the list of agent
    strategy = [a.strategy for a in model.schedule.agents]
    # get the list of agent performances
    coops = [a.number_of_c for a in model.schedule.agents]
    # for each in that list, when strategy = x y z, sum their number to a value
    agent_coops = []
    for i in strategy:
            if i == "iWSLS":
                indices = strategy.index(i)
                agent = coops[indices]
                agent_coops.append(agent)

    # if sum(agent_coops) != 0:
    #     print("iwsls cooped", sum(agent_coops))
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

    def __init__(self, height=11, width=11,
                 number_of_agents=47,
                 schedule_type="Simultaneous",
                 rounds=250,
                 collect_data=True,
                 #score_vis=False,
                 agent_printing=False,
                 randspawn=True,
                 experimental_spawn=True,
                 test_scenario = True,
                 kNN_training=False,
                 DD=1,
                 CC=1.5,
                 CD=-2,
                 DC=2,
                 simplified_payoffs=False,
                 b=0,
                 c=0,
                 learning_rate=1,
                 gamma=0.015,
                 init_ppD=0.5,
                 k=5
                 ):

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
        self.experimental_spawn = experimental_spawn
        self.test_scenario = test_scenario
        self.rounds = rounds
        self.randspawn = randspawn
        self.iteration_n = 0
        self.new_filenumber = 0
        self.kNN_training = kNN_training
        self.kNN_accuracy = 0
        self.k = k

        self.experimental_strategies = {1: "DEVIL", 3: "DEVIL", 5: "DEVIL", 6: "DEVIL", 16: "DEVIL", 18: "DEVIL",
                                        20: "DEVIL", 29: "DEVIL", 31: "DEVIL", 33: "DEVIL", 34: "DEVIL", 44: "DEVIL",
                                        46: "DEVIL", 2: "ANGEL", 4: "ANGEL", 14: "ANGEL", 15: "ANGEL", 17: "ANGEL",
                                        19: "ANGEL", 28: "ANGEL", 30: "ANGEL", 32: "ANGEL", 42: "ANGEL", 43: "ANGEL",
                                        45: "ANGEL", 47: "ANGEL", 8: "VPP", 11: "VPP", 23: "VPP", 26: "VPP", 35: "VPP",
                                        38: "VPP", 41: "VPP", 7: "WSLS", 10: "WSLS", 13: "WSLS", 22: "WSLS", 25: "WSLS",
                                        37: "WSLS", 40: "WSLS", 9: "TFT", 12: "TFT", 21: "TFT", 24: "TFT", 27: "TFT",
                                        36: "TFT", 39: "TFT"}

        self.experimental_strategies_test = {2:"DEVIL", 4: "DEVIL", 14: "DEVIL", 15: "DEVIL", 17:"DEVIL", 19: "DEVIL",
                                             28: "DEVIL", 30: "DEVIL", 32: "DEVIL", 42: "DEVIL", 43: "DEVIL", 45: "DEVIL",
                                             47: "DEVIL", 1: "ANGEL", 3: "ANGEL", 5: "ANGEL", 6: "ANGEL", 16: "ANGEL",
                                             18: "ANGEL", 20: "ANGEL", 29: "ANGEL", 31: "ANGEL", 33: "ANGEL", 34: "ANGEL",
                                             44: "ANGEL", 46: "ANGEL", 7: "TFT", 10: "TFT", 13: "TFT", 23: "TFT", 26: "TFT",
                                             36: "TFT", 39: "TFT", 8: "VPP", 11: "VPP", 21: "VPP", 24: "VPP", 27: "VPP",
                                             37: "VPP", 40: "VPP", 9: "WSLS", 12: "WSLS", 12: "WSLS", 22: "WSLS", 25: "WSLS",
                                             35: "WSLS", 38: "WSLS", 41: "WSLS"}

        with open('filename_number.csv', 'r') as f:
            reader = csv.reader(f)  # pass the file to our csv reader
            rows = []
            for row in reader:
                rows.append(row)

            filenumber = rows[0]
            filenumber = filenumber[0]
            # filenumber = filenumber[3:]
            filenumber = int(filenumber)
            self.iteration_n = filenumber
            self.new_filenumber = [filenumber + 1]

        with open('filename_number.csv', 'w') as f:
            # Overwrite the old file with the modified rows
            writer = csv.writer(f)
            writer.writerow(self.new_filenumber)

        # self.iteration_n needs to be pulled from a csv file and then deleted from said csv file
        concatenator = ('scale2_wsls_8x8_no_25_%s' % (self.iteration_n), "a")
        self.exp_n = concatenator[0]

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
        self.experimental_coordinates = [(3,8), (4,8), (5,8), (6,8), (7,8), (1,7), (2,7), (3,7), (4,7), (5,7), (6,7),
                                         (7,7), (8,7), (9,7), (3,6), (4,6), (5,6), (6,6), (7,6), (1,5), (2,5), (3,5),
                                         (4,5), (5,5), (6,5), (7,5), (8,5), (9,5), (3,4), (4,4), (5,4), (6,4), (7,4),
                                         (1,3), (2,3), (3,3), (4,3), (5,3), (6,3), (7,3), (8,3), (9,3), (3,2), (4,2),
                                         (5,2), (6,2), (7,2)]

        self.agentIDs = list(range(1, (number_of_agents + 1)))

        # ----- Storage -----
        self.agents_cooperating = 0
        self.agents_defecting = 0
        self.number_of_defects = 0
        self.number_of_coops = 0
        self.coops_utility = 0
        self.defects_utility = 0
        self.highest_score = 0

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
            "iWSLS Performance": get_iwsls_performance,
            "iWSLS Cooperations": get_iwsls_cooperations,
            "Model Params": track_params,
            },
            agent_reporters={
                 "Cooperations": lambda x: x.number_of_c,
                 "Defections": lambda x: x.number_of_d
                })

        self.memory_states = self.get_memory_states(['C', 'D'])
        self.state_values = self.state_evaluation(self.memory_states)
        self.agent_ppds = {}
        self.set_ppds()
        self.agent_ppds = pickle.load(open("agent_ppds.p", "rb"))
        self.training_data = []
        self.training_data = pickle.load(open("training_data_5.p", "rb"))
        if not experimental_spawn:
            self.make_agents()
        elif experimental_spawn:
            self.make_set_agents()
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

        with open('{}_kNN.csv'.format(self.filename), 'a', newline='') as csvfile:
            fieldnames = ['k', 'accuracy',]

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            kNN_accuracy_percent = ((self.kNN_accuracy / 24) * 100)

            if self.step_count == 1:
                writer.writeheader()
            writer.writerow({'k': self.k, 'accuracy': kNN_accuracy_percent,
                             })

            self.kNN_accuracy = 0  # Hopefully resetting this value here is fine

        # with open('{} agent strategies.csv'.format(self.filename), 'a', newline='') as csvfile:
        #     fieldnames = ['stepcount', 'agent_strategy']
        #
        #     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        #
        #     if self.step_count == 1:
        #         writer.writeheader()
        #     writer.writerow({'stepcount': self.step_count, 'agent_strategy': self.agent_list})

    def get_memory_states(self, behaviours):
        """ Get a list of all possible states given n behaviour options and
            r spaces in the agent's memory - CURRENTLY: 7  """
        options = behaviours
        permutations = []
        for i1 in options:
            for i2 in options:
                for i3 in options:
                    for i4 in options:
                        for i5 in options:
                            for i6 in options:
                                for i7 in options:
                                    permutations.append([i1, i2, i3, i4, i5, i6, i7])

        # to generate the < step 7 states
        initial_state1 = [0, 0, 0, 0, 0, 0]
        initial_state2 = [0, 0, 0, 0, 0]
        initial_state3 = [0, 0, 0, 0]
        initial_state4 = [0, 0, 0]
        initial_state5 = [0, 0]
        initial_state6 = [0]

        for ii1 in options:
            new = initial_state1 + [ii1]
            permutations.append(new)
        for ii2 in options:
            for iii2 in options:
                new = initial_state2 + [ii2] + [iii2]
                permutations.append(new)
        for ii3 in options:
            for iii3 in options:
                for iiii3 in options:
                    new = initial_state3 + [ii3] + [iii3] + [iiii3]
                    permutations.append(new)
        for ii4 in options:
            for iii4 in options:
                for iiii4 in options:
                    for iiiii4 in options:
                        new = initial_state4 + [ii4] + [iii4] + [iiii4] + [iiiii4]
                        permutations.append(new)
        for ii5 in options:
            for iii5 in options:
                for iiii5 in options:
                    for iiiii5 in options:
                        for iiiiii5 in options:
                            new = initial_state5 + [ii5] + [iii5] + [iiii5] + [iiiii5] + [iiiiii5]
                            permutations.append(new)
        for ii6 in options:
            for iii6 in options:
                for iiii6 in options:
                    for iiiii6 in options:
                        for iiiiii6 in options:
                            for iiiiiii6 in options:
                                new = initial_state6 + [ii6] + [iii6] + [iiii6] + [iiiii6] + [iiiiii6] + [iiiiiii6]
                                permutations.append(new)
        return permutations

    def set_ppds(self):
        """ Function to set ppds based on the value specified as init_ppD """
        initialised = {}
        n_of_a = 0
        if self.experimental_spawn:
            n_of_a = 47
        else:
            n_of_a = 64

        for i in range(n_of_a):
            # print("n of a", i)
            initialised[i + 1] = [self.init_ppD, self.init_ppD, self.init_ppD, self.init_ppD]
            with open("agent_ppds.p", "wb") as f:
                pickle.dump(initialised, f)

            """ This is used for setting ppD to a model-specified value. For agents
                to alter their own ppDs for, they must use the kNN system and 
                extract from a pickle file [INCOMPLETE] the classification of partner
                etc. from the previous game."""

    def state_evaluation(self, state_list):
        # if self.stepCount == 1:
        """ Below: need to remove this part of the function as it will reset ppds to be whatever the br_params specifies,
                    when actually we want it to start at 0.5 and then go unaltered by this method for the subsequent games"""
        # self.set_ppds()

        state_value = []
        for i in state_list:
            current_value = 0

            if i == ['C', 'D', 'C', 'D', 'C', 'D', 'C']:
                current_value = 21
            elif i == ['D', 'C', 'D', 'C', 'D', 'C', 'D']:
                current_value = -21

            else:
                for j in range(len(i)):
                    item = i[j]
                    # print("Array", i, "Index", j, "Item", item)
                    if item == 'C':
                        current_value = current_value + (1 * j)  # Slight bias towards cooperation
                    if item == 'D':
                        current_value = current_value - (1 * j)
                    if item == 0:
                        current_value = current_value

            state_value.append(current_value)
        return state_value

    def get_highest_score(self):
        scores = [a.score for a in self.schedule.agents]
        self.highest_score = max(scores)

    def reset_values(self):
        # self.agents_defecting = 0
        # self.agents_cooperating = 0
        # self.number_of_defects = 0
        self.number_of_NULL = 0  # should be coops

    def training_data_collector(self):
        if self.kNN_training:
            if not os.path.isfile('training_data.p'):
                training_data = []
                with open("training_data.p", "wb") as f:
                    pickle.dump(training_data, f)

            agent_training_data = [a.training_data for a in self.schedule.agents]
            training_data = []

            for i in agent_training_data:
                # print("agent has:", i)
                if len(i) is not 0:
                    for j in range(len(i)):
                        jj = i[j]
                        # print("data to append", jj)
                        training_data.append(jj)

            # print("save data", save_data)
            with open("training_data.p", "rb") as f:
                training_update = pickle.load(f)

            print("Training Data Size Pre-Update:", len(training_update))
            for i in training_data:
                training_update.append(i)
            print("Training Data Size Post-Update:", len(training_update))
            # print(training_update)
            with open("training_data.p", "wb") as f:
                pickle.dump(training_update, f)
        else:
            return

    def make_agents(self):

        # generate current experiment ppD pickle if one does not exist?
        # if not os.path.isfile('agent_ppds.p'):
        #     initialised = {}
        #     for i in range(self.number_of_agents):
        #         initialised[i+1] = [self.init_ppD, self.init_ppD, self.init_ppD, self.init_ppD]
        #         pickle.dump(initialised, open("agent_ppds.p", "wb"))

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

    def update_agent_ppds(self, ppds):
        with open("agent_ppds.p", "wb") as f:
            pickle.dump(ppds, f)

    def make_set_agents(self):
        # generate current experiment ppD pickle if one does not exist?
        # if not os.path.isfile('agent_ppds.p'):
        #     initialised = {}
        #     for i in range(self.number_of_agents):
        #         initialised[i + 1] = [self.init_ppD, self.init_ppD, self.init_ppD, self.init_ppD]
        #         pickle.dump(initialised, open("agent_ppds.p", "wb"))

        for i in range(47):
            """This is for adding agents in sequentially."""
            # x, y = self.experimental_coordinates.pop(0)
            # print(i)
            x, y = self.experimental_coordinates[i]
            # print("x, y:", x, y)
            # x, y = self.grid.find_empty()
            pdagent = PDAgent((x, y), self, True)
            self.grid.place_agent(pdagent, (x, y))
            self.schedule.add(pdagent)

    def step(self):
        start = time.time()
        self.schedule.step()
        if self.step_count == self.rounds - 1:
            self.update_agent_ppds(self.agent_ppds)
            self.training_data_collector()
        self.step_count += 1
        # print("Step:", self.step_count)
        end = time.time()
        steptime = end - start
        if self.collect_data:
            self.output_data(steptime)
        self.datacollector.collect(self)
        self.get_highest_score()
        self.reset_values()

        # if self.step_count >= self.rounds:
            # sys.exit()  # Do we need it to kill itself?

    def run_model(self, rounds=250):
        for i in range(self.rounds):
            self.step()
