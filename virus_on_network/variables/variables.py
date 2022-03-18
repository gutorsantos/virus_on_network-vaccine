# Get the number of individuals with a certain state
def number_state(model, state):
    return sum(1 for a in model.grid.get_all_cell_contents() if a.state is state)