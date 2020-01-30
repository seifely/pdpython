from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule, TextElement
from mesa.visualization.UserParam import UserSettableParameter

from pdpython_model.agents import PDAgent
from pdpython_model.model import PDModel

# Green
RICH_COLOR = "#007f7f"
# Red
POOR_COLOR = "#ce0e2d"
# Blue
MID_COLOR = "#ffc0cb"

def gen_Model_Portrayal(agent):
    if agent is None:
        return

    portrayal = {}

    if type(agent) is PDAgent:
        portrayal = {"Shape": "circle",
                     "scale": 1,
                     # "Color": "white",
                     "Filled": "true",
                     "Layer": 1,
                     "r": 0.75,
                     "text": [agent.strategy, agent.score],
                     "text_color": "black",
                     "scale": 1
                     }

        color = MID_COLOR


        # set agent color based on savings and loans
        if agent.common_move == ["C"]:
            color = RICH_COLOR
        if agent.common_move == ["D"]:
            color = POOR_COLOR
        if agent.common_move == ["Eq"]:
            color = MID_COLOR

        portrayal["Color"] = color



        # if agent.strategy is None:
        #     portrayal = {"Shape": "circle",
        #                  "scale": 1,
        #                  "Color": "white",
        #                  "Filled": "true",
        #                  "Layer": 1,
        #                  "r": 0.75,
        #                  "text": [agent.common_move, agent.score],
        #                  "text_color": "black",
        #                  "scale": 1
        #                  }
        # elif agent.strategy == "ANGEL":
        #     portrayal = {"Shape": "circle",
        #                  "scale": 1,
        #                  "Color": "#ffe700",
        #                  "Filled": "true",
        #                  "Layer": 1,
        #                  "r": 0.75,
        #                  "text": [agent.common_move, agent.score],
        #                  "text_color": "#f08619",
        #                  "scale": 1
        #                  }
        # elif agent.strategy == "DEVIL":
        #     portrayal = {"Shape": "circle",
        #                  "scale": 1,
        #                  "Color": "#d52719",
        #                  "Filled": "true",
        #                  "Layer": 1,
        #                  "r": 0.75,
        #                  "text": [agent.common_move, agent.score],
        #                  "text_color": "#3e0400",
        #                  "scale": 1
        #                  }
        # elif agent.strategy == "EV":
        #     portrayal = {"Shape": "circle",
        #                  "scale": 1,
        #                  "Color": "#84f2cf",
        #                  "Filled": "true",
        #                  "Layer": 1,
        #                  "r": 0.75,
        #                  "text": [agent.common_move, agent.score],
        #                  "text_color": "#09806b",
        #                  "scale": 1
        #                  }
        # elif agent.strategy == "RANDOM":
        #     portrayal = {"Shape": "circle",
        #                  "scale": 1,
        #                  "Color": "grey",
        #                  "Filled": "true",
        #                  "Layer": 1,
        #                  "r": 0.75,
        #                  "text": [agent.common_move, agent.score],
        #                  "text_color": "white",
        #                  "scale": 1
        #                  }
        # elif agent.strategy == "VEV":
        #     portrayal = {"Shape": "circle",
        #                  "scale": 1,
        #                  "Color": "#008080",
        #                  "Filled": "true",
        #                  "Layer": 1,
        #                  "r": 0.75,
        #                  "text": [agent.common_move, agent.score],
        #                  "text_color": "#84f2cf",
        #                  "scale": 1
        #                  }
        # elif agent.strategy == "TFT":
        #     portrayal = {"Shape": "circle",
        #                  "scale": 1,
        #                  "Color": "#ffd0ef",
        #                  "Filled": "true",
        #                  "Layer": 1,
        #                  "r": 0.75,
        #                  "text": [agent.common_move, agent.score],
        #                  "text_color": "#f57694",
        #                  "scale": 1
        #                  }
        # elif agent.strategy == "WSLS":
        #     portrayal = {"Shape": "circle",
        #                  "scale": 1,
        #                  "Color": "#add8e6",
        #                  "Filled": "true",
        #                  "Layer": 1,
        #                  "r": 0.75,
        #                  "text": [agent.common_move, agent.score],
        #                  "text_color": "blue",
        #                  "scale": 1
        #                  }
        # elif agent.strategy == "VPP":
        #     portrayal = {"Shape": "circle",
        #                  "scale": 1,
        #                  "Color": "#003333",
        #                  "Filled": "true",
        #                  "Layer": 1,
        #                  "r": 0.75,
        #                  "text": [agent.common_move, agent.score],
        #                  "text_color": "#99cccc",
        #                  "scale": 1
        #                  }

    return portrayal


class StepCountDisplay(TextElement):

    def render(self, model):
        return "Step Count: " + str(model.step_count)


canvas_element = CanvasGrid(gen_Model_Portrayal, 8, 8, 500, 500)
step_element = StepCountDisplay()
# chart_element = ChartModule([{"Label": "Walkers", "Color": "#AA0000"},
#                              {"Label": "Closed Boxes", "Color": "#666666"}])

model_params = {"number_of_agents": UserSettableParameter('slider', 'Number of Agents', 64, 2, 64, 1),
                "rounds": UserSettableParameter('slider', 'Number of Rounds', 250,1,500,10),
                "collect_data": UserSettableParameter('checkbox', 'Collect Data', False),
                "agent_printing": UserSettableParameter('checkbox', 'Agent Printouts', False),
                "CC": UserSettableParameter('number', 'Payoff for C-C (Default: 3)', value=1.5),
                "CD": UserSettableParameter('number', 'Payoff for C-D (Default: 0)', value=-2),
                "DC": UserSettableParameter('number', 'Payoff for D-C (Default: 5)', value=2),
                "DD": UserSettableParameter('number', 'Payoff for D-D (Default: 2)', value=1),

                "simplified_payoffs": UserSettableParameter('checkbox', 'Simplified Payoffs', False),
                "b": UserSettableParameter('number', 'Simplified Payoffs: Benefit of Co-op', value=4),
                "c": UserSettableParameter('number', 'Simplified Payoffs: Cost of Co-op', value=1),

                }

chart_element = ChartModule([{"Label": "Cooperations", "Color": RICH_COLOR},
                             {"Label": "Defections", "Color": POOR_COLOR}])

server = ModularServer(PDModel, [canvas_element, step_element, chart_element], "Prisoner's Dilemma Simulation", model_params)
server.port = 8521
