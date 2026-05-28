"""
refresh_data.py — Pull fresh data from Salesforce and rebuild dashboard_data.json + dashboard.html

Queries:
  1. All Relationship__c rows (Type__c = 'Souled Coach') → rels + unique coach/student IDs
  2. Coach contacts → name, months employed
  3. Student contacts → name, SO/STAM/seminary/confirmed status

Then writes dashboard_data.json and runs generate_dashboard.py.

Usage:
    python3 refresh_data.py

Requires:
    - sf CLI authenticated as yspolter-admin
    - Run from the souled-coach-outcomes project directory (or any dir)
"""

import json
import os
import subprocess
import sys
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TARGET_ORG = "yspolter-admin"
DAYS_PER_MONTH = 30.44167  # average days per month

# On Windows, the sf CLI is a .cmd file — use shell=True or the full .cmd path
import shutil
SF_CMD = shutil.which("sf") or "sf"  # resolves to sf.cmd on Windows


def run_soql(query):
    """Run a SOQL query via sf CLI, return list of records. Handles all pagination."""
    result = subprocess.run(
        [SF_CMD, "data", "query", "--query", query, "--target-org", TARGET_ORG, "--json"],
        capture_output=True,
        text=True,
        shell=False,
    )
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"Failed to parse SF CLI output.\nstdout: {result.stdout[:500]}\nstderr: {result.stderr[:500]}", file=sys.stderr)
        sys.exit(1)
    if data.get("status") != 0:
        print(f"SOQL error: {data.get('message', 'unknown')}", file=sys.stderr)
        print(f"Query was: {query}", file=sys.stderr)
        sys.exit(1)
    records = data["result"]["records"]
    # Strip the attributes wrapper each record gets
    return records


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def id_list(ids):
    """Format a list of SF IDs for use in a SOQL IN clause."""
    return "('" + "','".join(ids) + "')"


# ---------------------------------------------------------------------------
# Step 1: Relationships
# ---------------------------------------------------------------------------
print("Step 1: Fetching Souled Coach relationships...")
rels_raw = run_soql(
    "SELECT Mentor__c, Student__c, Touch_Points__c "
    "FROM Relationship__c "
    "WHERE Type__c = 'Souled Coach'"
)
print(f"  {len(rels_raw)} relationship rows retrieved")

rels = []
coach_ids = set()
student_ids = set()

for r in rels_raw:
    c_id = r.get("Mentor__c")
    s_id = r.get("Student__c")
    tp = r.get("Touch_Points__c") or 0
    if c_id and s_id:
        rels.append({"c": c_id, "s": s_id, "t": int(tp)})
        coach_ids.add(c_id)
        student_ids.add(s_id)

print(f"  {len(coach_ids)} unique coaches, {len(student_ids)} unique students")

# ---------------------------------------------------------------------------
# Step 2: Coaches
# ---------------------------------------------------------------------------
print("Step 2: Fetching coach contact details...")
coaches = {}
coach_id_list = list(coach_ids)

for batch in chunks(coach_id_list, 200):
    records = run_soql(
        f"SELECT Id, Name, Days_Employed__c "
        f"FROM Contact "
        f"WHERE Id IN {id_list(batch)} "
        f"AND Test_Old__c = false "
        f"AND (NOT Name LIKE '%test%')"
    )
    for r in records:
        days = r.get("Days_Employed__c")
        me = round(days / DAYS_PER_MONTH, 1) if days else None
        mes = "employed" if days else "first_meeting"
        coaches[r["Id"]] = {"i": r["Id"], "n": r["Name"], "me": me, "mes": mes}

print(f"  {len(coaches)} coaches loaded")

# ---------------------------------------------------------------------------
# Step 3: Students
# ---------------------------------------------------------------------------
print("Step 3: Fetching student contact details (in batches of 200)...")
students = {}
student_id_list = list(student_ids)
batch_count = 0

for batch in chunks(student_id_list, 200):
    batch_count += 1
    records = run_soql(
        f"SELECT Id, Name, "
        f"Date_Became_SO__c, Date_Became_STAM__c, "
        f"Months_in_Seminary__c, "
        f"SO_Confirmed__c, STAM_Confirmed__c "
        f"FROM Contact "
        f"WHERE Id IN {id_list(batch)} "
        f"AND Test_Old__c = false "
        f"AND (NOT Name LIKE '%test%')"
    )
    for r in records:
        sm_raw = r.get("Months_in_Seminary__c") or 0
        students[r["Id"]] = {
            "n": r["Name"],
            "so": r.get("Date_Became_SO__c") is not None,
            "st": r.get("Date_Became_STAM__c") is not None,
            "sm": round(float(sm_raw), 1) if sm_raw else 0,
            "sc": bool(r.get("SO_Confirmed__c")),
            "tc": bool(r.get("STAM_Confirmed__c")),
        }
    print(f"  Batch {batch_count}: {len(records)} contacts loaded (total {len(students)})")

print(f"  {len(students)} students total")

# ---------------------------------------------------------------------------
# Step 4: Build dashboard_data.json
# ---------------------------------------------------------------------------
print("Step 4: Writing dashboard_data.json...")

# Summary stats
so_count = sum(1 for s in students.values() if s["so"])
st_count = sum(1 for s in students.values() if s["st"])
sc_count = sum(1 for s in students.values() if s["sc"])
tc_count = sum(1 for s in students.values() if s["tc"])
print(f"  SO: {so_count}  STAM: {st_count}  SO confirmed: {sc_count}  STAM confirmed: {tc_count}")

dashboard_data = {
    "coaches": sorted(coaches.values(), key=lambda c: c["n"]),
    "rels": rels,
    "students": students,
}

out_path = os.path.join(BASE_DIR, "dashboard_data.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(dashboard_data, f, separators=(",", ":"))
size_kb = os.path.getsize(out_path) / 1024
print(f"  Written {size_kb:.0f} KB to dashboard_data.json")

# ---------------------------------------------------------------------------
# Step 5: Regenerate dashboard.html
# ---------------------------------------------------------------------------
print("Step 5: Regenerating dashboard.html...")
gen_script = os.path.join(BASE_DIR, "generate_dashboard.py")
result = subprocess.run(
    [sys.executable, gen_script],
    capture_output=True,
    text=True,
    cwd=BASE_DIR,
)
if result.returncode != 0:
    print(f"generate_dashboard.py failed:\n{result.stderr}", file=sys.stderr)
    sys.exit(1)
print(f"  {result.stdout.strip()}")

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------
today = datetime.date.today().isoformat()
print(f"\nDone! Data as of {today}.")
print(f"  Coaches: {len(coaches)}, Students: {len(students)}, Relationships: {len(rels)}")
print(f"  SO outcomes: {so_count} ({sc_count} manager-confirmed)")
print(f"  STAM outcomes: {st_count} ({tc_count} manager-confirmed)")
print(f"\nNext step: commit dashboard.html and push.")
