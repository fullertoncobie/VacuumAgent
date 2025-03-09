This project simulates the behavior of an autonomous vacuum cleaner equipped with multiple sensors and actuators. 
The vacuum cleaner moves across a defined area, attempting to clean it as efficiently as possible. The area information is provided via an input CSV file.

usage: VacuumAgent.py [-h] [-v] [-s SETTINGS] [-a AREA]

Vacuum Agent Simulation
options:
  -h, --help Show this help message and exit
  -v, --verbose Enable verbose output
  -s, --settings Path to settings file (default: setting.txt)
  -a, --area Path to area file (default: area.csv)Input Files

Area Input File (area.csv)
This file defines the environment in which the vacuum cleaner operates. It contains the following columns:
  XCoordination: X coordinate of a point in the area
  YCoordination: Y coordinate of a point in the area
  DeltaL: Height difference between the current location and the one to its left
  DeltaR: Height difference between the current location and the one to its right
  DeltaU: Height difference between the current location and the one above
  DeltaD: Height difference between the current location and the one below
  Texture: Surface type of the current location:
  H: Hard floor (e.g., hardwood)
  S: Soft floor (e.g., carpet)
  DustWeight: Weight of dust in grams:
    < 2g: Can be vacuumed with normal pressure
    2g - 5g: Requires heavy pressure
    > 5g: Cannot be cleaned by this vacuum cleaner
  Note: The vacuum cleaner can detect the presence of dust but not its weight. Your code should consider the dust weight to determine the cleaning effect.

Settings Input File (setting.txt)
This file contains configuration values, one per line:
  Time duration required
  Power consumption per 90-degree rotation
  Power consumption per unit movement
  Power consumption per vacuuming attempt with normal pressure
  Power consumption per vacuuming attempt with heavy pressure
  Power consumption per unit of time while the vacuum cleaner is on
  Power consumption per sensor reading attempt
  Power consumption for all other activities
