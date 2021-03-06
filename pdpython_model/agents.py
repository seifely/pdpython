from mesa import Agent
import random
import csv
import numpy as np
import statistics
import pickle
from scipy.spatial import distance as dst
import copy
from pdpython_model import sarsa

"""Note on Strategies:
    RANDOM - Does what it says on the tin, each turn a random move is selected.
    EV - Expected Value. Has a static probability of prediction of what other partner
        will do, and picks the highest expected VALUE from those.
    VEV - Variable Expected Value. Agent reacts to partner's previous move, through altering EV probabilities.
    VPP - Variable Personal Probability. Agent changes own likelihood that it will defect in response to defection.
    ANGEL - Always co-operate.
    DEVIL - Always defect.

    TFT - The classic Tit for Tat strategy.
    WSLS - Win Stay Lose Switch """


class PDAgent(Agent):
    def __init__(self, pos, model,
                 stepcount=0,
                 pick_strat="RDISTRO",
                 strategy=None,
                 starting_move=None,
                 checkerboard=False,
                 lineplace=False,
                 ):
        super().__init__(pos, model)
        """ To set a heterogeneous strategy for all agents to follow, use strategy. If agents 
            are to spawn along a distribution, set number of strategy types, or with
            random strategies, use pick_strat and set strategy to None """

        self.pos = pos
        self.stepCount = stepcount
        self.ID = self.model.agentIDs.pop(0)
        self.score = 0
        self.strategy = strategy
        self.filename = ('%s agent %d.csv' % (self.model.exp_n, self.ID), "a")
        self.previous_moves = []
        self.pickstrat = pick_strat
        self.checkerboard = checkerboard
        self.lineplace = lineplace

        self.update_values = {}
        self.update_value = 0.015  # this is the value that will change each turn
        self.theta = 0.015  # uv we manipulate, stays static
        self.delta = self.model.msize  # max memory size
        if self.model.memoryPaired:
            if self.model.msize == 1:
                self.delta = 1
            if self.model.msize == 7:
                self.delta = 4
            #if self.model.msize == 2:
                #self.delta = 1
            #TODO: Figure out a consistent memory size metric

        #print('delta:', self.delta)

        self.init_uv = self.model.theta
        # self.init_ppD = model.init_ppD  # this isn't actually used

        self.move = None
        self.next_move = None
        self.printing = self.model.agent_printing
        if starting_move:
            self.move = starting_move
        else:
            self.move = self.random.choice(["C", "D"])

        self.payoffs = self.model.payoffs

        # ------------------------ LOCAL MEMORY --------------------------
        self.partner_IDs = []
        self.partner_moves = {}
        self.ppD_partner = 0
        self.per_partner_payoffs = {}  # this should be list of all prev payoffs from my partner, only used fr averaging
        self.partner_latest_move = {}  # this is a popped list
        #self.my_latest_move = {} # this is a popped list
        self.partner_scores = {}
        self.default_ppds = {}
        self.training_data = []
        self.per_partner_utility = {}
        self.per_partner_mcoops = {}  # MY cooperations that I perform
        self.per_partner_tcoops = {}  # THEIR cooperations that THEY perform
        self.per_partner_mutc = {}   # cumulative number of mutual cooperations me and each partner did
        self.per_partner_strategies = {}
        self.similar_partners = 0
        self.outcome_list = {}
        self.itermove_result = {}
        self.common_move = ""
        self.last_round = False
        self.wsls_failed = False

        self.globalAvPayoff = 0
        self.globalHighPayoff = 0  # effectively the highscore
        self.indivAvPayoff = {}
        self.proportional_score = 0  # this is used by the visualiser

        # self.average_payoff = 0  # should this be across partners or between them?

        self.working_memory = {}  # this is a popped list of size self.delta

        # ----------------------- SARSA GLOBALS ---------------------------

        self.states = []
        self.pp_sprime = {}
        self.pp_aprime = {}
        self.pp_payoff = {}
        self.oldstates = {}

        self.epsilon = copy.deepcopy(self.model.epsilon)
        self.alpha = copy.deepcopy(self.model.alpha)
        self.gamma = copy.deepcopy(self.model.gamma)

        # Per Partner Q Tables
        self.qtable = []

        # ----------------------- DATA TO OUTPUT --------------------------
        self.number_of_c = 0
        self.number_of_d = 0
        self.mutual_c_outcome = 0
        self.n_partners = 0

        # ----------------------- INTERACTIVE VARIABLES ----------------------
        # these values are increased if partner defects. ppC for each is 1 - ppD
        self.ppD_partner = {}
        self.rounds_left = self.model.rounds - self.stepCount

    def get_IDs(self):
        x, y = self.pos
        neighbouring_cells = [(x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)]  # N, E, S, W

        # First, get the neighbours
        for i in neighbouring_cells:
            bound_checker = self.model.grid.out_of_bounds(i)
            if not bound_checker:
                this_cell = self.model.grid.get_cell_list_contents([i])
                # print("This cell", this_cell)

                if len(this_cell) > 0:
                    partner = [obj for obj in this_cell
                               if isinstance(obj, PDAgent)][0]

                    partner_ID = partner.ID

                    if partner_ID not in self.partner_IDs:
                        self.partner_IDs.append(partner_ID)

                    # self.ppD_partner[partner_ID] = 0.5

    def set_defaults(self, ids):
        # open the ppD pickle
        # with open("agent_ppds.p", "rb") as f:
        #     agent_ppds = pickle.load(f)
        agent_ppds = copy.deepcopy(self.model.agent_ppds)
        # print("agent ppds are,", agent_ppds)
        my_pickle = agent_ppds[self.ID]
        # print("my defaults are", my_pickle)
        # j = 0
        for i in ids:
            index = ids.index(i)
            self.ppD_partner[i] = my_pickle[index]

            # print("this ppd was", self.ppD_partner[i])
            # print("this partner's pickled ppd is ", my_pickle[index])
            self.default_ppds[i] = my_pickle[index]

    def export_training_data(self):
        # print("the ppds are", self.default_ppds)
        my_data = []
        for i in self.partner_IDs:
            temp_data = []
            temp_data.append(self.per_partner_utility[i])
            temp_data.append(self.per_partner_mcoops[i])
            temp_data.append(self.per_partner_tcoops[i])
            temp_data.append(self.per_partner_mutc[i])
            temp_data.append(self.default_ppds[i])

            if self.per_partner_strategies[i] == 'VPP':
                temp_data.append(1)
            elif self.per_partner_strategies[i] == 'ANGEL':
                temp_data.append(2)
            elif self.per_partner_strategies[i] == 'DEVIL':
                temp_data.append(3)
            elif self.per_partner_strategies[i] == 'TFT':
                temp_data.append(4)
            elif self.per_partner_strategies[i] == 'WSLS':
                temp_data.append(5)
            elif self.per_partner_strategies[i] == 'iWSLS':
                temp_data.append(6)

            # print("It's the last turn, and this train_data is", temp_data)
            my_data.append(temp_data)

        # print("my_data", my_data)

        return my_data

    def pick_strategy(self):
        """ This is an initial strategy selector for agents """

        if self.model.kNN_spawn:
            if not self.model.kNN_testing:
                # print("My id is", self.ID)
                strat = "RANDOM"
                strat = self.model.kNN_strategies[self.ID]
                return str(strat)
            elif self.model.kNN_testing:
                # print("My id is", self.ID)
                strat = "RANDOM"
                strat = self.model.kNN_strategies[self.ID]
                return str(strat)

        elif self.model.sarsa_spawn:
            choices = ["LEARN", self.model.sarsa_oppo]
            if self.model.sarsa_distro > 0:
                weights = [self.model.sarsa_distro, 1-self.model.sarsa_distro]
                strat = np.random.choice(choices, 1, replace=False, p=weights)
                return str(strat[0])
            else:
                if len(choices) == 2:
                    if self.model.width == 8:
                        check_a = [1, 3, 5, 7, 10, 12, 14, 16, 17, 19, 21, 23, 26, 28, 30, 32, 33, 35, 37, 39,
                               42, 44, 46, 48, 49, 51, 53, 55, 58, 60, 62, 64]
                        check_b = [2, 4, 6, 8, 9, 11, 13, 15, 18, 20, 22, 24, 25, 27, 29, 31, 34, 36, 38, 40, 41,
                               43, 45, 47, 50, 52, 54, 56, 57, 59, 61, 63]
                    elif self.model.width == 3:
                        check_a = [1, 3, 5, 7, 9]
                        check_b = [2, 4, 6, 8]
                    elif self.model.width == 4:
                        check_a = [1, 3, 6, 8, 9, 11, 14, 16]
                        check_b = [2, 4, 5, 7, 10, 12, 13, 15]
                    elif self.model.width == 5:
                        check_a = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25]
                        check_b = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24]
                    elif self.model.width == 6:
                        check_a = [1, 3, 5, 8, 10, 12, 13, 15, 17, 20, 22, 24, 25, 27, 29, 32, 34, 36]
                        check_b = [2, 4, 6, 7, 9, 11, 14, 16, 18, 19, 21, 23, 26, 28, 30, 31, 33, 35]
                    elif self.model.width == 7:
                        check_a = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35,
                                   37, 39, 41, 43, 45, 47, 49]
                        check_b = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36,
                                   38, 40, 42, 44, 46, 48]
                    elif self.model.width == 2:
                        check_a = [1, 4]
                        check_b = [2, 3]

                    # print("My ID is:", self.ID, "and my coordinates are", self)
                    if self.ID in check_a:
                        strat = choices[0]
                        return str(strat)
                    elif self.ID in check_b:
                        strat = choices[1]
                        return str(strat)

        else:
            if self.pickstrat == "RANDOM":
                choices = ["EV", "ANGEL", "RANDOM", "DEVIL", "VEV", "TFT", "WSLS", "VPP", "iWSLS"]
                strat = random.choice(choices)
                # print("strat is", strat)
                return str(strat)
            elif self.pickstrat == "DISTRIBUTION":
                """ This is for having x agents start on y strategy and the remaining p agents
                    start on q strategy """

            elif self.pickstrat == "RDISTRO":  # Random Distribution of the selected strategies
                choices = ["iWSLS", "VPP"]
                if not self.checkerboard:
                    if not self.lineplace:
                        strat = random.choice(choices)
                        return str(strat)
                    elif self.lineplace:
                        if len(choices) == 2:
                            if (self.ID % 2) == 0:
                                strat = choices[0]
                                return str(strat)
                            else:
                                strat = choices[1]
                                return str(strat)
                        elif len(choices) == 3:
                            # make choices into a popped queue, take the front most and then add it in at the back after
                            # choosing
                            return
                elif self.checkerboard:
                    print("My ID is...", self.ID)
                    if len(choices) == 2:
                        check_a = [1, 3, 5, 7, 10, 12, 14, 16, 17, 19, 21, 23, 26, 28, 30, 32, 33, 35, 37, 39,
                                   42, 44, 46, 48, 49, 51, 53, 55, 58, 60, 62, 64]
                        check_b = [2, 4, 6, 8, 9, 11, 13, 15, 18, 20, 22, 24, 25, 27, 29, 31, 34, 36, 38, 40, 41,
                                   43, 45, 47, 50, 52, 54, 56, 57, 59, 61, 63]
                        if self.ID in check_a:
                            strat = choices[0]
                            return str(strat)
                        elif self.ID in check_b:
                            strat = choices[1]
                            return str(strat)

    def change_strategy(self):
        return

    def compare_score(self):
        """ Compares own score to current highest agent score in network for visualisation purposes"""
        if self.stepCount > 1:
            highscore = self.model.highest_score
            myscore = self.score
            # what percentage is my score of the highest score?
            self.proportional_score = ((myscore / highscore) * 100)

    def iter_pick_move(self, strategy, payoffs):
        """ Iterative move selection uses the pick_move function PER PARTNER, then stores this in a dictionary
        keyed by the partner it picked that move for. We can then cycle through these for iter. score incrementing"""
        versus_moves = {}
        x, y = self.pos
        neighbouring_cells = [(x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)]  # N, E, S, W

        # First, get the neighbours
        for i in neighbouring_cells:
            bound_checker = self.model.grid.out_of_bounds(i)
            if not bound_checker:
                this_cell = self.model.grid.get_cell_list_contents([i])
                # print("This cell", this_cell)

                if len(this_cell) > 0:
                    partner = [obj for obj in this_cell
                               if isinstance(obj, PDAgent)][0]

                    partner_ID = partner.ID

                    # pick a move
                    move = self.pick_move(strategy, payoffs, partner_ID, self.working_memory)
                    # add that move, with partner ID, to the versus choice dictionary
                    versus_moves[partner_ID] = move
        # print("agent", self.ID,"versus moves:", versus_moves)
        return versus_moves

    def iter_pick_nextmove(self, strategy, payoffs, nextstates):
        """ Iterative move selection uses the pick_move function PER PARTNER, then stores this in a dictionary
        keyed by the partner it picked that move for. We can then cycle through these for iter. score incrementing"""
        versus_moves = {}
        x, y = self.pos
        neighbouring_cells = [(x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)]  # N, E, S, W

        # First, get the neighbours
        for i in neighbouring_cells:
            bound_checker = self.model.grid.out_of_bounds(i)
            if not bound_checker:
                this_cell = self.model.grid.get_cell_list_contents([i])
                # print("This cell", this_cell)

                if len(this_cell) > 0:
                    partner = [obj for obj in this_cell
                               if isinstance(obj, PDAgent)][0]

                    partner_ID = partner.ID

                    # pick a move
                    move = self.pick_move(strategy, payoffs, partner_ID, nextstates)
                    # add that move, with partner ID, to the versus choice dictionary
                    versus_moves[partner_ID] = move
        # print("agent", self.ID,"versus moves:", versus_moves)
        return versus_moves

    def pick_move(self, strategy, payoffs, id, learning_state):
        """ given the payoff matrix, the strategy, and any other inputs (communication, trust perception etc.)
            calculate the expected utility of each move, and then pick the highest"""
        """AT THE MOMENT, THIS IS A GENERAL ONCE-A-ROUND FUNCTION, AND ISN'T PER PARTNER - THIS NEEDS TO CHANGE """

        if strategy is None or [] or 0:
            self.pick_strategy()

        elif strategy == "ANGEL":
            # print("I'm an angel, so I'll cooperate")
            self.number_of_c += 1
            return "C"

        elif strategy == "DEVIL":
            # print("I'm a devil, so I'll defect")
            self.number_of_d += 1
            return "D"

        elif strategy == "EV":  # this is under assumption of heterogeneity of agents
            """ EV is designed as a strategy not based on 'trust' (though it can reflect that), but instead on 
            the logic; 'I know they know defect is the best strategy usually, just as they know I know that'. """
            # Current set-up: We assume partner will defect

            ppD = 0.5  # probability of partner's defection
            ppC = 1 - ppD  # probability of partner's cooperation

            evCC = (payoffs["C", "C"] * ppC)
            evCD = (payoffs["C", "D"] * ppD)
            evDC = (payoffs["D", "C"] * ppC)
            evDD = (payoffs["D", "D"] * ppD)

            exp_util = (evCC, evCD, evDC, evDD)
            highest_ev = exp_util.index(max(exp_util))
            if highest_ev == 0:
                # print("Cooperate is best")
                self.number_of_c += 1
                return "C"
            elif highest_ev == 1:
                # print("Cooperate is best")
                self.number_of_c += 1
                return "C"
            elif highest_ev == 2:
                # print("Defect is best")
                self.number_of_d += 1
                return "D"
            elif highest_ev == 3:
                # print("Defect is best")
                self.number_of_d += 1
                return "D"

        elif strategy == "RANDOM":
            choice = self.random.choice(["C", "D"])
            if choice == "C":
                self.number_of_c += 1
            elif choice == "D":
                self.number_of_d += 1
            return choice

        elif strategy == "VEV":
            ppD = self.ppD_partner[id]
            ppC = 1 - self.ppD_partner[id]

            evCC = (payoffs["C", "C"] * ppC)
            evCD = (payoffs["C", "D"] * ppD)
            evDC = (payoffs["D", "C"] * ppC)
            evDD = (payoffs["D", "D"] * ppD)

            exp_value = (evCC, evCD, evDC, evDD)
            highest_ev = exp_value.index(max(exp_value))
            if highest_ev == 0:
                self.number_of_c += 1
                return "C"
            elif highest_ev == 1:
                self.number_of_c += 1
                return "C"
            elif highest_ev == 2:
                self.number_of_d += 1
                return "D"
            elif highest_ev == 3:
                self.number_of_d += 1
                return "D"

        elif strategy == "TFT":
            if self.stepCount == 1:
                self.number_of_c += 1
                return "C"
            else:
                if self.partner_latest_move[id] == 'C':
                    self.number_of_c += 1
                elif self.partner_latest_move[id] == 'D':
                    self.number_of_d += 1
                return self.partner_latest_move[id]

        elif strategy == "WSLS":
            """ This strategy picks C in the first turn, and then changes its move only if it 'loses' 
                - e.g. if it gets pwned or if both defect. """
            # if it's turn one, cooperate
            # after this, if the outcome for this partner was a winning one (either C-D or C-C?) then play the
            # same move again, if not, play the opposite move.

            if self.stepCount == 1:
                self.number_of_c += 1
                return "C"

            my_move = self.itermove_result[id]

            this_partner_move = self.partner_latest_move[id]
            outcome = [my_move, this_partner_move]

            failure_outcomes = [["C", "D"], ["D", "D"]]

            self.wsls_failed = False

            if outcome == ['C', 'C']:
                self.number_of_c += 1
                self.wsls_failed = False
            elif outcome == ['D', 'C']:
                self.number_of_d += 1
                self.wsls_failed = False
            elif outcome == ['C', 'D']:
                self.number_of_c += 1
                self.wsls_failed = True
                # print("I failed! Switching")
            elif outcome == ['D', 'D']:
                self.number_of_d += 1
                self.wsls_failed = True
                # print("I failed! Switching")

            if self.wsls_failed == True:
                if my_move == "C":
                    # self.number_of_c += 1
                    # print("Outcome was", outcome, "so Failure = ", self.wsls_failed, "So I will pick D")
                    self.wsls_failed = False
                    return "D"
                if my_move == "D":
                    # self.number_of_d += 1
                    # print("Outcome was", outcome, "so Failure = ", self.wsls_failed, "So I will pick C")
                    self.wsls_failed = False
                    return "C"
            else:
                # print("Outcome was", outcome, "so Failure = ", self.wsls_failed, "So I picked the same as last time")
                self.wsls_failed = False
                return my_move

        elif strategy == "iWSLS":
            """ This strategy picks C in the first turn, and then changes its move only if it 'loses'. 
                            - this is as alternative implementation of the previous WSLS strategy to 
                             check if it was performing as the lit suggests."""

            if self.stepCount == 1:
                self.number_of_c += 1
                return "C"

            my_move = self.itermove_result[id]
            this_partner_move = self.partner_latest_move[id]
            outcome = [my_move, this_partner_move]

            payoffs = self.payoffs
            outcome_payoff = payoffs[my_move, this_partner_move]

            aspiration_level = 1
            # print("My outcome was:", outcome)
            # print("My outcome payoff last turn was:", outcome_payoff, "whilst my aspiration level is", aspiration_level)
            if outcome_payoff <= aspiration_level:
                # print("My outcome was worse than my aspiration, sO I'll switch")
                if my_move == "C":
                    self.number_of_d += 1
                    return "D"
                if my_move == "D":
                    self.number_of_c += 1
                    return "C"
            else:
                # print("I'm doing good! I won't switch")
                if my_move == "C":
                    self.number_of_c += 1
                if my_move == "D":
                    self.number_of_d += 1
                return my_move

        elif strategy == "VPP":
            ppD = self.ppD_partner[id]
            ppC = 1 - self.ppD_partner[id]

            # Instead of using these values to calculate expected values/expected utilities, we use them to pick
            # our own move. This is a stochastic move selection weighted to respond to our partner's moves

            choices = ["C", "D"]
            weights = [ppC, ppD]

            choice = random.choices(population=choices, weights=weights, k=1)
            if choice == ["C"]:
                self.number_of_c += 1
                # print("number_of_c increased by 1, is now", self.number_of_c)
            elif choice == ["D"]:
                self.number_of_d += 1
                # print("number_of_d increased by 1, is now", self.number_of_d)
            return choice[0]

        elif strategy == "SWITCH":
            if self.stepCount <= 100:
                self.number_of_c += 1
                return "C"
            elif self.stepCount > 100 < 200:
                self.number_of_d += 1
                return "D"
            else:
                self.number_of_c += 1
                return "C"

        elif strategy == "LEARN":
            """ Use the epsilon-greedy algorithm to select a move to play. """
            if not learning_state:
                for j in self.partner_IDs:
                    blank_list = []
                    if self.model.memoryPaired:
                        # need to now vary the length of this depending on msize

                        for n in range(self.delta):
                            blank_list.append((0, 0))
                    elif not self.model.memoryPaired:
                        for n in range(self.delta):
                            blank_list.append(0)

                    learning_state[j] = blank_list


            egreedy = sarsa.egreedy_action(self.epsilon, self.qtable, tuple(learning_state[id]), self.model.memoryPaired)
            if egreedy == "C":
                self.number_of_c += 1
            elif egreedy == "D":
                self.number_of_d += 1
            return egreedy

    def change_update_value(self, partner_behaviour):
        """ Produce a [new update value] VALUE BY WHICH TO ALTER THE CURRENT UV given the current uv and the
        behaviour that partner has shown.
        Partner behaviour should be a list of self.delta size, ordered by eldest behaviour observed to most recent.
        current_uv should be a singular value """
        # let's start with a very simple lookup table version of behaviour comparison - probably only usable if
        # delta is fairly small, as we have to outline the specific behavioural patterns we are comparing
        """ NEW NOTE: Shaheen wants to use unordered lists, so the value judgements are just made on quantity of 
            recent good or bad interactions. This reduces the options down to 'do we have a hat trick' or 
            'is behaviour more one way or another'
            NEW NOTE mk. II: I have decided to disregard the above. Unordered lists that are only three long
            don't allow for any variability, so I'm just going to hard code it for now."""
        # THESE CONDITIONS BELOW ARE ONLY USABLE FOR A DELTA OF 3 EXACTLY

        # ** PROG NOTE: behaviour strings are capital letters
        # ** PROG NOTE: we never want the update value to be zero...
        # new_uv = current_uv
        # default
        # uv_modifier = 0
        theta = self.theta

        numberC = partner_behaviour.count('C')
        numberD = partner_behaviour.count('D')

        # # print("My partner did:", partner_behaviour)
        # if partner_behaviour == ['C', 'D', 'C']:  # Higher Value to Break Potential Cycles
        #     # print("I used behavioural rule 1, and I'm gonna return update value", theta * 3)
        #     return theta * 6
        #
        # elif partner_behaviour == ['D', 'C', 'D']:  # Higher Value to Break Potential Cycles
        #     # print("I used behavioural rule 1, and I'm gonna return update value", theta * 3)
        #     return theta * 6
        #
        # elif partner_behaviour == ['C', 'C', 'D']:  # Low Confidence due to New Behaviour
        #     # print("I used behavioural rule 2, and I'm gonna return update value", theta)
        #     return theta
        #
        # elif partner_behaviour == ['D', 'D', 'C']:  # Low Confidence due to New Behaviour
        #     # print("I used behavioural rule 2, and I'm gonna return update value", theta)
        #     return theta
        #
        # elif partner_behaviour == ['C', 'D', 'D']:  # Gaining Confidence/Trust
        #     # print("I used behavioural rule 3, and I'm gonna return update value", theta * 2)
        #     return theta * 4
        #
        # elif partner_behaviour == ['D', 'C', 'C']:  # Gaining Confidence/Trust
        #     # print("I used behavioural rule 3, and I'm gonna return update value", theta * 2)
        #     return theta * 4
        #
        # elif numberC or numberD == self.delta:  # High Value due to High Confidence
        #     # print("I used behavioural rule 4, and I'm gonna return update value", theta * 3)
        #     return theta * 6

        """ Acquire our state, then compare it to the list of all possible states generated by the 
            model. """

        all_states = copy.deepcopy(self.model.memory_states)
        state_values = copy.deepcopy(self.model.state_values)

        index = 0

        for i in all_states:
            if i == partner_behaviour:
                index = all_states.index(i)

        state_value = state_values[index]

        # TODO: This section is probably going to break to all hell when the new statemaker is used

        """" Now need to decide what the boundaries are for changing update value
            based on this state value that is returned... """
        # State values exist between values of 21 and -21, with a normal distribution of state values (i.e.
        # there are lower numbers of SUPER GOOD and SUPER BAD states, and where the numbers of C and D equal
        # out a bit there are more of those states). The value of middling states is zero and there is never more than
        # 16 of those states in those categories

        bound_a = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]
        bound_b = [-6, -7, -8, -9, 6, 7, 8, 9]
        bound_c = [-10, -11, -12, 10, 11, 12]
        bound_d = [-13, -14, -15, 13, 14, 15]
        bound_e = [-16, -17, -18, 16, 17, 18]
        bound_f = [-19, -20, -21, 19, 20, 21]

        if state_value in bound_a:
            return theta * 1
        if state_value in bound_b:
            return theta * 2
        if state_value in bound_c:
            return theta * 3
        if state_value in bound_d:
            return theta * 4
        if state_value in bound_e:
            return theta * 5
        if state_value in bound_f:
            return theta * 6

    def check_partner(self):
        """ Check Partner looks at all the partner's current move selections and adds them to relevant memory spaces"""
        x, y = self.pos
        neighbouring_cells = [(x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)]  # N, E, S, W

        # First, get the neighbours
        for i in neighbouring_cells:
            bound_checker = self.model.grid.out_of_bounds(i)
            if not bound_checker:
                this_cell = self.model.grid.get_cell_list_contents([i])
                # print("This cell", this_cell)
                if self.stepCount == 2:
                    self.n_partners += 1

                if len(this_cell) > 0:
                    partner = [obj for obj in this_cell
                               if isinstance(obj, PDAgent)][0]

                    partner_ID = partner.ID
                    partner_score = partner.score
                    partner_strategy = partner.strategy
                    partner_move = partner.itermove_result[self.ID]
                    partner_moves = partner.previous_moves

                    my_move = self.itermove_result[partner_ID]

                    # Wanna add each neighbour's move, score etc. to the respective memory banks
                    if self.partner_latest_move.get(partner_ID) is None:
                        self.partner_latest_move[partner_ID] = partner_move
                    else:
                        self.partner_latest_move[partner_ID] = partner_move
                        # this is stupidly redundant but I don't have the current brain energy to fix it

                    if self.per_partner_utility.get(partner_ID) is None:
                        self.per_partner_utility[partner_ID] = 0

                    if self.per_partner_payoffs.get(partner_ID) is None:
                        self.per_partner_payoffs[partner_ID] = [0]

                    if self.pp_payoff.get(partner_ID) is None:
                        self.pp_payoff[partner_ID] = 0

                    if self.per_partner_mcoops.get(partner_ID) is None:
                        self.per_partner_mcoops[partner_ID] = 0

                    if self.per_partner_tcoops.get(partner_ID) is None:
                        self.per_partner_tcoops[partner_ID] = 0

                    if self.per_partner_mutc.get(partner_ID) is None:
                        self.per_partner_mutc[partner_ID] = 0

                    if self.indivAvPayoff.get(partner_ID) is None:
                        self.indivAvPayoff[partner_ID] = 0

                    if self.per_partner_strategies.get(partner_ID) is None:
                        self.per_partner_strategies[partner_ID] = partner_strategy

                    if self.update_values.get(partner_ID) is None:  # add in default update value per partner
                        self.update_values[partner_ID] = self.init_uv  # this has to happen before change update value occurs!!

                    """ Below is the code for adding to and/or updating self.working_memory.
                     if WM does not have a key for current partner's ID in it, we open one
                     if it does, we extract it to a local variable by popping it
                     boobly boo, mess about with it and check what it means for us here
                     after it is updated and checked, we send it back to working memory
                    """
                    current_uv = self.update_value
                    if self.strategy == "VPP" or "LEARN":
                        if self.model.learnFrom != "us":
                            if self.working_memory.get(partner_ID) is None:
                                zeroes = []
                                for j in range(self.delta-1):
                                    zeroes.append(0)
                                zeroes.append(partner_move)
                                self.working_memory[partner_ID] = zeroes  # initialise with first value if doesn't exist
                            else:
                                current_state = self.working_memory.pop(partner_ID)

                                # first, check if it has more than three values
                                if len(current_state) < self.delta:  # if list hasn't hit delta, add in new move
                                    if self.model.learnFrom == "them":
                                        current_state.append(partner_move)
                                    elif self.model.learnFrom == "me":
                                        current_state.append(my_move)
                                elif len(current_state) == self.delta:
                                    current_state.pop(0)
                                    if self.model.learnFrom == "them":
                                        current_state.append(partner_move)  # we have the updated move list for that partner here
                                        current_uv = self.update_values[partner_ID]

                                        self.update_value = self.update_value + self.change_update_value(current_state)
                                    elif self.model.learnFrom == "me":
                                        current_state.append(my_move)

                                # print('My current partner history is now:', current_state)
                                self.working_memory[partner_ID] = current_state  # re-instantiate the memory to the bank

                        elif self.model.learnFrom == "us":
                            if self.working_memory.get(partner_ID) is None:
                                zeroes = []
                                if self.delta > 1:
                                    for j in range(self.delta-1):
                                        zeroes.append((0,0))
                                # print('mm', my_move, 'pm', partner_move)
                                zeroes.append((my_move, partner_move))
                                self.working_memory[partner_ID] = zeroes
                            else:
                                current_state = self.working_memory.pop(partner_ID)
                                # print('mmm', my_move, 'pmm', partner_move)
                                # print('len cs:', len(current_state), 'del', self.delta)
                                if len(current_state) < self.delta:
                                    current_state.append((my_move, partner_move))
                                elif len(current_state) == self.delta:
                                    current_state.pop(0)
                                    current_state.append((my_move, partner_move))
                                self.working_memory[partner_ID] = current_state

                                # self.update_value = self.update_value + self.change_update_value(current_state)
                                # TODO: Change the above so it doesn't need to work on just 7-count opponent values

                    """" ======================================================================================== """

                    # First, check if we have a case file on them in each memory slot
                    if self.partner_moves.get(partner_ID) is None:  # if we don't have one for this partner, make one
                        self.partner_moves[partner_ID] = []
                        self.partner_moves[partner_ID].append(partner_move)
                    else:
                        self.partner_moves[partner_ID].append(partner_move)
                        """ We should repeat the above process for the other memory fields too, like 
                        partner's gathered utility """

                    if partner_ID not in self.partner_IDs:
                        self.partner_IDs.append(partner_ID)

    def increment_score(self, payoffs):
        total_utility = 0
        outcome_listicle = {}
        for i in self.partner_IDs:
            my_move = self.itermove_result[i]

            this_partner_move = self.partner_latest_move[i]
            outcome = [my_move, this_partner_move]


            if my_move == 'C':
                self.per_partner_mcoops[i] += 1
                # print("I cooperated with my partner so my total C with them is,", self.per_partner_coops[i])
                # print("My score with them is", self.per_partner_utility[i])

            if this_partner_move == 'C':
                self.per_partner_tcoops[i] += 1

            if outcome == ['C', 'C']:
                self.mutual_c_outcome += 1
                self.per_partner_mutc[i] += 1

            outcome_listicle[i] = outcome
            outcome_payoff = payoffs[my_move, this_partner_move]
            # print("Outcome with partner %i was:" % i, outcome)

            self.per_partner_payoffs[i].append(outcome_payoff)
            self.pp_payoff[i] = outcome_payoff
            self.indivAvPayoff[i] = statistics.mean(self.per_partner_payoffs[i])
            # print("My individual average payoff for partner", i, "is ", self.indivAvPayoff[i])

            # ------- Here is where we change variables based on the outcome -------
            if self.strategy == "VEV" or "RANDOM" or "VPP" or "LEARN":
                if self.ppD_partner[i] < 1 and self.ppD_partner[i] > 0:

                    # if this_partner_move == "D":
                    #     self.ppD_partner[i] += 0.05
                    # elif this_partner_move == "C":
                    #     self.ppD_partner[i] -= 0.05
                    if this_partner_move == "D":
                        self.ppD_partner[i] += abs((outcome_payoff * self.update_value))  # self.update_values
                    elif this_partner_move == "C":
                        self.ppD_partner[i] -= abs((outcome_payoff * self.update_value))  # self.update_values

                if self.ppD_partner[i] > 1:
                    self.ppD_partner[i] = 1
                elif self.ppD_partner[i] < 0:
                    self.ppD_partner[i] = 0.001
                elif self.ppD_partner[i] == 6.938893903907228e-17:
                    self.ppD_partner[i] = 0.001

            outcome_payoff = payoffs[my_move, this_partner_move]
            current_partner_payoff = self.per_partner_utility[i]
            new_partner_payoff = current_partner_payoff + outcome_payoff
            self.per_partner_utility[i] = new_partner_payoff
            total_utility += outcome_payoff
            if self.printing:
                print("I am agent", self.ID, " I chose", my_move, " my partner is:", i, " they picked ",
                      this_partner_move, " so my payoff is ", outcome_payoff, " The p I will defect is now,",
                      self.ppD_partner)

        # self.score = self.score + total_utility
        self.outcome_list = outcome_listicle

        """ Here, we want to increment the GLOBAL, across-partner average payoff for the round """
        round_average = []
        for j in self.indivAvPayoff:
            item = self.indivAvPayoff[j]
            round_average.append(item)
        self.globalAvPayoff = statistics.mean(round_average)

        if self.globalAvPayoff > self.globalHighPayoff:
            self.globalHighPayoff = self.globalAvPayoff
        # print("My round average was ", self.globalAvPayoff, "and my highscore is ", self.globalHighPayoff)

        return total_utility

    def output_data_to_model(self):
        """ This sends the data to the model so the model can output it (I HOPE) """
        # print("Common move", self.common_move)
        if self.common_move == ['C']:
            self.model.agents_cooperating += 1
        elif self.common_move == ['D']:
            self.model.agents_defecting += 1
        # No line for Eq because the agent hasn't got a preference either way

        self.model.number_of_defects += self.number_of_d
        self.model.number_of_coops += self.number_of_c

        self.model.agent_list.append('{}, {}'.format(self.ID, self.strategy))

        # and also time each agent's step to create a total time thingybob

    def output_data_to_file(self, outcomes):
        """ Outputs the data collected each turn on multiple agent variables to a .csv file"""
        for m in self.per_partner_strategies:
            if self.per_partner_strategies[m] == self.strategy:
                self.similar_partners += 1

        prob_list = []
        util_list = []
        move_list = []
        average_list = []

        for i in self.indivAvPayoff:
            average_list.append(self.indivAvPayoff[i])

        avpay_partner_1 = 'None'
        avpay_partner_2 = 'None'
        avpay_partner_3 = 'None'
        avpay_partner_4 = 'None'

        if len(prob_list) == 0:
            avpay_partner_1 = 'None'
            avpay_partner_2 = 'None'
            avpay_partner_3 = 'None'
            avpay_partner_4 = 'None'
        elif len(prob_list) == 1:
            avpay_partner_1 = average_list[0]
            avpay_partner_2 = 'None'
            avpay_partner_3 = 'None'
            avpay_partner_4 = 'None'
        elif len(prob_list) == 2:
            avpay_partner_1 = average_list[0]
            avpay_partner_2 = average_list[1]
            avpay_partner_3 = 'None'
            avpay_partner_4 = 'None'
        elif len(prob_list) == 3:
            avpay_partner_1 = average_list[0]
            avpay_partner_2 = average_list[1]
            avpay_partner_3 = average_list[2]
            avpay_partner_4 = 'None'
        elif len(prob_list) == 4:
            avpay_partner_1 = average_list[0]
            avpay_partner_2 = average_list[1]
            avpay_partner_3 = average_list[2]
            avpay_partner_4 = average_list[3]

        for i in self.ppD_partner:
            prob_list.append(self.ppD_partner[i])

        ppd_partner_1 = 'None'
        ppd_partner_2 = 'None'
        ppd_partner_3 = 'None'
        ppd_partner_4 = 'None'

        if len(prob_list) == 0:
            ppd_partner_1 = 'None'
            ppd_partner_2 = 'None'
            ppd_partner_3 = 'None'
            ppd_partner_4 = 'None'
        elif len(prob_list) == 1:
            ppd_partner_1 = prob_list[0]
            ppd_partner_2 = 'None'
            ppd_partner_3 = 'None'
            ppd_partner_4 = 'None'
        elif len(prob_list) == 2:
            ppd_partner_1 = prob_list[0]
            ppd_partner_2 = prob_list[1]
            ppd_partner_3 = 'None'
            ppd_partner_4 = 'None'
        elif len(prob_list) == 3:
            ppd_partner_1 = prob_list[0]
            ppd_partner_2 = prob_list[1]
            ppd_partner_3 = prob_list[2]
            ppd_partner_4 = 'None'
        elif len(prob_list) == 4:
            ppd_partner_1 = prob_list[0]
            ppd_partner_2 = prob_list[1]
            ppd_partner_3 = prob_list[2]
            ppd_partner_4 = prob_list[3]

        for i in self.per_partner_utility:
            util_list.append(self.per_partner_utility[i])

        utility_partner_1 = 'None'
        utility_partner_2 = 'None'
        utility_partner_3 = 'None'
        utility_partner_4 = 'None'

        if len(util_list) == 0:
            utility_partner_1 = 'None'
            utility_partner_2 = 'None'
            utility_partner_3 = 'None'
            utility_partner_4 = 'None'
        elif len(util_list) == 1:
            utility_partner_1 = util_list[0]
            utility_partner_2 = 'None'
            utility_partner_3 = 'None'
            utility_partner_4 = 'None'
        elif len(util_list) == 2:
            utility_partner_1 = util_list[0]
            utility_partner_2 = util_list[1]
            utility_partner_3 = 'None'
            utility_partner_4 = 'None'
        elif len(util_list) == 3:
            utility_partner_1 = util_list[0]
            utility_partner_2 = util_list[1]
            utility_partner_3 = util_list[2]
            utility_partner_4 = 'None'
        elif len(util_list) == 4:
            utility_partner_1 = util_list[0]
            utility_partner_2 = util_list[1]
            utility_partner_3 = util_list[2]
            utility_partner_4 = util_list[3]

        for i in self.itermove_result:  # This encoding is per move type, allows graphing trends in move selection
            if self.itermove_result[i] == 'C':
                move_list.append(1)
                print()
            elif self.itermove_result[i] == 'D':
                move_list.append(2)

        move_partner_1 = 'None'
        move_partner_2 = 'None'
        move_partner_3 = 'None'
        move_partner_4 = 'None'

        if len(move_list) == 0:
            move_partner_1 = 'None'
            move_partner_2 = 'None'
            move_partner_3 = 'None'
            move_partner_4 = 'None'
        elif len(move_list) == 1:
            move_partner_1 = move_list[0]
            move_partner_2 = 'None'
            move_partner_3 = 'None'
            move_partner_4 = 'None'
        elif len(move_list) == 2:
            move_partner_1 = move_list[0]
            move_partner_2 = move_list[1]
            move_partner_3 = 'None'
            move_partner_4 = 'None'
        elif len(move_list) == 3:
            move_partner_1 = move_list[0]
            move_partner_2 = move_list[1]
            move_partner_3 = move_list[2]
            move_partner_4 = 'None'
        elif len(move_list) == 4:
            move_partner_1 = move_list[0]
            move_partner_2 = move_list[1]
            move_partner_3 = move_list[2]
            move_partner_4 = move_list[3]

        strategy_code = 'None'

        if self.strategy == 'RANDOM':
            strategy_code = 0
        elif self.strategy == 'ANGEL':
            strategy_code = 1
        elif self.strategy == 'DEVIL':
            strategy_code = 2
        elif self.strategy == 'EV':
            strategy_code = 3
        elif self.strategy == 'VEV':
            strategy_code = 4
        elif self.strategy == 'TFT':
            strategy_code = 5
        elif self.strategy == 'VPP':
            strategy_code = 6
        elif self.strategy == 'WSLS':
            strategy_code = 7
        elif self.strategy == "LEARN":
            strategy_code = 8

        """ The above will error catch for when agents don't have those values, and will still let us print 
            to csv. **** WOULD ALSO LIKE TO DO THIS FOR MOVE PER PARTNER """

        with open('{}.csv'.format(self.filename), 'a', newline='') as csvfile:
            if self.strategy == "VEV" or "RANDOM":
                fieldnames = ['stepcount_%d' % self.ID, 'strategy_%d' % self.ID, 'strat code_%d' % self.ID,
                              'move_%d' % self.ID,
                              'probabilities_%d' % self.ID, 'utility_%d' % self.ID, 'common_move_%d' % self.ID,
                              'number_coop_%d' % self.ID, 'number_defect_%d' % self.ID,
                              'outcomes_%d' % self.ID, 'p1_%d' % self.ID, 'p2_%d' % self.ID, 'p3_%d' % self.ID,
                              'p4_%d' % self.ID, 'u1_%d' % self.ID, 'u2_%d' % self.ID, 'u3_%d' % self.ID,
                              'u4_%d' % self.ID,
                              'm1_%d' % self.ID, 'm2_%d' % self.ID, 'm3_%d' % self.ID, 'm4_%d' % self.ID,
                              'uv_%d' % self.ID,
                              'wm_%d' % self.ID, 'nc_%d' % self.ID, 'mutC_%d' % self.ID, 'simP_%d' % self.ID,
                              'avp1_%d' % self.ID, 'avp2_%d' % self.ID, 'avp3_%d' % self.ID,'avp4_%d' % self.ID,
                              'globav_%d' % self.ID, 'epsilon_%d' % self.ID, 'alpha_%d' % self.ID]
            #     'p1', 'p2', 'p3', 'p4'
            else:
                fieldnames = ['stepcount_%d' % self.ID, 'strategy_%d' % self.ID, 'strat code_%d' % self.ID,
                              'move_%d' % self.ID,
                              'utility_%d' % self.ID, 'common_move_%d' % self.ID, 'number_coop_%d' % self.ID,
                              'number_defect_%d' % self.ID,
                              'outcomes_%d' % self.ID, 'u1_%d' % self.ID, 'u2_%d' % self.ID, 'u3_%d' % self.ID,
                              'u4_%d' % self.ID, 'm1_%d' % self.ID, 'm2_%d' % self.ID, 'm3_%d' % self.ID,
                              'm4_%d' % self.ID, 'uv_%d' % self.ID,
                              'wm_%d' % self.ID, 'nc_%d' % self.ID, 'mutC_%d' % self.ID, 'simP_%d' % self.ID,
                              'avp1_%d' % self.ID, 'avp2_%d' % self.ID, 'avp3_%d' % self.ID, 'avp4_%d' % self.ID,
                              'globav_%d' % self.ID, 'epsilon_%d' % self.ID, 'alpha_%d' % self.ID]

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # moves = []
            # for i in self.move:
            #     moves.append(self.move[i])

            if self.stepCount == 1:
                writer.writeheader()

            if self.strategy == "VEV" or "RANDOM":
                writer.writerow(
                    {'stepcount_%d' % self.ID: self.stepCount, 'strategy_%d' % self.ID: self.strategy,
                     'strat code_%d' % self.ID: strategy_code,
                     'move_%d' % self.ID: self.itermove_result, 'probabilities_%d' % self.ID: self.ppD_partner,
                     'utility_%d' % self.ID: self.score,
                     'common_move_%d' % self.ID: self.common_move, 'number_coop_%d' % self.ID: self.number_of_c,
                     'number_defect_%d' % self.ID: self.number_of_d, 'outcomes_%d' % self.ID: outcomes,
                     'p1_%d' % self.ID: ppd_partner_1,
                     'p2_%d' % self.ID: ppd_partner_2, 'p3_%d' % self.ID: ppd_partner_3,
                     'p4_%d' % self.ID: ppd_partner_4,
                     'u1_%d' % self.ID: utility_partner_1, 'u2_%d' % self.ID: utility_partner_2,
                     'u3_%d' % self.ID: utility_partner_3, 'u4_%d' % self.ID: utility_partner_4,
                     'm1_%d' % self.ID: move_partner_1,
                     'm2_%d' % self.ID: move_partner_2, 'm3_%d' % self.ID: move_partner_3,
                     'm4_%d' % self.ID: move_partner_4,
                     'uv_%d' % self.ID: self.update_value, 'wm_%d' % self.ID: self.working_memory,
                     'nc_%d' % self.ID: self.number_of_c,
                     'mutC_%d' % self.ID: self.mutual_c_outcome, 'simP_%d' % self.ID: self.similar_partners,
                     'avp1_%d' % self.ID: avpay_partner_1, 'avp2_%d' % self.ID: avpay_partner_2,
                     'avp3_%d' % self.ID: avpay_partner_3, 'avp4_%d' % self.ID: avpay_partner_4,
                     'globav_%d' % self.ID: self.globalAvPayoff, 'epsilon_%d' % self.ID: self.epsilon,
                     'alpha_%d' % self.ID: self.alpha})
            #
            else:
                writer.writerow(
                    {'stepcount_%d' % self.ID: self.stepCount, 'strategy_%d' % self.ID: self.strategy,
                     'strat code_%d' % self.ID: strategy_code,
                     'move_%d' % self.ID: self.itermove_result, 'utility_%d' % self.ID: self.score,
                     'common_move_%d' % self.ID: self.common_move, 'number_coop_%d' % self.ID: self.number_of_c,
                     'number_defect_%d' % self.ID: self.number_of_d, 'outcomes_%d' % self.ID: outcomes,
                     'u1_%d' % self.ID: utility_partner_1,
                     'u2': utility_partner_2, 'u3_%d' % self.ID: utility_partner_3,
                     'u4_%d' % self.ID: utility_partner_4, 'm1_%d' % self.ID: move_partner_1,
                     'm2_%d' % self.ID: move_partner_2, 'm3_%d' % self.ID: move_partner_3,
                     'm4_%d' % self.ID: move_partner_4, 'uv_%d' % self.ID: self.update_value,
                     'wm_%d' % self.ID: self.working_memory, 'nc_%d' % self.ID: self.number_of_c,
                     'mutC_%d' % self.ID: self.mutual_c_outcome,
                     'simP_%d' % self.ID: self.similar_partners,
                     'avp1_%d' % self.ID: avpay_partner_1, 'avp2_%d' % self.ID: avpay_partner_2,
                     'avp3_%d' % self.ID: avpay_partner_3, 'avp4_%d' % self.ID: avpay_partner_4,
                     'globav_%d' % self.ID: self.globalAvPayoff, 'epsilon_%d' % self.ID: self.epsilon,
                     'alpha_%d' % self.ID: self.alpha})

    def reset_values(self):
        """ Resets relevant global variables to default values. """
        self.number_of_d = 0
        self.number_of_c = 0
        self.update_value = self.init_uv
        self.mutual_c_outcome = 0

    # TODO: Move all the kNN stuff to a separate script that we just reference

    def knn_decision(self, partner_ids, partner_utils, partner_selfcoops, partner_oppcoops, partner_mutcoops, ppds):

        """ ppds needs to be self.model.agent_ppds"""
        updated_ppds = []
        old_ppds = self.model.agent_ppds[self.ID]
        # print("The old ppds are", old_ppds)

        updated_ppds = old_ppds
        training_data = copy.deepcopy(self.model.training_data)
        # print(len(training_data))
        decision_data = copy.deepcopy(self.model.training_data)

        for i in partner_ids:
            # training_data_list = training_data
            partner_index = partner_ids.index(i)
            game_utility = partner_utils[i]
            game_selfcoops = partner_selfcoops[i]
            game_oppcoops = partner_oppcoops[i]
            game_mutcoops = partner_mutcoops[i]
            game_ppd = ppds[i]

            """ The bit above might not work; because when we get ppds from the model it's a 4-long list,
                and some agents only use the first 2 to 3 items, we need to update the ppds in the list by 
                their indices to let them be used against the same agent next game"""

            class_list, classification = self.knn_analysis(game_utility, game_selfcoops, game_oppcoops, game_mutcoops,
                                                           game_ppd, training_data,
                                                           self.model.k)
            priority = "U"  # out of options 'C', 'U', and // TODO

            # print("My ID:", self.ID,
            #       "Partner ID:", i,
            #       "k Classifications:", class_list,
            #       "Decided Class:", classification)
            self.knn_error_statement(classification, i)
            # print("kNN was", self.knn_error_statement(classification, i))

            # so far, we should have a knn classification of what the ith partner is, which we then feed in to
            new_ppd = self.ppd_select(decision_data, classification, priority)

            updated_ppds[partner_index] = new_ppd

        # print("The Old ppds were:", old_ppds)
        # print("The new ppds are", updated_ppds)
        self.model.agent_ppds[self.ID] = updated_ppds
        return

    def knn_error_statement(self, classification, opp_id):

        strat = 0

        if self.per_partner_strategies[opp_id] == 'VPP':
            strat = 1
        elif self.per_partner_strategies[opp_id] == 'ANGEL':
            strat = 2
        elif self.per_partner_strategies[opp_id] == 'DEVIL':
            strat = 3
        elif self.per_partner_strategies[opp_id] == 'TFT':
            strat = 4
        elif self.per_partner_strategies[opp_id] == 'WSLS':
            strat = 5
        elif self.per_partner_strategies[opp_id] == 'iWSLS':
            strat = 6

        if classification != strat:
            return "Wrong"
        else:
            self.model.kNN_accuracy += 1
            return "Right"

    def BinaryPPDSearch(self, list, value, n_times, indx):
        """ This should return a list of indexes to search the data with """

        copy_list = copy.deepcopy(list)
        # print("bsearchinput", len(list), value, n_times, indx)
        # index_list = []
        data_list = []
        n_times = int(n_times)

        for i in range(0, n_times):     # would alternatively prefer this to be a while loop
            index = self.BSearch(copy_list, value, indx)  # get the index of the ppd item
            # print("I found an index, it's", index)
            # print(len(copy_list))
            if index != -1:
                # index_list.append(index)  # index list is garbage because of popping
                # print("The item is", copy_list[index])
                data_list.append(copy_list[index])
                # print("I appended it and the list now has", len(data_list), "items")
                # copy_list[index] = [0, 0, 0.0, 0]
                copy_list.pop(index)
                # print("I removed it")
            else:
                copy_list.pop(index)

        """ So, could we improve this by running the Search function indefinitely until it can no longer 
            find the value we're looking for? """
        # print("agent", self.ID, "index:",indx,"bsearch output", data_list)
        return data_list

    def BSearch(self, lys, val, indx_value):
        first = 0
        last = len(lys) - 1
        index = -1
        while (first <= last) and (index == -1):
            mid = (first + last) // 2
            if lys[mid][indx_value] == val:
                index = mid
            else:
                if val < lys[mid][indx_value]:
                    last = mid - 1
                else:
                    first = mid + 1
        return index

    def knn_analysis(self, utility, selfcoops, oppcoops, mutcoops, ppd, training_data, k):
        """ Takes an input, checks it against training data, and returns a partner classification """
        classification = 1  # CLASSES START AT 1 INSTEAD OF 0 BECAUSE IM A FOOL
        # print("Initialising knn analysis")
        current_data = [utility, selfcoops, oppcoops, mutcoops, ppd]
        current_data2 = [utility, selfcoops, ppd]
        # print(current_data)
        # print(len(training_data), type(training_data))

        relevant_data = []
        r_data_indices = []
        r_data_distances_to_goal = []

        # for i in training_data:
        #     """ We'll just use standard linear search for now, and maybe implement something faster later"""
        #     # get the third index of i
        #     if i[2] == ppd:
        #         relevant_data.append(i)
        #         r_data_indices.append(training_data.index(i))

        # For Binary Search, we need to know how many times to search the list - I think with the 113,400 data
        # it's 12,600 data points per ppd we collected
        # print("gonna do binary search with ppd of", ppd)
        training_size = len(training_data)
        relevant_data = self.BinaryPPDSearch(training_data, ppd, (training_size/3), 4)

        # print("rd", relevant_data)
        # can't get the indices from this, nor replace properly - but we don't need indices for a later search
        # because the search for optimal values will be a separate search

        for i in relevant_data:
            """ We take each item and calculate the Euclidean distance to the data we already have"""
            slice = i[:5]   #  =========== THIS MIGHT NEED TO BE 5 =======
            slice2 = [i[0], i[1], i[5]]
            distance_to_target = dst.cosine(current_data, slice)
            # print("data:", i, "distance:", distance_to_target)
            r_data_distances_to_goal.append(distance_to_target)

        # print("rel data", relevant_data)
        # print("distances", r_data_distances_to_goal)

        """ Now we have a list of distances to our current dataset, need to select k closest in terms of utility 
        and cooperations. Then access the relevant data and find the classification values ( i[3]) for them. """

        # sorted_distances = {k: v for k, v in sorted(r_data_distances_to_goal.items(), key=lambda item: item[1])}
        # # this may or may not work, it's a method taken from elsewhere...

        #
        ascending_data = sorted(zip(relevant_data, r_data_distances_to_goal), key=lambda t: t[1])[0:]
        # print("ass data", ascending_data)
        # print("ascend", ascending_data)
        # print(len(ascending_data))
        categories = []

        for i in range(0, k):
            # print("ass data2", ascending_data)
            temp = ascending_data[i]
            categories.append(temp[0][5])

        """Then, we find the most common category offered and return it. """
        # print("The k closest categories were:", categories)
        try:
            classification = statistics.mode(categories)
        except statistics.StatisticsError:
            classification = categories[0]
            # classification = statistics.mode(categories[0])

            # tryk = copy.deepcopy(k)
            # tryk = int((tryk/2)-1)

            # for i in range(0, tryk):
            #     # print("ass data2", ascending_data)
            #     temp = ascending_data[i]
            #     categories.append(temp[0][3])

            # classification = statistics.mode(categories)

            # if k < 3:
            #     classification = statistics.mode(categories[0])
            # if k > 3:
            #     classification = statistics.mode(categories[0:5])
        # print("The most common classification from the k neighbours is:", classification)
        # TODO - in future might want to weight each neighbour by closeness
        return categories, classification

    def ppd_select(self, list, classification, optimisation_choice):
        """ Takes a class of partner, given by the kNN algorithm, and returns a starting ppD to
        use in future games for the same partner based on which variable (or combo) we want to optimise """
        # don't need to make a deep copy of this list, because we're not altering it
        # print("pdsel", list, classification, optimisation_choice)
        # relevant_data = []

        relevant_data = self.BinaryPPDSearch(list,
                                             classification,
                                             (len(list)), 5)  # need to decide how many times to run this for
                                             # TODO my GODS why is this not fucking working
        npRev = np.array(relevant_data)
        # if len(npRev) == 0:
            # print("I'm agent", self.ID, "and ", len(list), classification, optimisation_choice, len(relevant_data))
            # print("npRev empty")

        col = 0
        if optimisation_choice == 'MC':  # optimise for MY cooperation
            col = 1
        elif optimisation_choice == 'U':  # optimise to maximise utility
            col = 0
        elif optimisation_choice == 'OC':
            col = 2
        elif optimisation_choice == 'MutC':
            col = 3

        npRev = npRev[np.argsort(npRev[:, col])]
        npRev = np.ndarray.tolist(npRev)
        # so, now we have a list sorted by the column we prefer, we can select the ppD associated with the highest score
        # print("checking npRev", npRev)

        highest = npRev[len(npRev)-1]
        new_ppd = highest[4]
        # print("I'm agent", self.ID, "My partner's class is", classification, "and the ppd I should use for them is", new_ppd)

        return new_ppd

    def find_average_move(self):
        """ Counts up how many of each behaviour type was performed that round and returns which was
            the most commonly chosen move (or Eq if there was a tie). """
        move_list = []
        for n in self.itermove_result:
            move_list.append(self.itermove_result[n])

        move_counter = {}
        for move in move_list:
            if move in move_counter:
                move_counter[move] += 1
            else:
                move_counter[move] = 1
        # print("Move counter:", move_counter)

        if move_counter.get('C') and move_counter.get('D') is not None:

            if move_counter['C'] == move_counter['D']:
                self.common_move = 'Eq'
                # print("Moves", self.move, "Counters: ", move_counter)
                # print("My most chosen move is:", self.common_move, 'because my counters are:', move_counter['C'],
                # move_counter['D'])

            else:
                commonest_move = sorted(move_counter, key=move_counter.get, reverse=True)
                self.common_move = commonest_move[
                                   :1]  # This isn't perfect as it doesn't display ties -----------------------
                # print("My most chosen move is:", self.common_move)
        else:
            commonest_move = sorted(move_counter, key=move_counter.get, reverse=True)
            self.common_move = commonest_move[:1]

    def outputQtable(self, init):
        # if I am the chosen one
        qvalues = []
        if self.ID == self.model.chosenOne:
            # get my qtable
            for i in self.qtable:
                pair = self.qtable[i]
                for j in pair:
                    qvalues.append(j)

            # for each numerical value in it, append it to a new list
            # for each item in that list, open up the csv and print it to it
        if init:
            for i in qvalues:
                with open('{} qinit_agent37.csv'.format(self.model.filename), 'a', newline='') as csvfile:
                    fieldnames = ['q']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    # writer.writeheader()
                    writer.writerow({'q': i})
        else:
            for i in qvalues:
                with open('{} qend_agent37.csv'.format(self.model.filename), 'a', newline='') as csvfile:
                    fieldnames = ['q']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    # writer.writeheader()
                    writer.writerow({'q': i})


    def outputData(self):
        self.output_data_to_model()
        if self.model.collect_data:
            self.output_data_to_file(self.outcome_list)

    def step(self):
        self.compare_score()
        self.reset_values()
        """  So a step for our agents, right now, is to calculate the utility of each option and then pick? """
        if self.stepCount == 1:
            # self.strategy = self.pick_strategy()
            self.set_defaults(self.partner_IDs)
            self.get_IDs()
            for i in self.partner_IDs:
                if self.model.learnFrom == "me":
                    zeroes = []
                    for j in range(self.delta):
                        zeroes.append(0)
                    self.oldstates[i] = zeroes
                elif self.model.learnFrom == "them":
                    zeroes = []
                    for j in range(self.delta):
                        zeroes.append(0)
                    self.oldstates[i] = zeroes
                elif self.model.learnFrom == "us":
                    zeroes = []
                    for j in range(self.delta):
                        zeroes.append((0,0))
                    self.oldstates[i] = zeroes

            if self.strategy is None or 0 or []:
                self.strategy = self.pick_strategy()
                # self.next_move = self.pick_move(self.strategy, self.payoffs, 0)
                self.previous_moves.append(self.move)
                self.set_defaults(self.partner_IDs)
                # print("My ppDs are:", self.ppD_partner)

                if self.strategy == 'LEARN':
                    # Initialise the q tables and states on the first turn
                    self.qtable = sarsa.init_qtable(copy.deepcopy(self.model.memory_states), 2, True)
                    self.states = copy.deepcopy(self.model.memory_states)

                self.itermove_result = self.iter_pick_move(self.strategy, self.payoffs)

                self.find_average_move()

                if self.model.schedule_type != "Simultaneous":
                    self.advance()

                # self.stepCount += 1
            else:

                self.set_defaults(self.partner_IDs)
                # print("My ppDs are:", self.ppD_partner)

                if self.strategy == 'LEARN':
                    # Initialise the q tables and states on the first turn
                    self.qtable = sarsa.init_qtable(copy.deepcopy(self.model.memory_states), 2, True)
                    self.states = copy.deepcopy(self.model.memory_states)

                self.itermove_result = self.iter_pick_move(self.strategy, self.payoffs)
                self.previous_moves.append(self.move)
                self.find_average_move()

                if self.model.schedule_type != "Simultaneous":
                    self.advance()

        else:
            if self.strategy is None or 0 or []:
                self.strategy = self.pick_strategy()
                # self.next_move = self.pick_move(self.strategy, self.payoffs, 0)
                self.previous_moves.append(self.move)

                if self.strategy == 'LEARN':
                    #if self.pp_aprime exists, itermove_result = copy.deepcopy(self.pp_aprime)
                    #clear next_action?
                    if self.pp_aprime:
                        self.itermove_result = copy.deepcopy(self.pp_aprime)
                        # TODO: Do I then need to wipe the aprime dict?
                else:
                    self.itermove_result = self.iter_pick_move(self.strategy, self.payoffs)

                self.find_average_move()

                if self.model.schedule_type != "Simultaneous":
                    self.advance()

                self.stepCount += 1
            else:

                if self.strategy == 'LEARN':
                    if self.pp_aprime:
                        self.itermove_result = copy.deepcopy(self.pp_aprime)
                        # TODO: Do I then need to wipe the aprime dict?
                else:
                    self.itermove_result = self.iter_pick_move(self.strategy, self.payoffs)

                self.previous_moves.append(self.move)  # Does this need to be here? Why is it nowhere else?
                self.find_average_move()

                if self.model.schedule_type != "Simultaneous":
                    self.advance()

        if self.stepCount == (self.model.rounds - 1):
            # print("My stepcount is", self.stepCount, "Next round is", (self.model.rounds - 1), "Next round is the last round!")
            self.last_round = True

        if self.printing:
            for n in range(1):
                print("----------------------------------------------------------")

    def advance(self):

        if self.strategy == 'LEARN':

            self.check_partner()  # We took action a, what s prime did we end up in?
            # ----- WORKING MEMORY IS NOW S-PRIME -----
            round_payoffs = self.increment_score(self.payoffs)  # Accept the reward for that s prime

            # update the sprimes (the states we have found ourselves in)
            # for i in self.working_memory:
            #     state = self.working_memory[i]
            #     obs = self.partner_latest_move[i]
            #     self.pp_sprime[i] = sarsa.output_sprime(state, obs)

            # get aprimes (next actions to do)
            self.pp_aprime = self.iter_pick_nextmove(self.strategy, self.payoffs, self.working_memory)

            # update the Q for the CURRENT sprime

            for i in self.partner_IDs:
                s = self.oldstates[i]           # the state I used to be in
                a = self.itermove_result[i]     # the action I took
                sprime = self.working_memory[i] # the state I found myself in
                reward = self.pp_payoff[i]      # the reward I observed
                aprime = self.pp_aprime[i]      # the action I will take next

                # print('ostates=', self.oldstates)
                # print('sstates=', self.itermove_result)
                # print('sprimes=', self.working_memory)
                if self.delta == 1:
                    if self.model.memoryPaired:
                        s = s[0]
                oldQValues = self.qtable[tuple(s)]  # THIS MIGHT BREAK BECAUSE OF TUPLES

                if a == 'C':  # This still works because it's keyed off the itermove_result and not part of the state
                    idx = 0
                elif a == 'D':
                    idx = 1

                if self.delta == 1:
                    if self.model.memoryPaired:
                        sprime = sprime[0]
                newQValues = self.qtable[tuple(sprime)]  # THIS ISN'T RIGHT IS IT?
                if aprime == 'C':
                    idxprime = 0
                elif aprime == 'D':
                    idxprime = 1

                Qsa = oldQValues[idx]
                Qsaprime = newQValues[idxprime]

                # update the Q value for the old state and old action

                newQsa = sarsa.update_q(reward, self.gamma, self.alpha, Qsa, Qsaprime)
                # print('My old Q for this partner was:', Qsa, 'and my new Q is:', newQsa)
                # then put newQ in the Qtable[s] at index idx
                change = self.qtable[tuple(s)]
                change[idx] = newQsa
                self.qtable[tuple(s)] = change


            # for i in self.working_memory:
            #     state = self.working_memory[i]
            #     my_move = self.itermove_result[i]
            #     reward = self.pp_payoff[i]  # the unmanipulated value
            #
            #     # for the states I'm in, update the relevant q value
            #     # access the qtable value we already have
            #     oldQValues = self.qtable[state]   # THIS MIGHT BREAK BECAUSE OF TUPLES
            #     if my_move == 'C':
            #         idx = 0
            #     elif my_move == 'D':
            #         idx = 1
            #
            #     next_state = self.pp_sprime[i]
            #     nextQValues = self.qtable[next_state]
            #     nextQValue = nextQValues[idx]  # this is wrong, just want
            #
            #     oldQValue = oldQValues[idx]
            #     new_value = sarsa.update_q(reward, self.gamma, self.alpha, oldQValue)

            # update epsilon
            self.epsilon = sarsa.decay_value(self.model.epsilon, self.epsilon, self.model.rounds, True, self.model.epsilon_floor)
            self.alpha = sarsa.decay_value(self.model.alpha, self.alpha, self.model.rounds, True, self.model.alpha_floor)

            # update s to be sprime
            for i in self.partner_IDs:
                self.oldstates[i] = self.working_memory[i]

            if self.model.export_q:
                if self.stepCount == 1:
                    self.outputQtable(True)
                elif self.stepCount == self.model.rounds - 1:
                    self.outputQtable(False)

            self.outputData()
            self.stepCount += 1

            if round_payoffs is not None:
                if self.printing:
                    print("I am agent", self.ID, ", and I have earned", round_payoffs, "this round")
                self.score += round_payoffs
                # print("My total overall score is:", self.score)
                return

        else:

            # self.move = self.next_move
            self.check_partner()  # Update Knowledge
            round_payoffs = self.increment_score(self.payoffs)
            if self.last_round:
                if self.strategy == 'VPP':
                    if self.model.kNN_training:
                        self.training_data = self.export_training_data()

            if self.stepCount == self.model.rounds - 1:
                if self.strategy == 'VPP':
                    if not self.model.kNN_training:
                        self.knn_decision(self.partner_IDs, self.per_partner_utility, self.per_partner_mcoops,
                                          self.per_partner_tcoops, self.per_partner_mutc, self.default_ppds)
                        # Only use this if we are not training as presumably we will have no training data because we will be training
            """ Because model outputting is below, we can add update values to the list before it *may get reset """
            # self.compare_score()

            self.outputData()
            self.stepCount += 1

            if round_payoffs is not None:
                if self.printing:
                    print("I am agent", self.ID, ", and I have earned", round_payoffs, "this round")
                self.score += round_payoffs
                # print("My total overall score is:", self.score)
                return

