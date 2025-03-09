"""
Vacuum Agent Simulation

A example simulation ofthe vacuum cleaner agent that navigates and cleans
a virtual grid-based environment.
"""

import argparse
import time
from Environment import Environment
from VacuumSettings import VacuumSettings
from VacuumAgent import VacuumAgent
from Direction import Direction

def run_simulation(settings_file: str, area_file: str, verbose: bool):
    """
    Run the vacuum agent simulation.
    
    Args:
        settings_file: Path to file containing vacuum settings
        area_file: Path to CSV file containing environment data
        verbose: Whether to print detailed output
    """
    # Initialize components
    settings = VacuumSettings(settings_file, verbose=verbose)
    environment = Environment(area_file)
    vacuum = VacuumAgent(settings)

    # Set up simulation
    max_ticks = int(settings.time_duration)
    print("\nStarting simulation...")

    # Main simulation loop
    for step in range(max_ticks):
        vacuum.decide_action(environment)
        
        # Print status periodically
        if step % 10 == 0:  
            if settings.verbose:
                environment.print_dust()
                print()  
            print(f"Step {step}: Cleanliness {100 - environment.percent_dirty():.1f}%")

    # Print final results
    print(f"\nSimulation complete!")
    print(f"Final cleanliness: {100 - environment.percent_dirty():.1f}%")
    print(f"Cells cleaned: {len(vacuum.cleaned_cells)}")
    print(f"Power consumed: {vacuum.power_consumed:.1f}")

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Vacuum Agent Simulation')
    parser.add_argument('-v', '--verbose', action='store_true', 
                       help='Enable verbose output')
    parser.add_argument('-s', '--settings', default='setting.txt',
                      help='Path to settings file (default: setting.txt)')
    parser.add_argument('-a', '--area', default='area.csv',
                      help='Path to area file (default: area.csv)')
    args = parser.parse_args()

    # Run the simulation
    run_simulation(args.settings, args.area, args.verbose)
