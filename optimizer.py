import datetime
import pandas as pd
from parser import ReportParser

# --- CONFIGURATION ---
STEM_CATEGORIES = ["MATHEMATICS", "COMPUTER SCIENCE REQUIRED COURSES", "COMPUTER SCIENCE REQ", "LIFE AND PHYSICAL SCIENCE", "OTHER COURSES", "ENGINEERING"]
FORBIDDEN_SUMMER = ["PHYS", "MATH", "COSC", "ENGR", "CHEM"]
STRICT_SUBJECTS = ["MATH", "PHYS", "COSC", "ENGR"]

# Strict sequence for Government
PREREQUISITES = {
    "MATH 2414": "MATH 2413", "MATH 2415": "MATH 2414", "MATH 2418": "MATH 2414", 
    "PHYS 2426": "PHYS 2425", 
    "COSC 1437": "COSC 1436", "COSC 2436": "COSC 1437",
    "GOVT 2306": "GOVT 2305", # 2306 often taken after 2305, or concurrently
    "HIST 1302": "HIST 1301"
}

PRIORITY_MAP = {
    "MATHEMATICS": 1, "COMPUTER SCIENCE REQUIRED COURSES": 1, 
    "LIFE AND PHYSICAL SCIENCE": 2, "OTHER COURSES": 3, "GOVERNMENT/POLITICAL SCIENCE": 4, 
    "AMERICAN HISTORY": 5, "COMMUNICATION": 6
}

def get_next_term(current_term):
    year = int(current_term[:4])
    semester = current_term[4:]
    if semester == "SP": return f"{year}SU"
    elif semester == "SU": return f"{year}FA"
    elif semester == "FA": return f"{year + 1}SP"
    return f"{year + 1}SP"

def get_real_time_start():
    today = datetime.date.today()
    if today.month >= 10: return f"{today.year + 1}SP"
    elif today.month <= 5: return f"{today.year}SU"
    else: return f"{today.year}FA"

def get_subject(course_code):
    return course_code.split()[0]

def calculate_plan(raw_text):
    parser = ReportParser(raw_text)
    df = parser.parse()
    
    # 1. Start Date
    real_time = get_real_time_start()
    history = df[df['Term'].notna()]
    current_term = real_time
    if not history.empty:
        last = history['Term'].max()
        if last >= real_time: current_term = get_next_term(last)
    
    # 2. Filter Queue
    to_take = df[df['Status'] == 'Not Started'].copy()
    to_take['Priority'] = to_take['Category'].map(PRIORITY_MAP).fillna(99)
    to_take = to_take.sort_values(by=['Priority', 'Course Code'])
    
    stem_queue = to_take[to_take['Category'].isin(STEM_CATEGORIES)].to_dict('records')
    core_queue = to_take[~to_take['Category'].isin(STEM_CATEGORIES)].to_dict('records')

    schedule = []
    completed_courses = set(df[df['Status'] != 'Not Started']['Course Code'].unique())

    # 3. Schedule Loop
    while stem_queue or core_queue:
        is_summer = "SU" in current_term
        max_courses = 2 if is_summer else 4
        semester_load = []
        subject_counts = {} 
        
        def try_add(queue):
            for i, course in enumerate(queue):
                code = course['Course Code']
                subject = get_subject(code)
                
                # Check Prereqs
                if code in PREREQUISITES and PREREQUISITES[code] not in completed_courses: continue
                # Check Summer Ban
                if is_summer and subject in FORBIDDEN_SUMMER: continue
                # Check Subject Cap (Allow GOVT double up, but limit STEM)
                if subject in STRICT_SUBJECTS and subject_counts.get(subject, 0) >= 1: continue

                c = queue.pop(i)
                subject_counts[subject] = subject_counts.get(subject, 0) + 1
                return c
            return None

        # Fill Semester
        while len(semester_load) < max_courses:
            added = False
            # Try STEM (if not summer)
            if not is_summer and len(semester_load) < max_courses:
                c = try_add(stem_queue)
                if c: semester_load.append(c); added = True
            
            # Try Core
            if len(semester_load) < max_courses:
                c = try_add(core_queue)
                if c: semester_load.append(c); added = True

            if not added: break

        # Save
        if semester_load:
            schedule.append({"term": current_term, "courses": semester_load})
            for c in semester_load: completed_courses.add(c['Course Code'])
            current_term = get_next_term(current_term)
        else:
            if is_summer and (stem_queue or core_queue):
                current_term = get_next_term(current_term)
            else:
                break
                
    return schedule