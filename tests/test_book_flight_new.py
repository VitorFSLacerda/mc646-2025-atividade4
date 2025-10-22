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
    # Quantidade de passageiros é igual à de assentos disponíveis (mata o mutante 17)
    (dict(
        passengers=5, available_seats=5
    ), dict(confirmation=True, total_price=0.0, refund_amount=0.0, points_used=False)),

    # Preço com exatamente 4 passageiros e ajuste de demanda (mata o mutante 36)
    (dict(
        passengers=4, available_seats=100, previous_sales=50
    ), dict(confirmation=True, total_price=160.0, refund_amount=0.0, points_used=False)),

    # Exatamente 1 ponto de recompensa disponível (mata o mutante 42)
    (dict(
        previous_sales=50, reward_points_available=1
    ), dict(confirmation=True, total_price=39.99, refund_amount=0.0, points_used=True)),

    # Pontos para chegar em preço final entre 0 e 1 (mata o mutante 50)
    (dict(
        previous_sales=50, reward_points_available=3950
    ), dict(confirmation=True, total_price=0.5, refund_amount=0.0, points_used=True)),

    # Cancelamento com reembolso e com exatamente 48h entre booking_time e departure_time (mata os mutante 53 e 54)
    (dict(
        is_cancellation=True, booking_time=datetime(2025, 10, 16, 12, 0), 
        departure_time=datetime(2025, 10, 18, 12, 0), previous_sales=50
    ), dict(confirmation=False, total_price=0.0, refund_amount=40.0, points_used=False))
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
