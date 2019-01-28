from mesa import Agent


class PDAgent(Agent):
    """ Agent member of the iterated prisoner's dilemma model """

    def __init__(self, pos, model, starting_move=None):
        """ Args:
                pos: (x, y), tuple of the agent's position.
                model: model instance
                starting_move: If provided, determines agent starting state: C or D.
                                Otherwise, random.

        """

        super().__init__(pos, model)
        self.pos = pos
        self.score = 0  # starting utility at zero
        if starting_move:
            self.move = starting_move
        else:
            #  self.move = self.random.choice(["C", "D"])  # random behaviours - we don't want this
            return

        @property # I AM NOT USED TO THIS SYNTAX BUT HEY LET'S TRY IT
        def isCooperating(self):
            return self.move == "C"

        def step(self):
            """  So a step for our agents, right now, is to calculate the utility of each option and then pick? """
            # if we were doing a spatial model, where agents looked at neighbours' choices, we would do:
            # neighbours = self.model.grid.get_neighbours(self.pos, True,
            #                                             include_center=True)
            # then whatever computation we want (finding out the best utility score out of all the neighbours and picking their strategy)



