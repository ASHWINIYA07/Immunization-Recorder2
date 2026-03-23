from datetime import datetime, timedelta

# Vaccine schedule (days from DOB)
VACCINE_SCHEDULE = {
    "BCG": 0,
    "Hepatitis B (Birth)": 0,
    "DTP 1": 42,
    "DTP 2": 70,
    "DTP 3": 98,
    "Polio 1": 42,
    "Polio 2": 70,
    "Polio 3": 98,
    "Measles": 270
}


# 🔹 Generate full schedule
def generate_schedule(dob: str):
    dob_date = datetime.strptime(dob, "%Y-%m-%d")
    schedule = []

    for vaccine, days in VACCINE_SCHEDULE.items():
        due_date = dob_date + timedelta(days=days)

        schedule.append({
            "vaccine": vaccine,
            "due_date": due_date.strftime("%Y-%m-%d"),
            "status": get_status(due_date),
            "taken": False
        })

    return schedule


# 🔹 Status Logic
def get_status(due_date):
    today = datetime.today()

    if due_date < today:
        return "overdue"
    elif (due_date - today).days <= 7:
        return "due soon"
    else:
        return "upcoming"


# 🔹 Update vaccine as DONE
def mark_vaccine_done(schedule, vaccine_name):
    for v in schedule:
        if v["vaccine"] == vaccine_name:
            v["taken"] = True
            v["status"] = "done"
            return True
    return False


# 🔹 Recalculate status (important after time passes)
def update_all_status(schedule):
    for v in schedule:
        if not v["taken"]:
            due_date = datetime.strptime(v["due_date"], "%Y-%m-%d")
            v["status"] = get_status(due_date)
    return schedule


# 🔹 Progress Calculation
def calculate_progress(schedule):
    total = len(schedule)
    completed = sum(1 for v in schedule if v["taken"])

    if total == 0:
        return 0

    return round((completed / total) * 100, 2)