import os
import glob

replacements = {
    "sortui -a": "sort-tui -a",
    "sortui --list": "sort-tui --list",
    "sortui --order": "sort-tui --order",
    "sortui --distribution": "sort-tui --distribution",
    "sortui --seed": "sort-tui --seed",
    "sortui --input": "sort-tui --input",
    "sortui --profile": "sort-tui --profile",
    "sortui --replay": "sort-tui --replay",
    "sortui --compare": "sort-tui --compare",
    "sortui --benchmark": "sort-tui --benchmark",
    "  sortui ": "  sort-tui ",
    "version=f\"sortui ": "version=f\"sort-tui ",
    "sortui_run_": "sort-tui_run_",
    "sortui-run-v1": "sort-tui-run-v1",
    "f\" sortui │": "f\" sort-tui │",
    "sortui challenges": "sort-tui challenges",
    "\"sortui\"": "\"sort-tui\"",
    "'sortui'": "'sort-tui'",
}

for root, _, files in os.walk('sortui'):
    for file in files:
        if file.endswith('.py'):
            path = os.path.join(root, file)
            with open(path, 'r') as f:
                content = f.read()
            for k, v in replacements.items():
                if "import" in k or "from" in k: continue # safety
                content = content.replace(k, v)
            with open(path, 'w') as f:
                f.write(content)

for root, _, files in os.walk('tests'):
    for file in files:
        if file.endswith('.py'):
            path = os.path.join(root, file)
            with open(path, 'r') as f:
                content = f.read()
            for k, v in replacements.items():
                content = content.replace(k, v)
            with open(path, 'w') as f:
                f.write(content)
