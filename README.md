# Digital Transformation of UM's Farm Energy Management  

**An innovative EMS (Energy Management System) that integrates solar arrays, electric vehicle charging, and cooling for produce storage, to modernize infrastructure operation and minimize greenhouse gas emissions.**
**Deployed to UM's farm operations with a software stack designed from scratch**


---


## Table of Contents  
- [Introduction](#introduction)  
- [Features](#features)  
- [System Architecture](#system-architecture)  
- [Installation](#installation)  
- [Usage](#usage)  
- [Acknowledgements](#acknowledgements)  

---

## Introduction  
This project addresses the growing need for sustainable energy solutions by:  
- **Reducing greenhouse gas emissions** through optimized energy use.  
- **Integrating renewable energy** (solar arrays), electric vehicle charging, and energy-efficient cooling systems (Coolth Mode and Eco Mode).  
- **Enhancing energy management** balances solar power usage and energy needs.  

Our system is designed to support sustainability while maintaining efficiency and cost-effectiveness.  
Our system has been deployed to the [UM Farm](https://mbgna.umich.edu/campus-farm-solar-powered-cooler-and-electric-delivery-vehicle-project)  

---

## Features  
- **Solar Array Integration**: Harnesses solar energy for sustainable power.  
- **EV Charging**: Smart management for optimal charging schedules.  
- **Cooling System**: Energy-efficient cooling for produce storage.  
- **Emission Reduction**: Built-in rule-based system to lower greenhouse gas emissions.
- **Vent Control**: Automated ventilation management to optimize airflow and maintain ideal storage conditions.

---

## System Architecture  
The system consists of the following components:  
1. **Solar Panels**: Generate renewable energy.  
2. **EV Charging Stations**: Prioritize charging based on energy availability and scheduled delivery.  
3. **Cooling System**: Maintains ideal conditions for produce storage.
4. **Vent**: A thermostat-regulated cold air intake system.

The **EMS** connects to the above hardware and uses a rule-based algorithm to reduce carbon emissions, reduce power from the grid, and ensure safety for the equipment. Here's diagram for this sytem.
<img width="1159" alt="Screenshot 2024-12-09 at 3 02 17 PM" src="https://github.com/user-attachments/assets/467d63be-dc3a-4360-860f-7a856ac9cb69">
P.S.: *Cooler Dirty Periods are calculated and extract from Wattime API which provides marginal emission data for electric grids.

The following two diagram shows **EMS** rules for **EV Charging Schedule** and **Vent Control**.

<img width="597" alt="Screenshot 2024-12-09 at 3 19 51 PM" src="https://github.com/user-attachments/assets/5f69624d-bbdc-4fc4-96e5-b6734817c070">

<img width="457" alt="Screenshot 2024-12-09 at 3 10 18 PM" src="https://github.com/user-attachments/assets/e4063d73-8d01-47e7-b02c-269ecfa71001">

P.S.: *EV Clean Periods are calculated based on next schedule delivery time, EV battery Level and Wattime API. It provides serveal time slots ranking from the lowest marginal emission data in grids from current to next schedule delivery task to fully charge the EV.

---

## Installation
First clone the Repo

`git clone https://github.com/keeeeeliu/CampusFarm.git`

##### Virtual Environment Setup
Make a virtual environment:

`python -m venv env`

If you are on Windows: 

`env\Scripts\activate.bat`

Else:

`source env/bin/activate`

Should now see (env) in terminal prompt, now install dependencies using `pyproject.toml`:

`pip install -e .`

This will install all dependencies defined in the `pyproject.toml` file.

If you need to add new packages, update the `dependencies` list in `pyproject.toml`.

---

## Usage

Run the following command to the program

`python EMS/real_time_ems.py`

---

## Acknowledgements  

We would like to express our gratitude to everyone who contributed to the success of this project:  

### Team Members  
- **Amanullah Azim**.  
- **Nolan Lysaght**.  
- **Nelson Figueroa**.  
- **Ke Liu**.
- **Xinyi Xu**.
- **Nathan Newman**.  
- **Tongyuan Miao**.

### Mentors  
- **Johanna Mathieu**.  
- **Ang Chen**.

### Sponsors  
- **Jeremy Moghtader** @ U-M Matthaei Botanical Gardens and Nichols Arboretum.

### Student Mentors
- **Samuel Fay**.
- **Brendan Ireland**.

Your support and expertise made this project possible, and we are deeply grateful!  
