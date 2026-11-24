# ShiftLens

A workshop quality tracker built with Python, Django, SQLite, HTML, CSS and JavaScript. The idea draws on practical experience operating a semi-automatic lathe in automotive manufacturing. The example records are fictional.

## What you can do

- Record a day or night shift for one machine and component.
- Select a machine or week, review daily output and inspect rejection reasons.
- Compare all machines by their weekly rejection rates, including tied defect reasons.
- Read the same weekly machine summary as JSON at `/api/weekly/?date=2026-11-23`.

## Run locally on Windows

From the project folder in PowerShell, using Python 3.12:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py loaddata workshop_demo
.\.venv\Scripts\python.exe manage.py test
.\.venv\Scripts\python.exe manage.py runserver
```

Load the fixture into a fresh database. Open [the sample report](http://127.0.0.1:8000/?date=2026-11-23) on the computer running the server. Select **Cylindrical grinder** to see 195 parts made, five rejected and a 97.4% inspection pass rate. The eight machines in the demo represent one example workshop.

## How the report works

Each saved row belongs to one date, shift period, machine and component. That combination must be unique. Rejected parts are counted once by their main defect, and their total cannot exceed production. The weekly pass rate is 100 times total accepted divided by total produced. A zero-output period has no pass rate.

The source is in `tracker/`. Start with `models.py` for the record, `forms.py` for data entry, `reports.py` for calculations, `views.py` for web requests and `tests.py` for the six automated tests. Settings are for a local demo.
