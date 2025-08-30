"""
Schedule Algorithm
"""


from typing import List, Sequence, Optional
import re


# Classes

class Period:
    def __init__(self, course: str, days: Sequence[str], time_start: str, time_end: str, location: str = "", instructor: str = ""):
        self.course = course
        self.days = list(days)
        self.timeStart = time_start
        self.timeEnd = time_end
        self.location = location
        self.instructor = instructor

    def __repr__(self):
        days = ','.join(self.days)
        return f"Period(id={self.course!r}, days=[{days}], {self.timeStart}-{self.timeEnd})"


class Course:
    def __init__(self, title: str, id: str):
        self.title = title
        self.id = id
        self.periods: List[Period] = []

    def addPeriod(self, period: Period) -> None:
        self.periods.append(period)

    def __repr__(self):
        return f"Course(title={self.title!r}, id={self.id!r}, periods={len(self.periods)})"


courses: List[Course] = []


# Functions

def main_menu():
    """
    Main interactive menu.
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
            sel = int(choice)
        except ValueError:
            print("Invalid entry. Please enter a valid number.")
            continue

        if sel < 0 or sel > 6:
            print("Invalid entry. Please enter a valid number. ")
            continue

        elif sel == 0:
            print("Goodbye")
            return 0

        elif sel == 1:
            display_courses()

        elif sel == 2:
            add_course()

        elif sel == 3:
            # Edit Course
            edit_course()

        elif sel == 4:
            # Delete Course
            print("Delete course: (not implemented yet)")

        elif sel == 5:
            # Edit Preferences
            print("Edit preferences: (not implemented yet)")

        elif sel == 6:
            # Create Schedules
            print("Create schedules: (not implemented yet)")


def display_courses(show_periods: bool = True):
    """
    Display all courses.
    If show_periods is True, print each course's periods too.
    """
    print("\n===== All Courses =====")
    if not courses:
        print("No courses have been added yet.")
        return

    for idx, course in enumerate(courses, start=1):
        print(f"{idx}. {course.title} ({course.id}) — {len(course.periods)} period(s)")
        if show_periods:
            if not course.periods:
                print("    [no periods]")
            else:
                for p_idx, period in enumerate(course.periods, start=1):
                    days = ", ".join(period.days)
                    # include location and instructor if available
                    extras = []
                    if getattr(period, "location", ""):
                        extras.append(period.location)
                    if getattr(period, "instructor", ""):
                        extras.append(period.instructor)
                    extras_str = f" | {' - '.join(extras)}" if extras else ""
                    print(f"    {p_idx}. {period.course}  |  {days}  |  {period.timeStart} - {period.timeEnd}{extras_str}")


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
        title = getattr(course, "title", repr(course))
        cid = getattr(course, "id", "")
        print(f"  {idx}. {title} ({cid}) - {len(course.periods)} period(s)")

    while True:
        choice = input("Enter number of course (or 'c' to cancel): ").strip()
        if not choice:
            print("Please enter a number or 'c' to cancel.")
            continue
        if choice.lower() == 'c':
            return -1
        if not choice.isdigit():
            print("Invalid entry. Please enter the numeric index shown (e.g. 1) or 'c' to cancel. ")
            continue
        sel = int(choice)
        if 1 <= sel <= len(courses):
            return sel - 1
        print(f"Out of range. Enter a number between 1 and {len(courses)}, or 'c' to cancel. ")


def add_course():
    print("\n===== Add Course =====")

    title = input("Course Title: ").strip()
    if title.lower() == "c":
        print("Cancelled")
        return

    cid = input("Course ID: ").strip()
    if cid.lower() == "c":
        print("Cancelled")
        return

    course = Course(title, cid)
    courses.append(course)
    print("Added course:", course.title, "-", course.id)

    # ask once if they want to add sections now; only accept 'y' or 'n'
    while True:
        resp = input("Add section(s) to this course now? (y/n): ").strip().lower()
        if resp == "y":
            # add_section handles adding multiple sections itself
            add_section(len(courses) - 1)
            break
        elif resp == "n":
            break
        else:
            print("Please enter 'y' or 'n'.")


def _parse_days(raw: str) -> list:
    """
    Turn user input like 'Mon,Wed' or 'Tue Thu' into ['Mon','Wed']
    """
    if not raw:
        return []
    parts = re.split(r"[,\s]+", raw.strip())
    return [p.strip().capitalize() for p in parts if p.strip()]


def _valid_time_format(t: str) -> bool:
    """
    Accept H:MM or HH:MM with 0<=H<=23 and 0<=MM<=59.
    """
    m = re.fullmatch(r"(\d{1,2}):(\d{2})", t.strip())
    if not m:
        return False
    h, mm = int(m.group(1)), int(m.group(2))
    return 0 <= h <= 23 and 0 <= mm <= 59


def add_section(course_index: Optional[int] = None) -> None:
    """
    Add one or more Periods to a course.
    If course_index is None, the user will be asked to choose a course.
    """
    print("\n===== Add Section =====")

    # Determine which course to add to
    if course_index is None:
        sel = choose_course()
        if sel == -1:
            print("Add section cancelled.")
            return
        course_index = sel

    # Validate course_index bounds (defensive)
    if course_index < 0 or course_index >= len(courses):
        print("Invalid course index.")
        return

    course = courses[course_index]

    while True:  # loop to allow multiple sections if user says 'y'
        print(f"\nAdding a section to: {course.title} ({course.id})")
        print("Enter 'c' at any prompt to cancel")

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
            start = input("Start time (HH:MM, 24-hour, e.g. 09:00) [enter for TBA]: ").strip()
            if start.lower() == "c":
                print("Cancelled adding section(s).")
                return
            if start == "":
                start = ""
                break
            if not _valid_time_format(start):
                print("Invalid time format. Use H:MM or HH:MM (00:00 - 23:59), or enter nothing for TBA.")
                continue
            break

        # End time (only if start provided)
        end = ""
        if start:
            while True:
                end = input("End time (HH:MM, 24-hour, e.g. 10:15): ").strip()
                if end.lower() == "c":
                    print("Cancelled adding section(s).")
                    return
                if not _valid_time_format(end):
                    print("Invalid time format. Use H:MM or HH:MM (00:00 - 23:59).")
                    continue
                # chronological check
                sh, sm = map(int, start.split(":"))
                eh, em = map(int, end.split(":"))
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
        new_period = Period(period_id, days, start, end, location, instructor)
        course.addPeriod(new_period)
        print(f"Added period {new_period} to course {course.title} ({course.id}).")

        # Ask explicitly and re-prompt until valid input
        while True:
            again = input("Add another section to this course? (y/n): ").strip().lower()
            if again == "y":
                break  # back to outer loop
            elif again == "n":
                return
            elif again == "c":
                print("Cancelled adding section(s).")
                return
            else:
                print("Please enter 'y' or 'n' (or 'c' to cancel).")


def choose_section_index(course: Course) -> int:
    """
    Prompt the user to pick a section index from course.periods.
    Returns 0-based index, or -1 if cancelled/back.
    """
    if not course.periods:
        print("This course has no sections.")
        return -1
    print(f"Select a section of {course.title} ({course.id}) ('c' to cancel):")
    for idx, p in enumerate(course.periods, start=1):
        days = ", ".join(p.days) if getattr(p, "days", None) else "TBA"
        print(f"  {idx}. {p.course} | {days} | {p.timeStart} - {p.timeEnd}")
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
        sel = int(choice)
        if 1 <= sel <= len(course.periods):
            return sel - 1
        print(f"Out of range. Enter 1..{len(course.periods)} or 'c' to cancel.")


def edit_course() -> None:
    """
    Edit a selected course (title, id) and its sections (periods).
    """
    ci = choose_course()
    if ci == -1:
        print("Edit cancelled or no courses.")
        return

    course = courses[ci]
    while True:
        print(f"\n--- Editing Course: {course.title} ({course.id}) ---")
        print(" 1) Edit course title")
        print(" 2) Edit course id")
        print(" 3) Edit sections")
        print(" 4) Add section")
        print(" 5) Delete course")
        print(" 0) Back")
        opt = input("Selection: ").strip().lower()

        if not opt:
            print("Please choose an option.")
            continue

        if opt == "0":
            print("Returning to main menu.")
            return

        if opt == "1":
            new_title = input(f"New title (current: {course.title}) [enter to cancel]: ").strip()
            if not new_title:
                print("Title edit cancelled.")
            else:
                course.title = new_title
                print("Title updated.")
            continue

        if opt == "2":
            new_id = input(f"New id (current: {course.id}) [enter to cancel]: ").strip()
            if not new_id:
                print("ID edit cancelled.")
            else:
                course.id = new_id
                print("ID updated.")
            continue

        if opt == "3":
            # Edit existing sections
            if not course.periods:
                print("Course has no sections. Use 'Add section' to create one.")
                continue

            sidx = choose_section_index(course)
            if sidx == -1:
                print("Section selection cancelled.")
                continue

            period = course.periods[sidx]
            # section edit submenu
            while True:
                days_str = ", ".join(period.days) if getattr(period, "days", None) else "TBA"
                print(f"\n--- Editing Section {sidx+1}: {period.course} ---")
                print(f"  Current: days={days_str}, start={period.timeStart}, end={period.timeEnd}, loc={period.location}, instr={period.instructor}")
                print(" 1) Edit section id")
                print(" 2) Edit days")
                print(" 3) Edit start time")
                print(" 4) Edit end time")
                print(" 5) Edit location")
                print(" 6) Edit instructor")
                print(" 7) Delete this section")
                print(" 0) Back to course menu")
                so = input("Selection: ").strip().lower()
                if not so:
                    print("Please choose an option.")
                    continue
                if so == "0":
                    break
                if so == "1":
                    new_pid = input(f"New section id (current: {period.course}) [enter to cancel]: ").strip()
                    if new_pid:
                        period.course = new_pid
                        print("Section id updated.")
                    else:
                        print("Cancelled.")
                    continue
                if so == "2":
                    raw = input(f"New days (current: {days_str}), e.g. Mon,Wed (enter to cancel): ").strip()
                    if not raw:
                        print("Cancelled.")
                        continue
                    days = _parse_days(raw)
                    period.days = days
                    print("Days updated.")
                    continue
                if so == "3":
                    new_start = input(f"New start time (current: {period.timeStart}) [H:MM or empty to set TBA]: ").strip()
                    if new_start.lower() == "c" or new_start == "":
                        print("Start time edit cancelled or set to TBA.")
                        if new_start == "":
                            period.timeStart = ""
                        continue
                    if not _valid_time_format(new_start):
                        print("Invalid time format. Edit cancelled.")
                        continue
                    period.timeStart = new_start
                    print("Start time updated.")
                    continue
                if so == "4":
                    new_end = input(f"New end time (current: {period.timeEnd}) [H:MM or empty to set TBA]: ").strip()
                    if new_end.lower() == "c" or new_end == "":
                        print("End time edit cancelled or set to TBA.")
                        if new_end == "":
                            period.timeEnd = ""
                        continue
                    if not _valid_time_format(new_end):
                        print("Invalid time format. Edit cancelled.")
                        continue
                    # if start present, check chronological order
                    if period.timeStart and new_end:
                        try:
                            sh, sm = map(int, period.timeStart.split(":"))
                            eh, em = map(int, new_end.split(":"))
                            if (eh * 60 + em) <= (sh * 60 + sm):
                                print("End time must be after start time. Edit cancelled.")
                                continue
                        except Exception:
                            # if time parsing fails, skip chronological check
                            pass
                    period.timeEnd = new_end
                    print("End time updated.")
                    continue
                if so == "5":
                    new_loc = input(f"New location (current: {period.location}) [enter to cancel]: ").strip()
                    if new_loc:
                        period.location = new_loc
                        print("Location updated.")
                    else:
                        print("Cancelled.")
                    continue
                if so == "6":
                    new_instr = input(f"New instructor (current: {period.instructor}) [enter to cancel]: ").strip()
                    if new_instr:
                        period.instructor = new_instr
                        print("Instructor updated.")
                    else:
                        print("Cancelled.")
                    continue
                if so == "7":
                    confirm = input("Delete this section? Type 'yes' to confirm: ").strip().lower()
                    if confirm == "yes":
                        del course.periods[sidx]
                        print("Section deleted.")
                        break  # back to course menu
                    else:
                        print("Deletion cancelled.")
                    continue

                print("Unknown option; choose 0-7.")
            continue  # back to course menu

        if opt == "4":
            # Add a section directly to this course
            add_section(ci)
            continue

        if opt == "5":
            confirm = input(f"Delete entire course '{course.title}'? Type 'delete' to confirm: ").strip().lower()
            if confirm == "delete":
                del courses[ci]
                print("Course deleted.")
                return
            else:
                print("Deletion cancelled.")
            continue

        print("Unknown option; choose 0-5.")


if __name__ == "__main__":
    print("Welcome to the Schedule Algorithm")

    main_menu()

    print("Thank you for using the Schedule Algorithm")
