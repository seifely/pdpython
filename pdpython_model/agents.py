from mesa import Agent
import random

class PDAgent(Agent):
    def __init__(self, pos, model, stepcount=0, strategy="FP",starting_move=None):
        super().__init__(pos, model)

        self.pos = pos
        self.stepCount = stepcount
        self.score = 0
        self.strategy = strategy
        self.move = None
        self.next_move = None
        if starting_move:
            self.move = starting_move
        else:
            self.move = self.random.choice(["C", "D"])

        self.payoffs = self.model.payoffs
        # pull in the payoff matrix (same for all agents IF WE ASSUME ALL AGENTS HAVE EQUAL PAYOFFS)

        # ------------------------ LOCAL MEMORY --------------------------
        # partner's moves (by position, read in order)
        # partner's scores
        self.previous_moves = []

    # pick a strategy - either by force, or by a decision mechanism
    def pick_strategy(self):
        """ This will later need more information coming into it - on what should I base my
        strategy selection? """
        if self.strategy is None:
            # decision mechanism goes here
            return

    # given the payoff matrix, the strategy, and any other inputs (communication, trust perception etc.)
    # calculate the expected utility of each move, and then pick the highest
    def pick_move(self, strategy, payoffs):

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
            print("EXPUTIL: ", exp_util)
            highest_eu = exp_util.index(max(exp_util))
            print("Highest EU: ", highest_eu)
            if highest_eu == 0:
                print("Cooperate is best")
                return "C"
            elif highest_eu == 1:
                print("Cooperate is best")
                return "C"
            elif highest_eu == 2:
                print("Defect is best")
                return "D"
            elif highest_eu == 3:
                print("Defect is best")
                return "D"

    # increment the agent's score - for iterated games
    def increment_score(self, payoffs):
        # Get Neighbours
        x, y = self.pos
        neighbouring_cells = [(x, y+1), (x+1, y), (x, y-1), (x-1, y)]  # N, E, S, W
        # --------------- THERE NEEDS TO BE AN IF X,Y IS IN RANGE ---------------------
        for i in neighbouring_cells:
            bound_checker = self.model.grid.out_of_bounds(i)
            if not bound_checker:
                this_cell = self.model.grid.get_cell_list_contents([i])

                if len(this_cell) > 0:
                    partner = [obj for obj in this_cell
                                   if isinstance(obj, PDAgent)][0]
                    partner_score = partner.score
                    partner.strategy = partner.strategy
                    partner_move = partner.move

                    my_move = self.move
                    outcome = [my_move, partner_move]  # what was the actual outcome
                    print("Outcome: ", outcome)
                    outcome_payoff = payoffs[self.move, partner_move]  # this might break # find out how much utility we got
                    print("The outcome payoff is ", outcome_payoff)
                    return outcome_payoff  # return the value to increment our current score by
                """ This will only work for one neighbour - when we have multiple neighbours,
                we will want to store them in a new list - where neighbour 0 has outcome-with-me 0
                in terms of indices. """
            else:
                return


    def step(self):
        """  So a step for our agents, right now, is to calculate the utility of each option and then pick? """
        if self.stepCount == 0:
            print(self.strategy)
            if self.strategy is None or 0 or []:
                self.strategy = self.pick_strategy()
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
        round_payoff = self.increment_score(self.payoffs)
        if round_payoff is not None:
            self.score += round_payoff
            return
