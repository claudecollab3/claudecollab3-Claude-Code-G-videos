from risk.position_sizing import calculate_position_size


def test_calculate_position_size_basic_math():
    # $1000 balance, 1% risk = $10 risk. Stop distance = 0.0050 = 50 pips.
    # pip value per lot = $10 -> volume = 10 / (50 * 10) = 0.02 lots.
    result = calculate_position_size(
        account_balance=1000.0,
        risk_per_trade_percent=1.0,
        entry_price=1.1000,
        stop_loss_price=1.0950,
        pip_value_per_lot=10.0,
        pip_size=0.0001,
        min_lot=0.01,
    )
    assert result.viable
    assert result.risk_amount == 10.0
    assert abs(result.volume - 0.02) < 1e-9


def test_calculate_position_size_warns_when_account_too_small():
    result = calculate_position_size(
        account_balance=5.0,
        risk_per_trade_percent=1.0,
        entry_price=1.1000,
        stop_loss_price=1.0950,
        pip_value_per_lot=10.0,
        pip_size=0.0001,
        min_lot=0.01,
    )
    assert result.viable is False
    assert result.warning is not None
    assert "too small" in result.warning


def test_calculate_position_size_zero_stop_distance_rejected():
    result = calculate_position_size(
        account_balance=1000.0,
        risk_per_trade_percent=1.0,
        entry_price=1.1000,
        stop_loss_price=1.1000,
    )
    assert result.viable is False


def test_calculate_position_size_caps_at_max_lot():
    result = calculate_position_size(
        account_balance=1_000_000.0,
        risk_per_trade_percent=5.0,
        entry_price=1.1000,
        stop_loss_price=1.0999,  # 1 pip stop -> huge raw volume
        pip_value_per_lot=10.0,
        pip_size=0.0001,
        max_lot=50.0,
    )
    assert result.viable
    assert result.volume == 50.0
