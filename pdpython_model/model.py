from mesa import Model
from mesa.time import BaseScheduler, RandomActivation, SimultaneousActivation
from mesa.space import SingleGrid  # doesn't need to be multigrid as agent's aren't moving atop one another
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
                 payoffs,
                 height=1,
                 width=2,
                 schedule_type="Sequential",
                 spatialty=False):
        # super().__init__()  # This could be wrong - look at how you've structured it in boxworld. no super init

        self.grid = SingleGrid(width, height, torus=True)
        self.schedule_type = schedule_type
        self.payoffs = payoffs
        self.nagents = nagents

        self.spatiality = spatialty  # This isn't functioning properly right now
        # Spatial placement of agents would basically include scaling up the world depending on how many agents you want
        # Basically, increase agents by some fixed multiple, then scale up world to fit.
        # e.g. 40 agents, 20 x 20 world, 50 agents, 25 x 25 world etc.


        # Create the agents
        for i in range(self.nagents):
            x, y = self.grid.find_empty()  # Find an empty spot - this is used for the non-spatial version
            agent = PDAgent((x, y), self)  # Create the agent itself
            self.grid.place_agent(agent, (x, y))  # Place it in the world
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
