# Transfer Pathway Optimizer

 **An automated degree planning engine for transfer students.**  Built with Python, Flask, Pandas, and pdfplumber.

# The Problem
Transfer students often struggle to decipher "Program Reports" from community colleges. Course codes (e.g., `GOVT 2305`) are buried in unstructured text, and students frequently accidentally schedule prerequisites out of order or overload their semesters with too many STEM classes.

# The Solution
I engineered a full-stack web application that parses raw PDF transcripts and generates a mathematically optimized semester schedule using a **Topological Sort-inspired algorithm**.

### Key Features
  Intelligent PDF Parsing: Uses regex pattern matching to extract course codes, completion status, and "Select One" elective groups from unstructured PDF blobs.
 Academic Load Balancing:The scheduler algorithm enforces a limit of **3 STEM classes per semester** and strictly prevents "Subject Overloading" (e.g., taking Calculus II and Discrete Math simultaneously) to ensure student success.
Prerequisite Enforcement: Implements a directed dependency graph for course sequences (e.g., `Physics I` must be completed before `Physics II`).
Summer Logic: Automatically detects short summer semesters and bans heavy 16-week lab courses (Physics/Chemistry) from being scheduled during those terms.


## Run it locally

This app parses PDFs on a Python server, so there's no hosted demo. A sample report (`Sample_Program_Report.pdf`) is included to try it.

```bash
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000 and upload the sample report.
