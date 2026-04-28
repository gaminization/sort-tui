# Configuration

The default config lives at:

```text
~/.config/sortui/config.toml
```

If the file is absent, `sortui` creates one with defaults.

Priority is:

```text
CLI flags > named profile > config file > hardcoded defaults
```

Example:

```toml
[defaults]
algorithm = "bubble"
speed = 1.0
order = "asc"
distribution = "random"
visualization_mode = "bars"

[display]
gradient_mode = false
heatmap_mode = false

[audio]
enabled = false
min_freq = 200
max_freq = 1200

[profiles.demo]
speed = 1.5
gradient_mode = true
```

Run a profile with:

```bash
sortui --profile demo
```

