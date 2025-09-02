"""
Schedule Algorithm
"""

from typing import List, Sequence, Optional
import re


# ===== Data Classes =====
class Period:
    def __init__(
        self, 
        period_id: str,
        days: Sequence[str], 
        time_start: str, 
        time_end: str, 
        location: str = "", 
        instructor: str = ""
    ):
        self.period_id = period_id
        self.days = list(days)
        self.time_start = time_start
        self.time_end = time_end
        self.location = location
        self.instructor = instructor

    def __repr__(self) -> str:
        days = ','.join(self.days)
        return f"Period(id={self.period_id!r}, days=[{days}], {self.time_start}-{self.time_end})"


class Course:
    def __init__(
        self, 
        title: str, 
        course_id: str
    ):
        self.title = title
        self.course_id = course_id
        self.periods: List[Period] = []

    def add_period(self, period: Period) -> None:
        self.periods.append(period)

    def __repr__(self):
        return f"Course(title={self.title!r}, course_id={self.course_id!r}, periods={len(self.periods)})"


# Global list of courses
courses: List[Course] = []


# ===== Helper Functions =====
def _parse_days(raw: str) -> List[str]:
    """
    Turn user input like 'Mon,Wed' or 'Tue Thu' into ['Mon','Wed'].
    """
    if not raw:
        return []
    parts = re.split(r"[,\s]+", raw.strip())
    return [p.strip().capitalize() for p in parts if p.strip()]

def _valid_time_format(t: str) -> bool:
    """
    Accept H:MM or HH:MM with 0<=H<=23 and 0<=MM<=59.
    """
    if not t:
        return False
    m = re.fullmatch(r"(\d{1,2}):(\d{2})", t.strip())
    if not m:
        return False
    h, mm = int(m.group(1)), int(m.group(2))
    return 0 <= h <= 23 and 0 <= mm <= 59


# ===== Functions =====
def main_menu() -> int:
    """
    Main interactive menu.
    Prints all menu options.
    Calls other functions based on user selection.
    """

    while True:
        print("\n\n===== Main Menu =====")
        print("What would you like to do?")
        print(" 1. List Courses")
        print(" 2. Add Course")
        print(" 3. Edit Course")
        print(" 4. Delete Course")
        print(" 5. Edit Preferences")
        print(" 6. Create Schedules")
        print(" 0. Exit")

        choice = input("Enter your selection: ").strip()
        if not choice:
            print("Please enter a selection")
            continue

        try:
            selection = int(choice)
        except ValueError:
            print("Invalid entry. Please enter a valid number.")
            continue

        if selection < 0 or selection > 6:
            print("Invalid entry. Please enter a valid number. ")
            continue

        elif selection == 0:
            print("Goodbye")
            return 0

        elif selection == 1:
            display_courses()

        elif selection == 2:
            add_course()

        elif selection == 3:
            edit_course()

        elif selection == 4:
            delete_course()

        elif selection == 5:
            # Edit Preferences
            print("Edit preferences: (not implemented yet)")

        elif selection == 6:
            # Create Schedules
            print("Create schedules: (not implemented yet)")


def display_courses(show_periods: bool = True):
    """
    Prints all courses and sections.
    """

    print("\n===== All Courses =====")
    if not courses:
        print("No courses have been added yet.")
        return

    for course_index, course in enumerate(courses, start=1):
        print(f"{course_index}. {course.title} ({course.course_id}) — {len(course.periods)} period(s)")
        if not show_periods:
            continue
        if not course.periods:
            print("    [no periods]")
            continue
        for section_index, period in enumerate(course.periods, start=1):
            days = ", ".join(period.days) if period.days else ""
            extras: List[str] = []
            if getattr(period, "location", ""):
                extras.append(period.location)
            if getattr(period, "instructor", ""):
                extras.append(period.instructor)
            extras_str = f" | {' - '.join(extras)}" if extras else ""
            print(
                f"    {section_index}. {period.period_id}  |  {days}  |  {period.time_start} - {period.time_end}{extras_str}"
            )


def choose_course() -> int:
    """
    Prompt the user to pick a course by number from the global course list.
    Returns the selected course index. Returns -1 if canceled.
    """

    if not courses:
        print("There are no courses to choose from.")
        return -1

    print("Select a course from the list ('c' to cancel):")
    for idx, course in enumerate(courses, start=1):
        print(f"  {idx}. {course.title} ({course.course_id}) - {len(course.periods)} period(s)")

    while True:
        choice = input("Enter number of course (or 'c' to cancel): ").strip()
        if not choice:
            print("Please enter a number or 'c' to cancel.")
            continue
        if choice.lower() == "c":
            return -1
        if not choice.isdigit():
            print("Invalid entry. Please enter the numeric index shown (e.g. 1) or 'c' to cancel.")
            continue
        selected_index = int(choice)
        if 1 <= selected_index <= len(courses):
            return selected_index - 1
        print(f"Out of range. Enter a number between 1 and {len(courses)}, or 'c' to cancel.")


def add_course() -> None:
    """Add a new Course and optionally add sections immediately."""
    print("\n===== Add Course =====")

    title = input("Course Title: ").strip()
    if title.lower() == "c":
        print("Cancelled")
        return

    course_id = input("Course ID: ").strip()
    if course_id.lower() == "c":
        print("Cancelled")
        return

    course = Course(title, course_id)
    courses.append(course)
    print("Added course:", course.title, "-", course.course_id)

    # Ask once if they want to add sections now; only accept 'y' or 'n'
    while True:
        resp = input("Add section(s) to this course now? (y/n): ").strip().lower()
        if resp == "y":
            # add_section handles adding multiple sections itself
            add_section(len(courses) - 1)
            break
        if resp == "n":
            break
        print("Please enter 'y' or 'n'.")


def add_section(course_index: Optional[int] = None) -> None:
    """
    Add one or more Periods to a course.
    If course_index is None, the user will be asked to choose a course.
    """
    print("\n===== Add Section =====")

    # Resolve course_index to local variable
    if course_index is None:
        selected_index = choose_course()
        if selected_index == -1:
            print("Add section cancelled.")
            return
        course_index_local = selected_index
    else:
        course_index_local = course_index

    # Validate index bounds (defensive)
    if course_index_local < 0 or course_index_local >= len(courses):
        print("Invalid course index.")
        return

    course = courses[course_index_local]

    while True:  # loop to allow multiple sections if user says 'y'
        print(f"\nAdding a section to: {course.title} ({course.course_id})")
        print("Enter 'c' at any prompt to cancel this section (and return to the caller).")

        # Section/period id
        while True:
            period_id = input("Section/Period ID (e.g. MATH101-A): ").strip()
            if not period_id:
                print("ID cannot be empty. Enter 'c' to cancel.")
                continue
            if period_id.lower() == "c":
                print("Cancelled adding section(s).")
                return
            break

        # Days
        raw_days = input("Days (comma or space separated, e.g. Mon,Wed or Tue Thu) [enter for TBA]: ").strip()
        if raw_days.lower() == "c":
            print("Cancelled adding section(s).")
            return
        days = _parse_days(raw_days)

        # Start time
        while True:
            time_start = input("Start time (HH:MM, 24-hour, e.g. 09:00) [enter for TBA]: ").strip()
            if time_start.lower() == "c":
                print("Cancelled adding section(s).")
                return
            if time_start == "":
                time_start = ""
                break
            if not _valid_time_format(time_start):
                print("Invalid time format. Use H:MM or HH:MM (00:00 - 23:59), or enter nothing for TBA.")
                continue
            break

        # End time (only if start provided)
        time_end = ""
        if time_start:
            while True:
                time_end = input("End time (HH:MM, 24-hour, e.g. 10:15): ").strip()
                if time_end.lower() == "c":
                    print("Cancelled adding section(s).")
                    return
                if not _valid_time_format(time_end):
                    print("Invalid time format. Use H:MM or HH:MM (00:00 - 23:59).")
                    continue
                # chronological check
                sh, sm = map(int, time_start.split(":"))
                eh, em = map(int, time_end.split(":"))
                if (eh * 60 + em) <= (sh * 60 + sm):
                    print("End time must be after start time.")
                    continue
                break

        # Optional details
        location = input("Location (optional, press Enter to skip): ").strip()
        if location.lower() == "c":
            print("Cancelled adding section(s).")
            return
        instructor = input("Instructor (optional, press Enter to skip): ").strip()
        if instructor.lower() == "c":
            print("Cancelled adding section(s).")
            return

        # Create Period object and add it to course
        new_period = Period(period_id, days, time_start, time_end, location, instructor)
        course.add_period(new_period)
        print(f"Added period {new_period} to course {course.title} ({course.course_id}).")

        # Ask explicitly and re-prompt until valid input
        while True:
            again = input("Add another section to this course? (y/n): ").strip().lower()
            if again == "y":
                break  # back to outer loop (add another)
            if again == "n":
                return
            if again == "c":
                print("Cancelled adding section(s).")
                return
            print("Please enter 'y' or 'n' (or 'c' to cancel).")


def choose_section_index(course: Course) -> int:
    """
    Prompt the user to pick a section index from course.periods.
    Returns 0-based index, or -1 if cancelled/back.
    """
    if not course.periods:
        print("This course has no sections.")
        return -1
    print(f"Select a section of {course.title} ({course.course_id}) ('c' to cancel):")
    for index, p in enumerate(course.periods, start=1):
        days = ", ".join(p.days) if getattr(p, "days", None) else "TBA"
        print(f"  {index}. {p.period_id} | {days} | {p.time_start} - {p.time_end}")
    while True:
        choice = input("Enter section number (or 'c' to cancel): ").strip()
        if not choice:
            print("Enter a number or 'c' to cancel.")
            continue
        if choice.lower() == "c":
            return -1
        if not choice.isdigit():
            print("Please enter a numeric index (e.g. 1).")
            continue
        selection = int(choice)
        if 1 <= selection <= len(course.periods):
            return selection - 1
        print(f"Out of range. Enter 1..{len(course.periods)} or 'c' to cancel.")


def edit_course() -> None:
    """
    Edit a selected course (title, course_id) and its sections (periods).
    """
    course_index = choose_course()
    if course_index == -1:
        print("Edit cancelled or no courses.")
        return

    course = courses[course_index]
    while True:
        print(f"\n--- Editing Course: {course.title} ({course.course_id}) ---")
        print(" 1) Edit course title")
        print(" 2) Edit course id")
        print(" 3) Edit sections")
        print(" 4) Add section")
        print(" 5) Delete course")
        print(" 0) Back")
        selection1 = input("Selection: ").strip().lower()

        if not selection1:
            print("Please choose an option.")
            continue
        if selection1 == "0":
            print("Returning to main menu.")
            return

        if selection1 == "1":
            new_title = input(f"New title (current: {course.title}) [enter to cancel]: ").strip()
            if not new_title:
                print("Title edit cancelled.")
            else:
                course.title = new_title
                print("Title updated.")
            continue

        if selection1 == "2":
            new_id = input(f"New id (current: {course.course_id}) [enter to cancel]: ").strip()
            if not new_id:
                print("ID edit cancelled.")
            else:
                course.course_id = new_id
                print("ID updated.")
            continue

        if selection1 == "3":
            # Edit existing sections
            if not course.periods:
                print("Course has no sections. Use 'Add section' to create one.")
                continue

            section_index = choose_section_index(course)
            if section_index == -1:
                print("Section selection cancelled.")
                continue

            period = course.periods[section_index]
            # section edit submenu
            while True:
                days_str = ", ".join(period.days) if getattr(period, "days", None) else "TBA"
                print(f"\n--- Editing Section {section_index+1}: {period.period_id} ---")
                print(
                    f"  Current: days={days_str}, start={period.time_start}, end={period.time_end}, "
                    f"loc={period.location}, instr={period.instructor}"
                )
                print(" 1) Edit section id")
                print(" 2) Edit days")
                print(" 3) Edit start time")
                print(" 4) Edit end time")
                print(" 5) Edit location")
                print(" 6) Edit instructor")
                print(" 7) Delete this section")
                print(" 0) Back to course menu")
                selection2 = input("Selection: ").strip().lower()
                if not selection2:
                    print("Please choose an option.")
                    continue
                if selection2 == "0":
                    break
                if selection2 == "1":
                    new_pid = input(f"New section id (current: {period.period_id}) [enter to cancel]: ").strip()
                    if new_pid:
                        period.period_id = new_pid
                        print("Section id updated.")
                    else:
                        print("Cancelled.")
                    continue
                if selection2 == "2":
                    raw = input(f"New days (current: {days_str}), e.g. Mon,Wed (enter to cancel): ").strip()
                    if not raw:
                        print("Cancelled.")
                        continue
                    days = _parse_days(raw)
                    period.days = days
                    print("Days updated.")
                    continue
                if selection2 == "3":
                    new_start = input(
                        f"New start time (current: {period.time_start}) [H:MM or empty to set TBA]: "
                    ).strip()
                    if new_start.lower() == "c" or new_start == "":
                        print("Start time edit cancelled or set to TBA.")
                        if new_start == "":
                            period.time_start = ""
                        continue
                    if not _valid_time_format(new_start):
                        print("Invalid time format. Edit cancelled.")
                        continue
                    period.time_start = new_start
                    print("Start time updated.")
                    continue
                if selection2 == "4":
                    new_end = input(
                        f"New end time (current: {period.time_end}) [H:MM or empty to set TBA]: "
                    ).strip()
                    if new_end.lower() == "c" or new_end == "":
                        print("End time edit cancelled or set to TBA.")
                        if new_end == "":
                            period.time_end = ""
                        continue
                    if not _valid_time_format(new_end):
                        print("Invalid time format. Edit cancelled.")
                        continue
                    # if start present, check chronological order
                    if period.time_start and new_end:
                        try:
                            sh, sm = map(int, period.time_start.split(":"))
                            eh, em = map(int, new_end.split(":"))
                            if (eh * 60 + em) <= (sh * 60 + sm):
                                print("End time must be after start time. Edit cancelled.")
                                continue
                        except Exception:
                            # if time parsing fails, skip chronological check
                            pass
                    period.time_end = new_end
                    print("End time updated.")
                    continue
                if selection2 == "5":
                    new_loc = input(f"New location (current: {period.location}) [enter to cancel]: ").strip()
                    if new_loc:
                        period.location = new_loc
                        print("Location updated.")
                    else:
                        print("Cancelled.")
                    continue
                if selection2 == "6":
                    new_instr = input(f"New instructor (current: {period.instructor}) [enter to cancel]: ").strip()
                    if new_instr:
                        period.instructor = new_instr
                        print("Instructor updated.")
                    else:
                        print("Cancelled.")
                    continue
                if selection2 == "7":
                    confirm = input("Delete this section? Type 'yes' to confirm: ").strip().lower()
                    if confirm == "yes":
                        del course.periods[section_index]
                        print("Section deleted.")
                        break  # back to course menu
                    print("Deletion cancelled.")
                    continue

                print("Unknown option; choose 0-7.")
            continue  # back to course menu

        if selection1 == "4":
            # Add a section directly to this course
            add_section(course_index)
            continue

        if selection1 == "5":
            confirm = input(f"Delete entire course '{course.title}'? Type 'delete' to confirm: ").strip().lower()
            if confirm == "delete":
                del courses[course_index]
                print("Course deleted.")
                return
            print("Deletion cancelled.")
            continue

        print("Unknown option; choose 0-5.")


def delete_course() -> None:
    """
    Allow the user to delete a whole course or a single section from a chosen course.
    """
    course_index = choose_course()
    if course_index == -1:
        print("Delete cancelled or no courses.")
        return

    course = courses[course_index]
    while True:
        print(f"\n--- Delete: {course.title} ({course.course_id}) ---")
        print(" 1) Delete entire course")
        print(" 2) Delete a section from this course")
        print(" 0) Cancel / Back")
        selection = input("Selection: ").strip().lower()

        if not selection:
            print("Please choose an option.")
            continue
        if selection == "0":
            print("Cancelled.")
            return

        if selection == "1":
            confirm = input(f"Delete the entire course '{course.title}'? Type 'delete' to confirm: ").strip().lower()
            if confirm == "delete":
                del courses[course_index]
                print(f"Course '{course.title}' deleted.")
                return
            print("Deletion cancelled.")
            continue

        if selection == "2":
            if not course.periods:
                print("This course has no sections to delete.")
                continue
            section_index = choose_section_index(course)
            if section_index == -1:
                print("Section deletion cancelled.")
                continue
            p = course.periods[section_index]
            confirm = input(f"Delete section '{p.period_id}'? Type 'yes' to confirm: ").strip().lower()
            if confirm == "yes":
                del course.periods[section_index]
                print(f"Deleted section '{p.period_id}' from {course.title}.")
            else:
                print("Deletion cancelled.")
            continue

        print("Unknown option; choose 0-2.")


if __name__ == "__main__":
    print("Welcome to the Schedule Algorithm")

    main_menu()

    print("Thank you for using the Schedule Algorithm")
