#!/usr/bin/python3    

	#Artifical load profile generator v1.0, generation of artificial load profiles to benchmark demand side management approaches
    #Copyright (C) 2016 Gerwin Hoogsteen

    #This program is free software: you can redistribute it and/or modify
    #it under the terms of the GNU General Public License as published by
    #the Free Software Foundation, either version 3 of the License, or
    #(at your option) any later version.

    #This program is distributed in the hope that it will be useful,
    #but WITHOUT ANY WARRANTY; without even the implied warranty of
    #MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    #GNU General Public License for more details.

    #You should have received a copy of the GNU General Public License
    #along with this program.  If not, see <http://www.gnu.org/licenses/>.
    

import random
import json
import astral
import numpy as np

import households

## Please select your output writer of preference
import writer as writer
#import trianawriter as writer

# Get configuration form conf file
file_config = json.loads(open('conf/tmp.json').read())

# Random seed
seed = 42
random.seed(seed)

# In and out files:
# Folder to write the output to
folder = file_config['root_output_folder']

# Input files:
weather_irradiation = file_config['weather_section']['irradiation_file']
weather_timebaseDataset = int(file_config['weather_section']['timebase_dataset'])  # in seconds per interval

# Simulation:
# number of days to simulate and skipping of initial days. Simulation starts at Sunday January 1.
numDays = int(file_config['num_days'])  # number of days
startDay = int(file_config['start_day'])  # Initial day

city_name = file_config['location_section']['name']
city = astral.Location(info=(city_name,
							 file_config['location_section']['country'],
							 float(file_config['location_section']['latitude']),
							 float(file_config['location_section']['longitude']),
							 file_config['location_section']['time_zone'],
							 float(file_config['location_section']['altitude'])))
city.solar_depression = file_config['location_section']['solar_depression']

# Devices
# Scale overall consumption:
consumptionFactor = float(file_config['devices_section']['consumption_factor'])  # consumption was a bit too high

# Penetration of emerging technology in percentages (%)
penetrationEV = float(file_config['devices_section']['EV']['penetration'])
penetrationPHEV = float(file_config['devices_section']['PHEV']['penetration'])
penetrationPV = float(file_config['devices_section']['PV']['penetration'])
penetrationBattery = float(file_config['devices_section']['battery']['penetration'])
# Note only houses with PV will receive a battery!
penetrationInductioncooking = float(file_config['devices_section']['kitchen']['induction_cooking_penetration'])

# Device parameters:
# EV and PHEV
capacityEV = float(file_config['devices_section']['EV']['capacity'])  # Wh
powerEV = float(file_config['devices_section']['EV']['power'])  # W
capacityPHEV = float(file_config['devices_section']['PHEV']['capacity'])  # Wh
powerPHEV = float(file_config['devices_section']['PHEV']['power'])  # W
commuteDistanceMean = float(file_config['devices_section']['PHEV']['distance_mean'])  # km
commuteDistanceSigma = float(file_config['devices_section']['PHEV']['distance_sigma'])  # km

# PV
PVProductionPerYear = float(file_config['devices_section']['PV']['production_per_year'])  # kWh
PVAngleMean = float(file_config['devices_section']['PV']['tilt_angle_mean'])  # degrees
PVAngleSigma = float(file_config['devices_section']['PV']['tilt_angle_sigma'])  # degrees
PVSouthAzimuthSigma = float(file_config['devices_section']['PV']['south_azimuth_sigma'])  # degrees
PVEfficiencyMin = float(file_config['devices_section']['PV']['efficiency_min'])  # % of max
PVEfficiencyMax = float(file_config['devices_section']['PV']['efficiency_max'])  # % of max

# Battery
capacityBatteryLarge = float(file_config['devices_section']['battery']['capacity_large'])  # Wh
capacityBatteryMedium = float(file_config['devices_section']['battery']['capacity_medium'])  # Wh
capacityBatterySmall = float(file_config['devices_section']['battery']['capacity_small'])  # Wh
powerBatteryLarge = float(file_config['devices_section']['battery']['power_large'])  # W
powerBatteryMedium = float(file_config['devices_section']['battery']['power_medium'])  # W
powerBatterySmall = float(file_config['devices_section']['battery']['power_small'])  # W

# Kitchen (devices consumption)
ConsumptionOven = float(file_config['devices_section']['kitchen']['power_consumption_oven'])  # W
ConsumptionMicroWave = float(file_config['devices_section']['kitchen']['power_consumption_microwave'])  # W
ConsumptionStoveVentilation = float(file_config['devices_section']['kitchen']['power_consumption_stove_ventilation'])  # W
# StoveVentilation is maximum, usually set lower!
ConsumptionInductionStove = float(file_config['devices_section']['kitchen']['power_consumption_induction_stove'])  # W
# Data of InductionStove taken from http://homeguides.sfgate.com/many-watts-induction-stove-85380.html
ConsumptionFridgeBigMin = float(file_config['devices_section']['kitchen']['power_consumption_fridge_big_min'])  # W
ConsumptionFridgeBigMax = float(file_config['devices_section']['kitchen']['power_consumption_fridge_big_max'])  # W
ConsumptionFridgeSmallMin = float(file_config['devices_section']['kitchen']['power_consumption_fridge_small_min'])  # W
ConsumptionFridgeSmallMax = float(file_config['devices_section']['kitchen']['power_consumption_fridge_small_max'])  # W
ConsumptionKettle = float(file_config['devices_section']['kitchen']['power_consumption_kettle'])  # W

# White goods
ConsumptionIron = float(file_config['devices_section']['white_goods']['power_consumption_iron'])  # W
ConsumptionVacuumcleaner = float(file_config['devices_section']['white_goods']['power_consumption_vacuum_cleaner'])  # W

# House
ConsumptionHouseVentilation = float(file_config['devices_section']['ventilation']['power_consumption'])  # W

# Household randomization (all values must be between 0-1000)
familyOutingChanceMin = float(file_config['households_section']['randomization']['perc_family_outing_chance_min'])  # %
familyOutingChanceMax = float(file_config['households_section']['randomization']['perc_family_outing_chance_max'])  # %
personWeekdayActivityChanceMin = float(file_config['households_section']['randomization']['perc_person_weekday_activity_chance_min'])  # %
personWeekdayActivityChanceMax = float(file_config['households_section']['randomization']['perc_person_weekday_activity_chance_max'])  # %
personWeekendActivityChanceMin = float(file_config['households_section']['randomization']['perc_person_weekend_activity_chance_min'])  # %
personWeekendActivityChanceMax = float(file_config['households_section']['randomization']['perc_person_weekend_activity_chance_max'])  # %

# Select the households

householdList = []

# Singles
num_singles_worker = 0
for i in range(0, int(file_config['households_section']['single_worker']['number'])):
	householdList.append(households.HouseholdSingleWorker(type='single_worker'))
	num_singles_worker += 1

num_singles_retired = 0
for i in range(0, int(file_config['households_section']['single_retired']['number'])):
	householdList.append(households.HouseholdSingleRetired(type='single_retired'))
	num_singles_retired += 1
	
# Couples
num_duals_worker = 0
for i in range(0, int(file_config['households_section']['dual_worker']['number'])):
	if file_config['households_section']['dual_worker']['parttime'] == 'true':
		householdList.append(households.HouseholdDualWorker(True, type='dual_worker'))
	else:
		householdList.append(households.HouseholdDualWorker(False, type='dual_worker'))
	num_duals_worker += 1

num_duals_retired = 0
for i in range(0, int(file_config['households_section']['dual_retired']['number'])):
	householdList.append(households.HouseholdDualRetired(type='dual_retired'))
	num_duals_retired += 1

# Families
num_families_single_worker = 0
for i in range(0, int(file_config['households_section']['family_single_worker']['number'])):
	er = float(file_config['households_section']['family_single_worker']['employment_rate'])
	kids = int(file_config['households_section']['family_single_worker']['kids'])
	hh = households.HouseholdFamilySingleWorker(employment_rate=er, kids=kids, type='family_single_worker')
	householdList.append(hh)
	del hh
	num_families_single_worker += 1

num_families_dual_workers = 0
for i in range(0, int(file_config['households_section']['family_dual_worker']['number'])):
	ers = np.array(file_config['households_section']['family_dual_worker']['employment_rates'], dtype='|S4')
	kids = int(file_config['households_section']['family_dual_worker']['kids'])
	hh = households.HouseholdFamilyDualWorker(employment_rates=ers.astype(np.float), kids=kids, type='family_dual_workers')
	householdList.append(hh)
	del hh
	num_families_dual_workers += 1

numHouses = len(householdList)

# DO NOT EDIT BEYOND THIS LINE:
# WARNING: The following option is untested:
# Output timebase in seconds
timeBase = 60  # must be a multiple of 60

# Do no touch this:
intervalLength = int(timeBase/60)		# set the rate in minutes, normal in minute intervals

# TRIANA SPECIFIC SETTINGS
# Control
# TODO MAKE USE OF IT
TrianaPlanning_LocalFlat = True
TrianaPlanning_ReplanningInterval = 96
TrianaPlanning_Horizon = 192
TrianaPlanning_MaximumIterations = 5
TrianaPlanning_MinImprovenemt = 10
trianaModelPath = 'models/newr/'

