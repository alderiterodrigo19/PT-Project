"""Topic 1: FCFS, SJF, SRTF, and Priority Scheduling."""

import tkinter as tk
from tkinter import ttk

import customtkinter as ctk

from cpu_core import INPUT_ORDER, MAX_JOBS, PROCESS_ID, common_schedules, parse_workload
from priority import HIGH_FIRST, LOW_FIRST, NON_PREEMPTIVE, PREEMPTIVE, priority_schedule
from theme import C, CFONT, FONT, P, px, setup_fonts, style_tables

EXAMPLE_ROWS = "P1   0   7   4\nP2   2   4   1\nP3   4   1   3\nP4   5   4   2"
PROCESS_COLORS = ("#16665e", "#245797", "#7c4a9b", "#a14c32",
                  "#42673d", "#865519", "#385975", "#9b3c71")


def make_tabs(parent):
    return ctk.CTkTabview(
        parent, fg_color=C("card"), anchor="nw", border_width=1, border_color=C("border"),
        segmented_button_font=FONT.bold, segmented_button_fg_color=C("segment"),
        segmented_button_unselected_color=C("segment"),
        segmented_button_unselected_hover_color=C("accent_hover"),
        segmented_button_selected_color=C("accent"),
        segmented_button_selected_hover_color=C("accent_hover"), text_color="white",
    )


def make_menu(parent, values, **kwargs):
    return ctk.CTkOptionMenu(
        parent, values=list(values), font=FONT.ui, dropdown_font=FONT.ui,
        fg_color=C("accent"), button_color=C("accent_hover"),
        button_hover_color=C("accent"), text_color="white",
        dropdown_fg_color=C("card"), dropdown_hover_color=C("accent_soft"),
        dropdown_text_color=C("text"), height=32, **kwargs,
    )


def make_table(parent, headings, widths):
    frame = ctk.CTkFrame(parent, fg_color=C("card"))
    frame.pack(fill="both", expand=True, padx=6, pady=6)
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)

    tree = ttk.Treeview(frame, columns=headings, show="headings", style="Result.Treeview", height=5)
    for name, width in zip(headings, widths, strict=True):
        width = max(px(width), CFONT.bold.measure(name) + px(16))
        tree.heading(name, text=name)
        tree.column(name, width=width, minwidth=width, stretch=False, anchor="center")
    tree.tag_configure("alternate", background=P()["soft"])

    vertical = ctk.CTkScrollbar(frame, command=tree.yview)
    horizontal = ctk.CTkScrollbar(frame, orientation="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
    tree.grid(row=0, column=0, sticky="nsew")
    vertical.grid(row=0, column=1, sticky="ns")
    horizontal.grid(row=1, column=0, sticky="ew")
    return tree


def fill_table(tree, rows):
    tree.delete(*tree.get_children())
    for index, row in enumerate(rows):
        tree.insert("", "end", values=row, tags=("alternate",) if index % 2 else ())
    for index, name in enumerate(tree["columns"]):
        widest = max((CFONT.ui.measure(str(row[index])) for row in rows), default=0)
        width = max(tree.column(name, "minwidth"), widest + px(16))
        tree.column(name, width=width)
    tree.xview_moveto(0)
    tree.yview_moveto(0)


class PriorityApp(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=C("bg"))
        self.title("Operating Systems Simulator · Topic 1")
        self.geometry("1280x800")
        self.minsize(1040, 660)
        setup_fonts(self)
        style_tables(self)
        self.results = {}

        header = ctk.CTkFrame(self, fg_color=C("card"), corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(header, text="Smart CPU Scheduler",
                     font=FONT.title, text_color=C("text")).pack(side="left", padx=18, pady=12)
        self.dark = tk.BooleanVar(master=self, value=False)
        ctk.CTkSwitch(header, text="Dark mode", variable=self.dark, command=self.toggle_dark,
                      font=FONT.ui, text_color=C("text")).pack(side="right", padx=18)

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=12, pady=(12, 0))
        body.rowconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)
        self.build_workload(body)
        self.build_results(body)

        self.status = ctk.CTkLabel(self, anchor="w", font=FONT.small, text_color=C("muted"))
        self.status.pack(fill="x", padx=16, pady=5)
        self.load_example()
        self.after(50, self.maximize)

    def maximize(self):
        try:
            self.state("zoomed")
        except tk.TclError:
            try:
                self.attributes("-zoomed", True)
            except tk.TclError:
                pass

    def build_workload(self, body):
        card = ctk.CTkScrollableFrame(
            body, width=320, fg_color=C("card"), scrollbar_button_color=C("scroll"),
            scrollbar_button_hover_color=C("scroll_hover"),
        )
        card.grid(row=0, column=0, sticky="ns", padx=(0, 12))
        ctk.CTkLabel(card, text="01   Workload", font=FONT.title,
                     text_color=C("text")).pack(anchor="w", padx=10, pady=(8, 4))

        count_row = ctk.CTkFrame(card, fg_color="transparent")
        count_row.pack(fill="x", padx=10, pady=(5, 10))
        ctk.CTkLabel(count_row, text="Number of processes", font=FONT.ui,
                     text_color=C("text")).pack(side="left")
        self.count = tk.StringVar(master=self)
        ctk.CTkButton(count_row, text="+", width=30, font=FONT.bold,
                      command=lambda: self.step_count(1)).pack(side="right")
        ctk.CTkEntry(count_row, width=48, font=FONT.ui, textvariable=self.count,
                     justify="center", fg_color=C("field"), text_color=C("text"),
                     border_color=C("border_strong")).pack(side="right", padx=4)
        ctk.CTkButton(count_row, text="−", width=30, font=FONT.bold,
                      command=lambda: self.step_count(-1)).pack(side="right")

        ctk.CTkLabel(card, text="ID   AT   BT   Priority", font=FONT.bold,
                     text_color=C("accent_text")).pack(anchor="w", padx=10)
        ctk.CTkLabel(card, text="One process per line. Use spaces to separate values.",
                     font=FONT.small, text_color=C("muted"), wraplength=290,
                     justify="left").pack(anchor="w", padx=10, pady=(0, 5))
        self.jobs = ctk.CTkTextbox(
            card, height=155, font=FONT.mono, wrap="none", undo=True,
            fg_color=C("field"), text_color=C("text"), border_width=2,
            border_color=C("border_strong"), scrollbar_button_color=C("scroll"),
        )
        self.jobs.pack(fill="x", padx=10, pady=(0, 10))

        options = ctk.CTkFrame(card, fg_color="transparent")
        options.pack(fill="x", padx=10)
        options.columnconfigure(1, weight=1)
        for row, (label, attr, values) in enumerate((
            ("Priority mode", "mode", (NON_PREEMPTIVE, PREEMPTIVE)),
            ("Higher priority", "order", (LOW_FIRST, HIGH_FIRST)),
            ("Same-arrival ties", "tie", (INPUT_ORDER, PROCESS_ID)),
        )):
            ctk.CTkLabel(options, text=label, font=FONT.ui, text_color=C("text")).grid(
                row=row, column=0, sticky="w", pady=4,
            )
            menu = make_menu(options, values, width=166)
            menu.grid(row=row, column=1, sticky="ew", padx=(6, 0), pady=4)
            setattr(self, attr, menu)

        actions = ctk.CTkFrame(card, fg_color="transparent")
        actions.pack(fill="x", padx=10, pady=(12, 8))
        actions.columnconfigure((0, 1), weight=1)
        ctk.CTkButton(actions, text="Run", font=FONT.bold, height=34,
                      fg_color=C("accent"), hover_color=C("accent_hover"),
                      command=self.run_all).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkButton(actions, text="Load example", font=FONT.ui, height=34,
                      fg_color=C("soft"), hover_color=C("border"), text_color=C("text"),
                      command=self.load_example).grid(row=0, column=1, sticky="ew")

    def build_results(self, body):
        card = ctk.CTkFrame(body, fg_color=C("card"))
        card.grid(row=0, column=1, sticky="nsew")
        ctk.CTkLabel(card, text="02   Results", font=FONT.title,
                     text_color=C("text")).pack(anchor="w", padx=14, pady=(8, 0))

        self.tabs = make_tabs(card)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        schedule = self.tabs.add("Schedule")
        compare = self.tabs.add("Compare all")

        toolbar = ctk.CTkFrame(schedule, fg_color="transparent")
        toolbar.pack(fill="x", padx=6, pady=(7, 0))
        ctk.CTkLabel(toolbar, text="Algorithm", font=FONT.ui,
                     text_color=C("text")).pack(side="left")
        self.algorithm = make_menu(
            toolbar, ["FCFS"], width=150, command=lambda _: self.show_schedule(),
        )
        self.algorithm.pack(side="left", padx=7)
        self.detail = ctk.CTkLabel(schedule, font=FONT.small, text_color=C("muted"),
                                   anchor="w", justify="left", wraplength=430)
        self.detail.pack(fill="x", padx=6, pady=(5, 0))
        self.averages = ctk.CTkLabel(schedule, font=FONT.bold, text_color=C("accent_text"),
                                     anchor="w", justify="left", wraplength=430)
        self.averages.pack(fill="x", padx=6)

        ctk.CTkLabel(schedule, text="Gantt chart · time units", font=FONT.bold,
                     text_color=C("text")).pack(anchor="w", padx=6, pady=(4, 0))
        self.plot = tk.Canvas(schedule, height=px(82), bg=P()["field"],
                              highlightbackground=P()["border"], highlightthickness=1)
        scrollbar = ctk.CTkScrollbar(schedule, orientation="horizontal", command=self.plot.xview)
        self.plot.configure(xscrollcommand=scrollbar.set)
        self.plot.pack(fill="x", padx=6)
        scrollbar.pack(fill="x", padx=6)
        self.plot.bind("<Configure>", lambda _: self.draw_chart())

        self.detail_tabs = make_tabs(schedule)
        self.detail_tabs.pack(fill="both", expand=True, padx=6)
        self.metrics = make_table(
            self.detail_tabs.add("Process metrics"),
            ("Process", "AT", "BT", "Priority", "CT", "TAT", "WT", "RT"),
            (103, 56, 56, 77, 58, 58, 58, 58),
        )
        self.trace = make_table(
            self.detail_tabs.add("Timeline steps"),
            ("Step", "Process", "Start", "End", "Ran", "Remaining BT"),
            (52, 103, 68, 68, 61, 119),
        )

        ctk.CTkLabel(compare, text="Same workload, four policies", font=FONT.bold,
                     text_color=C("text")).pack(anchor="w", padx=8, pady=(8, 0))
        self.comparison = ctk.CTkLabel(compare, font=FONT.ui, text_color=C("muted"),
                                      anchor="w", justify="left", wraplength=430)
        self.comparison.pack(fill="x", padx=8, pady=(3, 6))
        self.compare_table = make_table(
            compare, ("Algorithm", "Avg TAT", "Avg WT", "Avg RT"), (145, 92, 92, 92),
        )

    def step_count(self, delta):
        try:
            count = int(self.count.get())
        except ValueError:
            count = 1
        new_count = max(1, min(MAX_JOBS, count + delta))

        # Read the current rows from the text box
        lines = [line for line in self.jobs.get("1.0", "end").splitlines() if line.strip()]
        used = {line.replace(",", " ").split()[0] for line in lines}

        # Add rows: P1, P2, P3... skipping any ID already used
        while len(lines) < new_count:
            n = len(lines) + 1
            while f"P{n}" in used:
                n += 1
            used.add(f"P{n}")
            lines.append(f"P{n}   0   1   1")   # default AT=0, BT=1, Priority=1

        # Remove rows from the bottom if the count went down
        del lines[new_count:]

        self.jobs.delete("1.0", "end")
        self.jobs.insert("1.0", "\n".join(lines))
        self.count.set(str(new_count))

    def load_example(self):
        self.jobs.delete("1.0", "end")
        self.jobs.insert("1.0", EXAMPLE_ROWS)
        self.count.set(str(len(EXAMPLE_ROWS.splitlines())))
        self.mode.set(NON_PREEMPTIVE)
        self.order.set(LOW_FIRST)
        self.tie.set(INPUT_ORDER)
        self.run_all()

    def run_all(self):
        try:
            jobs = parse_workload(self.count.get(), self.jobs.get("1.0", "end"), with_priority=True)
            tie = self.tie.get()
            schedules = common_schedules(jobs, tie)
            schedules.append(priority_schedule(jobs, self.mode.get(), self.order.get(), tie))
        except ValueError as error:
            self.results = {}
            self.algorithm.set("")
            self.algorithm.configure(state="disabled")
            self.status.configure(text=str(error), text_color=C("error"))
        else:
            selected = self.algorithm.get()
            self.results = {schedule.name: schedule for schedule in schedules}
            self.algorithm.configure(values=list(self.results), state="normal")
            self.algorithm.set(selected if selected in self.results else schedules[0].name)
            self.status.configure(
                text=f"Calculated four policies for {len(jobs)} processes. Run again after editing inputs.",
                text_color=C("muted"),
            )
        self.show_schedule()
        self.show_comparison()

    def show_schedule(self):
        result = self.results.get(self.algorithm.get())
        if result is None:
            self.detail.configure(text="Enter a valid workload to see a schedule.")
            self.averages.configure(text="")
            fill_table(self.metrics, [])
            fill_table(self.trace, [])
        else:
            self.detail.configure(text=result.detail)
            tat, wt, rt = result.averages
            self.averages.configure(text=f"Avg TAT  {tat:.2f}     Avg WT  {wt:.2f}     Avg RT  {rt:.2f}")
            fill_table(self.metrics, [
                (m.process.pid, m.process.arrival, m.process.burst, m.process.priority,
                 m.completion, m.turnaround, m.waiting, m.response)
                for m in result.metrics
            ])
            fill_table(self.trace, [
                (i, step.pid or "Idle", step.start, step.end, step.end - step.start,
                 "-" if step.remaining is None else step.remaining)
                for i, step in enumerate(result.slices, 1)
            ])
        self.draw_chart()

    def show_comparison(self):
        scores = [(result.name, result.averages) for result in self.results.values()]
        fill_table(self.compare_table, [
            (name, *(f"{value:.2f}" for value in averages)) for name, averages in scores
        ])
        if not scores:
            self.comparison.configure(text="Run a valid workload to compare the four policies.")
            return

        lines = [self.results["Priority"].detail]
        for index, label in enumerate(("turnaround", "waiting", "response")):
            best = min(values[index] for _, values in scores)
            winners = ", ".join(name for name, values in scores if values[index] == best)
            lines.append(f"Lowest average {label} · {winners} ({best:.2f})")
        self.comparison.configure(text="\n".join(lines))

    def draw_chart(self):
        p = P()
        self.plot.configure(bg=p["field"], highlightbackground=p["border"])
        self.plot.delete("all")
        result = self.results.get(self.algorithm.get())
        if result is None:
            self.plot.configure(scrollregion=(0, 0, 1, px(82)))
            return

        colors = {m.process.pid: PROCESS_COLORS[i % len(PROCESS_COLORS)]
                  for i, m in enumerate(result.metrics)}
        horizon = result.slices[-1].end
        font = CFONT.ui
        margin = max(px(30), font.measure(str(horizon)) // 2 + px(10))
        span = max(self.plot.winfo_width() - 2 * margin - px(3),
                   min(px(7200), len(result.slices) * px(78)))
        self.plot.configure(scrollregion=(0, 0, span + 2 * margin, px(82)))
        self.plot.xview_moveto(0)

        def x(time):
            return margin + span * time / horizon

        last_label_end = -px(100)
        final_label_start = x(horizon) - font.measure(str(horizon)) / 2
        for step in result.slices:
            left, right = x(step.start), x(step.end)
            self.plot.create_rectangle(left, px(10), right, px(48),
                                       fill=colors.get(step.pid, "#657689"), width=0)
            label = step.pid or "Idle"
            if right - left >= font.measure(label) + px(8):
                self.plot.create_text((left + right) / 2, px(29), text=label, fill="white", font=font)
            self.plot.create_line(left, px(49), left, px(56), fill=p["muted"])
            start_text = str(step.start)
            half = font.measure(start_text) / 2
            if left - half > last_label_end + px(5) and left + half < final_label_start - px(5):
                self.plot.create_text(left, px(68), text=start_text, fill=p["text"], font=font)
                last_label_end = left + half

        end = x(horizon)
        self.plot.create_line(end, px(49), end, px(56), fill=p["muted"])
        self.plot.create_text(end, px(68), text=str(horizon), fill=p["text"], font=font)

    def toggle_dark(self):
        ctk.set_appearance_mode("dark" if self.dark.get() else "light")
        style_tables(self)
        for table in (self.metrics, self.trace, self.compare_table):
            table.tag_configure("alternate", background=P()["soft"])
        self.draw_chart()


def main():
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    PriorityApp().mainloop()


if __name__ == "__main__":
    main()
