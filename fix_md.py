import os, glob
files = glob.glob('docs/**/*.md', recursive=True) + ['README.md']
for f in files:
    with open(f, 'r') as file:
        content = file.read()
    content = content.replace('sortui --', 'sort-tui --').replace('`sortui`', '`sort-tui`')
    with open(f, 'w') as file:
        file.write(content)
