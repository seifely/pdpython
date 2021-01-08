# pdpython
PhD Thesis Project on the Prisoner's Dilemma, implemented in Python 3.6

This project contains scripting using the Python library MESA (https://mesa.readthedocs.io/en/stable/) for simulating agents playing the Repeated Prisoner's Dilemma in a grid environemt.

UPDATE 08/01/21: The Master branch of this project does not include a functioning visualiser, and can only be used to run batch simulations that collect and export data via .csv files. 

TODO: Fix the visualiser to allow small batch testing and mid-test visualisation of variable changes, allowing for between-test alteration of starting variables.

# To Run Locally

- Ensure python is installed.
- Install the necessary libraries: mesa (pip install mesa), numpy and scipy (pip install numpy scipy), pandas (pip install pandas)
- If primarily testing standard SARSA agents against a variety of opponents, set the batch_run.py 'sarsa_spawn', 'sarsa_training' and 'sarsa_testing' variables to True 
- [CURRENTLY] Change the simulation variables in batch_run.py at the bottom of the script - br_params - so that uncommented lists contain the variable values wished to test
- [CURRENTLY] Change the csv filename variable around line 540 to a desired string, leaving the %s string replacements as is
- run the batch_run.py file to begin data collection

- By default, the simulation will run a 6x6 grid of 36 agents, and as long as the sarsa_distro variable is left untouched, these agents will spawn in a 'checkerboard' formation, where SARSA agents are pitted off against each strategy listed in the 'sarsa_oppo' br_params list

# Opponent Strategy Codes

- 'TFT' - Tit for Tat
- 'WSLS' - Win-Stay Lose-Shift
- 'DEVIL' - All-defectors
- 'ANGEL' - All-cooperators
- 'RANDOM' - Self-evident
- 'VPP' - Variable Personal Probability, a novel strategy designed by us that updates its probabilistic likelihood of defection incrementally based on observed behaviour
- 'SARSA' - The on-policy reinforcment learning algorithm, state-action-reward-state-action
