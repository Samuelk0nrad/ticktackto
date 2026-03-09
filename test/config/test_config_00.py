import backend


def test_config_00() -> None:
    config = backend.config.Config.get_instance()
    assert config

    assert "sqlite:///:memory:" == config.connection_string
