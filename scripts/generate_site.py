#!/usr/bin/env python3
import os, markdown

repo_dir = os.path.abspath(os.path.dirname(__file__) + '/..')
md_path = os.path.join(repo_dir, 'bugbounty_programs_details.md')
html_path = os.path.join(repo_dir, 'docs', 'index.html')

with open(md_path, 'r', encoding='utf-8') as f:
    md_text = f.read()

# Convert markdown to HTML using python-markdown
html_body = markdown.markdown(md_text, extensions=['tables', 'fenced_code'])

html_template = f"""<!DOCTYPE html>
<html lang='en'>
<head>
<meta charset='UTF-8'>
<title>Public Bug Bounty Programs</title>
<style>
body {font-family: Arial, sans-serif; margin: 2rem; line-height: 1.6;}
h1, h2, h3 {color: #2c3e50;}
pre {background:#f4f4f4; padding:1rem; overflow:auto;}
</style>
</head>
<body>
<h1>Public Bug Bounty Programs Database</h1>
{html_body}
</body>
</html>
"""

os.makedirs(os.path.dirname(html_path), exist_ok=True)
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_template)

print('Generated', html_path)
