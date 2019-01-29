from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.UserParam import UserSettableParameter

from .portrayal import portrayPDAgent
from .model import PDGrid


# World = 50 x 50, Display = 500 x 500
canvas_element = CanvasGrid(portrayPDAgent, 1, 2, 500, 500)  # Doesn't this need to work off hxw params?

model_params ={
    "height": 50,
    "width": 50,
    "schedule_type": UserSettableParameter("choice", "Scheduler Type", value="Sequential",
                                           choices=list(PDGrid.schedule_types.keys())),
    "number_agents": UserSettableParameter("slider", "Number of Agents", 2, 2, 2, 1)
    # "strategy_style"
    # "strategy_diversity"
}

server = ModularServer(PDGrid, [canvas_element], "Prisoner's Dilemma",
                       model_params)
