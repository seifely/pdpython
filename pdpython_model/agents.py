from mesa import Agent
import random

class PDAgent(Agent):
    def __init__(self, pos, model, stepcount=0, strategy="FP",starting_move=None):
        super().__init__(pos, model)

        self.pos = pos
        self.stepCount = stepcount
        self.ID = self.model.agentIDs.pop(0)
        self.score = 0
        self.strategy = strategy
        self.previous_moves = []
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

    # pick a strategy - either by force, or by a decision mechanism
    def pick_strategy(self):
        """ This will later need more information coming into it - on what should I base my
        strategy selection? """
        if self.strategy is None:
            # decision mechanism goes here
            return

    def pick_move(self, strategy, payoffs):
        """ given the payoff matrix, the strategy, and any other inputs (communication, trust perception etc.)
            calculate the expected utility of each move, and then pick the highest"""
        """AT THE MOMENT, THIS IS A GENERAL ONCE-A-ROUND FUNCTION, AND ISN'T PER PARTNER - THIS NEEDS TO CHANGE """

        if strategy is None or [] or 0:
            print("I don't know what to do!")
        elif strategy == "ANGEL":
            # print("I'm an angel, so I'll cooperate")
            return "C"
        elif strategy == "DEVIL":
            # print("I'm a devil, so I'll defect")
            return "D"

        elif strategy == "FP":  # this is under assumption of heterogeneity of agents
            """ FP is designed as a strategy not based on 'trust' (though it can reflect that), but instead on 
            the logic; 'I know they know defect is the best strategy usually, just as they know I know that'. """
            # Current set-up: We assume partner will defect

            ppD = 0.8  # probability of partner's defection
            ppC = 0.2  # probability of partner's cooperation

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
                return "C"
            elif highest_eu == 1:
                # print("Cooperate is best")
                return "C"
            elif highest_eu == 2:
                # print("Defect is best")
                return "D"
            elif highest_eu == 3:
                # print("Defect is best")
                return "D"

    def check_partner(self):
        """ Check Partner looks at all the partner's current move selections and adds them to relevant memory spaces"""
        x, y = self.pos
        neighbouring_cells = [(x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)]  # N, E, S, W

        # First, get the neighbours
        for i in neighbouring_cells:
            bound_checker = self.model.grid.out_of_bounds(i)  # Is the cell not off the map?
            if not bound_checker:
                this_cell = self.model.grid.get_cell_list_contents([i])
                # print("This cell", this_cell)
                #
                if len(this_cell) > 0:
                    partner = [obj for obj in this_cell
                               if isinstance(obj, PDAgent)][0]

                    partner_ID = partner.ID
                    partner_score = partner.score
                    partner_strategy = partner.strategy
                    partner_move = partner.move
                    partner_moves = partner.previous_moves # ******** this could either be redundant or MORE EFFICIENT than the current way of doing things - this is accessing the other agent's own record of its moves

                    # Wanna add each neighbour's move, score etc. to the respective memory banks
                    if self.partner_latest_move.get(partner_ID) is None:
                        self.partner_latest_move[partner_ID] = partner_move
                    else:
                        self.partner_latest_move[partner_ID] = partner_move  # this is stupidly redundant but I don't have the current brain energy to fix it

                    if self.per_partner_utility.get(partner_ID) is None:
                        self.per_partner_utility[partner_ID] = 0

                    """Below needs uncommenting when I want to do multi-round memory"""
                    # First, check if we have a casefile on them in each memory slot
                    # if self.partner_moves.get(partner_ID) is None:  # if we don't have a casefile for this partner
                    #     self.partner_moves[partner_ID] = []
                    #     self.partner_moves[partner_ID][0] = partner_move
                    # else:
                    #     sublist_len = len(self.partner_moves[partner_ID])
                    #     self.partner_moves[partner_ID][sublist_len+1] = partner_move   # ****** I don't know if this needs to be len+1, just len might be more appropriate
                    #     print("My partner's moves have been:", self.partner_moves[partner_ID])
                    #     """ We should repeat the above process for the other memory fields too, like partner's gathered utility """

                    if partner_ID not in self.partner_IDs:
                        self.partner_IDs.append(partner_ID)

        print("Partner IDs: ", self.partner_IDs)
        print("Partner Latest Moves:", self.partner_latest_move)

    # increment the agent's score - for iterated games
    def increment_score(self, payoffs):
        my_move = self.move
        total_utility = 0

        for i in self.partner_IDs:
            this_partner_move = self.partner_latest_move[i]
            outcome = [my_move, this_partner_move]
            print("Outcome with partner %i was:" % i, outcome)

            outcome_payoff = payoffs[self.move, this_partner_move]
            current_partner_payoff = self.per_partner_utility[i]
            new_partner_payoff = current_partner_payoff + outcome_payoff
            self.per_partner_utility[i] = new_partner_payoff
            total_utility += outcome_payoff

        # self.score = self.score + total_utility
        print("My total overall score is:", self.score)
        return total_utility

        # Get Neighbours
        #             my_move = self.move
        #             outcome = [my_move, partner_move]  # what was the actual outcome

        #             print("Outcome: ", outcome)
        #             outcome_payoff = payoffs[self.move, partner_move]  # this might break # find out how much utility we got
        #             print("The outcome payoff is ", outcome_payoff)
        #             return outcome_payoff  # return the value to increment our current score by
        #         """ This will only work for one neighbour - when we have multiple neighbours,
        #         we will want to store them in a new list - where neighbour 0 has outcome-with-me 0
        #         in terms of indices. """
        #     else:
        #         return


    def step(self):
        """  So a step for our agents, right now, is to calculate the utility of each option and then pick? """
        if self.stepCount == 0:
            print(self.strategy)
            if self.strategy is None or 0 or []:
                self.strategy = self.pick_strategy()
                self.next_move = self.pick_move(self.strategy, self.payoffs)
                self.previous_moves.append(self.move)

                # to_increment = self.increment_score(self.payoffs)
                # print("My utility this round is ", to_increment)
                # self.score += to_increment

                if self.model.schedule_type != "Simultaneous":
                    self.advance()

                self.stepCount += 1
            else:
                self.next_move = self.pick_move(self.strategy, self.payoffs)
                print("My move is ", self.move)

                self.previous_moves.append(self.move)

                # to_increment = self.increment_score(self.payoffs)
                # print("My utility this round is ", to_increment)
                # self.score += to_increment

                if self.model.schedule_type != "Simultaneous":
                    self.advance()

                self.stepCount += 1
        else:
            self.next_move = self.pick_move(self.strategy, self.payoffs)
            print("My move is ", self.move)

            self.previous_moves.append(self.move)

            # to_increment = self.increment_score(self.payoffs)
            # print("My utility this round is ", to_increment)
            # self.score += to_increment

            if self.model.schedule_type != "Simultaneous":
                self.advance()

            self.stepCount += 1

    def advance(self):
        self.move = self.next_move
        self.check_partner()  # Check what all of our partners picked, so our knowledge is up-to-date
        round_payoff = self.increment_score(self.payoffs)
        if round_payoff is not None:
            self.score += round_payoff
            return
