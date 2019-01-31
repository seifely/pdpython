from mesa import Agent

# Stratgey Key:
    # ANGEL - Always Cooperate
    # DEVIL - Always Defect
    # FP - Fixed Probabilities, multiplying the payoff matrix by the likelihood of each outcome (dependant on other)


class PDAgent(Agent):
    """ Agent member of the iterated prisoner's dilemma model """

    def __init__(self, pos, model, starting_move=None, strategy='ANGEL'):
        """ Args:
                pos: (x, y), tuple of the agent's position.
                model: model instance
                starting_move: If provided, determines agent starting state: C or D.
                                Otherwise, random.

        """

        super().__init__(pos, model)
        self.pos = pos
        self.score = 0  # starting utility at zero
        self.strategy = strategy
        self.move = None
        self.previous_moves = []
        self.payoffs = self.model.payoffs
        self.stepcount = 0
        # pull in the payoff matrix (same for all agents IF WE ASSUME ALL AGENTS HAVE EQUAL PAYOFFS)

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
            print("I'm an angel, so I'll cooperate")
            return "C"
        elif strategy == "DEVIL":
            print("I'm a devil, so I'll defect")
            return "D"

        elif strategy == "FP":  # this is under assumption of heterogeneity of agents
            """ FP is designed as a strategy not based on 'trust' (though it can reflect that), but instead on 
            the logic; 'I know they know defect is the best strategy usually, just as they know I know that'. """
            # Current set-up: We assume partner will defect

            ppD = 0.8  # probability of partner's defection
            ppC = 0.2  # probability of partner's cooperation

            euCD = (payoffs["C", "D"] * ppD)
            euCC = (payoffs["C", "C"] * ppC)
            euDD = (payoffs["C", "D"] * ppD)
            euDC = (payoffs["D", "C"] * ppC)

            exp_util = (euCC, euCD, euDC, euDD)
            highest_eu = exp_util.index(max(exp_util))

            if exp_util[highest_eu] == euCD or euCC:
                return "C"
            elif exp_util[highest_eu] == euDD or euDC:
                return "D"

    # increment the agent's score - for iterated games
    def increment_score(self, payoffs):
        # get payoff matrix
        # ------- FIND THE OPPONENTS MOVE --------
        neighbors = self.model.grid.get_neighbors(self.pos, True,
                                                      include_center=False)
        print("fellow cool kids:", neighbors)
        for i in neighbors:
            partner_move = neighbors[i].move
            print("fellow cool kids' move:", partner_move)
            my_move = self.move
            outcome = [my_move, partner_move]  # what was the actual outcome
            outcome_payoff = payoffs[outcome]  # this might break # find out how much utility we got
            print("The outcome payoff is ", outcome_payoff)
            return outcome_payoff  # return the value to increment our current score by
        """ This will only work for one neighbour - when we have multiple neighbours,
        we will want to store them in a new list - where neighbour 0 has outcome-with-me 0
        in terms of indices. """

    # @property # I AM NOT USED TO THIS SYNTAX BUT HEY LET'S TRY IT
    # def isCooperating(self):
    #     return self.move == "C"

    def step(self):
        """  So a step for our agents, right now, is to calculate the utility of each option and then pick? """
        if self.stepcount == 0:
            print(self.strategy)
            if self.strategy is None or 0 or []:
                self.strategy = self.pick_strategy()
                self.move = self.pick_move(self.strategy, self.payoffs)
                print("My move is ", self.move)

                self.previous_moves.append(self.move)

                to_increment = self.increment_score(self.payoffs)
                print("My utility this round is ", to_increment)
                self.score += to_increment
            else:
                self.move = self.pick_move(self.strategy, self.payoffs)
                print("My move is ", self.move)

                self.previous_moves.append(self.move)

                to_increment = self.increment_score(self.payoffs)
                print("My utility this round is ", to_increment)
                self.score += to_increment




