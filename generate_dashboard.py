"""Generate the Souled Coach Outcomes dashboard HTML with embedded data."""
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, 'dashboard_data.json')) as f:
    data_json = f.read()

html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Souled Coach Outcomes Report</title>
<style>
  :root {
    --bg: #f8f9fa; --card-bg: #fff; --text: #1a1a2e;
    --border: #e0e0e0; --accent: #4361ee; --green: #2d9a4e;
    --blue: #2563eb; --purple: #7c3aed; --orange: #ea580c;
    --row-alt: #f8fafc; --hover: #eef2ff;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: var(--bg); color: var(--text); line-height: 1.5; }
  .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
  h1 { font-size: 1.8rem; font-weight: 700; margin-bottom: 4px; }
  .subtitle { color: #666; font-size: 0.95rem; margin-bottom: 20px; }
  .controls { background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; padding: 20px; margin-bottom: 20px; display: flex; gap: 40px; flex-wrap: wrap; align-items: flex-end; }
  .control-group { display: flex; flex-direction: column; gap: 6px; }
  .control-group label { font-size: 0.85rem; font-weight: 600; color: #555; }
  .control-row { display: flex; align-items: center; gap: 10px; }
  .control-row input[type=range] { width: 180px; accent-color: var(--accent); }
  .control-row .val { font-size: 1.1rem; font-weight: 700; color: var(--accent); min-width: 30px; text-align: center; }
  .control-row input[type=number] { width: 70px; padding: 4px 8px; border: 1px solid var(--border); border-radius: 6px; font-size: 0.95rem; text-align: center; }
  .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin-bottom: 20px; }
  .card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; padding: 16px; text-align: center; }
  .card .num { font-size: 2rem; font-weight: 800; }
  .card .lbl { font-size: 0.8rem; color: #666; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }
  .card.so .num { color: var(--green); }
  .card.stam .num { color: var(--blue); }
  .card.ay .num { color: var(--purple); }
  .card.any .num { color: var(--orange); }
  .table-wrap { background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; overflow: hidden; }
  table { width: 100%; border-collapse: collapse; }
  th { background: #f1f3f5; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.5px; padding: 12px 16px; text-align: left; font-weight: 600; color: #555; border-bottom: 2px solid var(--border); cursor: pointer; user-select: none; white-space: nowrap; position: relative; }
  th[title]:hover::after { content: attr(title); position: absolute; left: 0; top: 100%; z-index: 10; background: #333; color: #fff; font-size: 0.75rem; font-weight: 400; text-transform: none; letter-spacing: 0; padding: 8px 12px; border-radius: 6px; max-width: 260px; white-space: normal; line-height: 1.4; box-shadow: 0 2px 8px rgba(0,0,0,0.2); }
  th:hover { background: #e8eaed; }
  th .arrow { font-size: 0.7rem; margin-left: 4px; opacity: 0.4; }
  th.sorted .arrow { opacity: 1; }
  td { padding: 10px 16px; border-bottom: 1px solid #f0f0f0; font-size: 0.95rem; }
  tr:nth-child(even) td { background: var(--row-alt); }
  tr:hover td { background: var(--hover); }
  tr.totals td { font-weight: 700; background: #f1f3f5 !important; border-top: 2px solid var(--border); }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 0.75rem; font-weight: 600; }
  .badge-so { background: #dcfce7; color: var(--green); }
  .badge-stam { background: #dbeafe; color: var(--blue); }
  .badge-ay { background: #ede9fe; color: var(--purple); }
  .expand-btn { cursor: pointer; color: var(--accent); font-weight: 600; }
  .expand-btn:hover { text-decoration: underline; }
  .student-detail td { padding: 0 !important; background: #fafbfc !important; }
  .student-list { padding: 8px 16px 8px 40px; }
  .student-list table { font-size: 0.85rem; }
  .student-list th { background: #eef0f2; padding: 6px 10px; font-size: 0.75rem; cursor: default; }
  .student-list td { padding: 6px 10px; }
  .rate-cell { white-space: nowrap; }
  .rate-bar-bg { display: inline-block; width: 60px; height: 14px; background: #eee; border-radius: 7px; vertical-align: middle; margin-right: 8px; overflow: hidden; }
  .rate-bar { height: 100%; border-radius: 7px; transition: width 0.3s; }
  .rate-val { font-weight: 700; font-size: 0.95rem; vertical-align: middle; }
  .data-note { text-align: center; color: #999; font-size: 0.8rem; margin-top: 16px; }
  @media (max-width: 768px) {
    .controls { flex-direction: column; gap: 16px; }
    .summary { grid-template-columns: repeat(2, 1fr); }
    td, th { padding: 8px 10px; font-size: 0.85rem; }
  }
</style>
</head>
<body>
<div class="container">
  <h1>Souled Coach Outcomes Report</h1>
  <p class="subtitle">Student outcomes by coach &mdash; SO (Shomer Shabbos), STAM (Shomer Torah and Mitzvos), and AY (Attended Yeshiva/Seminary)</p>

  <div class="controls">
    <div class="control-group">
      <label>Minimum Meetings to Count as Coach's Student</label>
      <div class="control-row">
        <input type="range" id="minMeetings" min="1" max="50" value="3">
        <span class="val" id="minMeetingsVal">3</span>
        <input type="number" id="minMeetingsNum" min="1" max="200" value="3" title="Type a custom value">
      </div>
    </div>
    <div class="control-group">
      <label>Minimum Seminary Months for AY</label>
      <div class="control-row">
        <input type="range" id="minSemMonths" min="0.1" max="24" step="0.1" value="1">
        <span class="val" id="minSemMonthsVal">1</span>
        <input type="number" id="minSemMonthsNum" min="0.1" max="60" step="0.1" value="1" title="Type a custom value">
      </div>
    </div>
    <div class="control-group">
      <label>Outcome Rate Based On</label>
      <div class="control-row">
        <select id="rateMetric" style="padding:4px 8px;border:1px solid var(--border);border-radius:6px;font-size:0.95rem;">
          <option value="any" selected>Any Outcome</option>
          <option value="so">SO Only</option>
          <option value="stam">STAM Only</option>
          <option value="ay">AY Only</option>
        </select>
      </div>
    </div>
    <div class="control-group">
      <label>Minimum Total Meetings (any coach) to Include Student</label>
      <div class="control-row">
        <input type="range" id="minTotalMeetings" min="1" max="50" value="1">
        <span class="val" id="minTotalMeetingsVal">1</span>
        <input type="number" id="minTotalMeetingsNum" min="1" max="200" value="1" title="Type a custom value">
      </div>
    </div>
    <div class="control-group" style="justify-content:flex-end;">
      <label style="display:flex;align-items:center;gap:8px;cursor:pointer;font-size:0.9rem;font-weight:600;color:#555;">
        <input type="checkbox" id="confirmedOnly" style="width:16px;height:16px;accent-color:var(--accent);cursor:pointer;">
        Manager-confirmed outcomes only
      </label>
      <div style="font-size:0.75rem;color:#999;margin-top:2px;">Only count SO/STAM students confirmed by a manager</div>
    </div>
  </div>

  <div class="summary">
    <div class="card"><div class="num" id="sumCoaches">0</div><div class="lbl">Coaches</div></div>
    <div class="card"><div class="num" id="sumStudents">0</div><div class="lbl">Unique Students</div></div>
    <div class="card so"><div class="num" id="sumSO">0</div><div class="lbl">Became SO</div></div>
    <div class="card stam"><div class="num" id="sumSTAM">0</div><div class="lbl">Became STAM</div></div>
    <div class="card ay"><div class="num" id="sumAY">0</div><div class="lbl">Attended Seminary</div></div>
    <div class="card any"><div class="num" id="sumAny">0</div><div class="lbl">Any Outcome</div></div>
  </div>

  <div class="table-wrap">
    <table id="mainTable">
      <thead>
        <tr>
          <th data-col="name">Coach Name <span class="arrow">&#9650;</span></th>
          <th data-col="me" title="How many months this coach has been employed by Souled. Helps contextualize raw outcome counts &mdash; veteran coaches have had more time to accumulate outcomes.">Months Employed <span class="arrow">&#9650;</span></th>
          <th data-col="students" title="Number of students who had at least the minimum number of meetings with this coach">Students <span class="arrow">&#9650;</span></th>
          <th data-col="so" title="Students who became Shomer Shabbos">SO <span class="arrow">&#9650;</span></th>
          <th data-col="stam" title="Students who became Shomer Torah and Mitzvos">STAM <span class="arrow">&#9650;</span></th>
          <th data-col="ay" title="Students who attended yeshiva/seminary for at least the minimum months">AY <span class="arrow">&#9650;</span></th>
          <th data-col="any" title="Students who achieved at least one outcome (SO, STAM, or AY)">Any Outcome <span class="arrow">&#9650;</span></th>
          <th data-col="rate" class="sorted" title="Percentage of this coach's students who achieved any outcome &mdash; normalizes for how long a coach has been working">Outcome Rate <span class="arrow">&#9660;</span></th>
        </tr>
      </thead>
      <tbody id="tableBody"></tbody>
    </table>
  </div>

  <p class="data-note">Data fetched from Salesforce on 2026-04-16. Click a coach name to expand student details. Use controls to adjust thresholds &mdash; table updates instantly.</p>
</div>

<script>
const DATA = __DATA_PLACEHOLDER__;

let sortCol = 'rate', sortDir = -1;
let expandedCoach = null;

function compute(minMeetings, minSemMonths, minTotalMeetings, rateMetric, confirmedOnly) {
  // First, compute total meetings per student across all coaches
  var studentTotalMeetings = {};
  DATA.rels.forEach(function(r) {
    if (!studentTotalMeetings[r.s]) studentTotalMeetings[r.s] = 0;
    studentTotalMeetings[r.s] += (r.t || 0);
  });

  const coachMap = {};
  DATA.coaches.forEach(function(c) { coachMap[c.i] = { id: c.i, name: c.n, me: c.me, studentMap: {} }; });

  DATA.rels.forEach(function(r) {
    if (r.t >= minMeetings && coachMap[r.c] && (studentTotalMeetings[r.s] || 0) >= minTotalMeetings) {
      // Keep highest touch points if duplicate
      if (!coachMap[r.c].studentMap[r.s] || coachMap[r.c].studentMap[r.s] < r.t) {
        coachMap[r.c].studentMap[r.s] = r.t;
      }
    }
  });

  var results = [];
  var globalStudents = {};
  var globalSO = {};
  var globalSTAM = {};
  var globalAY = {};
  var globalAny = {};

  Object.keys(coachMap).forEach(function(cid) {
    var coach = coachMap[cid];
    var so = 0, stam = 0, ay = 0, any = 0;
    var studentDetails = [];
    var studentIds = Object.keys(coach.studentMap);

    studentIds.forEach(function(sid) {
      var s = DATA.students[sid];
      var isSO = s ? (confirmedOnly ? s.sc === true : s.so) : false;
      var isSTAM = s ? (confirmedOnly ? s.tc === true : s.st) : false;
      var isAY = s ? (s.sm >= minSemMonths && s.sm > 0) : false;
      var hasAny = isSO || isSTAM || isAY;
      if (isSO) { so++; globalSO[sid] = true; }
      if (isSTAM) { stam++; globalSTAM[sid] = true; }
      if (isAY) { ay++; globalAY[sid] = true; }
      if (hasAny) { any++; globalAny[sid] = true; }
      globalStudents[sid] = true;
      studentDetails.push({
        name: s ? s.n : sid,
        so: isSO, stam: isSTAM, ay: isAY,
        semMonths: s ? s.sm : 0,
        tp: coach.studentMap[sid]
      });
    });

    studentDetails.sort(function(a, b) { return a.name.localeCompare(b.name); });

    var rateNum = rateMetric === 'so' ? so : rateMetric === 'stam' ? stam : rateMetric === 'ay' ? ay : any;
    var rate = studentIds.length > 0 ? Math.round((rateNum / studentIds.length) * 100) : 0;
    results.push({
      name: coach.name, id: coach.id, me: coach.me,
      students: studentIds.length, so: so, stam: stam, ay: ay, any: any,
      rate: rate,
      details: studentDetails
    });
  });

  return {
    rows: results,
    totals: {
      coaches: results.length,
      students: Object.keys(globalStudents).length,
      so: Object.keys(globalSO).length,
      stam: Object.keys(globalSTAM).length,
      ay: Object.keys(globalAY).length,
      any: Object.keys(globalAny).length
    }
  };
}

function esc(s) { var d = document.createElement('div'); d.textContent = s; return d.innerHTML; }

function render() {
  var minM = parseFloat(document.getElementById('minMeetings').value);
  var minS = parseFloat(document.getElementById('minSemMonths').value);
  var minT = parseFloat(document.getElementById('minTotalMeetings').value);
  var rateMetric = document.getElementById('rateMetric').value;
  var confirmedOnly = document.getElementById('confirmedOnly').checked;

  // Sync number inputs
  document.getElementById('minMeetingsNum').value = minM;
  document.getElementById('minSemMonthsNum').value = minS;
  document.getElementById('minTotalMeetingsNum').value = minT;

  var result = compute(minM, minS, minT, rateMetric, confirmedOnly);
  var rows = result.rows;
  var totals = result.totals;

  document.getElementById('sumCoaches').textContent = totals.coaches;
  document.getElementById('sumStudents').textContent = totals.students;
  document.getElementById('sumSO').textContent = totals.so;
  document.getElementById('sumSTAM').textContent = totals.stam;
  document.getElementById('sumAY').textContent = totals.ay;
  document.getElementById('sumAny').textContent = totals.any;

  rows.sort(function(a, b) {
    var va = a[sortCol], vb = b[sortCol];
    if (typeof va === 'string') return va.localeCompare(vb) * sortDir;
    return (va - vb) * sortDir;
  });

  var tbody = document.getElementById('tableBody');
  tbody.innerHTML = '';

  // Find max rate for scaling the bar
  var maxRate = Math.max.apply(null, rows.map(function(r) { return r.rate; })) || 1;

  rows.forEach(function(r) {
    var tr = document.createElement('tr');
    var arrow = expandedCoach === r.id ? '&#9660; ' : '&#9654; ';
    var barWidth = maxRate > 0 ? Math.round((r.rate / maxRate) * 100) : 0;
    var rateColor = r.rate >= 20 ? '#2d9a4e' : r.rate >= 10 ? '#5bb975' : r.rate > 0 ? '#8fd4a8' : '#ccc';
    var meDisplay = (r.me != null) ? Math.round(r.me) : '—';
    tr.innerHTML = '<td><span class="expand-btn" data-coach="' + r.id + '">' + arrow + esc(r.name) + '</span></td>'
      + '<td>' + meDisplay + '</td>'
      + '<td>' + r.students + '</td>'
      + '<td>' + (r.so || '-') + '</td>'
      + '<td>' + (r.stam || '-') + '</td>'
      + '<td>' + (r.ay || '-') + '</td>'
      + '<td>' + (r.any || '-') + '</td>'
      + '<td class="rate-cell"><div class="rate-bar-bg"><div class="rate-bar" style="width:' + barWidth + '%;background:' + rateColor + '"></div></div><span class="rate-val">' + r.rate + '%</span></td>';
    tbody.appendChild(tr);

    if (expandedCoach === r.id) {
      var detailTr = document.createElement('tr');
      detailTr.className = 'student-detail';
      var detailTd = document.createElement('td');
      detailTd.colSpan = 8;
      if (r.details.length === 0) {
        detailTd.innerHTML = '<div class="student-list"><em>No students meet the minimum meeting threshold.</em></div>';
      } else {
        var html = '<div class="student-list"><table><thead><tr><th>Student Name</th><th>Meetings</th><th>SO</th><th>STAM</th><th>AY</th><th>Seminary Months</th></tr></thead><tbody>';
        r.details.forEach(function(d) {
          html += '<tr><td>' + esc(d.name) + '</td>'
            + '<td>' + d.tp + '</td>'
            + '<td>' + (d.so ? '<span class="badge badge-so">SO</span>' : '-') + '</td>'
            + '<td>' + (d.stam ? '<span class="badge badge-stam">STAM</span>' : '-') + '</td>'
            + '<td>' + (d.ay ? '<span class="badge badge-ay">AY</span>' : '-') + '</td>'
            + '<td>' + (d.semMonths > 0 ? d.semMonths.toFixed(1) : '-') + '</td></tr>';
        });
        html += '</tbody></table></div>';
        detailTd.innerHTML = html;
      }
      detailTr.appendChild(detailTd);
      detailTr.style.display = '';
      tbody.appendChild(detailTr);
    }
  });

  // Totals row
  var totTr = document.createElement('tr');
  totTr.className = 'totals';
  var rateMetric = document.getElementById('rateMetric').value;
  var totalRateNum = rateMetric === 'so' ? totals.so : rateMetric === 'stam' ? totals.stam : rateMetric === 'ay' ? totals.ay : totals.any;
  var totalRate = totals.students > 0 ? Math.round((totalRateNum / totals.students) * 100) : 0;
  totTr.innerHTML = '<td>TOTAL (de-duplicated)</td><td>&mdash;</td><td>' + totals.students + '</td><td>' + totals.so + '</td><td>' + totals.stam + '</td><td>' + totals.ay + '</td><td>' + totals.any + '</td><td>' + totalRate + '%</td>';
  tbody.appendChild(totTr);
}

// Wire up controls
['minMeetings', 'minSemMonths', 'minTotalMeetings'].forEach(function(id) {
  var slider = document.getElementById(id);
  var valSpan = document.getElementById(id + 'Val');
  var numInput = document.getElementById(id + 'Num');

  slider.addEventListener('input', function() {
    valSpan.textContent = slider.value;
    numInput.value = slider.value;
    render();
  });
  numInput.addEventListener('change', function() {
    var v = parseFloat(numInput.value);
    if (!isNaN(v) && v >= 0) {
      slider.value = Math.min(v, parseFloat(slider.max));
      valSpan.textContent = numInput.value;
      render();
    }
  });
});

// Rate metric dropdown
document.getElementById('rateMetric').addEventListener('change', function() { render(); });

// Confirmed only toggle
document.getElementById('confirmedOnly').addEventListener('change', function() { render(); });

// Sorting
document.querySelectorAll('#mainTable thead th').forEach(function(th) {
  th.addEventListener('click', function() {
    var col = th.dataset.col;
    if (sortCol === col) { sortDir *= -1; }
    else { sortCol = col; sortDir = 1; }
    document.querySelectorAll('#mainTable thead th').forEach(function(t) {
      t.classList.remove('sorted');
      t.querySelector('.arrow').innerHTML = '&#9650;';
    });
    th.classList.add('sorted');
    th.querySelector('.arrow').innerHTML = sortDir === 1 ? '&#9650;' : '&#9660;';
    render();
  });
});

// Expand/collapse student details
document.getElementById('tableBody').addEventListener('click', function(e) {
  var btn = e.target.closest('.expand-btn');
  if (!btn) return;
  var coachId = btn.dataset.coach;
  expandedCoach = (expandedCoach === coachId) ? null : coachId;
  render();
});

// Initial render
render();
</script>
</body>
</html>"""

html = html.replace('__DATA_PLACEHOLDER__', data_json)

with open(os.path.join(BASE_DIR, 'dashboard.html'), 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Dashboard generated: {len(html):,} bytes ({len(html)/1024:.0f} KB)")
