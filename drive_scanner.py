import os
import sys
import hashlib
from collections import defaultdict
from pathlib import Path
from datetime import datetime
import time

def format_size(size_bytes):
    """Convert bytes to human-readable string (KB, MB, GB) with raw size for sorting."""
    if size_bytes == 0:
        return "0 B", 0
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = 0
    s = float(size_bytes)
    while s >= 1024 and i < len(size_name) - 1:
        s /= 1024.0
        i += 1
    formatted = f"{s:.1f} {size_name[i]}" if i > 0 else f"{int(s)} B"
    return formatted, size_bytes

def collect_files(root_dir):
    """Walks through the root directory and collects all file metadata."""
    files_list = []
    total_folders = 0
    
    root_path = Path(root_dir)
    if not root_path.exists():
        print(f"[Error] Path '{root_dir}' does not exist.")
        sys.exit(1)

    print(f"Scanning directory: {root_dir} ... Please wait.")
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        total_folders += len(dirnames)
        for filename in filenames:
            full_path = Path(dirpath) / filename
            try:
                stat = full_path.stat()
                size = stat.st_size
                rel_path = full_path.relative_to(root_path)
                files_list.append({
                    'name': filename,
                    'path': str(full_path),
                    'rel_path': str(rel_path).replace('\\', '/'),
                    'size': size,
                    'extension': full_path.suffix.lower()
                })
            except (PermissionError, OSError):
                continue
                
    return files_list, total_folders

def calculate_folder_sizes(files_list, root_dir):
    """Calculates cumulative storage and file counts for each folder."""
    folder_data = defaultdict(lambda: {'size': 0, 'count': 0})
    root_path = Path(root_dir).resolve()
    
    for f in files_list:
        file_path = Path(f['path']).resolve()
        current = file_path.parent
        while True:
            try:
                current.relative_to(root_path)
                p_str = str(current)
                folder_data[p_str]['size'] += f['size']
                folder_data[p_str]['count'] += 1
                if current == root_path:
                    break
                current = current.parent
            except ValueError:
                break

    sorted_folders = sorted(folder_data.items(), key=lambda x: x[1]['size'], reverse=True)
    return sorted_folders

def find_same_name_files(files_list):
    """Groups files by filename to find same-name files (Level 1)."""
    name_dict = defaultdict(list)
    for f in files_list:
        name_dict[f['name']].append(f)
        
    same_name_groups = {name: items for name, items in name_dict.items() if len(items) > 1}
    return same_name_groups

def get_file_hash(filepath, chunk_size=65536):
    """Calculates SHA-256 hash of a file for exact duplicate detection."""
    hasher = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return None

def find_exact_duplicates(files_list):
    """Finds exact duplicate files based on size and SHA-256 hash (Level 2)."""
    size_dict = defaultdict(list)
    for f in files_list:
        if f['size'] > 0:
            size_dict[f['size']].append(f)

    potential_duplicates = {}
    for size, items in size_dict.items():
        if len(items) > 1:
            hash_dict = defaultdict(list)
            for item in items:
                file_hash = get_file_hash(item['path'])
                if file_hash:
                    hash_dict[file_hash].append(item)
            
            for f_hash, h_items in hash_dict.items():
                if len(h_items) > 1:
                    filename = h_items[0]['name']
                    potential_duplicates[filename] = {
                        'hash': f_hash,
                        'items': h_items,
                        'wasted_size': size * (len(h_items) - 1)
                    }
                    
    return potential_duplicates

def identify_videos(files_list):
    """Filters files categorized as videos."""
    video_extensions = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v'}
    return [f for f in files_list if f['extension'] in video_extensions]

def find_empty_folders(root_dir):
    """Scans for completely empty folders."""
    empty_folders = []
    root_path = Path(root_dir)
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        if not dirnames and not filenames:
            try:
                rel = Path(dirpath).relative_to(root_path)
                empty_folders.append(str(rel).replace('\\', '/'))
            except ValueError:
                empty_folders.append(dirpath)
    return empty_folders

def generate_html(report_data):
    """Generates a unique timestamped standalone interactive HTML report."""
    
    root_dir = report_data['root_dir']
    scan_duration = report_data['scan_duration']
    total_size_str, total_size_bytes = format_size(report_data['total_size'])
    total_files = report_data['total_files']
    total_folders = report_data['total_folders']
    
    same_name_groups = report_data['same_name_groups']
    exact_dups = report_data['exact_dups']
    videos = report_data['videos']
    largest_files = report_data['largest_files']
    folder_sizes = report_data['folder_sizes']
    empty_folders = report_data['empty_folders']
    file_types = report_data['file_types']
    
    recoverable_bytes = sum(group['wasted_size'] for group in exact_dups.values())
    recoverable_str, _ = format_size(recoverable_bytes)

    # Unique Output File Name Format: drive_cleanup_report - YYYY-MM-DD - HH-MM-SS.html
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H-%M-%S")
    output_file = f"drive_cleanup_report - {date_str} - {time_str}.html"

    # HTML Template Construction
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Drive Cleanup Report</title>
    <style>
        :root {{
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --border-color: #334155;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent-blue: #38bdf8;
            --accent-green: #34d399;
            --accent-yellow: #fbbf24;
            --accent-red: #f87171;
            --shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif; }}
        html {{ scroll-behavior: smooth; }}
        body {{ background: var(--bg-color); color: var(--text-primary); line-height: 1.6; padding: 24px; }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        header {{ background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 12px; padding: 28px; margin-bottom: 24px; box-shadow: var(--shadow); }}
        header h1 {{ font-size: 30px; color: var(--accent-blue); margin-bottom: 8px; }}
        header p {{ color: var(--text-secondary); font-size: 14px; }}
        .scan-warning {{ margin-top: 16px; padding: 12px 14px; border: 1px solid rgba(251, 191, 36, 0.35); background: rgba(251, 191, 36, 0.08); color: var(--accent-yellow); border-radius: 8px; font-size: 13px; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-top: 22px; }}
        .stat-card {{ background: rgba(15, 23, 42, 0.65); border: 1px solid var(--border-color); border-radius: 8px; padding: 16px; text-align: center; }}
        .stat-card h3 {{ font-size: 11px; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 5px; }}
        .stat-card .value {{ font-size: 23px; font-weight: 700; }}
        .green {{ color: var(--accent-green); }}
        .yellow {{ color: var(--accent-yellow); }}
        .red {{ color: var(--accent-red); }}
        .blue {{ color: var(--accent-blue); }}
        nav {{ display: flex; gap: 8px; margin-bottom: 24px; flex-wrap: wrap; position: sticky; top: 0; z-index: 10; background: rgba(15, 23, 42, 0.95); padding: 10px 0; backdrop-filter: blur(8px); }}
        nav a {{ background: var(--card-bg); color: var(--text-secondary); padding: 8px 12px; border-radius: 6px; text-decoration: none; border: 1px solid var(--border-color); font-size: 13px; transition: all 0.2s; }}
        nav a:hover {{ background: var(--accent-blue); color: var(--bg-color); border-color: var(--accent-blue); }}
        section {{ background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 12px; padding: 22px; margin-bottom: 24px; box-shadow: var(--shadow); }}
        section h2 {{ font-size: 20px; margin-bottom: 16px; color: var(--accent-blue); border-bottom: 1px solid var(--border-color); padding-bottom: 10px; }}
        .toolbar {{ display: flex; gap: 10px; margin-bottom: 14px; flex-wrap: wrap; }}
        .search-box, .select-box {{ flex: 1; min-width: 220px; background: #0f172a; color: var(--text-primary); border: 1px solid var(--border-color); border-radius: 6px; padding: 9px 11px; outline: none; }}
        .search-box:focus, .select-box:focus {{ border-color: var(--accent-blue); }}
        .table-wrapper {{ overflow-x: auto; }}
        table {{ width: 100%; border-collapse: collapse; text-align: left; font-size: 13px; min-width: 650px; }}
        th, td {{ padding: 11px; border-bottom: 1px solid var(--border-color); vertical-align: middle; }}
        th {{ color: var(--text-secondary); font-weight: 600; background: rgba(15, 23, 42, 0.25); }}
        tr:hover td {{ background: rgba(56, 189, 248, 0.035); }}
        tr:last-child td {{ border-bottom: none; }}
        .path {{ word-break: break-all; }}
        .size {{ white-space: nowrap; font-weight: 600; }}
        .btn-open {{ background: #2563eb; color: white; padding: 5px 11px; border-radius: 4px; text-decoration: none; font-size: 12px; display: inline-block; transition: background 0.2s; white-space: nowrap; }}
        .btn-open:hover {{ background: #1d4ed8; }}
        .group-container {{ background: rgba(15, 23, 42, 0.4); border: 1px solid var(--border-color); border-radius: 8px; margin-bottom: 14px; overflow: hidden; }}
        .group-header {{ display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 14px; cursor: pointer; background: rgba(36, 50, 71, 0.35); }}
        .group-header:hover {{ background: rgba(36, 50, 71, 0.65); }}
        .group-title {{ font-weight: 600; }}
        .group-content {{ padding: 0 14px 14px; display: block; }}
        .collapsed .group-content {{ display: none; }}
        .collapse-icon {{ transition: transform 0.2s; }}
        .collapsed .collapse-icon {{ transform: rotate(-90deg); }}
        .group-meta {{ color: var(--text-secondary); font-size: 12px; margin-top: 3px; }}
        .badge {{ background: rgba(56, 189, 248, 0.15); color: var(--accent-blue); padding: 3px 8px; border-radius: 4px; font-size: 11px; white-space: nowrap; }}
        .badge-warning {{ background: rgba(248, 113, 113, 0.15); color: var(--accent-red); }}
        .info-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }}
        .info-card {{ background: rgba(15, 23, 42, 0.4); border: 1px solid var(--border-color); border-radius: 8px; padding: 15px; }}
        .info-card h3 {{ font-size: 12px; color: var(--text-secondary); text-transform: uppercase; margin-bottom: 5px; }}
        .info-card p {{ font-size: 18px; font-weight: 700; }}
        footer {{ text-align: center; color: var(--text-secondary); font-size: 12px; margin-top: 35px; padding-top: 18px; border-top: 1px solid var(--border-color); }}
        @media (max-width: 700px) {{ body {{ padding: 12px; }} header, section {{ padding: 16px; }} nav {{ position: static; }} }}
    </style>
</head>
<body>
    <div class="container">
        <!-- HEADER -->
        <header>
            <h1>Drive Cleanup Report</h1>
            <p>
                <strong>Root Folder:</strong> {root_dir}
                &nbsp;&bull;&nbsp;
                <strong>Generated:</strong> {now.strftime("%B %d, %Y at %H:%M:%S")}
                &nbsp;&bull;&nbsp;
                <strong>Scan Time:</strong> {scan_duration}
            </p>
            <div class="scan-warning">
                This report only analyzes your files. No files or folders were deleted or modified automatically. Review the results manually before deleting anything.
            </div>
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>Total Storage</h3>
                    <div class="value">{total_size_str}</div>
                </div>
                <div class="stat-card">
                    <h3>Total Files</h3>
                    <div class="value">{total_files:,}</div>
                </div>
                <div class="stat-card">
                    <h3>Total Folders</h3>
                    <div class="value">{total_folders:,}</div>
                </div>
                <div class="stat-card">
                    <h3>Same-Name Groups</h3>
                    <div class="value yellow">{len(same_name_groups):,}</div>
                </div>
                <div class="stat-card">
                    <h3>Exact Duplicate Groups</h3>
                    <div class="value red">{len(exact_dups):,}</div>
                </div>
                <div class="stat-card">
                    <h3>Recoverable Space</h3>
                    <div class="value green">{recoverable_str}</div>
                </div>
            </div>
        </header>

        <!-- NAVIGATION -->
        <nav>
            <a href="#overview">Overview</a>
            <a href="#folder-sizes">Folder Sizes</a>
            <a href="#same-name">Same-Name</a>
            <a href="#exact-duplicates">Exact Duplicates</a>
            <a href="#videos">Videos</a>
            <a href="#largest-files">Largest Files</a>
            <a href="#file-types">File Types</a>
            <a href="#empty-folders">Empty Folders</a>
        </nav>

        <!-- OVERVIEW -->
        <section id="overview">
            <h2>Overview</h2>
            <div class="info-grid">
                <div class="info-card">
                    <h3>Largest File</h3>
                    <p>{largest_files[0]['size_str'] if largest_files else 'N/A'}</p>
                    <div class="group-meta">{largest_files[0]['rel_path'] if largest_files else 'N/A'}</div>
                </div>
                <div class="info-card">
                    <h3>Largest Folder</h3>
                    <p>{format_size(folder_sizes[0][1]['size'])[0] if folder_sizes else 'N/A'}</p>
                    <div class="group-meta">{folder_sizes[0][0] if folder_sizes else 'N/A'}</div>
                </div>
                <div class="info-card">
                    <h3>Video Storage</h3>
                    <p>{file_types.get('Videos', {'size_str': '0 B'})['size_str']}</p>
                    <div class="group-meta">{file_types.get('Videos', {'pct': '0%'})['pct']} of total storage</div>
                </div>
                <div class="info-card">
                    <h3>Exact Duplicate Storage</h3>
                    <p>{recoverable_str}</p>
                    <div class="group-meta">Potential recoverable space</div>
                </div>
            </div>
        </section>

        <!-- FOLDER SIZES -->
        <section id="folder-sizes">
            <h2>1. Folder Sizes</h2>
            <div class="toolbar">
                <input type="text" class="search-box" placeholder="Search folder..." onkeyup="filterTable('folderTable', this.value)">
                <select class="select-box" onchange="sortTable('folderTable', this.value)">
                    <option value="name">Sort by Name</option>
                    <option value="size-desc">Largest First</option>
                    <option value="size-asc">Smallest First</option>
                </select>
            </div>
            <div class="table-wrapper">
                <table id="folderTable">
                    <thead>
                        <tr>
                            <th>Folder Path</th>
                            <th style="width:150px;">Size</th>
                            <th style="width:120px;">Files</th>
                        </tr>
                    </thead>
                    <tbody>"""
    
    for f_path, data in folder_sizes[:100]:
        f_size_str, f_size_val = format_size(data['size'])
        html_content += f"""
                        <tr>
                            <td class="path">{f_path}</td>
                            <td class="size" data-size="{f_size_val}">{f_size_str}</td>
                            <td>{data['count']:,}</td>
                        </tr>"""

    html_content += f"""
                    </tbody>
                </table>
            </div>
        </section>

        <!-- SAME NAME FILES -->
        <section id="same-name">
            <h2>2. Same-Name Files (Level 1)</h2>
            <p style="color: var(--text-secondary); font-size: 13px; margin-bottom: 15px;">
                Files are grouped only by filename. Their contents may be completely different. Review them manually before deleting anything.
            </p>"""

    for name, items in list(same_name_groups.items())[:50]:
        html_content += f"""
            <div class="group-container">
                <div class="group-header" onclick="toggleGroup(this)">
                    <div>
                        <div class="group-title">{name}</div>
                        <div class="group-meta">{len(items)} locations</div>
                    </div>
                    <div>
                        <span class="badge">Same Name</span>
                        <span class="collapse-icon">▼</span>
                    </div>
                </div>
                <div class="group-content">
                    <div class="table-wrapper">
                        <table>
                            <thead>
                                <tr>
                                    <th>Location</th>
                                    <th style="width:120px;">Size</th>
                                    <th style="width:90px;text-align:center;">Action</th>
                                </tr>
                            </thead>
                            <tbody>"""
        for item in items:
            item_size_str, _ = format_size(item['size'])
            file_url = f"file:///{item['path'].replace(os.sep, '/')}"
            html_content += f"""
                                <tr>
                                    <td class="path">{item['rel_path']}</td>
                                    <td class="size">{item_size_str}</td>
                                    <td style="text-align:center;">
                                        <a href="{file_url}" class="btn-open">Open</a>
                                    </td>
                                </tr>"""
        html_content += f"""
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>"""

    html_content += f"""
        </section>

        <!-- EXACT DUPLICATES -->
        <section id="exact-duplicates">
            <h2>3. Exact Duplicates (Level 2)</h2>
            <p style="color:var(--text-secondary);font-size:13px;margin-bottom:15px;">
                These files have identical content based on their file hash.
            </p>"""

    for name, group in list(exact_dups.items())[:50]:
        wasted_str, _ = format_size(group['wasted_size'])
        html_content += f"""
            <div class="group-container">
                <div class="group-header" onclick="toggleGroup(this)">
                    <div>
                        <div class="group-title">{name}</div>
                        <div class="group-meta">SHA-256: <code>{group['hash'][:16]}...</code></div>
                    </div>
                    <div>
                        <span class="badge badge-warning">Potential Saving: {wasted_str}</span>
                        <span class="collapse-icon">▼</span>
                    </div>
                </div>
                <div class="group-content">
                    <div class="table-wrapper">
                        <table>
                            <thead>
                                <tr>
                                    <th>Location</th>
                                    <th style="width:120px;">Size</th>
                                    <th style="width:90px;text-align:center;">Action</th>
                                </tr>
                            </thead>
                            <tbody>"""
        for item in group['items']:
            item_size_str, _ = format_size(item['size'])
            file_url = f"file:///{item['path'].replace(os.sep, '/')}"
            html_content += f"""
                                <tr>
                                    <td class="path">{item['rel_path']}</td>
                                    <td class="size">{item_size_str}</td>
                                    <td style="text-align:center;">
                                        <a href="{file_url}" class="btn-open">Open</a>
                                    </td>
                                </tr>"""
        html_content += f"""
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>"""

    html_content += f"""
        </section>

        <!-- VIDEOS -->
        <section id="videos">
            <h2>4. Video Files</h2>
            <div class="toolbar">
                <input type="text" class="search-box" placeholder="Search video..." onkeyup="filterTable('videoTable', this.value)">
                <select class="select-box" onchange="sortTable('videoTable', this.value)">
                    <option value="name">Sort by Name</option>
                    <option value="size-desc">Largest First</option>
                    <option value="size-asc">Smallest First</option>
                </select>
            </div>
            <div class="table-wrapper">
                <table id="videoTable">
                    <thead>
                        <tr>
                            <th>Folder</th>
                            <th>File Name</th>
                            <th style="width:120px;">Size</th>
                            <th style="width:90px;text-align:center;">Action</th>
                        </tr>
                    </thead>
                    <tbody>"""

    for v in videos[:100]:
        v_size_str, v_size_val = format_size(v['size'])
        parent_dir = str(Path(v['rel_path']).parent).replace('\\', '/')
        file_url = f"file:///{v['path'].replace(os.sep, '/')}"
        html_content += f"""
                        <tr>
                            <td class="path">{parent_dir if parent_dir != '.' else ''}</td>
                            <td>{v['name']}</td>
                            <td class="size" data-size="{v_size_val}">{v_size_str}</td>
                            <td style="text-align:center;"><a href="{file_url}" class="btn-open">Open</a></td>
                        </tr>"""

    html_content += f"""
                    </tbody>
                </table>
            </div>
        </section>

        <!-- LARGEST FILES -->
        <section id="largest-files">
            <h2>5. Largest Files</h2>
            <div class="table-wrapper">
                <table id="largestFilesTable">
                    <thead>
                        <tr>
                            <th>Location</th>
                            <th style="width:120px;">Size</th>
                            <th style="width:90px;text-align:center;">Action</th>
                        </tr>
                    </thead>
                    <tbody>"""

    for lf in largest_files[:30]:
        file_url = f"file:///{lf['path'].replace(os.sep, '/')}"
        html_content += f"""
                        <tr>
                            <td class="path">{lf['rel_path']}</td>
                            <td class="size">{lf['size_str']}</td>
                            <td style="text-align:center;"><a href="{file_url}" class="btn-open">Open</a></td>
                        </tr>"""

    html_content += f"""
                    </tbody>
                </table>
            </div>
        </section>

        <!-- FILE TYPES -->
        <section id="file-types">
            <h2>6. Storage by File Type</h2>
            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>Category</th>
                            <th>Extensions</th>
                            <th>Files</th>
                            <th>Storage</th>
                            <th>Percentage</th>
                        </tr>
                    </thead>
                    <tbody>"""

    for cat, info in file_types.items():
        exts_str = ", ".join(info['exts'])
        html_content += f"""
                        <tr>
                            <td>{cat}</td>
                            <td>{exts_str}</td>
                            <td>{info['count']:,}</td>
                            <td>{info['size_str']}</td>
                            <td>{info['pct']}</td>
                        </tr>"""

    html_content += f"""
                    </tbody>
                </table>
            </div>
        </section>

        <!-- EMPTY FOLDERS -->
        <section id="empty-folders">
            <h2>7. Empty Folders</h2>
            <p style="color:var(--text-secondary);font-size:13px;margin-bottom:15px;">
                These folders contain no files or subfolders.
            </p>
            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>Folder Path</th>
                            <th style="width:90px;text-align:center;">Action</th>
                        </tr>
                    </thead>
                    <tbody>"""

    for ef in empty_folders[:50]:
        folder_url = f"file:///{Path(root_dir, ef).resolve().as_posix()}"
        html_content += f"""
                        <tr>
                            <td class="path">{ef}</td>
                            <td style="text-align:center;"><a href="{folder_url}" class="btn-open">Open</a></td>
                        </tr>"""

    html_content += f"""
                    </tbody>
                </table>
            </div>
        </section>

        <footer>
            Drive Cleanup Report &bull; Standalone Python Tool &bull; No automatic deletion
        </footer>
    </div>

    <script>
        function toggleGroup(header) {{
            const container = header.parentElement;
            container.classList.toggle('collapsed');
        }}

        function filterTable(tableId, query) {{
            const table = document.getElementById(tableId);
            const trs = table.getElementsByTagName('tr');
            const q = query.toLowerCase();
            for (let i = 1; i < trs.length; i++) {{
                let text = trs[i].textContent.toLowerCase();
                trs[i].style.display = text.includes(q) ? '' : 'none';
            }}
        }}

        function sortTable(tableId, sortBy) {{
            const table = document.getElementById(tableId);
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            
            rows.sort((a, b) => {{
                if (sortBy === 'name') {{
                    let textA = a.cells[0].textContent.trim();
                    let textB = b.cells[0].textContent.trim();
                    return textA.localeCompare(textB);
                }} else if (sortBy === 'size-desc' || sortBy === 'size-asc') {{
                    let sizeA = parseFloat(a.querySelector('.size')?.getAttribute('data-size') || 0);
                    let sizeB = parseFloat(b.querySelector('.size')?.getAttribute('data-size') || 0);
                    return sortBy === 'size-desc' ? sizeB - sizeA : sizeA - sizeB;
                }}
                return 0;
            }});
            
            rows.forEach(row => tbody.appendChild(row));
        }}
    </script>
</body>
</html>
"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"[Success] New report generated: {output_file}")


def main():
    print("==========================================")
    print("         Drive Cleanup Scanner            ")
    print("==========================================")
    
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]
    else:
        root_dir = input("Enter directory path to scan (e.g., D:\\MyDrive or . for current folder): ").strip()
        if not root_dir:
            root_dir = "."

    start_time = time.time()
    
    files_list, total_folders = collect_files(root_dir)
    total_files = len(files_list)
    total_size_bytes = sum(f['size'] for f in files_list)
    
    print(f"Found {total_files:,} files across {total_folders:,} folders.")

    folder_sizes = calculate_folder_sizes(files_list, root_dir)

    print("Analyzing same-name files...")
    same_name_groups = find_same_name_files(files_list)

    print("Detecting exact duplicates (hashing files)...")
    exact_dups = find_exact_duplicates(files_list)

    videos = identify_videos(files_list)

    sorted_largest = sorted(files_list, key=lambda x: x['size'], reverse=True)
    largest_files = []
    for f in sorted_largest:
        f_str, _ = format_size(f['size'])
        largest_files.append({**f, 'size_str': f_str})

    print("Checking empty folders...")
    empty_folders = find_empty_folders(root_dir)

    categories = {
        'Videos': {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v'},
        'Archives': {'.zip', '.rar', '.7z', '.tar', '.gz'},
        'Documents': {'.pdf', '.docx', '.xlsx', '.pptx', '.txt', '.odt'},
        'Images': {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.svg'}
    }
    
    cat_stats = defaultdict(lambda: {'count': 0, 'size': 0, 'exts': set()})
    other_stats = {'count': 0, 'size': 0, 'exts': set()}
    
    for f in files_list:
        ext = f['extension']
        matched = False
        for cat, exts in categories.items():
            if ext in exts:
                cat_stats[cat]['count'] += 1
                cat_stats[cat]['size'] += f['size']
                cat_stats[cat]['exts'].add(ext)
                matched = True
                break
        if not matched:
            other_stats['count'] += 1
            other_stats['size'] += f['size']
            if ext:
                other_stats['exts'].add(ext)
                
    file_types = {}
    for cat, info in cat_stats.items():
        size_str, _ = format_size(info['size'])
        pct = f"{(info['size'] / total_size_bytes * 100):.0f}%" if total_size_bytes > 0 else "0%"
        file_types[cat] = {'count': info['count'], 'size_str': size_str, 'pct': pct, 'exts': list(info['exts'])}
        
    other_size_str, _ = format_size(other_stats['size'])
    other_pct = f"{(other_stats['size'] / total_size_bytes * 100):.0f}%" if total_size_bytes > 0 else "0%"
    file_types['Other'] = {'count': other_stats['count'], 'size_str': other_size_str, 'pct': other_pct, 'exts': ['Other extensions']}

    end_time = time.time()
    elapsed_secs = int(end_time - start_time)
    scan_duration = f"{elapsed_secs // 3600:02d}:{(elapsed_secs % 3600) // 60:02d}:{elapsed_secs % 60:02d}"

    report_data = {
        'root_dir': os.path.abspath(root_dir),
        'scan_duration': scan_duration,
        'total_size': total_size_bytes,
        'total_files': total_files,
        'total_folders': total_folders,
        'same_name_groups': same_name_groups,
        'exact_dups': exact_dups,
        'videos': videos,
        'largest_files': largest_files,
        'folder_sizes': folder_sizes,
        'empty_folders': empty_folders,
        'file_types': file_types
    }

    generate_html(report_data)

if __name__ == '__main__':
    main()