from src.energy.EnergyManagementResult import EnergyManagementResult

def test_energy_management_result_repr():
    """
    Testa a representação em string (repr) do EnergyManagementResult
    para matar os mutantes 5, 6, 7 e 8.
    """

    result = EnergyManagementResult(device_status={"Heating": False, "Cooling": False},
            energy_saving_mode=False, temperature_regulation_active=False, total_energy_used=25.0)

    expected_string = (
        "EnergyManagementResult(device_status={'Heating': False, 'Cooling': False}, "
        "energy_saving_mode=False, "
        "temperature_regulation_active=False, "
        "total_energy_used=25.0)"
    )

    assert repr(result) == expected_string