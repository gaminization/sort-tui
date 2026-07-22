# Configuration and Profiles

You can heavily customize the defaults, displays, and audio settings of `sort-tui` via a standard TOML configuration file.

## Configuration File Location

The default configuration lives at:
```text
~/.config/sortui/config.toml
```

> [!NOTE]
> If the configuration directory or file is absent on startup, `sort-tui` will automatically create it and populate it with safe defaults.

## The Configuration Cascade

Settings are evaluated in the following priority order (from highest to lowest):

1. **CLI Flags:** Values passed directly in the terminal (e.g. `--speed 2.0`)
2. **Named Profiles:** A block defined in the config file under `[profiles.<name>]`
3. **Config File Defaults:** The base `[defaults]`, `[display]`, and `[audio]` blocks.
4. **Hardcoded Defaults:** The engine's fallback values.

## Example `config.toml`

```toml
# Base simulation defaults
[defaults]
algorithm = "bubble"
speed = 1.0
order = "asc"
distribution = "random"
visualization_mode = "bars"

# Visual modifiers
[display]
gradient_mode = false
heatmap_mode = false

# Audio engine parameters
[audio]
enabled = false
min_freq = 200
max_freq = 1200

# A custom named profile for demonstrations
[profiles.demo]
speed = 1.5
gradient_mode = true
algorithm = "quicksort"
```

## Using Profiles

To run the application using the custom `demo` profile defined above, simply pass the `--profile` flag:

```bash
sortui --profile demo
```
