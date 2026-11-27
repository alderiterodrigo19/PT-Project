# Smart CPU Scheduler — Topic 1

A desktop simulator for **CPU scheduling algorithms** built as part of an Operating Systems coursework (Topic 1). Implements four classic policies with an interactive GUI, live Gantt charts, and detailed process metrics.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![customtkinter](https://img.shields.io/badge/customtkinter-6.0.0-orange)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

| Algorithm | Type | Description |
|-----------|------|-------------|
| **FCFS** | Non-preemptive | First Come, First Served — processes run in arrival order |
| **SJF** | Non-preemptive | Shortest Job First — picks the process with the smallest burst time |
| **SRTF** | Preemptive | Shortest Remaining Time First — preemptive version of SJF |
| **Priority** | Both | Priority-based scheduling — configurable preemptive/non-preemptive, priority direction, and tie-breaking |

### GUI Capabilities
- **Interactive workload editor** — add/remove processes, set arrival time, burst time, and priority
- **Live Gantt chart** — visual timeline rendered on a Tkinter Canvas with horizontal scrolling
- **Process metrics table** — completion time, turnaround time, waiting time, response time per process
- **Timeline steps table** — step-by-step execution trace (start, end, remaining burst)
- **Comparison view** — side-by-side averages (Avg TAT, Avg WT, Avg RT) for all four policies
- **Dark / Light mode** — toggle appearance instantly
- **Example workload** — one-click load of a sample scenario

---

## 🖥️ Screenshots

> *Add screenshots here after running the app (drag & drop into this README or place in an `assets/` folder).*

---

## 📦 Installation

### Prerequisites
- **Python 3.10+**
- `pip` (or `pipx` / `uv`)

### Quick start
```bash
# 1. Clone or navigate to the project folder
cd topic_1_priority_app

# 2. Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the simulator
python main.py
```

### Dependencies
```
customtkinter==6.0.0
```
Only one external dependency — `customtkinter` (modern themed Tkinter). Standard library modules used: `tkinter`, `ttk`, `dataclasses`, `typing`, `font`, `sys`.

---

## 🚀 Usage

### Input format
Enter one process per line in the workload text area:
```
ID   AT   BT   Priority
```
- **ID** — unique identifier (1–24 printable characters, no spaces)
- **AT** — Arrival Time (integer ≥ 0)
- **BT** — Burst Time (integer ≥ 1)
- **Priority** — integer (negative or positive; higher/lower wins based on setting)

Example:
```
P1   0   7   4
P2   2   4   1
P3   4   1   3
P4   5   4   2
```

### Configuration options
| Option | Values | Effect |
|--------|--------|--------|
| **Priority mode** | Non-preemptive / Preemptive | Whether a running process can be interrupted by a higher-priority arrival |
| **Higher priority** | Smaller number first / Larger number first | Direction of priority comparison |
| **Same-arrival ties** | Input order / Process ID | Tie-breaker when multiple processes arrive at the same time |

### Running a simulation
1. Adjust **Number of processes** with `+` / `−` buttons (or edit directly)
2. Enter or edit the workload lines
3. Choose scheduling options
4. Click **Run** — results populate instantly
5. Switch tabs to view **Schedule** (per-algorithm detail) or **Compare all** (summary table)
6. Click **Load example** to reset to the built-in demo workload

---

## 📁 Project Structure

```
topic_1_priority_app/
├── main.py          # GUI application entry point (PriorityApp class)
├── cpu_core.py      # Core data classes (Process, Slice, Metrics, Schedule)
│                    # + FCFS/SJF/SRTF scheduling logic + workload parsing
├── priority.py      # Priority scheduling (preemptive & non-preemptive)
├── theme.py         # Colors, fonts, ttk styles, dark/light palette
├── requirements.txt # Python dependencies
└── README.md        # This file
```

### Module overview
| File | Responsibility |
|------|----------------|
| `main.py` | `PriorityApp` (CTk window), tabs, tables, Gantt canvas, event handlers |
| `cpu_core.py` | Data models, `parse_workload()`, `schedule_by_rank()`, FCFS/SJF/SRTF via `common_schedules()` |
| `priority.py` | `priority_schedule()` — wraps `schedule_by_rank()` with priority-based ranking |
| `theme.py` | `COLORS` dict, `FONT`/`CFONT` namespaces, `setup_fonts()`, `style_tables()`, scaling helper `px()` |

---

## 🧠 Algorithm Details

All policies share a **rank-based scheduler** (`schedule_by_rank`) that:
1. Maintains a `pending` list of unfinished processes
2. At each decision point, builds a `ready` queue (arrived processes)
3. Chooses the process with minimal `rank(job, remaining_burst)`
4. Runs it until completion (non-preemptive) or until a new arrival with better rank appears (preemptive)
5. Merges adjacent identical-PID slices for clean Gantt blocks

| Policy | Rank function | Preemptive? |
|--------|---------------|-------------|
| FCFS | `arrival` | No |
| SJF | `burst` | No |
| SRTF | `remaining_burst` | Yes |
| Priority | `±priority` (direction configurable) | Configurable |

**Metrics computed per process:**
- **CT** — Completion Time
- **TAT** — Turnaround Time = CT − AT
- **WT** — Waiting Time = TAT − BT
- **RT** — Response Time = first_start − AT

---

## 🛠️ Development

### Running from source
```bash
python main.py
```

### Code style
- Type hints throughout (`dataclass`, `Callable`, `list[…]`)
- `frozen=True` dataclasses for immutability
- Single-responsibility modules
- No external config files — all defaults in code

### Extending
To add a new algorithm:
1. Add a `(name, rank_fn, preemptive, detail)` tuple to `common_schedules()` in `cpu_core.py`
2. Or create a new module like `priority.py` and call `schedule_by_rank()` with a custom rank function

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 👤 Author

**Rodrigo Alderite** — Operating Systems coursework (Topic 1)  
Universidade do Minho · 2023/2024

> This project is part of the **PT-Project** repository. See the main repo for other topics.