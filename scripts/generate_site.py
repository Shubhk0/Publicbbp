#!/usr/bin/env python3
import os
import json
import datetime

repo_dir = os.path.abspath(os.path.dirname(__file__) + '/..')
json_path = os.path.join(repo_dir, 'data', 'programs.json')
html_path = os.path.join(repo_dir, 'docs', 'index.html')

def generate_html():
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        programs = data.get('programs', [])

    table_rows = []
    for p in programs:
        name = p.get('name', 'Unknown')
        url = p.get('url', '#')
        bounty = "✅ Yes" if p.get('bounty') else "❌ No"
        swag = "🎁 Yes" if p.get('swag') else "❌ No"
        domains = ", ".join(p.get('domains', []))
        if not domains:
            domains = "N/A"
        elif len(domains) > 50:
            domains = domains[:47] + "..."

        row = f"""
        <tr>
            <td><strong>{name}</strong></td>
            <td><a href="{url}" target="_blank">Policy/Program</a></td>
            <td>{bounty}</td>
            <td>{swag}</td>
            <td class="domains">{domains}</td>
        </tr>
        """
        table_rows.append(row)

    last_updated = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M:%S UTC")

    html_template = f"""<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Public Bug Bounty Programs Database</title>
    <style>
        :root {{
            --bg-color: #f8f9fa;
            --text-color: #333;
            --header-bg: #2c3e50;
            --header-text: #fff;
            --table-border: #dee2e6;
            --row-alt-bg: #f2f2f2;
            --link-color: #3498db;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: var(--bg-color);
            color: var(--text-color);
            line-height: 1.6;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: var(--header-bg);
            text-align: center;
            margin-bottom: 5px;
        }}
        .stats {{
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }}
        .search-container {{
            margin-bottom: 20px;
            text-align: center;
        }}
        #searchInput {{
            width: 80%;
            max-width: 500px;
            padding: 12px 20px;
            font-size: 16px;
            border: 1px solid #ccc;
            border-radius: 25px;
            outline: none;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid var(--table-border);
        }}
        th {{
            background-color: var(--header-bg);
            color: var(--header-text);
            position: sticky;
            top: 0;
        }}
        tr:nth-child(even) {{
            background-color: var(--row-alt-bg);
        }}
        tr:hover {{
            background-color: #e9ecef;
        }}
        a {{
            color: var(--link-color);
            text-decoration: none;
            font-weight: bold;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        .domains {{
            font-size: 0.9em;
            color: #555;
            word-break: break-all;
        }}
        footer {{
            text-align: center;
            margin-top: 40px;
            font-size: 0.9em;
            color: #777;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Public Bug Bounty Programs</h1>
        <div class="stats">
            Total Programs: <strong>{len(programs)}</strong> | Last Updated: {last_updated}
        </div>

        <div class="search-container">
            <input type="text" id="searchInput" onkeyup="filterTable()" placeholder="Search for programs or domains...">
        </div>

        <table id="programsTable">
            <thead>
                <tr>
                    <th>Program Name</th>
                    <th>URL</th>
                    <th>Offers Bounty</th>
                    <th>Offers Swag</th>
                    <th>Scope / Domains</th>
                </tr>
            </thead>
            <tbody>
                {''.join(table_rows)}
            </tbody>
        </table>
    </div>

    <footer>
        Data aggregated from public repositories (<a href="https://github.com/projectdiscovery/public-bugbounty-programs">ProjectDiscovery</a> & <a href="https://github.com/disclose/diodb">Disclose.io</a>).<br>
        Built with GitHub Actions.
    </footer>

    <script>
        function filterTable() {{
            var input, filter, table, tr, td, i, j, txtValue;
            input = document.getElementById("searchInput");
            filter = input.value.toUpperCase();
            table = document.getElementById("programsTable");
            tr = table.getElementsByTagName("tr");

            for (i = 1; i < tr.length; i++) {{
                tr[i].style.display = "none";
                td = tr[i].getElementsByTagName("td");
                for (j = 0; j < td.length; j++) {{
                    if (td[j]) {{
                        txtValue = td[j].textContent || td[j].innerText;
                        if (txtValue.toUpperCase().indexOf(filter) > -1) {{
                            tr[i].style.display = "";
                            break;
                        }}
                    }}
                }}
            }}
        }}
    </script>
</body>
</html>
"""

    os.makedirs(os.path.dirname(html_path), exist_ok=True)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_template)

    print('Generated', html_path)

if __name__ == "__main__":
    generate_html()
