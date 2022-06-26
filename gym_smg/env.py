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

class SMGEnv:

    FREE: int = 0
    OBSTACLE: int = 1
    MOVES: dict[int,tuple] = {
        0: (0, 0), #STAY
        1: (-1, 0), #UP
        2: (1, 0), #DOWN
        3: (0, -1), #LEFT
        4: (0, 1) #RIGHT
    }

    def __init__(self,     
        #seed: Optional[int] = None,
        num_agents: int = None,
        starts_xy: list[tuple] = None,
        goals_xy: list[tuple] = None,
        disappear_on_goal: bool = True,
        map_name: str = None,
        custom_map: list[str] = None,
    ):
        # Grid confinguration
        self.n_agents = num_agents
        self.starts_xy = starts_xy
        self.goals_xy = goals_xy
        self.disappear_on_goal = disappear_on_goal
        self.map_name = map_name
        self.custom_map = custom_map

        # Environment configuration
        self.obstacles = self.parse_map()
        self.positions = self.initialise_positions()
        self.nrow, self.ncol = self.obstacles.shape
        self.action_space = ...
        self.observation_space = ...

        # Agent configuration
        self.agents_pos_xy = starts_xy
        self.dones = [self.on_goal for _ in range(self.n_agents)]
        self.infos = None

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

        TODO: add check on initial positions, they must not overlap with obstacles
        """
        positions = np.zeros(self.obstacles.shape, dtype=int)
        for x,y in self.starts_xy:
            if self.obstacles[x,y] == self.FREE:
                positions[x,y] = self.OBSTACLE
            else:
                raise ValueError(f"The agent in start position {(x,y)} overlaps with obstacles.")
        return positions

    def to_s(self, row: int, col: int) -> int:
        """
        Transform a (row, col) point to a state in the observation space.
        """
        return row * self.ncol + col

    def to_xy(self, s: int) -> tuple[int, int]:
        """
        Transform a state in the observation space to a (row, col) point.
        """
        return (s // self.ncol, s % self.ncol)

    def on_goal(self, agent_idx: int) -> bool:
        """
        Check if the agent is on the goal.
        """
        return self.agents_pos_xy[agent_idx] == self.goals_xy[agent_idx]

    def is_free(self, row: int, col: int) -> bool:
        """
        Check if a cell is free.
        """
        occupancy_map = self.obstacles + self.positions
        return occupancy_map[row, col] == self.FREE
    
    def is_in_bounds(self, row: int, col: int) -> bool:
        """
        Check if a cell is in bounds.
        """
        return 0 <= row < self.nrow and 0 <= col < self.ncol

    def move(self, agent_idx: int, action: int) -> None:
        """
        Move the agent in the given direction.
        """
        #assert action in self.action_space

        # Get the current position of the agent
        row, col = self.agents_pos_xy[agent_idx]
        dx, dy = self.MOVES[action]

        # Compute the target position of the agent
        target_row = row + dx
        target_col = col + dy

        # Check if the move is valid
        if not self.dones[agent_idx] and self.is_free(target_row, target_col) and self.is_in_bounds(target_row, target_col):
            self.positions[row, col] = self.FREE
            self.positions[target_row, target_col] = self.OBSTACLE
            self.agents_pos_xy[agent_idx] = (target_row, target_col)
            self.dones[agent_idx] = self.on_goal(agent_idx)
        
    def step(self, actions: list[int]):
        """
        Take a step in the environment.
        """
        for agent_idx, action in enumerate(actions):
            self.move(agent_idx, action)

        return self.agents_pos_xy, self.dones, self.infos

    def reset(self):
        """
        Reset the environment.
        """
        self.positions = self.initialise_positions()
        self.agents_pos_xy = self.starts_xy
        self.dones = [self.on_goal(agent_idx) for agent_idx in range(self.n_agents)]
        self.infos = None
        return self.agents_pos_xy, self.dones, self.infos
