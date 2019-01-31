from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.UserParam import UserSettableParameter

# from pdpython_model.fixed_model.agents import PDAgent
# from pdpython_model.fixed_model.model import PDGrid

def portrayPDAgent(agent):
    if agent is None:
        return

    portrayal = {}

    if type(agent) is PDAgent:
        portrayal["Shape"] = "circle",
        portrayal["scale"]= 1,
        portrayal["Filled"]= "true",
        portrayal["Layer"]= 1,
        portrayal["r"]= 0.5,
        # portrayal["text"]= "ᕕ( ՞ ᗜ ՞ )ᕗ",
        portrayal["text_color"]= "black",
        portrayal["scale"]= 1

        if agent.strategy == "ANGEL":
            portrayal["Color"] = "yellow",
            portrayal["text"] = agent.move, agent.score
        elif agent.strategy == "DEVIL":
            portrayal["Color"] = "red",
            portrayal["text"] = agent.move, agent.score
        else:
            portrayal["Color"] = "black"

    return portrayal

# World = 50 x 50, Display = 500 x 500
canvas_element = CanvasGrid(portrayPDAgent, 1, 2, 500, 500)  # Doesn't this need to work off hxw params?

model_params ={
    "height": 50,
    "width": 50,
    "schedule_type": UserSettableParameter("choice", "Scheduler Type", value="Sequential",
                                           choices=list(PDGrid.schedule_types.keys())),
    # "number_agents": UserSettableParameter("slider", "Number of Agents", 2, 2, 2, 1)
    # "strategy_style"
    # "strategy_diversity"
}

server = ModularServer(PDGrid, [canvas_element], "Prisoner's Dilemma",
                       model_params)
