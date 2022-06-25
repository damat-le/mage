from gym_smg.grid_config import GridConfig
import numpy as np

MAPS = {
    "4x4": ["EEEE", "EWEW", "EEEW", "WEEE"],
    "8x8": [
        "00000000",
        "00000000",
        "00010000",
        "00000100",
        "00010000",
        "01100010",
        "01001010",
        "00010000",
    ],
}

class Grid:

    FREE: int = 0
    OBSTACLE: int = 1
    MOVES: dict[int,tuple] = {
        0: (0, 0),
        1: (-1, 0),
        2: (1, 0),
        3: (0, -1),
        4: (0, 1)
    }

    def __init__(self,     
        #seed: Optional[int] = None,
        num_agents: int = None,
        starts_xy: list = None,
        goals_xy: list = None,
        disappear_on_goal: bool = True,
        map_name: str = None,
        custom_map: list= None,
    ):
        self.n_agents = num_agents
        self.starts_xy = starts_xy
        self.goals_xy = goals_xy
        self.disappear_on_goal = disappear_on_goal
        self.map_name = map_name
        self.custom_map = custom_map

        self.obstacles = self.parse_map()
        self.positions = self.initialise_positions()

    def parse_map(self) -> np.ndarray:
        """
        Initialise the grid.

        The grid is described by a map, i.e. a list of strings where each string dnotes a row of the grid and is a squence of 0s and 1s, where 0 denotes a free cell and 1 denotes a wall cell.

        The grid can be initialised by passing a map name or a custom map.
        If a map name is passed, the map is loaded from a set of pre-existing maps. If a custom map is passed, the map provided by the user is parsed and loaded.

        Examples
        --------
        >>> map = ["001", "010", "011]
        >>> SimpleGridEnv.parse_map()
        array([[0, 0, 1],
               [0, 1, 0],
               [0, 1, 1]])
        """
        if self.custom_map is not None:
            map_str = np.asarray(self.custom_map, dtype='c')
            map_int = np.asarray(map_str, dtype=int)
            return map_int
        if self.custom_map is None and self.map_name is None:
            raise ValueError("Either `map` or `map_name` must be provided in grid configuration.")
            #self.custom_map = generate_random_map()
            #return np.asarray(self.custom_map, dtype="c")
        if self.custom_map is None and self.map_name is not None:
            self.custom_map = MAPS[self.map_name]
            map_str = np.asarray(self.custom_map, dtype='c')
            map_int = np.asarray(map_str, dtype=int)
            return map_int
        
    def initialise_positions(self):
        """
        Initialise the positions of the agents.

        The output of this funtion is np.ndarray with the same shape as the grid. Each element of the array is 0, except for the elements corresponding to the agent positions that contain 1.
        """
        positions = np.zeros(self.obstacles.shape, dtype=int)
        for i in range(self.nA):
            x, y = self.gc.starts_xy[i]
            positions[x,y] = self.OBSTACLE
        return positions