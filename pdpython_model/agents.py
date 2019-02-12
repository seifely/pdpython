from mesa import Agent
import random
import csv
import time

class PDAgent(Agent):
    def __init__(self, pos, model, stepcount=0, pick_strat="RANDOM", strategy="RANDOM", starting_move="C"):
        super().__init__(pos, model)

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

    # pick a strategy - either by force, or by a decision mechanism
    # *** FOR FUTURE: *** Should agents pick strategies for each of their partners, or for all of their
    # interactions?
    def pick_strategy(self):
        """ This will later need more information coming into it - on what should I base my
        strategy selection? """
        # if self.strategy is None:
            # decision mechanism goes here
            # return
        if self.pickstrat == "HET":
            # all agents must use the same strategy
            return
        elif self.pickstrat == "RANDOM":
            choices = ["FP", "ANGEL", "RANDOM", "DEVIL"]
            strat = random.choice(choices)
            # print("strat is", strat)
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
                    move = self.pick_move(strategy, payoffs)
                    # add that move, with partner ID, to the versus choice dictionary
                    versus_moves[partner_ID] = move
        # print("agent", self.ID,"versus moves:", versus_moves)
        return versus_moves

    def pick_move(self, strategy, payoffs):
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
            ppC = 0.8  # probability of partner's cooperation

            euCC = (payoffs["C", "C"] * ppC)
            euCD = (payoffs["C", "D"] * ppD)
            euDC = (payoffs["D", "C"] * ppC)
            euDD = (payoffs["C", "D"] * ppD)

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

    # increment the agent's score - for iterated games
    def increment_score(self, payoffs):
        # my_move = self.move=
        total_utility = 0

        for i in self.partner_IDs:
            my_move = self.itermove_result[i]

            this_partner_move = self.partner_latest_move[i]
            outcome = [my_move, this_partner_move]
            # print("Outcome with partner %i was:" % i, outcome)

            outcome_payoff = payoffs[my_move, this_partner_move]
            current_partner_payoff = self.per_partner_utility[i]
            new_partner_payoff = current_partner_payoff + outcome_payoff
            self.per_partner_utility[i] = new_partner_payoff
            total_utility += outcome_payoff
            print("I am agent", self.ID, ", I chose", my_move, ", my partner is:", i, ", they picked ",
                  this_partner_move, ", so my payoff is ", outcome_payoff)

        # self.score = self.score + total_utility
        return total_utility

    def output_data_to_model(self):
        """ This sends the data to the model so the model can output it (I HOPE) """
        print("Common move", self.common_move)
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
        # output utility this round
        
        # open the csv files 
        with open('{}.csv'.format(self.filename), 'a', newline='') as csvfile:
            fieldnames = ['stepcount', 'move', 'utility', 'common_move', 'number_coop', 'number_defect',
                          'outcomes']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # moves = []
            # for i in self.move:
            #     moves.append(self.move[i])

            if self.stepCount == 1:
                writer.writeheader()
            writer.writerow({'stepcount': self.stepCount, 'move': self.itermove_result, 'utility': self.score,
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
        if self.stepCount == 0:
            self.strategy = self.pick_strategy()  # this will eventually do something
            # print(self.strategy)

            if self.strategy is None or 0 or []:
                self.strategy = self.pick_strategy()  # this will eventually do something
                self.next_move = self.pick_move(self.strategy, self.payoffs)
                self.previous_moves.append(self.move)
                self.itermove_result = self.iter_pick_move(self.strategy, self.payoffs)
                self.find_average_move()
                self.output_data_to_model()  # DOES RESET VALUES NEED TO COME AFTER THIS HERE?
                if self.model.collect_data:
                    self.output_data_to_file('outcomes go here')
                self.reset_values()  # ------------------> Or do they need to go here?

                if self.model.schedule_type != "Simultaneous":
                    self.advance()

                self.stepCount += 1
            else:
                self.next_move = self.pick_move(self.strategy, self.payoffs)
                # print("My move is ", self.move)
                self.itermove_result = self.iter_pick_move(self.strategy, self.payoffs)
                self.previous_moves.append(self.move)
                self.find_average_move()
                self.output_data_to_model()  # DOES RESET VALUES NEED TO COME AFTER THIS HERE?
                if self.model.collect_data:
                    self.output_data_to_file('outcomes go here')
                self.reset_values()  # ------------------> Or do they need to go here?

                if self.model.schedule_type != "Simultaneous":
                    self.advance()

                self.stepCount += 1
        else:
            self.next_move = self.pick_move(self.strategy, self.payoffs)
            # print("My move is ", self.move)
            self.itermove_result = self.iter_pick_move(self.strategy, self.payoffs)
            self.previous_moves.append(self.move)
            self.find_average_move()
            self.output_data_to_model()  # DOES RESET VALUES NEED TO COME AFTER THIS HERE?
            if self.model.collect_data:
                self.output_data_to_file('outcomes go here')
            self.reset_values()  # ------------------> Or do they need to go here?

            if self.model.schedule_type != "Simultaneous":
                self.advance()

            self.stepCount += 1

        # self.find_average_move()

        for n in range(1):
            print("----------------------------------------------------------")

    def advance(self):
        self.move = self.next_move
        self.check_partner()  # Check what all of our partners picked, so our knowledge is up-to-date
        round_payoffs = self.increment_score(self.payoffs)

        if round_payoffs is not None:
            print("I am agent", self.ID, ", and I have earned", round_payoffs, "this round")
            self.score += round_payoffs
            # print("My total overall score is:", self.score)
            return
