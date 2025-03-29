class Day:
    def __init__(self, name, period, classname):
        self.name = name
        self.period = period
        self.classname = classname  # list of periods in the day


class Timetable:
    def __init__(self, days):
        self.days = days  # list of days

    def __str__(self):
        self.sort_days()  # Ensure the timetable is sorted before displaying
        for day in self.days:
            print(f"{day.name}, {day.period}, {day.classname}")
        return ""

    def search_by_day(self, day_name):
        for day in self.days:
            if day.name == day_name:
                return f"{day.name}, {day.period}, {day.classname}"
        return None

    def remove_by_day(self, day_name):
        for day in self.days:
            if day.name == day_name:
                self.days.remove(day)
                return True
        return False

    def sort_days(self):
        # Define the order of days
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        # Sort the days based on the predefined order
        self.days.sort(key=lambda day: day_order.index(day.name) if day.name in day_order else float('inf'))


def create_timetable():
    days = []
    while True:
        name = input("Enter the name of the day: ")
        if name == "":
            break
        period = input("Enter the period of the day: ")
        classname = input("Enter the class name for the day: ")

        day = Day(name, period, classname)
        days.append(day)

    timetable = Timetable(days)
    timetable.sort_days()  # Sort the timetable after creation
    return timetable


def add_day(timetable):
    name = input("Enter the name of the day: ")
    period = input("Enter the period of the day: ")
    classname = input("Enter the class name for the day: ")

    day = Day(name, period, classname)
    timetable.days.append(day)
    timetable.sort_days()  # Sort the timetable after adding a new day


def main():
    print("Welcome to the Timetable program!")
    timetable = None  # Initialize timetable as None

    while True:
        print("\nMenu:")
        print("1. Create Timetable")
        print("2. View Timetable")
        print("3. Search by Day")
        print("4. Add Day")
        print("5. Remove Day")
        print("6. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            timetable = create_timetable()
        elif choice == "2":
            if timetable is None or not timetable.days:
                print("The timetable is empty.")
            else:
                print(timetable)
        elif choice == "3":
            if timetable is None or not timetable.days:
                print("The timetable is empty. Please create a timetable first.")
            else:
                day_name = input("Enter the name of the day to search for: ")
                result = timetable.search_by_day(day_name)
                if result:
                    print(result)
                else:
                    print("Day not found.")
        elif choice == "4":
            if timetable is None:
                print("Please create a timetable first.")
            else:
                add_day(timetable)
        elif choice == "5":
            if timetable is None or not timetable.days:
                print("The timetable is empty. Please create a timetable first.")
            else:
                day_name = input("Enter the name of the day to remove: ")
                if timetable.remove_by_day(day_name):
                    print(f"Day '{day_name}' removed successfully.")
                else:
                    print("Day not found.")
        elif choice == "6":
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()