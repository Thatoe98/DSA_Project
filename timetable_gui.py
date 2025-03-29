import tkinter as tk
from tkinter import ttk, messagebox


class Day:
    def __init__(self, name, period, classname):
        self.name = name
        self.period = period
        self.classname = classname  # list of periods in the day


class Timetable:
    def __init__(self):
        self.days = []  # list of days

    def __str__(self):
        self.sort_days()  # Ensure the timetable is sorted before displaying
        return "\n".join([f"{day.name}, {day.period}, {day.classname}" for day in self.days])

    def search_by_day(self, day_name):
        results = [f"{day.name}, {day.period}, {day.classname}" for day in self.days if day.name == day_name]
        return results if results else None

    def remove_by_day(self, day_name):
        # Remove all entries for the specified day
        initial_count = len(self.days)
        self.days = [day for day in self.days if day.name != day_name]
        return len(self.days) < initial_count  # Return True if any entries were removed

    def sort_days(self):
        # Define the order of days
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        # Sort the days based on the predefined order
        self.days.sort(key=lambda day: day_order.index(day.name) if day.name in day_order else float('inf'))


class TimetableApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Timetable Manager")
        self.root.attributes("-fullscreen", True)  # Enable full-screen mode
        self.timetable = Timetable()

        # Apply a theme
        style = ttk.Style()
        style.theme_use("clam")  # Use a modern theme
        style.configure("TButton", font=("Arial", 12), padding=5)
        style.configure("TLabel", font=("Arial", 12))

        # Main layout
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.pack(fill="both", expand=True)

        # Sidebar for buttons
        self.sidebar = ttk.Frame(self.main_frame, width=200, padding=10)
        self.sidebar.pack(side="left", fill="y")

        # Content area for dynamic widgets
        self.content_area = ttk.Frame(self.main_frame, padding=10)
        self.content_area.pack(side="right", fill="both", expand=True)

        # Sidebar buttons
        ttk.Button(self.sidebar, text="Create Timetable", command=self.create_timetable).pack(fill="x", pady=5)
        ttk.Button(self.sidebar, text="View Timetable", command=self.view_timetable).pack(fill="x", pady=5)
        ttk.Button(self.sidebar, text="Search by Day", command=self.search_by_day).pack(fill="x", pady=5)
        ttk.Button(self.sidebar, text="Remove Day", command=self.remove_day).pack(fill="x", pady=5)
        ttk.Button(self.sidebar, text="Exit", command=self.exit_program).pack(fill="x", pady=5)

    def clear_content_area(self):
        # Clear all widgets in the content area
        for widget in self.content_area.winfo_children():
            widget.destroy()

    def create_timetable(self):
        self.clear_content_area()
        valid_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        valid_periods = ["9:00-11:50", "12:00-2:50", "3:00-5:50"]

        def add_day_to_timetable():
            name = day_name_combobox.get()
            period = period_combobox.get()
            classname = classname_entry.get()

            if not name:
                ttk.Label(self.content_area, text="Error: Please select a valid day.", font=("Arial", 12), foreground="red").pack(pady=5)
                return
            if not period:
                ttk.Label(self.content_area, text="Error: Please select a valid period.", font=("Arial", 12), foreground="red").pack(pady=5)
                return

            # Check if the same day and period already exist
            for day in self.timetable.days:
                if day.name == name and day.period == period:
                    ttk.Label(self.content_area, text="Error: There is a class already in that period. Please remove the class and try again.", font=("Arial", 12), foreground="red").pack(pady=5)
                    return

            # Add the new day and period
            self.timetable.days.append(Day(name, period, classname))
            self.timetable.sort_days()

            # Display success message in the content area
            ttk.Label(self.content_area, text=f"Success: Day '{name}' added to the timetable!", font=("Arial", 12), foreground="green").pack(pady=5)

            # Clear the fields after adding a day
            day_name_combobox.set("")
            period_combobox.set("")
            classname_entry.delete(0, tk.END)

        ttk.Label(self.content_area, text="Create Timetable", font=("Arial", 16, "bold")).pack(pady=10)
        ttk.Label(self.content_area, text="Day Name:").pack(pady=5)
        day_name_combobox = ttk.Combobox(self.content_area, values=valid_days, state="readonly")
        day_name_combobox.pack()

        ttk.Label(self.content_area, text="Period:").pack(pady=5)
        period_combobox = ttk.Combobox(self.content_area, values=valid_periods, state="readonly")
        period_combobox.pack()

        ttk.Label(self.content_area, text="Class Name:").pack(pady=5)
        classname_entry = ttk.Entry(self.content_area)
        classname_entry.pack()

        ttk.Button(self.content_area, text="Add Day", command=add_day_to_timetable).pack(pady=10)

    def view_timetable(self):
        self.clear_content_area()

        # Define valid days and periods
        valid_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        valid_periods = ["9:00-11:50", "12:00-2:50", "3:00-5:50"]

        ttk.Label(self.content_area, text="Timetable", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=len(valid_periods) + 1, pady=10)

        # Create table headers for periods
        ttk.Label(self.content_area, text="Days/Periods", font=("Arial", 12, "bold")).grid(row=1, column=0, padx=5, pady=5)
        for col, period in enumerate(valid_periods, start=1):
            ttk.Label(self.content_area, text=period, font=("Arial", 12, "bold")).grid(row=1, column=col, padx=5, pady=5)

        # Populate the table with days and classes
        for row, day in enumerate(valid_days, start=2):
            # Add day label
            ttk.Label(self.content_area, text=day, font=("Arial", 12, "bold")).grid(row=row, column=0, padx=5, pady=5)

            for col, period in enumerate(valid_periods, start=1):
                # Check if a class exists for the current day and period
                class_found = None
                for entry in self.timetable.days:
                    if entry.name == day and entry.period == period:
                        class_found = entry.classname
                        break

                if class_found:
                    # Add a cell with a blue background and white text for the class
                    label = tk.Label(self.content_area, text=class_found, font=("Arial", 12), bg="blue", fg="white", width=15, height=2)
                    label.grid(row=row, column=col, padx=5, pady=5)
                else:
                    # Add an empty cell
                    label = tk.Label(self.content_area, text="", font=("Arial", 12), bg="white", width=15, height=2, relief="solid")
                    label.grid(row=row, column=col, padx=5, pady=5)

    def search_by_day(self):
        self.clear_content_area()
        valid_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

        def search():
            day_name = day_name_combobox.get()
            if not day_name:
                messagebox.showerror("Error", "Please select a valid day.")
                return

            result = self.timetable.search_by_day(day_name)
            self.clear_content_area()  # Clear the content area to display the result
            ttk.Label(self.content_area, text="Search Result", font=("Arial", 16, "bold")).pack(pady=10)

            if result:
                for res in result:
                    ttk.Label(self.content_area, text=res, font=("Arial", 12)).pack(pady=5)
            else:
                ttk.Label(self.content_area, text="Day not found.", font=("Arial", 12)).pack(pady=5)

        ttk.Label(self.content_area, text="Search by Day", font=("Arial", 16, "bold")).pack(pady=10)
        ttk.Label(self.content_area, text="Day Name:").pack(pady=5)
        day_name_combobox = ttk.Combobox(self.content_area, values=valid_days, state="readonly")
        day_name_combobox.pack()

        ttk.Button(self.content_area, text="Search", command=search).pack(pady=10)

    def remove_day(self):
        self.clear_content_area()
        valid_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

        def remove():
            day_name = day_name_combobox.get()
            if not day_name:
                ttk.Label(self.content_area, text="Error: Please select a valid day.", font=("Arial", 12), foreground="red").pack(pady=5)
                return

            if self.timetable.remove_by_day(day_name):
                # Display success message in the content area
                ttk.Label(self.content_area, text=f"Success: All periods for '{day_name}' removed successfully.", font=("Arial", 12), foreground="green").pack(pady=5)
            else:
                ttk.Label(self.content_area, text="Error: Day not found.", font=("Arial", 12), foreground="red").pack(pady=5)

        ttk.Label(self.content_area, text="Remove Day", font=("Arial", 16, "bold")).pack(pady=10)
        ttk.Label(self.content_area, text="Day Name:").pack(pady=5)
        day_name_combobox = ttk.Combobox(self.content_area, values=valid_days, state="readonly")
        day_name_combobox.pack()

        ttk.Button(self.content_area, text="Remove", command=remove).pack(pady=10)

    def exit_program(self):
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = TimetableApp(root)
    root.mainloop()