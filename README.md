# Autonomous Vacuum Cleaner Simulation

This project simulates the behavior of an autonomous vacuum cleaner equipped with multiple sensors and actuators. 
The vacuum cleaner moves across a defined area, attempting to clean it as efficiently as possible. The area information is provided via an input CSV file.

## Usage
`VacuumAgent.py [-h] [-v] [-s SETTINGS] [-a AREA]`  

options:
  
  -h, --help Show this help message and exit <br/>
  -v, --verbose Enable verbose output <br/>
  -s, --settings Path to settings file (default: setting.txt) <br/>
  -a, --area Path to area file (default: area.csv)Input Files <br/>

## Input Files

### Area Input File (area.csv)
This file defines the environment in which the vacuum cleaner operates. It contains the following columns: <br/>
  - **XCoordination**: X coordinate of a point in the area

  - **YCoordination**: Y coordinate of a point in the area

  - **DeltaL**: Height difference between the current location and the one to its left

  - **DeltaR**: Height difference between the current location and the one to its right

  - **DeltaU**: Height difference between the current location and the one above

  - **DeltaD**: Height difference between the current location and the one below

  - **Texture**: Surface type of the current location:

    - `H`: Hard floor (e.g., hardwood)
    - `S`: Soft floor (e.g., carpet)

  - **DustWeight**: Weight of dust in grams:

    - `< 2g`: Can be vacuumed with normal pressure
    - `2g - 5g`: Requires heavy pressure
    - `> 5g`: Cannot be cleaned by this vacuum cleaner

  - **Note:** The vacuum cleaner can detect the presence of dust but not its weight. Your code should consider the dust weight to determine the cleaning effect.
### Settings Input File (setting.txt) <br/>
This file contains configuration values, one per line: <br/>

  1. Time duration required
  2. Power consumption per 90-degree rotation
  3. Power consumption per unit movement
  4. Power consumption per vacuuming attempt with normal pressure
  5. Power consumption per vacuuming attempt with heavy pressure
  6. Power consumption per unit of time while the vacuum cleaner is on
  7. Power consumption per sensor reading attempt
  8. Power consumption for all other activities
