from sortui.config import SortuiConfig


def test_default_config_created_if_absent(tmp_path):
    path = tmp_path / "config.toml"
    cfg = SortuiConfig(path)
    assert path.exists()
    assert cfg.algorithm == "bubble"


def test_malformed_values_fall_back_to_defaults(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text(
        """
[defaults]
speed = "fast"
order = "sideways"
distribution = "unknown"

[display]
heatmap_mode = "yes please"
""",
        encoding="utf-8",
    )
    cfg = SortuiConfig(path)
    assert cfg.speed == 1.0
    assert cfg.order == "asc"
    assert cfg.distribution == "random"
    assert cfg.heatmap_mode is False


def test_profile_priority_order():
    cfg = SortuiConfig.__new__(SortuiConfig)
    cfg._raw = {
        "defaults": {"algorithm": "bubble"},
        "profiles": {"demo": {"algorithm": "merge"}},
    }
    assert cfg.resolve_option("algorithm", profile_name="demo") == "merge"
    assert cfg.resolve_option("algorithm", cli_value="quick", profile_name="demo") == "quick"
    assert cfg.resolve_option("speed", profile_name="missing") == 1.0

