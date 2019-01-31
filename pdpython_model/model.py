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

    schedule_types = {"Sequential": BaseScheduler,
                      "Random": RandomActivation,
                      "Simultaneous": SimultaneousActivation}

    def __init__(self, height=5, width=5,
                 number_of_agents=1,
                 schedule_type="Random", ):

        # Model Parameters
        self.height = height
        self.width = width
        self.number_of_agents = number_of_agents
        self.step_count = 0
        self.schedule_type = schedule_type

        # Model Functions
        self.schedule = self.schedule_types[self.schedule_type](self)
        self.grid = SingleGrid(self.height, self.width, torus=True)

        self.make_agents()
        self.running = True

    def make_agents(self):
        for i in range(self.number_of_agents):
            x, y = self.grid.find_empty()
            pdagent = PDAgent((x, y), self, True)
            self.grid.place_agent(pdagent, (x, y))
            self.schedule.add(pdagent)
            print("agent added")

    def step(self):
        self.schedule.step()
        self.step_count += 1

    def run_model(self, rounds=1):
        for i in range(rounds):
            self.step()

    # def __init__(self,
    #              nagents=4,
    #              payoffs={("C", "C"): 3,
    #           ("C", "D"): 0,
    #           ("D", "C"): 5,
    #           ("D", "D"): 2},
    #              rounds=1,
    #              height=1,
    #              width=2,
    #              schedule_type="Sequential",
    #              spatialty=False):
    #
    #     self.grid = SingleGrid(width, height, torus=True)
    #     self.schedule_type = schedule_type
    #     self.schedule = self.schedule_types[self.schedule_type](self)
    #     self.payoffs = payoffs
    #     self.nagents = nagents
    #     self.rounds = rounds
    #
    #     # Create the agents
    #     for i in range(self.nagents):
    #         x, y = self.grid.find_empty()  # Find an empty spot - this is used for the non-spatial version
    #         agent = PDAgent((x, y), self)  # Create the agent itself
    #         self.grid.place_agent(agent, (x, y))  # Place it in the world
    #         self.schedule.add(agent)
    #         print("Agent Spawned")
    #
    #     # Collect Data
    #     # on agent utilities? (or on utility per strategy?)
    #     """ We could collect data on:
    #         Number of Agents in Each Strat
    #         Total Utility Achieved """
    #
    #     self.running = True
    #     # self.datacollector.collect(self)
    #
    # def step(self):
    #     """ Take a step in the model - equates to one round of decision making"""
    #     self.schedule.step()
    #     # self.datacollector.collect(self)  # collect data
    #
    # def run(self, rounds):
    #     """ Run the model for n epochs - for the iterated Dilemma """
    #     for i in range(rounds):
    #         self.step()
