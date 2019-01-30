from mesa import Agent

# Stratgey Key:
    # ANGEL - Always Cooperate
    # DEVIL - Always Defect
    # FP - Fixed Probabilities, multiplying the payoff matrix by the likelihood of each outcome (dependant on other)


class PDAgent(Agent):
    """ Agent member of the iterated prisoner's dilemma model """

    def __init__(self, pos, model, starting_move=None, strategy=None):
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


        # pull in the payoff matrix (same for all agents IF WE ASSUME ALL AGENTS HAVE EQUAL PAYOFFS)
        self.payoffs = self.model.payoffs

        # pick a strategy - either by force, or by a decision mechanism
        def pick_strategy(self, strategy):
            if strategy is None:
                # decision mechanism goes here
                return


        # given the payoff matrix, the strategy, and any other inputs (communication, trust perception etc.)
        # calculate the expected utility of each move, and then pick the highest
        def pick_move(self, strategy, payoffs):

            if strategy is None or [] or 0:
                print("I don't know what to do!")
            elif strategy == "ANGEL":
                return "C"
            elif strategy == "DEVIL":
                return "D"

            elif strategy = "FP":  # this is under assumption of heterogeneity of agents
                """ FP is designed as a strategy not based on 'trust' (though it can reflect that), but instead on 
                the logic; 'I know they know defect is the best strategy usually, just as they know I know that'. """

                ppD = 0.8  # probability of partner's defection
                ppC = 0.2  # probability of partner's cooperation

                euCD = (payoffs["C, D"]




        # increment the agent's score - for iterated games
        def increment_score(self, current_score):




























        # if starting_move:
        #     self.move = starting_move
        # else:
        #     #  self.move = self.random.choice(["C", "D"])  # random behaviours - we don't want this
        #     return
        #
        # def pick_strategy(self, payoff):
        #     new_strategy = ""
        #     # bloo bloo pick strategy based on something
        #     return new_strategy
        #     # then need to set self.strategy to the new strategy
        #
        #
        # def pick_move(self, strategy, payoff):
        #     move = []
        #     if strategy == None:
        #         # pick_strategy(self, 1)
        #         return
        #     elif strategy == "ANGEL":
        #         return move == "C"
        #     elif strategy == "DEVIL":
        #         return move == "D"


        # @property # I AM NOT USED TO THIS SYNTAX BUT HEY LET'S TRY IT
        # def isCooperating(self):
        #     return self.move == "C"

        def increment_score

        def step(self):
            """  So a step for our agents, right now, is to calculate the utility of each option and then pick? """
            # if we were doing a spatial model, where agents looked at neighbours' choices, we would do:
            # neighbours = self.model.grid.get_neighbours(self.pos, True,
            #                                             include_center=True)
            # then whatever computation we want (finding out the best utility score out of all the neighbours and picking their strategy)

            #if stepcount = 0, pick a strategy (this is for simulation type 1)?

            # self.move = pick_move(self, self.strategy, self.model.payoff)?
            # self.increment_score


