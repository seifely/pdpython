def portrayPDAgent(agent):
    """ MESA Suggestion: Portraying agents in their current decision state, for the visualisation """
    assert agent is not None
    return {
        "Shape": "rect",
        "w": 1,
        "h": 1,
        "Filled": "true",
        "Layer": 0,
        "x": agent.pos[0],
        "y": agent.pos[1],
        "Color": "green" if agent.isCooroperating else "red"  # This will need to be altered when we start
        # diversifying behaviour
    }