import numpy as np
from gym_smg.window import Window
import gym_smg.rendering as r

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
        agents_colors: list[str] = None,
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

        # Rendering configuration
        self.window = None
        self.agents_color = agents_colors
        self.tile_cache = {}
        self.fps = 10

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
        if not self.dones[agent_idx] and self.is_in_bounds(target_row, target_col) and self.is_free(target_row, target_col):
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

    def close(self):
        """
        Close the environment.
        """
        if self.window:
            self.window.close()
        return None

    def render(self, mode='human'):
        """
        Render the environment.
        """
        if mode == "human":
            return self.render_gui()
        else:
            raise ValueError(f"Unsupported rendering mode {mode}")
    
    def render_gui(self, tile_size=r.TILE_PIXELS, highlight_mask=None):
        """
        @NOTE: Once again, if agent position is (x,y) then, to properly 
        render it, we have to pass (y,x) to the grid.render method.

        tile_size: tile size in pixels
        """
        width = self.ncol
        height = self.nrow

        if highlight_mask is None:
            highlight_mask = np.zeros(shape=(width, height), dtype=bool)

        # Compute the total grid size
        width_px = width * tile_size
        height_px = height * tile_size

        img = np.zeros(shape=(height_px, width_px, 3), dtype=np.uint8)

        # Render grid with obstacles
        for x in range(self.nrow):
            for y in range(self.ncol):
                if self.obstacles[x,y] == self.OBSTACLE:
                    cell = r.Wall(color='black')
                    tile_img = self.render_tile(cell, tile_size=tile_size)
                else:
                    cell = None
                    tile_img = self.render_tile(cell, tile_size=tile_size)

                height_min = x * tile_size
                height_max = (x+1) * tile_size
                width_min = y * tile_size
                width_max = (y+1) * tile_size
                img[height_min:height_max, width_min:width_max, :] = tile_img

        # Render goals
        for agent_idx, (x, y) in enumerate(self.goals_xy):
            cell = r.Goal(color=self.agents_color[agent_idx])
            tile_img = self.render_tile(cell, tile_size=tile_size)
            height_min = x * tile_size
            height_max = (x+1) * tile_size
            width_min = y * tile_size
            width_max = (y+1) * tile_size
            img[height_min:height_max, width_min:width_max, :] = tile_img

        # Render agents
        for agent_idx, (x, y) in enumerate(self.agents_pos_xy):
            cell = r.Agent(color=self.agents_color[agent_idx])
            tile_img = self.render_tile(cell, tile_size=tile_size)
            height_min = x * tile_size
            height_max = (x+1) * tile_size
            width_min = y * tile_size
            width_max = (y+1) * tile_size
            img[height_min:height_max, width_min:width_max, :] = tile_img
            
        if not self.window:
            self.window = Window('my_custom_env')
            self.window.show(block=False)
        self.window.show_img(img, self.fps)

    def render_tile(
        self,
        obj: r.WorldObj,
        highlight=False,
        tile_size=r.TILE_PIXELS,
        subdivs=3
    ):
        """
        Render a tile and cache the result
        """

        # Hash map lookup key for the cache
        if not isinstance(obj, r.Agent):
            key = (None, highlight, tile_size)
            key = obj.encode() + key if obj else key

            if key in self.tile_cache:
                return self.tile_cache[key]

        img = np.zeros(shape=(tile_size * subdivs, tile_size * subdivs, 3), dtype=np.uint8) + 255

        if obj != None:
            obj.render(img)

        # Highlight the cell if needed
        if highlight:
            r.highlight_img(img)

        # Draw the grid lines (top and left edges)
        r.fill_coords(img, r.point_in_rect(0, 0.031, 0, 1), (170, 170, 170))
        r.fill_coords(img, r.point_in_rect(0, 1, 0, 0.031), (170, 170, 170))

        # Downsample the image to perform supersampling/anti-aliasing
        img = r.downsample(img, subdivs)

        # Cache the rendered tile
        if not isinstance(obj, r.Agent):
            self.tile_cache[key] = img

        return img

    def encode(self, vis_mask=None):
        """
        Produce a compact numpy encoding of the grid
        """
        width = self.ncol
        height = self.nrow

        if vis_mask is None:
            vis_mask = np.ones((width, height), dtype=bool)

        array = np.zeros((width, height, 3), dtype='uint8')

        for i in range(width):
            for j in range(height):
                if vis_mask[i, j]:
                    v = self.get(i, j)

                    if v is None:
                        array[i, j, 0] = r.OBJECT_TO_IDX['empty']
                        array[i, j, 1] = 0
                        array[i, j, 2] = 0

                    else:
                        array[i, j, :] = v.encode()

        return array

    # @staticmethod
    # def decode(array):
    #     """
    #     Decode an array grid encoding back into a grid
    #     """

    #     width, height, channels = array.shape
    #     assert channels == 3

    #     vis_mask = np.ones(shape=(width, height), dtype=bool)

    #     grid = SimpleGrid(width, height)
    #     for i in range(width):
    #         for j in range(height):
    #             type_idx, color_idx, state = array[i, j]
    #             v = WorldObj.decode(type_idx, color_idx, state)
    #             grid.set(i, j, v)
    #             vis_mask[i, j] = (type_idx != OBJECT_TO_IDX['unseen'])

    #     return grid, vis_mask
