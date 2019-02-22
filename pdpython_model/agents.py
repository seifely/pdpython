from mesa import Agent
import random
import csv
import time

"""Note on Strategies:
    RANDOM - Does what it says on the tin, each turn a random move is selected.
    FP - Fixed Probabilities. Has a static probability of prediction of what other partner
        will do, and picks the highest expected utility from those
    ANGEL - Always co-operate.
    DEVIL - Always defect.
    VP - Agent reacts to partner's previous move."""

class PDAgent(Agent):
    def __init__(self, pos, model, stepcount=0, pick_strat="CONSPLIT", strategy=None , starting_move=None,
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
        self.itermove_result = {}
        self.common_move = ""

        # ----------------------- DATA TO OUTPUT --------------------------
        self.number_of_c = 0
        self.number_of_d = 0

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

    def pick_strategy(self):
        """ This will later need more information coming into it - on what should I base my
        strategy selection? """
        # if self.strategy is None:
            # decision mechanism goes here
            # return
        # if self.pickstrat == "HET":
        #
        #     return
        if self.pickstrat == "RANDOM":
            # print("IM GONNA PICK ONE AT RANDOM")
            choices = ["FP", "ANGEL", "RANDOM", "DEVIL", "VP"]
            strat = random.choice(choices)
            # print("strat is", strat)
            return str(strat)
        elif self.pickstrat == "DISTRIBUTION":
            """ This is for having x agents start on y strategy and the remaining p agents
                start on q strategy """
        elif self.pickstrat == "CONSPLIT":
            choices = ["VP", "RANDOM"]
            strat = random.choice(choices)
            return str(strat)

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
            # self.number_of_c += 1
            return "C"

        elif strategy == "DEVIL":
            # print("I'm a devil, so I'll defect")
            # self.number_of_d += 1
            return "D"

        elif strategy == "FP":  # this is under assumption of heterogeneity of agents
            """ FP is designed as a strategy not based on 'trust' (though it can reflect that), but instead on 
            the logic; 'I know they know defect is the best strategy usually, just as they know I know that'. """
            # Current set-up: We assume partner will defect

            ppD = 0.2  # probability of partner's defection
            ppC = 1 - ppD  # probability of partner's cooperation

            euCC = (payoffs["C", "C"] * ppC)
            euCD = (payoffs["C", "D"] * ppD)
            euDC = (payoffs["D", "C"] * ppC)
            euDD = (payoffs["D", "D"] * ppD)

            exp_util = (euCC, euCD, euDC, euDD)
            # print("EXPUTIL: ", exp_util)
            highest_eu = exp_util.index(max(exp_util))
            # print("Highest EU: ", highest_eu)
            if highest_eu == 0:
                # print("Cooperate is best")
                # self.number_of_c += 1
                return "C"
            elif highest_eu == 1:
                # print("Cooperate is best")
                # self.number_of_c += 1
                return "C"
            elif highest_eu == 2:
                # print("Defect is best")
                # self.number_of_d += 1
                return "D"
            elif highest_eu == 3:
                # print("Defect is best")
                # self.number_of_d += 1
                return "D"

        elif strategy == "RANDOM":
            choice = self.random.choice(["C", "D"])
            # if choice == "C":
                # self.number_of_c += 1
            # elif choice == "D":
                # self.number_of_d += 1
            return choice

        elif strategy == "VP":
            ppD = self.ppD_partner[id]
            ppC = 1 - self.ppD_partner[id]

            euCC = (payoffs["C", "C"] * ppC)
            euCD = (payoffs["C", "D"] * ppD)
            euDC = (payoffs["D", "C"] * ppC)
            euDD = (payoffs["D", "D"] * ppD)

            exp_util = (euCC, euCD, euDC, euDD)
            # print("EXPUTIL: ", exp_util)
            highest_eu = exp_util.index(max(exp_util))
            # print("Highest EU: ", highest_eu)
            if highest_eu == 0:
                # print("Cooperate is best")
                # self.number_of_c += 1
                return "C"
            elif highest_eu == 1:
                # print("Cooperate is best")
                # self.number_of_c += 1
                return "C"
            elif highest_eu == 2:
                # print("Defect is best")
                # self.number_of_d += 1
                return "D"
            elif highest_eu == 3:
                # print("Defect is best")
                # self.number_of_d += 1
                return "D"

        elif strategy == "TITFORTAT":
            if self.stepCount == 1:
                return "C"
            else:
                return self.partner_latest_move

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

                    # First, check if we have a casefile on them in each memory slot
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

        # print("Partner IDs: ", self.partner_IDs)
        # print("Partner Latest Moves:", self.partner_latest_move)

    def increment_score(self, payoffs):
        total_utility = 0

        for i in self.partner_IDs:
            my_move = self.itermove_result[i]

            this_partner_move = self.partner_latest_move[i]
            outcome = [my_move, this_partner_move]
            # print("Outcome with partner %i was:" % i, outcome)

            # ------- Here is where we change variables based on the outcome -------
            if self.strategy == "VP":
                if self.ppD_partner[i] < 1 and self.ppD_partner[i] > 0:
                    if this_partner_move == "D":
                        self.ppD_partner[i] += 0.05
                    elif this_partner_move == "C":
                        self.ppD_partner[i] -= 0.05

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
                print("I am agent", self.ID, ", I chose", my_move, ", my partner is:", i, ", they picked ",
                    this_partner_move, ", so my payoff is ", outcome_payoff)

        # self.score = self.score + total_utility
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

        # also want to output every agent's utility into one big vector - HOW DO THIS
        # either every agent creates a new column in the SAME document -
        # this is dangerous because they will all be editing the same file so probably a big fuck up

        # and also time each agent's step to create a total time thingybob

    def output_data_to_file(self, outcomes):

            prob_list = []
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

            """ The above will error catch for when agents don't have those values, and will still let us print 
                to csv. **** WOULD ALSO LIKE TO DO THIS FOR MOVE PER PARTNER """

            with open('{}.csv'.format(self.filename), 'a', newline='') as csvfile:
                if self.strategy == "VP":
                    fieldnames = ['stepcount', 'strategy', 'move', 'utility', 'common_move', 'number_coop',
                                  'number_defect', 'p1', 'p2', 'p3', 'p4',
                                  'outcomes', 'probabilities']
                #     'p1', 'p2', 'p3', 'p4'
                else:
                    fieldnames = ['stepcount', 'strategy', 'move', 'utility', 'common_move', 'number_coop',
                                  'number_defect',
                                  'outcomes']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                # moves = []
                # for i in self.move:
                #     moves.append(self.move[i])

                if self.stepCount == 1:
                    writer.writeheader()

                if self.strategy == "VP":
                    writer.writerow(
                        {'stepcount': self.stepCount, 'strategy': self.strategy, 'move': self.itermove_result,
                         'utility': self.score,
                         'common_move': self.common_move, 'number_coop': self.number_of_c,
                         'number_defect': self.number_of_d,  'p1': ppd_partner_1,
                        'p2': ppd_partner_2, 'p3': ppd_partner_3, 'p4': ppd_partner_4,'outcomes': outcomes,
                         'probabilities': self.ppD_partner})
                #
                else:
                    writer.writerow(
                        {'stepcount': self.stepCount, 'strategy': self.strategy, 'move': self.itermove_result,
                         'utility': self.score,
                         'common_move': self.common_move, 'number_coop': self.number_of_c,
                         'number_defect': self.number_of_d, 'outcomes': outcomes})

    def reset_values(self):
        self.number_of_d = 0
        self.number_of_c = 0

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
            self.number_of_d += move_counter.get('D')
            self.number_of_c += move_counter.get('C')
            if move_counter['C'] == move_counter['D']:
                self.common_move = 'Eq'
                # print("Moves", self.move, "Counters: ", move_counter)
                # print("My most chosen move is:", self.common_move, 'because my counters are:', move_counter['C'], move_counter['D'])

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
                self.output_data_to_model()
                if self.model.collect_data:
                    self.output_data_to_file('outcomes')
                self.reset_values()

                if self.model.schedule_type != "Simultaneous":
                    self.advance()

                self.stepCount += 1
            else:
                # self.next_move = self.pick_move(self.strategy, self.payoffs, 0)
                # this line is now redundant in a system that picks multiple moves per turn
                self.set_defaults(self.partner_IDs)
                # print("My ppDs are:", self.ppD_partner)

                self.itermove_result = self.iter_pick_move(self.strategy, self.payoffs)
                self.previous_moves.append(self.move)
                self.find_average_move()
                self.output_data_to_model()
                if self.model.collect_data:
                    self.output_data_to_file('outcomes')
                self.reset_values()

                if self.model.schedule_type != "Simultaneous":
                    self.advance()

                self.stepCount += 1
        else:
            if self.strategy is None or 0 or []:
                self.strategy = self.pick_strategy()
                # self.next_move = self.pick_move(self.strategy, self.payoffs, 0)
                self.previous_moves.append(self.move)
                # print("My ppDs are:", self.ppD_partner)

                self.itermove_result = self.iter_pick_move(self.strategy, self.payoffs)
                self.find_average_move()
                self.output_data_to_model()
                if self.model.collect_data:
                    self.output_data_to_file('outcomes')
                self.reset_values()

                if self.model.schedule_type != "Simultaneous":
                    self.advance()

                self.stepCount += 1
            else:
                # self.next_move = self.pick_move(self.strategy, self.payoffs, 0)
                # this line is now redundant in a system that picks multiple moves per turn
                # print("My ppDs are:", self.ppD_partner)

                self.itermove_result = self.iter_pick_move(self.strategy, self.payoffs)
                self.previous_moves.append(self.move)
                self.find_average_move()
                self.output_data_to_model()
                if self.model.collect_data:
                    self.output_data_to_file('outcomes')
                self.reset_values()

                if self.model.schedule_type != "Simultaneous":
                    self.advance()

                self.stepCount += 1

        # self.find_average_move()
        if self.printing:
            for n in range(1):
                print("----------------------------------------------------------")

    def advance(self):
        # self.move = self.next_move
        self.check_partner()  # Update Knowledge
        round_payoffs = self.increment_score(self.payoffs)

        if round_payoffs is not None:
            if self.printing:
                print("I am agent", self.ID, ", and I have earned", round_payoffs, "this round")
            self.score += round_payoffs
            # print("My total overall score is:", self.score)
            return
