import pytest
from datetime import datetime, timedelta

from src.fraud.FraudDetectionSystem import FraudDetectionSystem
from src.fraud.Transaction import Transaction
from src.fraud.FraudCheckResult import FraudCheckResult


def _mk_tx(amount, location, base_time, minutes_ago=0):
    # Helper para criar transações com timestamp válido
    ts = base_time - timedelta(minutes=minutes_ago)
    return Transaction(amount=amount, location=location, timestamp=ts)


@pytest.mark.parametrize("amount, prev_trans_data, location, blacklist, expected", [
    # Valor da transação exatamente igual a 10000 (mata o mutante 72)
    (10000, [], "A", ["B"], FraudCheckResult(False, False, False, 0)),

    # Valor da transação exatamente igual a 10001 (mata o mutante 73)
    (10001, [], "A", ["B"], FraudCheckResult(True, False, True, 50)),

    # Exatamente 10 transações recentes (mata o mutante 81)
    (100, [(10, "A", i) for i in range(10)], "A", ["B"], 
    FraudCheckResult(False, False, False, 0)),

    # Muitas transações recentes realizadas há exatamente 61 minutos (mata o mutante 86)
    (100, [(10, "C", 61) for _ in range(11)], "A", ["B"],
    FraudCheckResult(False, False, False, 0)),

    # Muitas transações recentes realizadas há exatamente 60 minutos (mata o mutante 88)
    (100, [(10, "C", 60) for _ in range(11)], "A", ["B"],
    FraudCheckResult(False, True, False, 30)),

    # Exatamente 11 transações recentes (mata o mutante 94)
    (100, [(10, "A", i) for i in range(11)], "A", ["B"],
    FraudCheckResult(False, True, False, 30)),

    # Valor de transação muito alto e muitas transações recentes (mata o mutante 97)
    (20000, [(10, "A", i) for i in range(11)], "A", ["B"],
    FraudCheckResult(True, True, True, 80)),

    # Última transação foi há exatamente 30 minutos e em local diferente (mata os mutantes 106, 108 e 109)
    (100, [(10, "C", 30)], "A", ["B"],
    FraudCheckResult(False, False, False, 0)),

    # Valor de transação muito alto, última transação há menos de 30 minutos e em local diferente (mata o mutante 116)
    (20000, [(10, "C", 29)], "A", ["B"],
    FraudCheckResult(True, False, True, 70)),
])
def test_check_for_fraud(amount, prev_trans_data, location, blacklist, expected):
    system = FraudDetectionSystem()

    base_time = datetime.now()
    prev_trans = [_mk_tx(amount, location, base_time, minutes_ago=minutes) for (amount, location, minutes) in prev_trans_data]

    current = _mk_tx(amount=amount, location=location, base_time=base_time, minutes_ago=0)
    result = system.check_for_fraud(current, prev_trans, blacklist)

    assert result.is_fraudulent == expected.is_fraudulent
    assert result.is_blocked == expected.is_blocked
    assert result.verification_required == expected.verification_required
    assert result.risk_score == expected.risk_score
