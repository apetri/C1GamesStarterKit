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

    #Declate some constants to avoid magic numbers
    CORES_REQUIRED = 34
    BITS_REQUIRED = 16
    LOW_HEALTH_THRESHHOLD = 7

    #The way we track cores last turn is one example of how to maintain a variable across multiple turns
    cores_last_turn = 0
    doomsday_device_active = False
    plan_b_active = False
    plan_b_initiated = False
    plan_b_encryptors = []
    plan_b_location = 0
    charging_up = False

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

        self.starter_strategy(game_state)

        game_state.submit_turn()

    """
    NOTE: All the methods after this point are part of the sample starter-algo
    strategy and can safely be replaced for your custom algo.
    """
    def starter_strategy(self, game_state):
        """
        This strategy is based around surviving and attempting to save resources, 
        then choosing an evil plan to close out the game
        """
        self.build_defences(game_state)

        if self.doomsday_device_active:
            self.GG(game_state)
        elif self.plan_b_active:
            self.plan_b(game_state)
        else:
            self.stall(game_state)


    def build_defences(self, game_state):
        primary_filters = [[0, 13], [3, 13], [8, 13], [19, 13], [24, 13], [27, 13]]
        primary_destructors = [[1, 12], [2, 12], [9, 12], [10, 12], [17, 12], [18, 12], [25, 12], [26, 12]]

        game_state.attempt_spawn(DESTRUCTOR, primary_destructors)
        game_state.attempt_spawn(FILTER, primary_filters)

        #If we haven't initiated an evil plan yet, lets figure out what to do...
        if not self.doomsday_device_active and not self.plan_b_active:
            cores = game_state.get_resource(game_state.CORES, 0)
            bits = game_state.get_resource(game_state.BITS, 0)
            gamelib.debug_write(f'We have {bits} bits and {cores} cores')
            if cores >= self.CORES_REQUIRED and bits >= self.BITS_REQUIRED:
                #We have everything we need! Activate the machine!
                gamelib.debug_write('The end is near!')
                self.doomsday_device_active = True
            elif cores < self.cores_last_turn or (cores < 5 and game_state.turn_number > 2) or game_state.my_health <= self.LOW_HEALTH_THRESHHOLD:
                gamelib.debug_write(f'Cores: {cores}, Cores last turn: {self.cores_last_turn}, ')
                gamelib.debug_write('Our plans are being thwarted, it\'s time for plan B!')
                self.plan_b_active = True
            else:
                gamelib.debug_write('Doomsday is averted...for now')

        secondary_destructors = [[19, 12], [24, 12], [23, 11], [24, 11], [20, 10], [22, 10], [23, 10]]
        secondary_filters = [[25, 13], [26, 13], [23, 12], [20, 11], [22, 11]]
        game_state.attempt_spawn(DESTRUCTOR, secondary_destructors)
        game_state.attempt_spawn(FILTER, secondary_filters)


    def stall(self, game_state):
        cores = game_state.get_resource(game_state.CORES, 0)
        if game_state.my_health < 28 and cores < self.CORES_REQUIRED * 0.75:
            gamelib.debug_write('We need more time! Sending some lackeys to stall!')

            #Send out 2 lackeys
            game_state.attempt_spawn(SCRAMBLER, [5, 8], 1)
            game_state.attempt_spawn(SCRAMBLER, [22, 8], 1)
            
            bottom_left_locations = game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_LEFT)
            bottom_right_locations = game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)
            possilbe_locations = bottom_left_locations + bottom_right_locations

            #Send out 2 random lackies to stall the game
            if game_state.my_health < 20:
                gamelib.debug_write('One last line of defence!')
                emergency_destructors = [[23, 12], [23, 11], [4, 12], [4, 11], [13, 8], [14, 8]]
                emergency_filters = [[12, 8], [15, 8]]
                game_state.attempt_spawn(DESTRUCTOR, emergency_destructors, 1)
                game_state.attempt_spawn(FILTER, emergency_filters, 1)
                for _ in range(2):
                    random_index = random.randrange(0, len(possilbe_locations))
                    game_state.attempt_spawn(SCRAMBLER, possilbe_locations[random_index])


    def plan_b(self, game_state):
        gamelib.debug_write('Its now or never!')
        '''
            Our alternative plan is to find the safest path,
            And surround it with as many encryptors as is possible
        '''
        #One-time setup for plan B, choose a location we will attack from
        if not self.plan_b_initiated:
            self.plan_b_initiated = True
            bottom_left_locations = game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_LEFT)
            bottom_right_locations = game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)
            possilbe_locations = bottom_left_locations + bottom_right_locations
            self.possilbe_locations = possilbe_locations

            best_choice = possilbe_locations[0]
            best_danger = math.inf
            
            # Keep track of location danger scores
            start_location_dangers = {}

            for n,location in enumerate(possilbe_locations):
                if game_state.game_map[location]: #If this location is blocked, we skip it
                    continue
                if location[0] <= 13:
                    target_edge = game_state.game_map.TOP_RIGHT
                else: 
                    target_edge = game_state.game_map.TOP_LEFT
                path = game_state.find_path_to_edge(location, target_edge)
                path_danger = 0

                #Make sure the current path we are looking at ends at a location we can score, and starts in the back of our territory
                score_locations = game_state.game_map.get_edge_locations(target_edge)
                if path[-1] in score_locations and path[0][1] < 4:
                    for path_location in path:
                        #As a rough measure of path danger, check how many destructors we pass near
                        for i in range(3):
                            for j in range(3):
                                units_at_location = game_state.game_map[path_location[0] - 1 + i, path_location[0] - 1 + j]
                                if units_at_location:
                                    for unit in units_at_location:
                                        if unit.unit_type == DESTRUCTOR:
                                            path_danger += 1

                    start_location_dangers[n] = path_danger

                    if path_danger < best_danger:
                        best_choice = location
                        best_danger = path_danger

                else:
                    start_location_dangers[n] = math.inf
                

            #Sort locations in ascending order of danger (less danger is best)
            self.locations_sorted = sorted(start_location_dangers,key=start_location_dangers.get)
            self.dangers_sorted = [ start_location_dangers[i] for i in self.locations_sorted ]
            self.try_locations = [ x for x in self.locations_sorted if not start_location_dangers[x]==math.inf ]


#            best_path = game_state.find_path_to_edge(best_choice, target_edge)
#            self.plan_b_location = best_choice

#            for tile in best_path[0:4]:
                    #As a rough measure of path danger, check how many destructors we pass near
#                    for i in range(3):
#                        for j in range(3):
#                            check_tile = [tile[0] - 1 + i, tile[1] - 1 + j]
#                            if check_tile not in best_path:
#                                self.plan_b_encryptors.append(check_tile)
        
        #After initializing, each successive time... activate plan B!
        if not self.charging_up:

            #game_state.attempt_spawn(ENCRYPTOR, self.plan_b_encryptors)
            
            N = len(self.try_locations)
            for iloc in self.try_locations:
                nping = game_state.number_affordable(PING)
                game_state.attempt_spawn(PING,self.possilbe_locations[iloc],nping//min(N,nping)) 
            
            self.charging_up = True
        

        else:
            #We only fire our attack every other turn
            self.charging_up = False

    def filter_blocked_locations(self, locations, game_state):
        filtered = []
        for location in locations:
            if not game_state.contains_stationary_unit(location):
                filtered.append(location)
        return filtered

    #################################################################################################
    #################################################################################################
    
    def GG(self, game_state):
        '''
        Thats alot of points! 
        You can get a copy a large number of points like this using community created tool like this one: 
        https://www.kevinbai.design/terminal-map-maker 
        '''
        if not self.charging_up:
            bottom_left_locations = game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_LEFT)
            bottom_right_locations = game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)
            possilbe_locations = bottom_left_locations + bottom_right_locations
            self.possilbe_locations = possilbe_locations

            best_choice = possilbe_locations[0]
            best_danger = math.inf
            
            # Keep track of location danger scores
            start_location_dangers = {}

            for n,location in enumerate(possilbe_locations):
                if game_state.game_map[location]: #If this location is blocked, we skip it
                    continue
                if location[0] <= 13:
                    target_edge = game_state.game_map.TOP_RIGHT
                else: 
                    target_edge = game_state.game_map.TOP_LEFT
                path = game_state.find_path_to_edge(location, target_edge)
                path_danger = 0

                #Make sure the current path we are looking at ends at a location we can score, and starts in the back of our territory
                score_locations = game_state.game_map.get_edge_locations(target_edge)
                if path[-1] in score_locations and path[0][1] < 4:
                    for path_location in path:
                        #As a rough measure of path danger, check how many destructors we pass near
                        for i in range(3):
                            for j in range(3):
                                units_at_location = game_state.game_map[path_location[0] - 1 + i, path_location[0] - 1 + j]
                                if units_at_location:
                                    for unit in units_at_location:
                                        if unit.unit_type == DESTRUCTOR:
                                            path_danger += 1

                    start_location_dangers[n] = path_danger

                    if path_danger < best_danger:
                        best_choice = location
                        best_danger = path_danger


                else:
                    start_location_dangers[n] = math.inf

            best_path = game_state.find_path_to_edge(best_choice, target_edge)
            self.plan_b_location = best_choice

            for tile in best_path[0:4]:
                for i in range(3):
                    for j in range(3):
                        check_tile = [tile[0] - 1 + i, tile[1] - 1 + j]
                        if check_tile not in best_path:
                            self.plan_b_encryptors.append(check_tile)

            game_state.attempt_spawn(ENCRYPTOR, self.plan_b_encryptors)
            game_state.attempt_spawn(PING, best_path[0], 666)

            # the_blueprint = [[7, 7], [8, 7], [10, 7], [11, 7], [12, 7], [13, 7], [14, 7], [15, 7], [16, 7], [7, 6], [8, 6], 
            # [10, 6], [11, 6], [12, 6], [13, 6], [14, 6], [15, 6], [16, 6], [17, 6], [8, 5], [17, 5], [18, 5], [9, 4], [10, 4], 
            # [11, 4], [12, 4], [13, 4], [14, 4], [15, 4], [17, 4], [18, 4], [10, 3], [11, 3], [12, 3], [13, 3], [14, 3], [15, 3], 
            # [17, 3], [11, 2], [12, 2], [12, 1], [14, 1], [15, 1]]
            # game_state.attempt_spawn(ENCRYPTOR, the_blueprint)
            # game_state.attempt_spawn(PING, [14,0], 666) #Attempt to spawn 666 pings at this location. The boss prefers to aim high.
            self.charging_up = True
        else:
            self.charging_up = False



if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
