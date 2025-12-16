import re
import pandas as pd

class ReportParser:
    def __init__(self, raw_text):
        self.raw_text = raw_text
        self.courses = []

    def parse(self):
        self._extract_courses()
        return pd.DataFrame(self.courses)

    def _extract_courses(self):
        lines = self.raw_text.split('\n')
        current_status = "Not Started"
        current_category = "GENERAL"
        
        in_choice_group = False 
        choice_options = []
        choice_category = ""

        for i, line in enumerate(lines):
            line = line.strip()
            if any(x in line for x in ["age limit", "Financial Aid", "GPA", "View/Print"]): continue

            # 1. DETECT CATEGORY HEADERS
            section_match = re.search(r"^[CNIP]\)\s*[A-Z0-9]+:\s*(.*?)(?:\(|$)", line)
            if section_match:
                # Flush previous elective group with "Smart Summary"
                if in_choice_group and choice_options:
                    self.courses.append(self._create_smart_elective(choice_category, choice_options))
                    choice_options = []
                    in_choice_group = False

                raw_cat = section_match.group(1).strip().upper()
                if "SUBRQMT" in raw_cat: raw_cat = "CORE REQUIREMENT"
                current_category = raw_cat
                
                if line.startswith("C)"): current_status = "Complete"
                elif line.startswith("P)"): current_status = "Preregistered"
                elif line.startswith("N)"): current_status = "Not Started"

            # 2. DETECT CHOICE GROUPS
            if "Select ONE" in line:
                in_choice_group = True
                choice_category = current_category
                continue
            elif "Select EACH" in line:
                in_choice_group = False
                continue

            # 3. DETECT COURSES (With Prefix Carry-Over)
            # This regex captures "GOVT" and "2305", then "2306"
            # It looks for "AAAA 1111" OR just "1111"
            clean_line = line.replace("-", " ")
            
            # Find all numbers that look like course numbers
            potential_courses = re.findall(r"([A-Z]{3,4})?\s*(\d{3,4})", clean_line)
            
            # Context Variables for this line
            last_seen_prefix = None
            found_courses_on_line = []

            for prefix, number in potential_courses:
                # Filter out years (2025, 2026, 2027) which are often confused for courses
                if number.startswith("20") and int(number) > 2020:
                    continue

                # Logic: If we see "GOVT", remember it. If we see empty prefix, use remembered one.
                if prefix:
                    last_seen_prefix = prefix
                elif last_seen_prefix:
                    prefix = last_seen_prefix
                else:
                    continue # Skip numbers without a prefix (like credit hours)

                code = f"{prefix} {number}"
                found_courses_on_line.append(code)

            # Check Term/Status
            term_match = re.search(r"(202\d[A-Z]{2})", line)
            this_term = term_match.group(1) if term_match else None
            if not this_term and i + 1 < len(lines):
                next_term = re.search(r"(202\d[A-Z]{2})", lines[i+1])
                if next_term: this_term = next_term.group(1)
            
            this_status = "Preregistered" if this_term else current_status

            # Add to list
            for code in found_courses_on_line:
                if in_choice_group and current_status == "Not Started":
                    choice_options.append(code)
                    continue
                
                # Determine Name
                name = "Requirement"
                if len(found_courses_on_line) == 1:
                     match_idx = clean_line.find(code.split()[1])
                     if match_idx != -1:
                        remaining = clean_line[match_idx+4:].strip()
                        if len(remaining) > 2: 
                            name = remaining.split('(')[0].replace("and", "").strip()

                self.courses.append({
                    "Category": current_category,
                    "Course Code": code,
                    "Course Name": name,
                    "Credits": int(code.split()[1][1]),
                    "Status": this_status,
                    "Term": this_term
                })
        
        # Flush any remaining choice group at the very end
        if in_choice_group and choice_options:
            self.courses.append(self._create_smart_elective(choice_category, choice_options))


    def _create_smart_elective(self, category, options):
        """
        Takes raw options: ['ENGL 2321', 'ENGL 2322', 'HUMA 1301', 'PHIL 1301']
        Returns display: "ENGL 2321 & others, HUMA 1301 & others, PHIL 1301..."
        """
        seen_prefixes = set()
        display_parts = []
        
        for opt in options:
            prefix = opt.split()[0]
            if prefix not in seen_prefixes:
                display_parts.append(f"{opt} & others")
                seen_prefixes.add(prefix)
        
        # Join nicely
        display_name = ", ".join(display_parts)
        
        return {
            "Category": category,
            "Course Code": "ELECTIVE",
            "Course Name": f"Select 1: {display_name}",
            "Credits": 3, "Status": "Not Started", "Term": None
        }