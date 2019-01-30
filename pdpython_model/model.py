from mesa import Model
from mesa.time import BaseScheduler, RandomActivation, SimultaneousActivation
from mesa.space import SingleGrid  # doesn't need to be multigrid as agent's aren't moving atop one another
from mesa.datacollection import DataCollector

from .agents import PDAgent


class PDGrid(Model):
    """ Initial goals for the model: Single Iteration Classic Strategy. Agents access the payoff matrix
        available to them, and then make a decision based on that. """

    nagents = 2
    # where first column is relevant to current agent accessing matrix, and the result is when it is combined w/ partner
    # if I pick C and they defect, I lose, whereas if they pick C and I defect, I win
    payoffs = {("C", "C"): 3,
              ("C", "D"): 0,
              ("D", "C"): 5,
              ("D", "D"): 2}
    schedule_types = {"Sequential": BaseScheduler,
                      "Random": RandomActivation,
                      "Simultaneous": SimultaneousActivation}
    spatiality = False
    rounds = 1

    def __init__(self,
                 nagents,
                 payoffs,
                 rounds,
                 height=1,
                 width=2,
                 schedule_type="Sequential",
                 spatialty=False):

        self.grid = SingleGrid(width, height, torus=True)
        self.schedule_type = schedule_type
        self.payoffs = payoffs
        self.nagents = nagents
        self.rounds = rounds

        # Create the agents
        for i in range(self.nagents):
            x, y = self.grid.find_empty()  # Find an empty spot - this is used for the non-spatial version
            agent = PDAgent((x, y), self)  # Create the agent itself
            self.grid.place_agent(agent, (x, y))  # Place it in the world
            self.schedule.add(agent)

        # Collect Data
        # on agent utilities? (or on utility per strategy?)

        self.running = True
        # self.datacollector.collect(self)

    def step(self):
        """ Take a step in the model - equates to one round of decision making"""
        self.schedule.step()
        # self.datacollector.collect(self)  # collect data

    def run(self, rounds):
        """ Run the model for n epochs - for the iterated Dilemma """
        for i in range(rounds):
            self.step()
