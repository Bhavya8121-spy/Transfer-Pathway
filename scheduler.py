from collections import defaultdict, deque

class DegreePlanner:
    def __init__(self):
        self.graph = defaultdict(list) # Adjacency list: Prereq -> Course
        self.in_degree = defaultdict(int) # Count of prereqs for each course
        self.all_courses = set()
    
    def add_course(self, course, prereqs):
        self.all_courses.add(course)
        # If no prereqs, ensure it's in the in_degree dict
        if course not in self.in_degree:
            self.in_degree[course] = 0
            
        for p in prereqs:
            self.graph[p].append(course)
            self.in_degree[course] += 1
            self.all_courses.add(p)
            if p not in self.in_degree:
                self.in_degree[p] = 0

    def generate_schedule(self, max_courses_per_sem=4):
        # 1. Find all courses with 0 prerequisites (ready to take)
        queue = deque([c for c in self.all_courses if self.in_degree[c] == 0])
        semester_plan = []
        
        while queue:
            current_semester = []
            # Take up to max_courses_per_sem from the available queue
            for _ in range(min(len(queue), max_courses_per_sem)):
                course = queue.popleft()
                current_semester.append(course)
            
            semester_plan.append(current_semester)
            
            # "Complete" these courses and unlock the next ones
            next_round_queue = [] # Temp storage to preserve semester order
            for course in current_semester:
                for neighbor in self.graph[course]:
                    self.in_degree[neighbor] -= 1
                    if self.in_degree[neighbor] == 0:
                        queue.append(neighbor)
                        
        return semester_plan

# --- TEST THE ALGORITHM ---
planner = DegreePlanner()
# "I need Calc 1 before Calc 2"
planner.add_course("MATH 2414 (Calc II)", ["MATH 2413 (Calc I)"]) 
# "I need Calc 2 before Calc 3"
planner.add_course("MATH 2415 (Calc III)", ["MATH 2414 (Calc II)"])
# "I need Phys 1 before Phys 2"
planner.add_course("PHYS 2426 (Phys II)", ["PHYS 2425 (Phys I)"])
# "I need Calc 1 to take Phys 1"
planner.add_course("PHYS 2425 (Phys I)", ["MATH 2413 (Calc I)"])

schedule = planner.generate_schedule()
for i, sem in enumerate(schedule):
    print(f"Semester {i+1}: {sem}")