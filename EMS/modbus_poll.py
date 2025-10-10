from pymodbus.client import ModbusTcpClient

# Initialize the client with correct settings
client = ModbusTcpClient('127.0.0.1', port=502, timeout=5)

# Connect to the Modbus server
if client.connect():
    # Reading the instantaneous grid power
    print("Reading Instantaneous Grid Power:")

    # Read total grid power (Register 169)
    grid_power_result = client.read_holding_registers(169, count=1, slave=1)
    
    if not grid_power_result.isError():
        total_grid_power = grid_power_result.registers[0]
        print(f"Total Grid Power (L1 + L2): {total_grid_power} W")
    else:
        print("Error reading total grid power")

    # # Optionally, read grid power for each phase (Registers 167 and 168)
    # grid_power_l1_result = client.read_holding_registers(167, count=1, slave=1)
    # grid_power_l2_result = client.read_holding_registers(168, count=1, slave=1)

    # if not grid_power_l1_result.isError() and not grid_power_l2_result.isError():
    #     grid_power_l1 = grid_power_l1_result.registers[0]
    #     grid_power_l2 = grid_power_l2_result.registers[0]
    #     print(f"Grid Power L1: {grid_power_l1} W")
    #     print(f"Grid Power L2: {grid_power_l2} W")
    # else:
    #     print("Error reading grid power for L1 or L2")

    # Reading PV Input Power
    print("\nReading PV Input Power:")
    pv1_result = client.read_holding_registers(186, count=1, slave=1)
    pv2_result = client.read_holding_registers(187, count=1, slave=1)

    if not pv1_result.isError() and not pv2_result.isError():
        pv1_power = pv1_result.registers[0] * 1  # Apply scaling factor if needed (1.5?)
        pv2_power = pv2_result.registers[0] * 1  # Apply scaling factor if needed (1.5? might need this for inverter power outm)
        total_pv_power = pv1_power + pv2_power
        print(f"PV1 Input Power: {pv1_power} watts")
        print(f"PV2 Input Power: {pv2_power} watts")
        print(f"Total PV Input Power: {total_pv_power} watts")
    else:
        if pv1_result.isError():
            print("Error reading PV1 Input Power")
        if pv2_result.isError():
            print("Error reading PV2 Input Power")

    # Reading Daily PV Power
    print("\nReading Daily PV Power:")
    daily_pv_result = client.read_holding_registers(108, count=1, slave=1)
    
    if not daily_pv_result.isError():
        daily_pv_power = daily_pv_result.registers[0] * 0.1  # 0.1 kWh scaling
        print(f"Daily PV Power: {daily_pv_power} kWh")
    else:
        print("Error reading daily PV power")

    # Reading Instantaneous Power Consumption (Power Out)
    print("\nReading Instantaneous Power Out (Inverter Output Power):")
    power_out_result = client.read_holding_registers(175, count=1, slave=1)

    if not power_out_result.isError():
        power_out = power_out_result.registers[0]
        print(f"Inverter Output Power (Total): {power_out} W")
    else:
        print("Error reading inverter output power")

    # Close the connection
    client.close()
else:
    print("Unable to connect to Modbus server")
