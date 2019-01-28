from mesa import Model
from mesa.time import BaseScheduler, RandomActivation, SimultaneousActivation
from mesa.space import SingleGrid # doesn't need to be multigrid as agent's aren't moving atop one another
from mesa.datacollection import DataCollector

from .agents import PDAgent

class PDGrid(Model):
    """ Initial goals for the model: Single Iteration Classic Strategy. Agents access the payoff matrix
        available to them, and then make a decision based on that. """

    nagents = 2
    payoffs = {}
    schedule_types = {"Sequential": BaseScheduler,
                      "Random": RandomActivation,
                      "Simultaneous": SimultaneousActivation}
    spatiality = False


    def __init__(self,
                 nagents,
                 height,
                 width,
                 payoffs,
                 schedule_type="Sequential",
                 spatialty=False):
        # super().__init__()  # This could be wrong - look at how you've structured it in boxworld. no super init

        self.grid = SingleGrid(width, height, torus=True)
        self.schedule_type = schedule_type
        self.payoffs = payoffs
        self.nagents = nagents

        self.spatiality = spatialty  # This isn't functioning properly right now
        # Actual spatial placement of agents (basically iterating through free grid cells) isn't happening
        # Below, but if we want it to we need to fix this/rewrite it ***

        if not self.spatiality:
            self.height = 50
            self.width = 50
        elif self.spatiality:
            self.height = nagents
            self.width = nagents

        # Create the agents
        for i in range(self.nagents):
            x, y = self.grid.find_empty()  # Find an empty spot - this is used for the non-spatial version
            agent = PDAgent((x, y), self)  # Create the agent itself
            self.grid.place_agent(agent, (x, y))
            self.schedule.add(agent)

        self.datacollector = DataCollector({
            "Cooperating Agents":
                lambda m: len([a for a in m.schedule.agents if a.move == "C"])
        })

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        """ Take a step in the model - equates to one round of decision making"""
        self.schedule.step()
        # collect the data needed
        self.datacollector.collect(self)

    def run(self, n):
        """ Run the model for n epochs - for the iterated Dilemma """
        for i in range(n):
            self.step()
