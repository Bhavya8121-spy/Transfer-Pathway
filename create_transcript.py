import pandas as pd
import io

# This is the data extracted from your PDF report
csv_content = """Category,Course Code,Course Name,Credits,Status,Term,Notes
Communication,ENGL 1301,Composition I,3,Not Started,,Grade of C or better required
Communication,ENGL 1302,Composition II,3,Preregistered,2025SU,*PR (Preregistered)
Mathematics,MATH 2413,Calculus I,4,Not Started,,Grade of C or better required
Life & Physical Science,PHYS 2425,University Physics I,4,Not Started,,
Life & Physical Science,PHYS 2426,University Physics II,4,Not Started,,
Lang Phil & Culture,Elective,Select 1 (e.g. PHIL 1301),3,Not Started,,See catalog for options
Creative Arts,Elective,Select 1 (e.g. ARTS 1301),3,Not Started,,See catalog for options
American History,HIST 1301,US History I,3,Not Started,,
American History,HIST 1302,US History II,3,Not Started,,Select from HIST 1302 2301 2328 or 2381
Govt/Poli Science,GOVT 2305,Federal Government,3,Not Started,,
Govt/Poli Science,GOVT 2306,Texas Government,3,Not Started,,
Computer Science Req,COSC 1436,Programming Fundamentals I,4,Not Started,,
Computer Science Req,COSC 1437,Programming Fundamentals II,4,Not Started,,
Computer Science Req,COSC 2436,Programming Fundamentals III,4,Not Started,,
Computer Science Req,ENGR 2105,Electrical Circuits I Lab,1,Not Started,,
Computer Science Req,MATH 2305,Discrete Mathematics,3,Not Started,,
Computer Science Req,MATH 2414,Calculus II,4,Not Started,,
Computer Science Req,MATH 2418,Linear Algebra,4,Not Started,,
Other Courses,ENGR 1201,Intro to Engineering,2,Not Started,,
Additional Registered,MATH 1314,College Algebra,3,Preregistered,2025SU,*PR (Preregistered)
Additional Registered,PSYC 2301,General Psychology,3,Preregistered,2025SU,*PR (Preregistered)"""

# 1. Convert the text string into a Pandas DataFrame
df = pd.read_csv(io.StringIO(csv_content))

# 2. Save it to a real file on your computer
filename = "dallas_transcript.csv"
df.to_csv(filename, index=False)

# 3. Print the output to the console so you can "see" it
print(f"✅ Successfully created {filename}")
print("-" * 50)
print(df.head(10)) # Shows the first 10 rows
print("-" * 50)
print(f"\nTotal Credits Accounted For: {df['Credits'].sum()}")
print("You can now open 'dallas_transcript.csv' in Excel or use it in our Optimizer.")