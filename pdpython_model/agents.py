from mesa import Agent
import random
import csv
import time
from math import ceil

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
        self.update_value = 0.015
        self.gamma = 0.015  # uv we manipulate
        self.delta = 3  # max memory size
        self.init_uv = self.gamma

        self.move = None
        self.next_move = None
        self.printing = self.model.agent_printing
        if starting_move:
            self.move = starting_move
        else:
            self.move = self.random.choice(["C", "D"])

        self.payoffs = self.model.payoffs
        # pull in the payoff matrix (same for all agents IF WE ASSUME ALL AGENTS HAVE EQUAL PAYOFFS)

        # ------------------------ LOCAL MEMORY --------------------------
        self.partner_IDs = []
        self.partner_moves = {}
        self.partner_latest_move = {}  # this is a popped list
        self.partner_scores = {}
        self.per_partner_utility = {}
        self.per_partner_strategies = {}
        self.similar_partners = 0
        self.outcome_list = {}
        self.itermove_result = {}
        self.common_move = ""
        self.last_round = False
        self.wsls_failed = False

        self.working_memory = {}  # this is a popped list of size self.delta

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
        for i in ids:
            self.ppD_partner[i] = 0.5

    # def pattern_detector(self, input_list):
    #     """ This isn't learning, it's a small, imprecise detector for history of consistency in behaviour.
    #         It returns true if, in over half the instances of the memory list, point-to-point repeated behaviour was
    #         detected over two rounds. ONLY USEFUL FOR SMALL MEMORIES. """
    #     list_len = len(input_list)
    #     repeated_behaviour = 0
    #     non_repeated_behaviour = 0
    #
    #     for i in input_list:
    #         if i != 0:
    #             if input_list[i] != input_list[i - 1]:
    #                 non_repeated_behaviour += 1
    #             else:
    #                 repeated_behaviour += 1
    #
    #     if repeated_behaviour >= ceil(list_len/2):
    #         # some behavioural consistency
    #         return True
    #     else:
    #         return False

    def pick_strategy(self):
        """ This is an initial strategy selector for agents """

        if self.pickstrat == "RANDOM":
            choices = ["EV", "ANGEL", "RANDOM", "DEVIL", "VEV", "TFT", "WSLS", "VPP"]
            strat = random.choice(choices)
            # print("strat is", strat)
            return str(strat)
        elif self.pickstrat == "DISTRIBUTION":
            """ This is for having x agents start on y strategy and the remaining p agents
                start on q strategy """

        elif self.pickstrat == "RDISTRO": # Random Distribution of the two selected strategies
            choices = ["VPP", "TFT"]
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

                    # if (self.ID % 2) == 0:
                    #     if self.ID >= 1 and self.ID < 9:
                    #         if (self.ID % 2) == 0:
                    #             strat = choices[0]
                    #             return str(strat)
                    #         else:
                    #             strat = choices[1]
                    #             return str(strat)
                    #     elif self.ID >= 9 and self.ID < 17:
                    #         if (self.ID % 2) == 0:
                    #             strat = choices[1]
                    #             return str(strat)
                    #         else:
                    #             strat = choices[0]
                    #             return str(strat)
                    #     elif self.ID >= 17 and self.ID < 25:
                    #         if (self.ID % 2) == 0:
                    #             strat = choices[0]
                    #             return str(strat)
                    #         else:
                    #             strat = choices[1]
                    #             return str(strat)
                    #     elif self.ID >= 25 and self.ID < 33:
                    #         if (self.ID % 2) == 0:
                    #             strat = choices[1]
                    #             return str(strat)
                    #         else:
                    #             strat = choices[0]
                    #             return str(strat)
                    #     elif self.ID >= 33 and self.ID < 41:
                    #         if (self.ID % 2) == 0:
                    #             strat = choices[0]
                    #             return str(strat)
                    #         else:
                    #             strat = choices[1]
                    #             return str(strat)
                    #     elif self.ID >= 41 and self.ID < 49:
                    #         if (self.ID % 2) == 0:
                    #             strat = choices[1]
                    #             return str(strat)
                    #         else:
                    #             strat = choices[0]
                    #             return str(strat)
                    #     elif self.ID >= 49 and self.ID < 57:
                    #         if (self.ID % 2) == 0:
                    #             strat = choices[0]
                    #             return str(strat)
                    #         else:
                    #             strat = choices[1]
                    #             return str(strat)
                    #     elif self.ID >= 57:
                    #         if (self.ID % 2) == 0:
                    #             strat = choices[1]
                    #             return str(strat)
                    #         else:
                    #             strat = choices[0]
                    #             return str(strat)


    def change_strategy(self):
        return

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
                    move = self.pick_move(strategy, payoffs, partner_ID)
                    # add that move, with partner ID, to the versus choice dictionary
                    versus_moves[partner_ID] = move
        # print("agent", self.ID,"versus moves:", versus_moves)
        return versus_moves

    def pick_move(self, strategy, payoffs, id):
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

            ppD = 0.2  # probability of partner's defection
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
            elif highest_ev== 2:
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
        gamma = self.gamma

        numberC = partner_behaviour.count('C')
        numberD = partner_behaviour.count('D')
        #print("Number of C is", numberC)
        #print("Number of D is", numberD)
        #
        #
        #
        #

        #print("My partner did:", partner_behaviour)
        if partner_behaviour == ['C', 'D', 'C']:  # Higher Value to Break Potential Cycles
            #print("I used behavioural rule 1, and I'm gonna return update value", gamma * 3)
            return gamma * 3

        elif partner_behaviour == ['D', 'C', 'D']:  # Higher Value to Break Potential Cycles
            #print("I used behavioural rule 1, and I'm gonna return update value", gamma * 3)
            return gamma * 3

        elif partner_behaviour == ['C', 'C', 'D']:  # Low Confidence due to New Behaviour
            #print("I used behavioural rule 2, and I'm gonna return update value", gamma)
            return gamma

        elif partner_behaviour == ['D', 'D', 'C']:  # Low Confidence due to New Behaviour
            #print("I used behavioural rule 2, and I'm gonna return update value", gamma)
            return gamma

        elif partner_behaviour == ['C', 'D', 'D']:  # Gaining Confidence/Trust
            #print("I used behavioural rule 3, and I'm gonna return update value", gamma * 2)
            return gamma * 2

        elif partner_behaviour == ['D', 'C', 'C']:  # Gaining Confidence/Trust
            #print("I used behavioural rule 3, and I'm gonna return update value", gamma * 2)
            return gamma * 2

        elif numberC or numberD == self.delta:  # High Value due to High Confidence
            #print("I used behavioural rule 4, and I'm gonna return update value", gamma * 3)
            return gamma * 3
        #
        # elif not consistency:
        #     return gamma * 2

        # we also need an emergency catch-all for up and down behaviour, to break us out of toxic loops
        # this either needs to come from LONG TERM MEMORY or it needs to come here ??? figure this out after testing
        # round one
        # if new_uv = 0
        #       new_uv = 0.001?

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
                    # ******** this could either be redundant or MORE EFFICIENT than the current way of doing things -
                    # this is accessing the other agent's own record of its moves

                    # Wanna add each neighbour's move, score etc. to the respective memory banks
                    if self.partner_latest_move.get(partner_ID) is None:
                        self.partner_latest_move[partner_ID] = partner_move
                    else:
                        self.partner_latest_move[partner_ID] = partner_move
                        # this is stupidly redundant but I don't have the current brain energy to fix it

                    if self.per_partner_utility.get(partner_ID) is None:
                        self.per_partner_utility[partner_ID] = 0

                    if self.per_partner_strategies.get(partner_ID) is None:
                        self.per_partner_strategies[partner_ID] = partner_strategy

                    if self.update_values.get(partner_ID) is None:  # add in default update value per partner
                        self.update_values[partner_ID] = 0.01  # this has to happen before change update value occurs!!

                    """ Below is the code for adding to and/or updating self.working_memory.
                     if WM does not have a key for current partner's ID in it, we open one
                     if it does, we extract it to a local variable by popping it
                     boobly boo, mess about with it and check what it means for us here
                     after it is updated and checked, we send it back to working memory
                    """
                    current_uv = self.update_value

                    if self.working_memory.get(partner_ID) is None:
                        self.working_memory[partner_ID] = [partner_move]  # initialise with first value if doesn't exist
                    else:
                        current_partner = self.working_memory.pop(partner_ID)
                        # first, check if it has more than three values
                        if len(current_partner) < self.delta:  # if list hasn't hit delta, add in new move
                            current_partner.append(partner_move)
                        elif len(current_partner) == self.delta:
                            current_partner.pop(0)
                            current_partner.append(partner_move)  # we have the updated move list for that partner here
                            current_uv = self.update_values[partner_ID]
                                             # for now, let's add the evaluation of a partner's treatment of us here
                        # self.update_values[partner_ID] = self.change_update_value(current_partner, current_uv)
                        #     print("Gonna update my UV!", self.update_value)
                            self.update_value = self.update_value + self.change_update_value(current_partner)

                        # - UNCOMMENT ABOVE FOR MEMORY SYSTEM TO WORK
                        #     print("I updated it!", self.update_value)

                        self.working_memory[partner_ID] = current_partner  # re-instantiate the memory to the bank

                    # First, check if we have a case file on them in each memory slot
                    if self.partner_moves.get(partner_ID) is None:  # if we don't have one for this partner, make one
                        self.partner_moves[partner_ID] = []
                        # print("partner moves dict:", self.partner_moves)
                        self.partner_moves[partner_ID].append(partner_move)
                        # print("partner moves dict2:", self.partner_moves)
                    else:
                        self.partner_moves[partner_ID].append(partner_move)
                        # print("My partner's moves have been:", self.partner_moves)
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

            if outcome == ['C','C']:
                self.mutual_c_outcome += 1

            outcome_listicle[i] = outcome
            outcome_payoff = payoffs[my_move, this_partner_move]
            # print("Outcome with partner %i was:" % i, outcome)

            # ------- Here is where we change variables based on the outcome -------
            if self.strategy == "VEV" or "RANDOM" or "VPP":
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
                    self.ppD_partner[i] = 0
                elif self.ppD_partner[i] == 6.938893903907228e-17:
                    self.ppD_partner[i] = 0

            outcome_payoff = payoffs[my_move, this_partner_move]
            current_partner_payoff = self.per_partner_utility[i]
            new_partner_payoff = current_partner_payoff + outcome_payoff
            self.per_partner_utility[i] = new_partner_payoff
            total_utility += outcome_payoff
            if self.printing:
                print("I am agent", self.ID, " I chose", my_move, " my partner is:", i, " they picked ",
                    this_partner_move, " so my payoff is ", outcome_payoff, " The p I will defect is now,", self.ppD_partner)

        # self.score = self.score + total_utility
        self.outcome_list = outcome_listicle
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

            for m in self.per_partner_strategies:
                if self.per_partner_strategies[m] == self.strategy:
                    self.similar_partners += 1

            prob_list = []
            util_list = []
            move_list = []

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

            """ The above will error catch for when agents don't have those values, and will still let us print 
                to csv. **** WOULD ALSO LIKE TO DO THIS FOR MOVE PER PARTNER """

            with open('{}.csv'.format(self.filename), 'a', newline='') as csvfile:
                if self.strategy == "VEV" or "RANDOM":
                    fieldnames = ['stepcount_%d' % self.ID, 'strategy_%d' % self.ID, 'strat code_%d' % self.ID, 'move_%d' % self.ID,
                                  'probabilities_%d' % self.ID, 'utility_%d' % self.ID, 'common_move_%d' % self.ID,
                                  'number_coop_%d' % self.ID, 'number_defect_%d' % self.ID,
                                  'outcomes_%d' % self.ID, 'p1_%d' % self.ID, 'p2_%d' % self.ID, 'p3_%d' % self.ID,
                                  'p4_%d' % self.ID, 'u1_%d' % self.ID, 'u2_%d' % self.ID, 'u3_%d' % self.ID, 'u4_%d' % self.ID,
                                  'm1_%d' % self.ID, 'm2_%d' % self.ID, 'm3_%d' % self.ID, 'm4_%d' % self.ID, 'uv_%d' % self.ID,
                                  'wm_%d' % self.ID, 'nc_%d' % self.ID, 'mutC_%d' % self.ID, 'simP_%d' % self.ID]
                #     'p1', 'p2', 'p3', 'p4'
                else:
                    fieldnames = ['stepcount_%d' % self.ID, 'strategy_%d' % self.ID, 'strat code_%d' % self.ID, 'move_%d' % self.ID,
                                  'utility_%d' % self.ID, 'common_move_%d' % self.ID, 'number_coop_%d' % self.ID,
                                  'number_defect_%d' % self.ID,
                                  'outcomes_%d' % self.ID, 'u1_%d' % self.ID, 'u2_%d' % self.ID, 'u3_%d' % self.ID,
                                  'u4_%d' % self.ID, 'm1_%d' % self.ID, 'm2_%d' % self.ID, 'm3_%d' % self.ID, 'm4_%d' % self.ID, 'uv_%d' % self.ID,
                                  'wm_%d' % self.ID, 'nc_%d' % self.ID, 'mutC_%d' % self.ID, 'simP_%d' % self.ID]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                # moves = []
                # for i in self.move:
                #     moves.append(self.move[i])

                if self.stepCount == 1:
                    writer.writeheader()

                if self.strategy == "VEV" or "RANDOM":
                    writer.writerow(
                        {'stepcount_%d' % self.ID: self.stepCount, 'strategy_%d' % self.ID: self.strategy, 'strat code_%d' % self.ID: strategy_code,
                         'move_%d' % self.ID: self.itermove_result, 'probabilities_%d' % self.ID: self.ppD_partner,
                         'utility_%d' % self.ID: self.score,
                         'common_move_%d' % self.ID: self.common_move, 'number_coop_%d' % self.ID: self.number_of_c,
                         'number_defect_%d' % self.ID: self.number_of_d, 'outcomes_%d' % self.ID: outcomes, 'p1_%d' % self.ID: ppd_partner_1,
                        'p2_%d' % self.ID: ppd_partner_2, 'p3_%d' % self.ID: ppd_partner_3, 'p4_%d' % self.ID: ppd_partner_4,
                         'u1_%d' % self.ID: utility_partner_1, 'u2_%d' % self.ID: utility_partner_2,
                         'u3_%d' % self.ID: utility_partner_3, 'u4_%d' % self.ID: utility_partner_4, 'm1_%d' % self.ID: move_partner_1,
                         'm2_%d' % self.ID: move_partner_2, 'm3_%d' % self.ID: move_partner_3, 'm4_%d' % self.ID: move_partner_4,
                         'uv_%d' % self.ID: self.update_value, 'wm_%d' % self.ID: self.working_memory, 'nc_%d' % self.ID: self.number_of_c,
                         'mutC_%d' % self.ID: self.mutual_c_outcome, 'simP_%d' % self.ID: self.similar_partners})
                #
                else:
                    writer.writerow(
                        {'stepcount_%d' % self.ID: self.stepCount, 'strategy_%d' % self.ID: self.strategy, 'strat code_%d' % self.ID: strategy_code,
                         'move_%d' % self.ID: self.itermove_result, 'utility_%d' % self.ID: self.score,
                         'common_move_%d' % self.ID: self.common_move, 'number_coop_%d' % self.ID: self.number_of_c,
                         'number_defect_%d' % self.ID: self.number_of_d, 'outcomes_%d' % self.ID: outcomes, 'u1_%d' % self.ID: utility_partner_1,
                         'u2': utility_partner_2, 'u3_%d' % self.ID: utility_partner_3, 'u4_%d' % self.ID: utility_partner_4, 'm1_%d' % self.ID: move_partner_1,
                         'm2_%d' % self.ID: move_partner_2, 'm3_%d' % self.ID: move_partner_3, 'm4_%d' % self.ID: move_partner_4, 'uv_%d' % self.ID: self.update_value,
                         'wm_%d' % self.ID: self.working_memory, 'nc_%d' % self.ID: self.number_of_c, 'mutC_%d' % self.ID: self.mutual_c_outcome,
                         'simP_%d' % self.ID: self.similar_partners})

    def reset_values(self):
        self.number_of_d = 0
        self.number_of_c = 0
        self.update_value = self.init_uv
        self.mutual_c_outcome = 0

    def find_average_move(self):
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

    def step(self):
        """  So a step for our agents, right now, is to calculate the utility of each option and then pick? """
        if self.stepCount == 1:
            # self.strategy = self.pick_strategy()
            self.set_defaults(self.partner_IDs)
            self.get_IDs()

            if self.strategy is None or 0 or []:
                self.strategy = self.pick_strategy()
                # self.next_move = self.pick_move(self.strategy, self.payoffs, 0)
                self.previous_moves.append(self.move)
                self.set_defaults(self.partner_IDs)
                # print("My ppDs are:", self.ppD_partner)

                self.itermove_result = self.iter_pick_move(self.strategy, self.payoffs)

                self.find_average_move()

                # self.output_data_to_model()
                # if self.model.collect_data:
                #     self.output_data_to_file(self.outcome_list)
                # self.reset_values()

                if self.model.schedule_type != "Simultaneous":
                    self.advance()

                # self.stepCount += 1
            else:
                # self.next_move = self.pick_move(self.strategy, self.payoffs, 0)
                # this line is now redundant in a system that picks multiple moves per turn
                self.set_defaults(self.partner_IDs)
                # print("My ppDs are:", self.ppD_partner)

                self.itermove_result = self.iter_pick_move(self.strategy, self.payoffs)
                self.previous_moves.append(self.move)
                # print("Number of c and d at V3S3: ", self.number_of_c, self.number_of_d)
                # print("Number of C and D at V3S3: ", self.model.number_of_coops, self.model.number_of_defects)
                self.find_average_move()
                # print("Number of c and d at V3S4: ", self.number_of_c, self.number_of_d)
                # print("Number of C and D at V3S4: ", self.model.number_of_coops, self.model.number_of_defects)

                # self.output_data_to_model()
                # if self.model.collect_data:
                #     self.output_data_to_file(self.outcome_list)
                # self.reset_values()

                if self.model.schedule_type != "Simultaneous":
                    self.advance()

                # self.stepCount += 1
        else:
            if self.strategy is None or 0 or []:
                self.strategy = self.pick_strategy()
                # self.next_move = self.pick_move(self.strategy, self.payoffs, 0)
                self.previous_moves.append(self.move)
                # print("My ppDs are:", self.ppD_partner)

                self.itermove_result = self.iter_pick_move(self.strategy, self.payoffs)
                self.find_average_move()

                # self.output_data_to_model()
                # if self.model.collect_data:
                #     self.output_data_to_file(self.outcome_list)
                # self.reset_values()

                if self.model.schedule_type != "Simultaneous":
                    self.advance()

                self.stepCount += 1
            else:
                # self.next_move = self.pick_move(self.strategy, self.payoffs, 0)
                # this line is now redundant in a system that picks multiple moves per turn
                # print("My ppDs are:", self.ppD_partner)

                self.itermove_result = self.iter_pick_move(self.strategy, self.payoffs)
                self.previous_moves.append(self.move)
                # print("Number of c and d at V4S3: ", self.number_of_c, self.number_of_d)
                # print("Number of C and D at V4S3: ", self.model.number_of_coops, self.model.number_of_defects)
                self.find_average_move()
                # print("Number of c and d at V4S4: ", self.number_of_c, self.number_of_d)
                # print("Number of C and D at V4S4: ", self.model.number_of_coops, self.model.number_of_defects)

                # self.output_data_to_model()
                # if self.model.collect_data:
                #     self.output_data_to_file(self.outcome_list)
                # self.reset_values()

                if self.model.schedule_type != "Simultaneous":
                    self.advance()

        if self.stepCount == (self.model.rounds - 1):
            # print("My stepcount is", self.stepCount, "Next round is", (self.model.rounds - 1), "Next round is the last round!")
            self.last_round = True

        # self.find_average_move()
        # print("At the end of this agent, model C and D are:", self.model.number_of_coops,
        #       self.model.number_of_defects, ", total:", (self.model.number_of_defects + self.model.number_of_coops))
        if self.printing:
            for n in range(1):
                print("----------------------------------------------------------")

    def advance(self):
        # self.move = self.next_move
        self.check_partner()  # Update Knowledge
        round_payoffs = self.increment_score(self.payoffs)
        """ Because model outputting is below, we can add update values to the list before it *may get reset """
        self.output_data_to_model()
        if self.model.collect_data:
            self.output_data_to_file(self.outcome_list)
        self.reset_values()

        self.stepCount += 1

        if round_payoffs is not None:
            if self.printing:
                print("I am agent", self.ID, ", and I have earned", round_payoffs, "this round")
            self.score += round_payoffs
            # print("My total overall score is:", self.score)
            return
