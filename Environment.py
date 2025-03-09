import csv
from typing import Dict, Tuple, Optional

class Environment:
    """Grid-based environment with dust, texture, and height deltas."""
    
    def __init__(self, area_file: str):
        """Initialize environment from CSV file."""
        self.grid = {}
        self.load_area(area_file)
        
    def load_area(self, area_file: str):
        """Load environment data from CSV file."""
        with open(area_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                x = int(row['XCoordination'])
                y = int(row['YCoordination'])
                self.grid[(x, y)] = {
                    'delta_l': int(row['DeltaL']),
                    'delta_r': int(row['DeltaR']),
                    'delta_u': int(row['DeltaU']),
                    'delta_d': int(row['DeltaD']),
                    'texture': row['Texture'],
                    'dust_weight': float(row['DustWeight']),
                    'cleaned': False
                }
    
    def get_cell(self, x: int, y: int) -> Optional[Dict]:
        """Get cell data at specified coordinates."""
        return self.grid.get((x, y))
    
    def get_sucked(self, x: int, y: int, pressure: float):
        """Remove dust from a cell based on suction pressure."""
        cell = self.grid.get((x, y))
        if not cell:
            return
            
        dust_weight = cell['dust_weight']

        # If pressure is enough to clean the cell
        if 0 >= dust_weight - pressure:
            self.grid[(x, y)]['dust_weight'] = 0
            self.grid[(x, y)]['cleaned'] = True

    def get_dimensions(self) -> Tuple[int, int]:
        """Get maximum x and y coordinates in the grid."""
        if not self.grid:
            return 0, 0
            
        x_coords, y_coords = zip(*self.grid.keys())
        return max(x_coords), max(y_coords)
    
    def percent_dirty(self) -> float:
        """Calculate percentage of dirty cells (0-100)."""
        if not self.grid:
            return 0.0
            
        total_cells = len(self.grid)
        dirty_cells = sum(1 for cell in self.grid.values() if cell['dust_weight'] > 0)
        
        return (dirty_cells / total_cells) * 100
    
    def print_dust(self):
        """Print dust levels in a grid format."""
        max_x, max_y = self.get_dimensions()
        
        for y in range(max_y + 1):
            for x in range(max_x + 1):
                cell = self.get_cell(x, y)
                if cell:
                    print(f"{cell['dust_weight']:.1f}", end="\t")
                else:
                    print("-", end="\t")
            print()
