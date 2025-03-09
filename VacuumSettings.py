class VacuumSettings:
    """Stores operational parameters for the vacuum agent."""
    
    def __init__(self, settings_file: str, verbose: bool = False):
        """Load settings from file and set up operational constants."""
        with open(settings_file, 'r') as f:
            settings = [float(line.strip()) for line in f.readlines()]
        
        self.verbose = verbose
        
        # Constants
        self.MAX_SAFE_HEIGHT = 3  # Maximum safe height difference for movement
        self.MAX_SUCTION_WEIGHT = {'normal': 1, 'heavy': 5}  # Dust removal per suction type

        # Settings from file
        self.time_duration = settings[0]  
        self.rotation_power = settings[1] 
        self.move_power = settings[2]  
        self.normal_vacuum_power = settings[3]  
        self.heavy_vacuum_power = settings[4] 
        self.time_power = settings[5]  
        self.sensor_power = settings[6]
        self.other_power = settings[7] 

        if verbose:
            self._print_settings()
    
    def _print_settings(self):
        """Print the loaded settings."""
        print("Vacuum settings loaded:")
        print(f"Time duration: {self.time_duration}")
        print(f"Rotation power: {self.rotation_power}")
        print(f"Move power: {self.move_power}")
        print(f"Normal vacuum power: {self.normal_vacuum_power}")
        print(f"Heavy vacuum power: {self.heavy_vacuum_power}")
