from mesa import Model
from mesa.space import SingleGrid
from mesa.time import BaseScheduler, RandomActivation, SimultaneousActivation
from pdpython_model.fixed_random_agents import PDAgent

from mesa.datacollection import DataCollector
from mesa.batchrunner import BatchRunner
import random
import time
import csv
import numpy as np
import pandas as pd
import statistics
import sys
import os
import pickle
import copy
from pdpython_model import statemaker
from pdpython_model import statemaker_moody

from pdpython_model import random_network_functions as rnf
import matplotlib.pyplot as plt
import networkx as nx


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


def get_learn_performance(model):
    """ For acquiring the sum total performance of a strategy"""

    # get the list of agent
    strategy = [a.strategy for a in model.schedule.agents]
    # get the list of agent performances
    scores = [a.score for a in model.schedule.agents]
    # for each in that list, when strategy = x y z, sum their number to a value
    agent_scores = []
    for i in strategy:
            if i == "LEARN":
                indices = strategy.index(i)
                agent = scores[indices]
                agent_scores.append(agent)

    # if sum(agent_scores) != 0:
        # print("vpp scored", sum(agent_scores))
    return sum(agent_scores)


def get_learn_mutC(model):
    """ For acquiring the sum total performance of a strategy"""

    # get the list of agent
    strategy = [a.strategy for a in model.schedule.agents]
    # get the list of agent performances
    mutc = [a.mutual_c_outcome for a in model.schedule.agents]
    # for each in that list, when strategy = x y z, sum their number to a value
    agent_mutc = []
    for i in strategy:
            if i == "LEARN":
                indices = strategy.index(i)
                agent = mutc[indices]
                agent_mutc.append(agent)

    # if sum(agent_scores) != 0:
        # print("vpp scored", sum(agent_scores))
    return sum(agent_mutc)


def get_learn_cooperations(model):
    """ For acquiring the sum total cooperations of a strategy"""

    # get the list of agent
    strategy = [a.strategy for a in model.schedule.agents]
    # get the list of agent performances
    coops = [a.number_of_c for a in model.schedule.agents]
    # for each in that list, when strategy = x y z, sum their number to a value
    agent_coops = []
    for i in strategy:
            if i == "LEARN":
                indices = strategy.index(i)
                agent = coops[indices]
                agent_coops.append(agent)

    # if sum(agent_coops) != 0:
        # print("vpp cooped", sum(agent_coops))
    return sum(agent_coops)


def get_moodylearn_performance(model):
    """ For acquiring the sum total performance of a strategy"""

    # get the list of agent
    strategy = [a.strategy for a in model.schedule.agents]
    # get the list of agent performances
    scores = [a.score for a in model.schedule.agents]
    # for each in that list, when strategy = x y z, sum their number to a value
    agent_scores = []
    for i in strategy:
            if i == "MOODYLEARN":
                indices = strategy.index(i)
                agent = scores[indices]
                agent_scores.append(agent)

    # if sum(agent_scores) != 0:
        # print("vpp scored", sum(agent_scores))
    return sum(agent_scores)


def get_moodylearn_mutC(model):
    """ For acquiring the sum total performance of a strategy"""

    # get the list of agent
    strategy = [a.strategy for a in model.schedule.agents]
    # get the list of agent performances
    mutc = [a.mutual_c_outcome for a in model.schedule.agents]
    # for each in that list, when strategy = x y z, sum their number to a value
    agent_mutc = []
    for i in strategy:
            if i == "MOODYLEARN":
                indices = strategy.index(i)
                agent = mutc[indices]
                agent_mutc.append(agent)

    # if sum(agent_scores) != 0:
        # print("vpp scored", sum(agent_scores))
    return sum(agent_mutc)


def get_moodylearn_cooperations(model):
    """ For acquiring the sum total cooperations of a strategy"""

    # get the list of agent
    strategy = [a.strategy for a in model.schedule.agents]
    # get the list of agent performances
    coops = [a.number_of_c for a in model.schedule.agents]
    # for each in that list, when strategy = x y z, sum their number to a value
    agent_coops = []
    for i in strategy:
            if i == "MOODYLEARN":
                indices = strategy.index(i)
                agent = coops[indices]
                agent_coops.append(agent)

    # if sum(agent_coops) != 0:
        # print("vpp cooped", sum(agent_coops))
    return sum(agent_coops)


def track_params(model):
    return (model.number_of_agents,
            model.theta,
            #model.learning_rate
            model.init_ppD,
            model.k,
            model.alpha,
            model.gamma,
            model.epsilon,
            model.msize,
            )

def get_average_payoffs(model):
    # get the average payoff of all agents
    average_payoffs = [a.globalAvPayoff for a in model.schedule.agents]
    # get the average payoff of each strategy
    # ???

    # return these thingies
    return statistics.mean(average_payoffs)

def calcInteractions(height):
    innSquare = ((height - 2) * (height - 2)) * 4
    outWalls = ((height - 2) * 3) * 4
    corners = 4 * 2
    return innSquare + outWalls + corners


class PDModel(Model):

    schedule_types = {"Sequential": BaseScheduler,
                     "Random": RandomActivation,
                     "Simultaneous": SimultaneousActivation}

    def __init__(self, height=5, width=5,    # even numbers are checkerboard fair
                 number_of_agents=25,
                 schedule_type="Simultaneous",
                 rounds=50,
                 collect_data=True,
                 agent_printing=False,
                 randspawn=False,

                 kNN_spawn=False,
                 kNN_training=False,
                 kNN_testing=False,
                 DD=1,
                 CC=1.5,
                 CD=-2,
                 DC=2,
                 simplified_payoffs=False,
                 b=0,
                 c=0,
                 batch_iterations=2,  # wait what is this doing again
                 learning_rate=1,
                 theta=0.015,
                 init_ppD = 0.5,
                 k=11,
                 msize=1,  # the n of obj in short memory, e.g. 2 =[('C', 'C')] or [('C', 'C'), ('C', 'D')] if paired
                 memoryPaired=False,  # set to True for states/memory items as paired outcomes, e.g. ('C', 'D')
                 learnFrom="them",  # options being 'me', 'them', 'us', for my own history, opponent history and paired
                 chosenOne=7,

                 sarsa_spawn=False,  # should mean checkerboard
                 sarsa_training=False,          #TODO: THESE VARIABLES HAVE BEEN TURNED OFF FOR MOODY SARSA TESTING
                 sarsa_testing=True,
                 sarsa_distro=0,
                 sarsa_oppo="LEARN",
                 epsilon=0.99,
                 alpha=0.1,
                 gamma=0.95,
                 export_q=True,
                 alpha_floor=0.01,
                 epsilon_floor=0.05,

                 moody_sarsa_spawn=True,  # should mean checkerboard
                 sensitive_agents=[],

                 moody_sarsa_training=True,
                 moody_sarsa_testing=True,
                 moody_sarsa_distro=0,
                 moody_sarsa_oppo="TFT",
                 moody_epsilon=0.9,
                 moody_alpha=0.1,
                 moody_gamma=0.95,
                 moody_export_q=True,
                 moody_alpha_floor=0.01,
                 moody_epsilon_floor=0.01,
                 moody_msize=20,  # the n of obj in short memory, e.g. 2 =[('C', 'C')] or [('C', 'C'), ('C', 'D')] if paired
                 moody_memoryPaired=False,  # set to True for states/memory items as paired outcomes, e.g. ('C', 'D')
                 moody_learnFrom="them",  # options being 'me', 'them', 'us', for my own history, opponent history and paired
                 moody_chosenOne=6,
                 moody_statemode='stateless',
                 moody_MA=1,
                 moody_opponents=True,
                 moody_startmood=50,
                 startingBehav='C',

                 sensitivity=0,
                 graph_probability=0.4,
                 changeFrequency=5,
                 ):

        # ---------- Model Parameters --------
        self.height = height
        self.width = width
        self.number_of_agents = number_of_agents
        self.agentIDs = list(range(1, (number_of_agents + 1)))
        self.step_count = 0
        self.DD = DD
        self.CC = CC
        self.CD = CD
        self.DC = DC
        self.b = b
        self.c = c
        self.batch_iterations = batch_iterations
        self.theta = theta
        self.init_ppD = init_ppD
        self.learning_rate = learning_rate
        self.simplified_payoffs = simplified_payoffs
        self.rounds = rounds
        self.randspawn = randspawn
        self.iteration_n = 0
        self.new_filenumber = 0
        self.kNN_spawn = kNN_spawn
        self.kNN_testing = kNN_testing
        self.kNN_training = kNN_training
        self.kNN_accuracy = 0
        self.k = k
        self.msize = msize
        self.memoryPaired = memoryPaired

        self.sarsa_spawn = sarsa_spawn
        self.sarsa_training = sarsa_training
        self.sarsa_testing = sarsa_testing
        self.sarsa_distro = sarsa_distro
        self.sarsa_oppo = sarsa_oppo
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.export_q = export_q
        self.learnFrom = learnFrom
        self.chosenOne = chosenOne
        self.alpha_floor = alpha_floor
        self.epsilon_floor = epsilon_floor

        self.moody_msize = moody_msize
        self.moody_memoryPaired = moody_memoryPaired

        self.moody_sarsa_spawn = moody_sarsa_spawn
        self.moody_sarsa_training = moody_sarsa_training
        self.moody_sarsa_testing = moody_sarsa_testing
        self.moody_sarsa_distro = moody_sarsa_distro
        self.moody_sarsa_oppo = moody_sarsa_oppo
        self.moody_alpha = moody_alpha
        self.moody_gamma = moody_gamma
        self.moody_epsilon = moody_epsilon
        self.moody_export_q = moody_export_q
        self.moody_learnFrom = moody_learnFrom
        self.moody_chosenOne = moody_chosenOne
        self.moody_alpha_floor = moody_alpha_floor
        self.moody_epsilon_floor = moody_epsilon_floor
        self.moody_statemode = moody_statemode
        self.moody_MA = moody_MA
        self.moody_opponents = moody_opponents
        self.moody_startmood = moody_startmood

        self.sensitivity = sensitivity
        self.sensitive_agents = sensitive_agents
        self.coop_index = (self.CC - self.DD) / (self.DC - self.CD)

        self.startingBehav = startingBehav

        # ========================== RANDOM GRAPH VARIABLES =============================

        self.initial_graphG = 0
        self.initial_graphD = {}
        self.updated_graphD = {}
        self.updated_graphG = 0
        self.end_graphG = 0
        self.end_graphD = {}
        self.graph_additions = []
        self.graph_removals = []

        self.agent_positions = {}
        self.agent_strategies = {}
        self.graph_probability = graph_probability
        self.graph_connectedness = []
        self.max_edges = 0
        self.groupDegreeCentralities = {}
        # if len(self.groupDegreeCentralities) == 0:  # Initialise the centralities in case any agent doesn't get partners initially
        for j in self.agentIDs:
            self.groupDegreeCentralities[j] = 0
        self.group_degree_centralization = 0
        self.change_frequency = changeFrequency

        self.checkTurn = False
        self.resetTurn = False

        # TODO: Add opponents to the oppoList for if opponent 'MIXED' is used
        self.oppoList = [
                         "TFT",
                         "LEARN",
                         "MOODYLEARN",
                          "ANGEL",
                         "DEVIL",
                         "VPP",
                         "RANDOM",
                         "WSLS",
                         # "iWSLS",
                         ]

        if self.kNN_training:
            self.kNN_strategies = {1: "DEVIL", 3: "DEVIL", 5: "DEVIL", 6: "DEVIL", 16: "DEVIL", 18: "DEVIL",
                                            20: "DEVIL", 29: "DEVIL", 31: "DEVIL", 33: "DEVIL", 34: "DEVIL", 44: "DEVIL",
                                            46: "DEVIL", 2: "ANGEL", 4: "ANGEL", 14: "ANGEL", 15: "ANGEL", 17: "ANGEL",
                                            19: "ANGEL", 28: "ANGEL", 30: "ANGEL", 32: "ANGEL", 42: "ANGEL", 43: "ANGEL",
                                            45: "ANGEL", 47: "ANGEL", 8: "VPP", 11: "VPP", 23: "VPP", 26: "VPP", 35: "VPP",
                                            38: "VPP", 41: "VPP", 7: "WSLS", 10: "WSLS", 13: "WSLS", 22: "WSLS", 25: "WSLS",
                                            37: "WSLS", 40: "WSLS", 9: "TFT", 12: "TFT", 21: "TFT", 24: "TFT", 27: "TFT",
                                            36: "TFT", 39: "TFT"}
        elif self.kNN_testing:
            self.kNN_strategies = {2: "DEVIL", 4: "DEVIL", 14: "DEVIL", 15: "DEVIL", 17: "DEVIL", 19: "DEVIL",
                                             28: "DEVIL", 30: "DEVIL", 32: "DEVIL", 42: "DEVIL", 43: "DEVIL",
                                             45: "DEVIL",
                                             47: "DEVIL", 1: "ANGEL", 3: "ANGEL", 5: "ANGEL", 6: "ANGEL", 16: "ANGEL",
                                             18: "ANGEL", 20: "ANGEL", 29: "ANGEL", 31: "ANGEL", 33: "ANGEL",
                                             34: "ANGEL",
                                             44: "ANGEL", 46: "ANGEL", 7: "TFT", 10: "TFT", 13: "TFT", 23: "TFT",
                                             26: "TFT",
                                             36: "TFT", 39: "TFT", 8: "VPP", 11: "VPP", 21: "VPP", 24: "VPP", 27: "VPP",
                                             37: "VPP", 40: "VPP", 9: "WSLS", 12: "WSLS", 22: "WSLS",
                                             25: "WSLS",
                                             35: "WSLS", 38: "WSLS", 41: "WSLS"}

        # self.experimental_defectors = [42, 64, 86, 19, 51, 73, 17, 38, 60, 82, 15, 47, 69]
        # self.experimental_coordinators = [53, 75, 107, 40, 62, 84, 49, 71, 105, 103, 36, 58, 80]
        # self.experimental_vpp = [41, 74, 50, 83, 26, 59, 92]
        # self.experimental_wsls = [30, 63, 96, 39, 72, 48, 81]
        # self.experimental_tft = [52, 85, 28, 61, 94, 37, 70]

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
        if self.sarsa_spawn:
            concatenator = ('wave3_neutralpayoff_%s_%s_%s_sarsa_no_%s' % (self.msize, self.learnFrom, self.sarsa_oppo, self.iteration_n), "a")
        elif self.moody_sarsa_spawn:
            if type(self.moody_sarsa_oppo) == list:
                concatenator = ('csvfix_mood%s_DC_%s_%sx%s_mA_%s_%s_%s_msarsa_no_%s' % (
                self.moody_startmood, self.DC, self.width, self.width, self.moody_MA,
                self.moody_statemode, "mixedOppo", self.iteration_n), "a")
            else:
                concatenator = ('swaptest_%s-%s-%s-%s_round%s_mood%s_graphprob%s_%sx%s_mA_%s_%s_%s_msarsa_no_%s' % (self.DC, self.CC, self.DD, self.CD, self.change_frequency, self.moody_startmood, self.graph_probability, self.width, self.width, self.moody_MA,
                                                                                          self.moody_statemode, self.moody_sarsa_oppo, self.iteration_n), "a")
        else:
            concatenator = ('xxx_nosarsa_no_%s' % (self.iteration_n), "a")
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
        self.experimental_coordinates = [(3, 8), (4, 8), (5, 8), (6, 8), (7, 8), (1, 7), (2, 7), (3, 7), (4, 7), (5, 7),
                                         (6, 7),
                                         (7, 7), (8, 7), (9, 7), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6), (1, 5), (2, 5),
                                         (3, 5),
                                         (4, 5), (5, 5), (6, 5), (7, 5), (8, 5), (9, 5), (3, 4), (4, 4), (5, 4), (6, 4),
                                         (7, 4),
                                         (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3), (9, 3), (3, 2),
                                         (4, 2),
                                         (5, 2), (6, 2), (7, 2)]



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
            "LEARN Performance": get_learn_performance,
            "MutualCooperations": get_learn_mutC,
            "LEARN Cooperations": get_learn_cooperations,
            "moodyLEARN Performance": get_moodylearn_performance,
            "moodyMutualCooperations": get_moodylearn_mutC,
            "moodyLEARN Cooperations": get_moodylearn_cooperations,
            "Model Params": track_params,
        },
            agent_reporters={
                "Cooperations": lambda x: x.number_of_c,
                "Defections": lambda x: x.number_of_d
            })

        self.memory_states = statemaker.get_memory_states([0, 'C', 'D'], self.msize, self.memoryPaired)
        self.moody_memory_states = statemaker_moody.get_memory_states([0, 'C', 'D'], self.moody_statemode, self.number_of_agents)
        self.state_values = self.state_evaluation(self.memory_states)
        self.moody_state_values = self.moody_state_evaluation(self.moody_memory_states)

        self.firstgame = self.first_game_check()
        self.agent_ppds = {}
        self.set_ppds()
        self.agent_ppds = pickle.load(open("agent_ppds.p", "rb"))
        self.training_data = []
        self.training_data = pickle.load(open("training_data_50.p", "rb"))  # //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        self.init_graph()
        self.updated_graphD = copy.deepcopy(self.initial_graphD)  # Put the first update as the initial graph

        if not kNN_spawn:
            self.make_agents()
        elif kNN_spawn:
            self.make_set_agents()



        self.running = True
        self.datacollector.collect(self)

    def first_game_check(self):
        try:
            success = pickle.load(open("firstgame.p", "rb"))
            # print("Val of Success was : ", success)
            if success == 1:
                return False
        except (OSError, IOError) as e:
            foo = 1
            pickle.dump(foo, open("firstgame.p", "wb"))
            return True

    def output_data(self, steptime):
        with open('{}.csv'.format(self.filename), 'a', newline='') as csvfile:
            fieldnames = ['n agents', 'stepcount', 'steptime', 'cooperating', 'defecting', 'coop total', 'defect total',]

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if self.step_count == 1:
                writer.writeheader()
            writer.writerow({'n agents': self.number_of_agents, 'stepcount': self.step_count, 'steptime': steptime, 'cooperating': self.agents_cooperating, 'defecting': self.agents_defecting,
                             'coop total': self.number_of_coops, 'defect total': self.number_of_defects,
                             })
        if self.kNN_testing:
            with open('{}_kNN.csv'.format(self.filename), 'a', newline='') as csvfile:
                fieldnames = ['k', 'accuracy', 'accuracy_p',]

                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                kNN_accuracy_percent = ((self.kNN_accuracy / 24) * 100)

                if self.step_count == 1:
                    writer.writeheader()
                writer.writerow({'k': self.k, 'accuracy': self.kNN_accuracy, 'accuracy_p': kNN_accuracy_percent,
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

    # def get_memory_states(self, behaviours):
    #     """ Get a list of all possible states given n behaviour options and
    #         r spaces in the agent's memory - Size: msize  """
    #     options = behaviours
    #     permutations = []
    #
    #     if self.msize == 7:
    #     for i1 in options:
    #         for i2 in options:
    #             for i3 in options:
    #                 for i4 in options:
    #                     for i5 in options:
    #                         for i6 in options:
    #                             for i7 in options:
    #                                 permutations.append([i1, i2, i3, i4, i5, i6, i7])
    #
    #     # to generate the < step 7 states
    #     permutations.append([0, 0, 0, 0, 0, 0, 0])
    #
    #     initial_state1 = [0, 0, 0, 0, 0, 0]
    #     initial_state2 = [0, 0, 0, 0, 0]
    #     initial_state3 = [0, 0, 0, 0]
    #     initial_state4 = [0, 0, 0]
    #     initial_state5 = [0, 0]
    #     initial_state6 = [0]
    #
    #     for ii1 in options:
    #         new = initial_state1 + [ii1]
    #         permutations.append(new)
    #     for ii2 in options:
    #         for iii2 in options:
    #             new = initial_state2 + [ii2] + [iii2]
    #             permutations.append(new)
    #     for ii3 in options:
    #         for iii3 in options:
    #             for iiii3 in options:
    #                 new = initial_state3 + [ii3] + [iii3] + [iiii3]
    #                 permutations.append(new)
    #     for ii4 in options:
    #         for iii4 in options:
    #             for iiii4 in options:
    #                 for iiiii4 in options:
    #                     new = initial_state4 + [ii4] + [iii4] + [iiii4] + [iiiii4]
    #                     permutations.append(new)
    #     for ii5 in options:
    #         for iii5 in options:
    #             for iiii5 in options:
    #                 for iiiii5 in options:
    #                     for iiiiii5 in options:
    #                         new = initial_state5 + [ii5] + [iii5] + [iiii5] + [iiiii5] + [iiiiii5]
    #                         permutations.append(new)
    #     for ii6 in options:
    #         for iii6 in options:
    #             for iiii6 in options:
    #                 for iiiii6 in options:
    #                     for iiiiii6 in options:
    #                         for iiiiiii6 in options:
    #                             new = initial_state6 + [ii6] + [iii6] + [iiii6] + [iiiii6] + [iiiiii6] + [iiiiiii6]
    #                             permutations.append(new)
    #     return permutations

    def init_graph(self):
        self.initial_graphD, self.initial_graphG = rnf.initRandomGraph(self.number_of_agents, self.graph_probability,
                                                                       self.agentIDs)
        print("I've made a graph!")
        plt.figure()
        nx.draw_networkx(self.initial_graphG, ax=None)
        plt.savefig(self.exp_n + "-initGraph.png")
        self.max_edges = rnf.maxEdgesPossible(self.number_of_agents, self.agentIDs)
        self.graph_connectedness = (nx.number_of_edges(self.initial_graphG)) / self.max_edges
        return

    def change_graph(self, additions, removals, old_graph):
        #Previous Graph Stata
        print("OLD Density:", nx.density(self.updated_graphG), " Nodes:", nx.number_of_nodes(self.updated_graphG), " Edges:", nx.number_of_edges(self.updated_graphG))

        updated_graph, updated_graphG = rnf.update_graph(self.updated_graphD, self.graph_additions, self.graph_removals,
                                                         True, self.agentIDs)
        # Reset the additions and removal request lists
        self.graph_additions = []
        self.graph_removals = []

        #New Graph Stats
        print("OLD Density:", nx.density(updated_graphG), " Nodes:", nx.number_of_nodes(updated_graphG), " Edges:", nx.number_of_edges(updated_graphG))
        return updated_graph, updated_graphG

    def set_ppds(self):
        """ Below: need to remove this part of the function as it will reset ppds to be whatever the br_params specifies,
                    when actually we want it to start at 0.5 and then go unaltered by this method for the subsequent games"""
        initialised = {}
        n_of_a = 0
        if self.kNN_spawn:
            n_of_a = 47
        else:
            n_of_a = self.number_of_agents

        if self.firstgame:
            for i in range(n_of_a):
                # print("n of a", i)
                # TODO: THIS IS A TEMPORARY FIX FOR THE PPD SITUATION, BASICALLY PPDS WERE INITIALLY SET FOR 4 PARTNERS FIXED - NOW THERE WILL BE ONE FOR ALL 25 PARTNERS - NOT SURE HOW TO HANDLE THIS IF PARTNERS CHANGE THO BUT THIS IS LEGACY CODE
                inits = []
                for n in range(n_of_a+1):
                    inits.append(self.init_ppD)
                print("inits", inits)
                initialised[i + 1] = inits
                with open("agent_ppds.p", "wb") as f:
                    pickle.dump(initialised, f)

                """ This is used for setting ppD to a model-specified value. For agents
                    to alter their own ppDs for, they must use the kNN system and 
                    extract from a pickle file [INCOMPLETE] the classification of partner
                    etc. from the previous game."""

    def state_evaluation(self, state_list):
        # if self.stepCount == 1:

        state_value = []
        if not self.memoryPaired:

            for i in state_list:
                current_value = 0
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

        elif self.memoryPaired:
            for i in state_list:
                counter = 0
                i = list(i)
                # print(i)
                current_value = 0
                for j in i:
                    # item = i[1]  # should hopefully index the opponent's move in each of the pairs
                    # TODO: I don't think state_evaluation currently affects anything but we will see
                    item = j
                    # print("Array", i, "Index", j, "Item", item)
                    if item == 'C':
                        current_value = current_value + (1 * counter)  # Should there be a slight bias towards C?
                    if item == 'D':
                        current_value = current_value - (1 * counter)
                    if item == 0:
                        current_value = current_value
                    counter += 1
                state_value.append(current_value)

        return state_value

    def moody_state_evaluation(self, state_list):
        # if self.stepCount == 1:

        state_value = []
        if not self.moody_memoryPaired:

            for i in state_list:
                current_value = 0
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

        elif self.moody_memoryPaired:
            for i in state_list:
                counter = 0
                i = list(i)
                # print(i)
                current_value = 0
                for j in i:
                    # item = i[1]  # should hopefully index the opponent's move in each of the pairs
                    # TODO: I don't think state_evaluation currently affects anything but we will see
                    item = j
                    # print("Array", i, "Index", j, "Item", item)
                    if item == 'C':
                        current_value = current_value + (1 * counter)  # Should there be a slight bias towards C?
                    if item == 'D':
                        current_value = current_value - (1 * counter)
                    if item == 0:
                        current_value = current_value
                    counter += 1
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
        with open("agent_ppds.p", "rb") as f:
            self.agent_ppds = pickle.load(f)

        if not self.randspawn:
            for i in range(self.number_of_agents):
                """This is for adding agents in sequentially."""
                # print(self.coordinates)
                x, y = self.coordinates.pop(0)
                # print("x, y:", x, y)
                # x, y = self.grid.find_empty()
                pdagent = PDAgent((x, y), self, True)
                self.grid.place_agent(pdagent, (x, y))
                self.agent_positions[i+1] = (x, y)  # Add in a storage of where each agent is, by ID no.
                self.schedule.add(pdagent)

        elif self.randspawn:
            """ This is for adding in agents randomly """
            for i in range(self.number_of_agents):
                x, y = self.coordinates.pop(random.randrange(len(self.coordinates)))
                # print("x, y:", x, y)
                # x, y = self.grid.find_empty()
                pdagent = PDAgent((x, y), self, True)
                self.grid.place_agent(pdagent, (x, y))
                self.agent_positions[i+1] = (x, y)  # Add in a storage of where each agent is, by ID no.
                self.schedule.add(pdagent)

    def export_q_tables(self, init):      # TODO: Does this need a moody counterpart? =============================
        qs = [a.qtable for a in self.schedule.agents]
        # we need to print/save a list of the keys
        # then print/save each
        # print('qs', qs)
        qvals = []
        for i in qs:
            if i is not []:
                # take each agent's qtable
                # print('i', i)
                for j in i:
                    # take each item in that table
                    temp_qs = []
                    # print('j', j)
                    item = i[j]
                    for k in item:
                        temp_qs.append(k)
                        # append all the qvalues into one big list
                    qvals.append(temp_qs)

        # print('qvals', qvals)
        if init:
            with open('{} qinit.csv'.format(self.filename), 'a', newline='') as csvfile:
                fieldnames = ['q']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow({'q': qvals})
        else:
            with open('{} qend.csv'.format(self.filename), 'a', newline='') as csvfile:
                fieldnames = ['q']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow({'q': qvals})

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

    #  ===== This was me trying to calculate GDC by myself, when in fact network x has a function for it
    def calculate_GDC(self, centralities, IDs, nAgents):
        # print("THE CENTRALITIES ARE", centralities, "and the connections are", self.updated_graphD)
        # print("centrals", centralities)
        highest = -1
        highest_id = 0
        if not IDs:
            IDs = list(range(1, (nAgents + 1)))

        # print("model centralities", centralities)
        for i in IDs:
            if centralities[i] > highest:
                # print(centralities[i], "is higher than", highest, "so I'll replace it")
                highest = centralities[i]
                highest_id = i
        # sum the observed differences between the highest and all the others
        summedDiff = 0
        othersList = copy.deepcopy(centralities)
        othersIDs = copy.deepcopy(IDs)
        # print("I'm gonna remove", highest_id, "from the lists")
        othersIDs.remove(highest_id)
        othersList.pop(highest_id)
        # othersList = othersList.remove(highest_id)
        for i in othersIDs:
            # print("highest is", highest, "other is ", othersList[i])
            # print("diff was", summedDiff)
            diff = (highest - othersList[i])
            # print("the difference was", diff)
            # print("diff is now", summedDiff + diff)
            summedDiff = summedDiff + diff
        denom = (nAgents - 1) * (nAgents - 2)
        # print("the denom is ", denom)
        return summedDiff / denom

    def roundCheck(self, n, frequency):
        if n > 1:
            if n % frequency == 0:
                return True
            else:
                return False
        else:
            return False

    def colorPicker(self, strategy):
        if strategy == 'RANDOM':
            return('gray')
        elif strategy == 'ANGEL':
            return ('yellow')
        elif strategy == 'DEVIL':
            return ('red')
        elif strategy == 'EV':
            return ('plum')
        elif strategy == 'VEV':
            return ('violet')
        elif strategy == 'TFT':
            return ('deepskyblue')
        elif strategy == 'VPP':
            return ('magenta')
        elif strategy == 'WSLS':
            return ('lime')
        elif strategy == "LEARN":
            return ('blue')
        elif strategy == "MOODYLEARN":
            return ('darkorange')

    def getColorMap(self, strategies, graph):
        color_map = []
        for node in graph:
            #if the node number is in strategies
            color = self.colorPicker(strategies[node])
            color_map.append(color)
        return color_map

    def step(self):

        start = time.time()
        self.checkTurn = self.roundCheck(self.step_count, self.change_frequency)
        self.schedule.step()
        if self.updated_graphG == 0:
            graph_connect = self.initial_graphG
        else:
            graph_connect = self.updated_graphG
        self.graph_connectedness = (nx.number_of_edges(graph_connect))/self.max_edges
        self.group_degree_centralization = self.calculate_GDC(self.groupDegreeCentralities, self.agentIDs, self.number_of_agents)

        # if self.step_count !=0:
        #     with open('latest_sim_output.csv', 'a') as ff:
        #         # Overwrite the old file with the modified rows
        #         writer = csv.writer(ff)
        #         writer.writerow(rnf.analysis(self.updated_graphD, self.updated_graphG))

        if self.step_count == self.rounds - 1:
            color_map = self.getColorMap(self.agent_strategies, self.updated_graphG)
            plt.figure()
            # print("gonna make an output graph")
            # print(rnf.analysis(self.updated_graphD, self.updated_graphG))
            nx.draw_networkx(self.updated_graphG, node_color=color_map)
            plt.savefig(self.exp_n + "-finalGraph.png")
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
        if self.checkTurn:
            self.resetTurn = True
        if not self.checkTurn:
            self.resetTurn = False

        # Update the graph using rnf and the agent's requests for changes
        # print("graph D", self.updated_graphD)
        # print("adds", self.graph_additions)
        # print("removes", self.graph_removals)
        self.updated_graphD, self.updated_graphG = rnf.update_graph(self.updated_graphD, self.graph_additions, self.graph_removals, True, list(range(1, (self.number_of_agents + 1))))
        # The reset those lists to empty
        self.graph_additions = []
        self.graph_removals = []

        # Update the Graph that Agents will Read From
        #self.updated_graphD, self.updated_graphG = self.change_graph(self.graph_additions, self.graph_removals,
         #                                                            self.updated_graphD)

        # if self.export_q:
        #     if self.step_count == 1:
        #         self.export_q_tables(True)
        #     export intitial q tables
        if self.step_count == self.rounds-1:
            if self.export_q:
                for j in self.memory_states:
                    for k in range(2):
                        with open('{} states_agent37.csv'.format(self.filename), 'a', newline='') as csvfile:
                            fieldnames = ['state']
                            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                            # writer.writeheader()
                            writer.writerow({'state': j})

            if self.moody_export_q:
                for j in self.moody_memory_states:
                    for k in range(2):
                        with open('{} states_agent36.csv'.format(self.filename), 'a', newline='') as csvfile:
                            fieldnames = ['state']
                            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                            # writer.writeheader()
                            writer.writerow({'state': j})


        # if self.step_count >= self.rounds:
            # sys.exit()  # Do we need it to kill itself?

    def run_model(self, rounds=50):
        for i in range(self.rounds):
            self.step()


# parameter lists for each parameter to be tested in batch run
br_params = {#"number_of_agents": [64],
             #"theta": [0.015, #0.01, 0.015, 0.02],
             #model.learning_rate
             #"init_ppD": [0.5],
             #"k": [35],
             #"alpha": [0.1],
             #"gamma": [0.95],
             #"epsilon": [0.99],
             #"sarsa_distro": [0.25, 0.50, 0.75],
             "DC": [5],
             "CC": [3],
             "DD": [1],
             "CD": [0],
             #"sarsa_oppo": [#"TFT", "ANGEL", "DEVIL", "LEARN", "VPP", "RANDOM", "WSLS", "iWSLS",
                            #"MOODYLEARN"],

             # "learnFrom": ["them"],
             # "memoryPaired": [False],
             #"msize": [1,4,7],

             "moody_alpha": [0.1],
             "moody_gamma": [0.95],
             "moody_epsilon": [0.1,
                               #0.5,
                               #0.9
                               ],
             "moody_sarsa_oppo": [#"TFT",
                                  "LEARN",
                                  #"MOODYLEARN",
                                #"ANGEL", "DEVIL", "VPP", "RANDOM", "WSLS", "iWSLS",
                                #'MIXED',
                                  ],
             "moody_statemode": [#'stateless',
                                 #'agentstate',
                                 'moodstate'
                                 ],
             "moody_startmood": [#1,
                                 #99,
                                 50,
                                 ],
             "moody_MA": [#0,
                          #0.001,
                          #0.1,
                          #0.2,
                          #0.4,
                          #0.6,
                          0.8,
                          #'v',
                          ],
             "moody_opponents": [True,
                                 #False
                                 ],
             "startingBehav": ['C',
                              #'D',
                              ],
             "changeFrequency": [5],
             #"sensitivity": [0],
             "sensitive_agents": [(0,), #(0, 13]),
                                  ],  # This will get clunky if we want to randomly distribute them every time, or if we want to include all agents
             }


""" For collecting training data for kNN, please run one init_ppD at a time.
    Otherwise, it doesn't export the ppD variable correctly to the pickle! """


br = BatchRunner(PDModel,
                 br_params,
                 iterations=1,
                 max_steps=50,  # This should be 10k, but have set it to 5k because it now takes ages to run
                 model_reporters={"Data Collector": lambda m: m.datacollector})

if __name__ == '__main__':
    br.run_all()
    br_df = br.get_model_vars_dataframe()
    br_step_data = pd.DataFrame()
    for i in range(len(br_df["Data Collector"])):
        if isinstance(br_df["Data Collector"][i], DataCollector):
            i_run_data = br_df["Data Collector"][i].get_model_vars_dataframe()
            br_step_data = br_step_data.append(i_run_data, ignore_index=True)
    br_step_data.to_csv("PDModel_Step_Data_%s.csv" % (str(random.randint(1,200000))))  # this might not be as useful for importing





