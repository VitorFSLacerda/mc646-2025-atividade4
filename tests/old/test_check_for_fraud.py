import pytest
from datetime import datetime, timedelta

from src.fraud.FraudDetectionSystem import FraudDetectionSystem
from src.fraud.Transaction import Transaction
from src.fraud.FraudCheckResult import FraudCheckResult


def _mk_tx(amount, location, minutes_ago=0):
    # Helper para criar transações com timestamp válido
    ts = datetime.now() - timedelta(minutes=minutes_ago)
    return Transaction(amount=amount, location=location, timestamp=ts)


@pytest.mark.parametrize("amount, prev_trans, location, blacklist, expected", [
    # TC1 – caminho nominal, sem flags
    (100, [], "A", ["B"], FraudCheckResult(False, False, False, 0)),

    # TC2 – valor muito alto (pode ativar verificação/fraude dependendo da regra)
    (20000, [], "A", ["B"], FraudCheckResult(True, False, True, 50)),

    # TC3 – localização em blacklist → bloqueio
    (100, [], "B", ["B"], FraudCheckResult(False, True, False, 100)),

    # TC4 – muitas transações recentes (ex.: 12 em < 60 min) → bloqueio/risco
    (100, [_mk_tx(10, "A", minutes_ago=i) for i in range(12)], "A", ["B"],
     FraudCheckResult(False, True, False, 30)),

    # TC5 – transação recente em local diferente → verificação
    (100, [_mk_tx(20, "Z", minutes_ago=10)], "A", ["B"],
     FraudCheckResult(True, False, True, 20)),

    # TC6 – histórico “ok” (sem risco extra)
    (100, [_mk_tx(20, "A", minutes_ago=120)], "A", ["B"],
     FraudCheckResult(False, False, False, 0)),
])
def test_check_for_fraud(amount, prev_trans, location, blacklist, expected):
    system = FraudDetectionSystem()

    current = _mk_tx(amount=amount, location=location, minutes_ago=0)
    result = system.check_for_fraud(current, prev_trans, blacklist)

    assert result.is_fraudulent == expected.is_fraudulent
    assert result.is_blocked == expected.is_blocked
    assert result.verification_required == expected.verification_required
    assert result.risk_score == expected.risk_score
