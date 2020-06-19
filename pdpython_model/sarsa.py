import random


def init_qtable(states,n_actions):
    iqtable = {}   # does this want to be a list or a dict?

    for i in states:
        indx = tuple(i)
        vu = []
        for j in range(n_actions):
            vu.append(random.uniform(0.0, 1.0))
        iqtable[indx] = vu

    return iqtable


def egreedy_action(e, qtable, current_state):
    """ Qtable should be a dict keyed by the states - tuples of 7 values. """

    p = random.random()

    if p < e:
        return random.choice(['C', 'D'])
    else:
        # index qtable by current_state
        current = qtable[current_state]
        # pick the action with the highest Q value - if indx:0, C, if indx:1, D
        if current[0] > current[1]:
            return 'C'
        else:  # this might need to be an elif, but with two behaviours it's fine
            return 'D'


def sarsa(alpha, epsilon, gamma):
    # initialise q table

    return


def update_q(reward, gamma, alpha, oldQ, nextQ):
    """ Where nextQ is determined by the epsilon greedy choice that has already been made. """

    newQ = oldQ + alpha * (reward + ((gamma*nextQ) - oldQ))

    return newQ

