import gamelib
import random
import math
import warnings
from sys import maxsize

"""
Most of the algo code you write will be in this file unless you create new
modules yourself. Start by modifying the 'on_turn' function.

Advanced strategy tips: 

Additional functions are made available by importing the AdvancedGameState 
class from gamelib/advanced.py as a replacement for the regular GameState class 
in game.py.

You can analyze action frames by modifying algocore.py.

The GameState.map object can be manually manipulated to create hypothetical 
board states. Though, we recommended making a copy of the map to preserve 
the actual current map state.
"""

class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        random.seed()

    def on_game_start(self, config):
        """ 
        Read in config and perform any initial setup here 
        """
        gamelib.debug_write('Configuring your custom algo strategy...')
        self.config = config
        global FILTER, ENCRYPTOR, DESTRUCTOR, PING, EMP, SCRAMBLER
        FILTER = config["unitInformation"][0]["shorthand"]
        ENCRYPTOR = config["unitInformation"][1]["shorthand"]
        DESTRUCTOR = config["unitInformation"][2]["shorthand"]
        PING = config["unitInformation"][3]["shorthand"]
        EMP = config["unitInformation"][4]["shorthand"]
        SCRAMBLER = config["unitInformation"][5]["shorthand"]


    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        game_state = gamelib.GameState(self.config, turn_state)
        gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_state.turn_number))
        game_state.suppress_warnings(True)  #Uncomment this line to suppress warnings.

        self.ping_rush_strategy(game_state)

        game_state.submit_turn()

    """
    NOTE: All the methods after this point are part of the sample starter-algo
    strategy and can safely be replaced for your custom algo.
    """
    def ping_rush_strategy(self, game_state):
        """
        Build the EMP line.
        """
        self.build_basic_base(game_state)

        """
        Build corner defense.
        """
        self.build_defences(game_state)

        """
        Finally deploy our information units to attack.
        """
        self.deploy_attackers(game_state)

    # Here we make the C1 Logo!
    def build_basic_base(self, game_state):
        """
        Build the filters in front, build these first to defend the fragile encyrptor units behind them
        """
        filter_locations = [[4,11]]
        for location in filter_locations:
            if game_state.can_spawn(FILTER, location):
                self.spawn_wrapper(game_state, FILTER, location)

        """
        We use Encryptors firewalls because they are cheap and give shields
        This will build the line that will boost our pings and rush a corner
        """
        encryptor_locations = [[4, 11], [5, 10], [6, 9], [7, 8], [20, 8], [21, 8], [22, 8], [8, 7], [19, 7], [9, 6], [18, 6], [10, 5], [17, 5], [11, 4], [16, 4], [12, 3], [15, 3], [13, 2], [14, 2]]
        for location in encryptor_locations:
            if game_state.can_spawn(ENCRYPTOR, location):
                self.spawn_wrapper(game_state, ENCRYPTOR, location)

        

    def build_defences(self, game_state):
        corner_filter_locations = [[25,13], [21,11]]
        corner_destructor_locations = [[21, 10], [22, 10], [23, 10], [24, 10]]
        corner_encryptor_locations = [[27,13], [26,12], [25,11]]

        total_cost = self.calculate_cost(game_state, FILTER, corner_filter_locations) + self.calculate_cost(game_state, DESTRUCTOR, corner_destructor_locations) + self.calculate_cost(game_state, ENCRYPTOR, corner_encryptor_locations)

        if total_cost <= game_state.get_resource(game_state.CORES):
            self.spawn_wrapper(game_state, FILTER, corner_filter_locations)
            self.spawn_wrapper(game_state, DESTRUCTOR, corner_destructor_locations)
            self.spawn_wrapper(game_state, ENCRYPTOR, corner_encryptor_locations)
        

    def deploy_attackers(self, game_state):
        # Spawn upto 100 EMPs at the location 25,11 every turn
        """
        First lets check if we have 10 bits, if we don't we lets wait for 
        a turn where we do.
        """
        if (game_state.get_resource(game_state.BITS) < 10):
            return
        
        self.spawn_wrapper(game_state, PING, [21, 7], 100)
        
        
    def filter_blocked_locations(self, locations, game_state):
        filtered = []
        for location in locations:
            if not game_state.contains_stationary_unit(location):
                filtered.append(location)
        return filtered

    def spawn_wrapper(self, game_state, unit_type, locations, num=1):
        game_state.attempt_spawn(unit_type, locations, num)

    def calculate_cost(self, game_state, unit_type, locations, num=1):
        if type(locations[0]) == int:
            locations = [locations]
        total_cost = 0
        for location in locations:
            if not game_state.contains_stationary_unit(location):
                total_cost += game_state.type_cost(unit_type) * num
        return total_cost

    

if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
