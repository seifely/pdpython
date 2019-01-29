from pdpython_model.agents import PDAgent

def portrayPDAgent(agent):
    """ MESA Suggestion: Portraying agents in their current decision state, for the visualisation """
    assert agent is not None
    # return {
    #     "Shape": "rect",
    #     "w": 1,
    #     "h": 1,
    #     "Filled": "true",
    #     "Layer": 0,
    #     "x": agent.pos[0],
    #     "y": agent.pos[1],
    #     "Color": "green" if agent.isCooroperating else "red"  # This will need to be altered when we start
    #     # diversifying behaviour
    # }  ^ this could be a more streamlined way of putting it, I'm not so familiar with @properties tho

    portrayal = {}

    if type(agent) is PDAgent:
        if agent.strategy == None:
            portrayal["Color"] = ["#00FF00", "#00CC00", "#009900"]
            portrayal["text"] = "I'm an Agent!"
        elif agent.strategy == "ANGEL":
            portrayal["Color"] = ["#84e184", "#adebad", "#d6f5d6"]
            portrayal["text"] = "I'm an Agent!"

        if agent.move == None:
            return
        # THIS NEEDS TO GO ON AND SO ON FOR EACH STRATEGY
        portrayal["Shape"] = "rect"
        portrayal["Filled"] = "true"
        portrayal["Layer"] = 0
        portrayal["w"] = 1
        portrayal["h"] = 1

    return portrayal

