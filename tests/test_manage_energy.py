import pytest
from datetime import datetime

from src.energy.EnergyManagementSystem import SmartEnergyManagementSystem


def _defaults(inputs: dict) -> dict:
    """Garante todos os 9 argumentos obrigatórios da função manage_energy."""
    base = {
        "current_price": 0.20,
        "price_threshold": 0.20,
        "device_priorities": {},
        "current_time": datetime.now(),
        "current_temperature": 22.0,
        "desired_temperature_range": [20.0, 24.0],
        "energy_usage_limit": 30.0,
        "total_energy_used_today": 25.0,
        "scheduled_devices": [],
    }
    base.update(inputs or {})
    return base


@pytest.mark.parametrize("inputs, expected", [
    # TC1 – preço abaixo do threshold e tudo dentro da faixa
    (dict(
        current_price=0.15, price_threshold=0.20,
        device_priorities={}, current_time=datetime(2025, 10, 16, 14, 0),
        current_temperature=22.0, desired_temperature_range=[20.0, 24.0],
        energy_usage_limit=30.0, total_energy_used_today=25.0,
        scheduled_devices=[]
    ), dict(device_status={"Heating": False, "Cooling": False},
            energy_saving_mode=False, temperature_regulation_active=False)),

    # TC2 – preço acima do threshold → modo economia; devices não prioritários desligados
    (dict(
        current_price=0.25, price_threshold=0.20,
        device_priorities={"Cooling": 2, "Light": 2, "Security": 1},
        energy_usage_limit=30.0, total_energy_used_today=25.0
    ), dict(device_status={"Heating": False, "Cooling": False, "Light": False, "Security": True},
            energy_saving_mode=True, temperature_regulation_active=False)),

    # TC3 – madrugada: luz desligada, segurança ligada, geladeira ligada, etc.
    (dict(
        current_time=datetime(2025, 10, 17, 2, 0),
        device_priorities={"Light": 2, "Security": 1, "Refrigerator": 1},
        total_energy_used_today=25.0
    ), dict(device_status={"Light": False, "Security": True, "Refrigerator": True, "Heating": False, "Cooling": False},
            energy_saving_mode=False, temperature_regulation_active=False)),

    # TC4 – temperatura abaixo da faixa → aquecimento
    (dict(
        current_temperature=15.0, desired_temperature_range=[20.0, 24.0],
        device_priorities={"Heating": 1}
    ), dict(device_status={"Heating": True},
            energy_saving_mode=False, temperature_regulation_active=True)),

    # TC5 – temperatura acima da faixa → resfriamento
    (dict(
        current_temperature=30.0, desired_temperature_range=[20.0, 24.0],
        device_priorities={"Cooling": 1}
    ), dict(device_status={"Cooling": True},
            energy_saving_mode=False, temperature_regulation_active=True)),

    # TC6 – consumo acima do limite → desligar até ficar <= limite
    (dict(
        energy_usage_limit=30.0, total_energy_used_today=31.5,
        device_priorities={"Refrigerator": 3, "Light": 2, "Security": 1}
    ), dict(device_status={"Refrigerator": False, "Light": False, "Security": False, "Heating": False, "Cooling": False},
            energy_saving_mode=True, temperature_regulation_active=False)),

    # TC7 – não conseguir reduzir (ou política mantém segurança ligada)
    (dict(
        energy_usage_limit=30.0, total_energy_used_today=31.0,
        device_priorities={"Security": 1}
    ), dict(device_status={"Security": True, "Heating": False, "Cooling": False},
            energy_saving_mode=False, temperature_regulation_active=False)),

    # TC8 – agendamento liga dispositivo específico no horário
    (dict(
        current_time=datetime(2025, 10, 16, 18, 0),
        scheduled_devices=[("Furnace", "18:00")]
    ), dict(device_status={"Furnace": True, "Heating": False, "Cooling": False},
            energy_saving_mode=False, temperature_regulation_active=False)),
])
def test_manage_energy(inputs, expected):
    system = SmartEnergyManagementSystem()

    p = _defaults(inputs)
    result = system.manage_energy(
        current_price=p["current_price"],
        price_threshold=p["price_threshold"],
        device_priorities=p["device_priorities"],
        current_time=p["current_time"],
        current_temperature=p["current_temperature"],
        desired_temperature_range=p["desired_temperature_range"],
        energy_usage_limit=p["energy_usage_limit"],
        total_energy_used_today=p["total_energy_used_today"],
        scheduled_devices=p["scheduled_devices"],
    )

    # O EnergyManagementResult NÃO possui o atributo total_energy_used_today — não comparar isso.
    assert result.device_status == expected["device_status"]
    assert result.energy_saving_mode == expected["energy_saving_mode"]
    assert result.temperature_regulation_active == expected["temperature_regulation_active"]
