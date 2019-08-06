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

        # Can store custom variables and settings here:
        self.hole_x_location = 17

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
        game_state.suppress_warnings(True)  #Comment this line to show warnings.

        self.emp_line_strategy(game_state)

        game_state.submit_turn()


    """
    NOTE: All the methods after this point are part of the sample starter-algo
    strategy and can safely be replaced for your custom algo.
    """
    def emp_line_strategy(self, game_state):
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
        filter_locations_x = [27, 24, 21, 18, 15, 12]
        for x in filter_locations_x:
            location = [x, 13]
            if game_state.can_spawn(FILTER, location):
                self.spawn_wrapper(game_state, FILTER, location)


        """
        We use Encryptors firewalls because they are cheap and give shields
        This will build the line that our EMPs will use to snipe.
        If they are destroyed we replace them with destructors.
        """
        encryptor_locations = []
        for x in range(26, 12, -1):
            # Because of the way pathing works don't need to build behind our Filters saving cores
            if x not in filter_locations_x and x != self.hole_x_location:
                encryptor_locations.append([x, 12])
        
        for location in encryptor_locations:
            if game_state.can_spawn(ENCRYPTOR, location):
                if game_state.turn_number < 2:
                    self.spawn_wrapper(game_state, ENCRYPTOR, location)
                else:
                    self.spawn_wrapper(game_state, DESTRUCTOR, location)


    def build_defences(self, game_state):
        # Build filters first
        filter_corner_locations = [[1,13],[3,13]]
        self.spawn_wrapper(game_state, FILTER, filter_corner_locations)

        # Then build destructors
        destructor_corner_locations = [[0,13],[1,12],[3,12]]
        self.spawn_wrapper(game_state, DESTRUCTOR, destructor_corner_locations)


    def deploy_attackers(self, game_state):
        # Spawn upto 100 EMPs at the location 25,11 every turn, if not many destructors spawn pings
        if self.detect_enemy_unit(game_state, DESTRUCTOR, valid_x=range(0,12), valid_y=range(14,18)) < 4:
            self.spawn_wrapper(game_state, PING, [25, 11], 100)
        else:
            self.spawn_wrapper(game_state, EMP, [25, 11], 100)

    def detect_enemy_unit(self, game_state, unit_type, valid_x = None, valid_y = None):
        total_destructors = 0
        for location in game_state.game_map:
            if game_state.contains_stationary_unit(location):
                for unit in game_state.game_map[location]:
                    if unit.player_index == 1 and unit.unit_type == unit_type and (valid_x is None or location[0] in valid_x) and (valid_y is None or location[1] in valid_y):
                        total_destructors += 1
        return total_destructors
        
    def filter_blocked_locations(self, locations, game_state):
        filtered = []
        for location in locations:
            if not game_state.contains_stationary_unit(location):
                filtered.append(location)
        return filtered

    def spawn_wrapper(self, game_state, unit_type, locations, num=1):
        # Can put code here like flip the x axis on all locations, or keep track of what you have spawned
        game_state.attempt_spawn(unit_type, locations, num)

if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
