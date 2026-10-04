# Drive_Cleanup_Scanner

Find duplicate files, identify large folders, spot empty directories, and analyze storage usage across a drive or folder using Python.

![GitHub repo size](https://img.shields.io/github/repo-size/TashinParvez/drive_cleanup_scanner)
![GitHub contributors](https://img.shields.io/github/contributors/TashinParvez/drive_cleanup_scanner)
![GitHub last commit](https://img.shields.io/github/last-commit/TashinParvez/drive_cleanup_scanner)
![Visitor Count](https://visitor-badge.laobi.icu/badge?page_id=TashinParvez.drive_cleanup_scanner)

<img width="1376" height="768" alt="img" src="https://github.com/user-attachments/assets/3a25aebd-de46-471d-a662-6c3b80f1f7ec" />

A practical Python tool for disk cleanup, duplicate detection, and storage analysis. It scans a folder recursively, collects file metadata, checks for same-name files, detects exact duplicates by SHA-256 hash, highlights video files, finds empty folders, and exports a detailed HTML report for manual review.

This project is especially useful for people who want to:

- free up disk space on Windows or local drives
- find duplicate photos, videos, and documents
- review large folders before deleting anything
- analyze storage usage without automatic deletion
- generate a readable HTML cleanup report

---

## Why This Project Is Useful

Storage clutter is one of the most common reasons people lose disk space without realizing it. Duplicate files, large media folders, and empty directories often build up over time on laptops, external drives, and shared storage.

This scanner helps by giving a clear overview of:

- total storage used
- biggest folders and files
- duplicate filenames across locations
- identical files by content hash
- video files taking space
- empty folders that can be cleaned up
- file type distribution such as images, videos, archives, and documents

Unlike a “delete everything” utility, this tool focuses on analysis and reporting first, making it safer and more useful for manual cleanup decisions.

---

## Key Features

- Recursive folder scan of any selected path
- Total file and folder counting
- Folder size analysis from root down to subfolders
- Same-name file detection (Level 1)
- Exact duplicate detection using SHA-256 hash (Level 2)
- Video file listing and size breakdown
- Largest files overview
- Empty folder detection
- Storage by file type summary
- Standalone HTML report generation with filters and sorting
- No automatic deletion; everything is reviewed manually

---

## How It Works

The script walks through every file and folder under the chosen root directory, gathers metadata such as:

- file name
- relative path
- file size
- file extension
- parent folder

Then it performs several analysis layers:

1. Folder size aggregation  
   Totals are accumulated for each folder and subfolder.

2. Same-name detection  
   Files with the same filename are grouped together for review.

3. Exact duplicate detection  
   Files are hashed using SHA-256 to detect exact content duplicates even when names differ.

4. Video detection  
   Video extensions such as `.mp4`, `.mkv`, `.avi`, `.mov`, and `.webm` are flagged.

5. Empty folder detection  
   Any folder with no files and no child folders is identified.

6. HTML report generation  
   The final result is saved as an interactive HTML report with clean tables and filters.

---

## Project Files

- `drive_scanner.py` — main Python script
- generated HTML reports — output examples created by the scanner

---

## Installation

### Requirements

- Python 3.8+
- A local folder or drive to scan

### Clone the Repository

```bash
git clone https://github.com/TashinParvez/my-drive-scanner.git
cd my-drive-scanner
```

No additional dependencies are required for the default script.

---

## Usage

Run the script from the terminal:

```bash
python drive_scanner.py
```

Or pass a folder directly:

```bash
python drive_scanner.py "D:\MyDrive"
```

For the current folder:

```bash
python drive_scanner.py .
```

The script will scan the selected location and generate a timestamped HTML report in the same directory, such as:

```bash
drive_cleanup_report - 2026-10-04 - 15-49-10.html
```

Then open the report in a browser to inspect:

- folder sizes
- same-name files
- exact duplicates
- large files
- video files
- empty folders
- file type breakdown

---

## Example Workflow

1. Open a terminal in the project folder.
2. Run:

```bash
python drive_scanner.py "E:\T&R\02. holud"
```

3. Wait for scanning to finish.
4. Open the generated HTML report.
5. Review duplicate or oversized content manually.
6. Delete only the items you confirm are safe to remove.

---

## What the Report Shows

The generated HTML report is designed to be readable and actionable:

- total storage used
- total files and folders found
- same-name duplicates
- exact content duplicates
- largest files
- largest folders
- file type distribution
- empty folders
- quick Open links for files and folders

This gives users a practical way to decide what to keep and what to clean up without risking important data.

---

## Why This Is Great for Search and GitHub Visibility

This project is intentionally written with search-friendly keywords relevant to real user problems, such as:

- duplicate file finder
- disk space analyzer
- drive cleanup tool
- folder size checker
- Python duplicate detector
- clean up large folders
- find empty folders
- remove duplicate files safely
- disk usage report generator

Using clear project naming and descriptive documentation increases the chance that people searching for practical storage-cleanup tools will discover the repository on GitHub and search engines.

---

## Best Use Cases

This tool is suitable for:

- cleaning up personal computers and laptops
- reviewing large external drives
- organizing family or team storage folders
- identifying duplicate media files
- preparing large folders for archiving
- understanding where disk space is being used

---

## Safety Note

This tool is designed for analysis, not automatic deletion.

It does not remove files or folders itself. That makes it safer for users who want to inspect file quality and storage usage before making cleanup decisions.

---

## License

This project is available for personal and educational use.

---

## Contact Me

Reach out for questions, suggestions, or feedback:

<p align="left">
  <a href="mailto:tashinparvez2002@gmail.com" target="_blank">
    <img src="https://img.shields.io/badge/Email-0078D4?style=for-the-badge&logo=gmail&logoColor=white" alt="Email" />
  </a>
  <a href="https://linkedin.com/in/tashinparvez" target="_blank">
    <img src="https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn" />
  </a>
</p>


---

## Final Note

If your goal is to clean up files safely, understand where your disk space is going, and find duplicate content quickly, this project is a simple and effective solution.

It is especially useful for developers, students, photographers, and anyone managing large personal storage folders.
