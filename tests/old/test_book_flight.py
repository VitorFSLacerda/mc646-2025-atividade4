import pytest
from datetime import datetime, timedelta

from src.flight.FlightBookingSystem import FlightBookingSystem


def _defaults(params: dict) -> dict:
    """Garante que TODOS os parâmetros obrigatórios sejam passados
    (evita TypeError por argumentos faltantes)."""
    now = datetime.now()
    base = {
        "passengers": 1,
        "available_seats": 10,
        "booking_time": now,
        "departure_time": now + timedelta(hours=24),
        "current_price": 100.0,
        "previous_sales": 0,
        "reward_points_available": 0,
        "is_cancellation": False,
    }
    base.update(params or {})
    return base


@pytest.mark.parametrize("params, expected", [
    # TC1 – compra simples com possível desconto (valores esperados conforme parte B)
    (dict(
        passengers=1, available_seats=10,
        booking_time=datetime(2025, 10, 16, 12, 0),
        departure_time=datetime(2025, 10, 17, 18, 0),
        current_price=100.0, reward_points_available=0,
        is_cancellation=False, previous_sales=50
    ), dict(confirmation=True, total_price=40.0, refund_amount=0.0, points_used=False)),

    # TC2 – sem assentos suficientes
    (dict(
        passengers=5, available_seats=4
    ), dict(confirmation=False, total_price=0.0, refund_amount=0.0, points_used=False)),

    # TC3 – janela de horário/precificação que pode aumentar preço (ex.: voo cedo)
    (dict(
        passengers=1,
        booking_time=datetime(2025, 10, 16, 12, 0),
        departure_time=datetime(2025, 10, 17, 0, 0),
        current_price=100.0, previous_sales=50
    ), dict(confirmation=True, total_price=140.0, refund_amount=0.0, points_used=False)),

    # TC4 – preço com múltiplos passageiros e ajuste de demanda
    (dict(
        passengers=5, current_price=100.0, previous_sales=50
    ), dict(confirmation=True, total_price=190.0, refund_amount=0.0, points_used=False)),

    # TC5 – uso de pontos recompensa parcial
    (dict(
        passengers=1, current_price=100.0, previous_sales=50, reward_points_available=1000
    ), dict(confirmation=True, total_price=30.0, refund_amount=0.0, points_used=True)),

    # TC6 – pontos suficientes para abater tudo
    (dict(
        passengers=1, current_price=100.0, reward_points_available=15000
    ), dict(confirmation=True, total_price=0.0, refund_amount=0.0, points_used=True)),

    # TC7 – cancelamento com reembolso (cenário 1)
    (dict(
        is_cancellation=True,
        booking_time=datetime(2025, 10, 16, 12, 0),
        departure_time=datetime(2025, 10, 18, 14, 0),
        current_price=100.0, previous_sales=50
    ), dict(confirmation=False, total_price=0.0, refund_amount=40.0, points_used=False)),

    # TC8 – cancelamento com reembolso (cenário 2)
    (dict(
        is_cancellation=True,
        booking_time=datetime(2025, 10, 16, 12, 0),
        departure_time=datetime(2025, 10, 17, 18, 0),
        current_price=100.0, previous_sales=50
    ), dict(confirmation=False, total_price=0.0, refund_amount=20.0, points_used=False)),
])
def test_book_flight(params, expected):
    sys_flight = FlightBookingSystem()

    p = _defaults(params)
    result = sys_flight.book_flight(
        passengers=p["passengers"],
        available_seats=p["available_seats"],
        booking_time=p["booking_time"],
        departure_time=p["departure_time"],
        current_price=p["current_price"],
        previous_sales=p["previous_sales"],
        reward_points_available=p["reward_points_available"],
        is_cancellation=p["is_cancellation"],
    )

    assert result.confirmation == expected["confirmation"]
    assert result.total_price == expected["total_price"]
    assert result.refund_amount == expected["refund_amount"]
    assert result.points_used == expected["points_used"]
