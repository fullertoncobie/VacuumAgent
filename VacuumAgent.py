import heapq
from typing import Tuple, Dict, List, Optional, Set
from VacuumSettings import VacuumSettings
from Direction import Direction
from Environment import Environment

class VacuumAgent:
    """
    Autonomous vacuum cleaner agent that navigates and cleans an environment.
    Uses sensors, memory, and decision-making algorithms to clean efficiently.
    """
    def __init__(self, settings: VacuumSettings):
        """Initialize agent with operational settings."""
        # Position and orientation
        self.position = (0, 0)
        self.direction = Direction.NORTH
        
        # Settings and resources
        self.settings = settings
        self.power_consumed = 0
        
        # Memory and navigation
        self.directions = [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]
        self.cleaned_cells = set()  
        self.dirty_cells = set()    
        self.map = {}               # Known environment information
        self.visited_cells = []     
        self.last_visit_time = {}   
        self.visit_count = {}       
        
        self.time = 0 
        self.current_path = None   

    # ---- Movement Methods ----
    
    def rotate(self, target_direction: Direction):
        """Rotate to face target direction and update power consumption."""
        current_angle = self.direction.angle
        target_angle = target_direction.angle
        
        # Calculate shortest rotation path
        diff = (target_angle - current_angle) % 360
        if diff > 180:
            diff -= 360
            
        # Update power and direction
        rotations = abs(diff) / 90
        self.power_consumed += rotations * self.settings.rotation_power
        self.direction = target_direction

    def move_forward(self, env: Environment) -> bool:
        """
        Move forward one cell in current direction.
        Returns True if successful, False otherwise.
        """
        new_pos = (
            self.position[0] + self.direction.movement_vector[0],
            self.position[1] + self.direction.movement_vector[1]
        )
    
        # Check if new position is valid
        if env.get_cell(*new_pos):
            self.position = new_pos
            self.power_consumed += self.settings.move_power
            return True
            
        if self.settings.verbose:
            print("Cannot move forward: No valid cell ahead")
        return False
    
    # ---- Sensing Methods ----
    
    def sense_height(self, env: Environment, sensor_position: str) -> Optional[int]:
        """Sense height delta in a direction relative to the agent."""
        self.power_consumed += self.settings.sensor_power
        
        current_cell = env.get_cell(*self.position)
        if not current_cell:
            return None
            
        if sensor_position == 'forward':
            return current_cell[self.direction.delta_key]
        elif sensor_position == 'left':
            return current_cell[self.direction.left.delta_key]
        elif sensor_position == 'right':
            return current_cell[self.direction.right.delta_key]
        
        return None
    
    def sense_dust(self, env: Environment, sensor_position: str) -> Optional[Tuple[Tuple[int, int], float]]:
        """
        Sense dust weight at a position relative to the agent.
        Returns ((x,y), dust_weight) or None if not available.
        """
        # Check current position
        if sensor_position == 'current':
            # Use cached data if available
            if self.position in self.map and 'dust_weight' in self.map[self.position]:
                return (self.position, self.map[self.position]['dust_weight'])
            
            # Otherwise use sensor
            cell = env.get_cell(*self.position)
            self.power_consumed += self.settings.sensor_power
            return (self.position, cell['dust_weight']) if cell else None

        # Check relative position
        move_vector = self.direction.get_relative_position(sensor_position)
        if not move_vector:
            return None
            
        target_x = self.position[0] + move_vector[0]
        target_y = self.position[1] + move_vector[1]
        target_pos = (target_x, target_y)
        
        # Use cached data if available
        if target_pos in self.map and 'dust_weight' in self.map[target_pos]:
            return (target_pos, self.map[target_pos]['dust_weight'])
        
        # Otherwise use sensor
        self.power_consumed += self.settings.sensor_power
        cell = env.get_cell(target_x, target_y)        
        return ((target_x, target_y), cell['dust_weight']) if cell else None

    # ---- Cleaning Methods ----
    
    def suck_dust(self, env: Environment, pressure: str):
        """Clean current cell with specified pressure level (normal/heavy)."""
        # Only consume power if not already cleaned
        if self.position not in self.cleaned_cells:
            vacuum_power_attr = f"{pressure}_vacuum_power"
            self.power_consumed += getattr(self.settings, vacuum_power_attr)
            
            # Apply suction to environment
            env.get_sucked(*self.position, self.settings.MAX_SUCTION_WEIGHT[pressure])

    # ---- Memory and Mapping ----
    
    def update_memory(self, env: Environment):
        """Update agent's memory with current sensor readings."""
        # Update time and visit tracking
        self.time += 1
        self.last_visit_time[self.position] = self.time
        self.visit_count[self.position] = self.visit_count.get(self.position, 0) + 1

        # Record visit if first time
        if self.position not in self.visited_cells:
            self.visited_cells.append(self.position)
        
        # Get current cell info
        current_cell_info = self.sense_dust(env, 'current')
        
        if current_cell_info:
            position, dust_weight = current_cell_info
            
            # Initialize map entry if needed
            if self.position not in self.map:
                self.map[self.position] = {}
                
            # Update dust and cleaning info
            self.map[self.position]['dust_weight'] = dust_weight
            self.map[self.position]['cleaned'] = dust_weight == 0
            
            # Sense heights in all directions
            for direction in ['forward', 'left', 'right']:
                height = self.sense_height(env, direction)
                if height is not None:
                    if direction == 'forward':
                        self.map[self.position][self.direction.delta_key] = height
                    elif direction == 'left':
                        self.map[self.position][self.direction.left.delta_key] = height
                    elif direction == 'right':
                        self.map[self.position][self.direction.right.delta_key] = height
            
            # Update dirty/clean cell sets
            if dust_weight > 0:
                self.dirty_cells.add(self.position)
            elif self.position in self.dirty_cells and dust_weight == 0:
                self.dirty_cells.remove(self.position)
                self.cleaned_cells.add(self.position)
        
        # Sense adjacent cells
        for sensor_position in ['forward', 'left', 'right']:
            adjacent_info = self.sense_dust(env, sensor_position)
            
            if adjacent_info:
                position, dust_weight = adjacent_info
                
                move_vector = self.direction.get_relative_position(sensor_position)
                if not move_vector:
                    continue

                # Update map for adjacent cell
                if position not in self.map:
                    self.map[position] = {}
                
                self.map[position]['dust_weight'] = dust_weight
                self.map[position]['cleaned'] = dust_weight == 0
                
                # Update dirty/clean cell sets for adjacent cell
                if dust_weight > 0:
                    self.dirty_cells.add(position)
                elif position in self.dirty_cells and dust_weight == 0:
                    self.dirty_cells.remove(position)
                    self.cleaned_cells.add(position)
    
    # ---- Pathfinding Methods ----
    
    def manhattan_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """Calculate Manhattan distance between two positions."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def find_path_to_dirt(self, env: Environment) -> Optional[List[Direction]]:
        """Find path to closest dirty cell using A* pathfinding."""
        if not self.dirty_cells:
            return None
        
        # Find closest dirty cell
        closest_dirt = None
        min_distance = float('inf')
        
        for dirt_pos in self.dirty_cells:
            distance = self.manhattan_distance(self.position, dirt_pos)
            if distance < min_distance:
                min_distance = distance
                closest_dirt = dirt_pos
        
        if closest_dirt:
            path = self.a_star_pathfind(closest_dirt)
            return path
        
        return None

    def a_star_pathfind(self, target_pos: Tuple[int, int]) -> Optional[List[Direction]]:
        """A* pathfinding algorithm to find path to target position."""
        # Initialize data structures
        open_set = []
        in_open_set = {}
        closed_set = set()
        
        g_score = {self.position: 0}
        f_score = {self.position: self.manhattan_distance(self.position, target_pos)}
        came_from = {}
        
        # Start from current position
        heapq.heappush(open_set, (f_score[self.position], self.position))
        in_open_set[self.position] = True
        
        while open_set:
            _, current_pos = heapq.heappop(open_set)
            in_open_set.pop(current_pos, None)
            
            # Check if reached target
            if current_pos == target_pos:
                return self.reconstruct_path(came_from, current_pos)
            
            closed_set.add(current_pos)
            
            # Check all possible directions
            for next_dir in self.directions:
                next_pos = (
                    current_pos[0] + next_dir.movement_vector[0],
                    current_pos[1] + next_dir.movement_vector[1]
                )
                
                # Skip if already evaluated
                if next_pos in closed_set:
                    continue
                    
                # Skip if not in map
                if next_pos not in self.map:
                    continue
                
                # Skip if height delta unknown
                if next_dir.delta_key not in self.map[current_pos]:
                    continue
                    
                # Skip if height difference too large
                height_diff = self.map[current_pos][next_dir.delta_key]
                if abs(height_diff) > self.settings.MAX_SAFE_HEIGHT:
                    continue
                
                # Calculate new score
                tentative_g_score = g_score[current_pos] + 1
                
                # Skip if already have better path
                if next_pos in g_score and tentative_g_score >= g_score[next_pos]:
                    continue
                    
                # Record this path
                came_from[next_pos] = (current_pos, next_dir)
                g_score[next_pos] = tentative_g_score
                f_score[next_pos] = tentative_g_score + self.manhattan_distance(next_pos, target_pos)
                
                # Add to open set if not already there
                if next_pos not in in_open_set:
                    heapq.heappush(open_set, (f_score[next_pos], next_pos))
                    in_open_set[next_pos] = True        
        return None

    def reconstruct_path(self, came_from: Dict, current_pos: Tuple[int, int]) -> List[Direction]:
        """Reconstruct path from A* pathfinding results."""
        path = []
        while current_pos in came_from:
            prev_pos, direction = came_from[current_pos]
            path.append(direction)
            current_pos = prev_pos
        
        return list(reversed(path))

    def follow_path(self, env: Environment, path: List[Direction]) -> bool:
        """Follow first step of path. Returns True if step was taken."""
        if not path:
            return False
            
        next_direction = path[0]
        
        # Rotate if needed
        if next_direction != self.direction:
            self.rotate(next_direction)
            return True
        
        # Otherwise move forward
        return self.move_forward(env)
    
    # ---- Decision-Making Methods ----
    
    def calculate_curiosity_factor(self) -> float:
        """
        Calculate exploration vs. exploitation factor.
        Returns a value between 0.1 and 1.0.
        """
        known_cells = len(self.map)
        if not known_cells:
            return 0.5
        
        # Base curiosity on cleaning progress
        cleaning_ratio = len(self.cleaned_cells) / known_cells if known_cells > 0 else 0
        dirty_ratio = len(self.dirty_cells) / known_cells if known_cells > 0 else 0
    
        # Increase curiosity as more cells cleaned and fewer dirty
        curiosity = 0.1 + 0.9 * cleaning_ratio * (1 - dirty_ratio)
        return min(1.0, max(0.1, curiosity))
    
    def calculate_frontier_value(self, position: Tuple[int, int]) -> float:
        """Calculate value based on unknown neighbors (exploration potential)."""
        if position not in self.map:
            return 0.0
        
        # Count unknown neighbors
        unknown_neighbors = 0
        for direction in self.directions:
            neighbor_pos = (
                position[0] + direction.movement_vector[0],
                position[1] + direction.movement_vector[1]
            )
            if neighbor_pos not in self.map:
                unknown_neighbors += 1
        
        # Return normalized value
        return unknown_neighbors / 4.0

    def calculate_move_utility(self, env: Environment, direction: Direction) -> float:
        """Calculate utility value of moving in specified direction."""
        utility = 0.0
        
        # Calculate target position
        target_x = self.position[0] + direction.movement_vector[0]
        target_y = self.position[1] + direction.movement_vector[1]
        target_pos = (target_x, target_y)
        
        # Check if target cell exists
        target_cell = env.get_cell(*target_pos)
        if not target_cell:
            return -100.0  # Large penalty for invalid moves
        
        # Calculate rotation cost
        rotation_cost = 0.0
        if direction != self.direction:
            diff = (direction.angle - self.direction.angle) % 360
            if diff > 180:
                diff -= 360
            rotations = abs(diff) / 90
            rotation_cost = rotations * self.settings.rotation_power
        
        # Check height safety
        current_cell = env.get_cell(*self.position)
        if current_cell and direction.delta_key in current_cell:
            height_diff = current_cell[direction.delta_key]
            if abs(height_diff) > self.settings.MAX_SAFE_HEIGHT:
                return -100.0  # Large penalty for unsafe moves
        
        # Utility factors
        
        # Bonus for dirty cells
        if target_pos in self.map and self.map[target_pos]['dust_weight'] > 0:
            utility += 75.0
        
        # Bonus for unexplored cells
        if target_pos not in self.visited_cells:
            utility += 30.0
        
        # Bonus for cells near dirt
        nearby_dirt_bonus = 0.0
        for dirty_pos in self.dirty_cells:
            distance = self.manhattan_distance(target_pos, dirty_pos)
            if distance <= 2:
                nearby_dirt_bonus += (3.0 - distance) * 3.0
        utility += nearby_dirt_bonus
        
        # Power consumption penalty
        power_cost = self.settings.move_power + rotation_cost
        power_penalty = power_cost * 5
        utility -= power_penalty

        # Exploration vs exploitation balance
        curiosity_factor = self.calculate_curiosity_factor()
            
        # Recency value (prefer cells not visited recently)
        recency_value = 0.0
        if target_pos in self.last_visit_time:
            time_since_visit = self.time - self.last_visit_time[target_pos]
            if time_since_visit < 10:
                recency_penalty = 50.0 / (time_since_visit + 1)  
                utility -= recency_penalty
            else:
                recency_value = min(30.0, time_since_visit / 5.0)  
        else:
            recency_value = 40.0  # Bonus for never visited
        
        # Frontier value (prefer cells at edge of known area)
        frontier_value = self.calculate_frontier_value(target_pos) * 35.0
        
        # Penalty for clean cells with no exploration value
        if frontier_value == 0 and target_cell['cleaned'] == True:
            utility -= 100

        # Frequency value (prefer cells visited fewer times)
        frequency_value = 0.0
        if target_pos in self.visit_count:
            visits = self.visit_count[target_pos]
            frequency_penalty = 10.0 * (visits - 1) 
            utility -= frequency_penalty
        else:
            frequency_value = 35.0  # Bonus for never visited
        
        # Combine exploration values with curiosity factor
        exploration_utility = (recency_value + frontier_value + frequency_value) * curiosity_factor
        utility += exploration_utility

        return utility

    def decide_next_move(self, env: Environment) -> Tuple[Direction, float]:
        """Decide best direction to move based on utility calculations."""
        utilities = {}
        
        # Calculate utility for each direction
        for direction in self.directions:
            utilities[direction] = self.calculate_move_utility(env, direction)
        
        # Find direction with highest utility
        best_direction = max(utilities, key=utilities.get)
        best_utility = utilities[best_direction]
        
        return best_direction, best_utility

    def decide_action(self, env: Environment):
        """Main decision-making method to determine next action."""
        # Update knowledge of environment
        self.update_memory(env)
        
        # Check if current cell needs cleaning
        current_dust = self.sense_dust(env, 'current')
        
        if (current_dust and current_dust[1] > 0) and (self.position not in self.cleaned_cells):
            # Try normal suction first
            self.suck_dust(env, "normal")
            current_dust = self.sense_dust(env, 'current')

            # If still dirty, use heavy suction
            if current_dust and current_dust[1] > 0:
                self.suck_dust(env, "heavy")

            # Mark as cleaned
            self.cleaned_cells.add(self.position)
        
        # If following a path, continue
        if self.current_path:
            next_direction = self.current_path[0]
            
            if next_direction != self.direction:
                self.rotate(next_direction)
                return
            
            moved = self.move_forward(env)
            if moved:
                self.current_path.pop(0)
            else:
                self.current_path = None
            return
        
        # Determine whether to clean or explore
        curiosity_factor = self.calculate_curiosity_factor()

        # If dirty cells known and not too curious, clean them
        if self.dirty_cells and curiosity_factor < 0.7:
            path = self.find_path_to_dirt(env)
            if path:
                self.current_path = path
                self.decide_action(env)
                return

        # Otherwise, choose best move based on utility
        best_direction, best_utility = self.decide_next_move(env)    
        
        # Only move if utility high enough
        if best_utility < 50.0:
            return 

        if best_direction != self.direction:
            self.rotate(best_direction)
        else:
            self.move_forward(env)
