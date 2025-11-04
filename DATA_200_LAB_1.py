import os, csv, hashlib, getpass, statistics, time
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional

class PasswordHasher:
    @staticmethod
    def hash_password(plaintext: str):
        return hashlib.sha256(plaintext.encode("utf-8")).hexdigest()
    @staticmethod
    def verify_password(plaintext: str, hashed: str):
        return hashlib.sha256(plaintext.encode("utf-8")).hexdigest() == hashed

@dataclass
class Course:
    Course_id: str
    Course_name: str
    Description: str = ""
    Credits: int = 3

@dataclass
class Professor:
    Professor_id: str
    Professor_Name: str
    Rank: str
    Course_id: str

@dataclass
class Student:
    Email_address: str
    First_name: str
    Last_name: str
    Course_id: str
    grades: str
    Marks: int

@dataclass
class LoginUser:
    User_id: str
    Password: str
    Role: str

class Grades:
    SCALE = [(90, "A+"), (80, "A"), (71, "B"), (61, "C"), (51, "D"), (0, "F")]
    @classmethod
    def letter_for(cls, marks: int):
        for low, letter in cls.SCALE:
            if marks >= low:
                return letter
        return "F"

class CSVstore:
    def __init__(self, path: str, headers: List[str]):
        self.path = path
        self.headers = headers
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if not os.path.exists(self.path):
            with open(self.path, "w", newline="") as f:
                csv.DictWriter(f, fieldnames=self.headers).writeheader()
    def read_all(self) -> List[Dict]:
        with open(self.path, newline="") as f:
            return list(csv.DictReader(f))
    def write_all(self, rows: List[Dict]) -> None:
        with open(self.path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=self.headers)
            w.writeheader()
            w.writerows(rows)

class CheckMyGradeApp:
    def __init__(self, data_dir: str = "data"):
        self.students_store = CSVstore(os.path.join(data_dir, "Student.csv"), ["Email_address", "First_name", "Last_name", "Course_id", "grades", "Marks"])
        self.courses_store  = CSVstore(os.path.join(data_dir, "Course.csv"), ["Course_id", "Course_name", "Description", "Credits"])
        self.profs_store    = CSVstore(os.path.join(data_dir, "Professor.csv"), ["Professor_id", "Professor_Name", "Rank", "Course_id"])
        self.users_store    = CSVstore(os.path.join(data_dir, "Login.csv"), ["User_id", "Password", "Role"])
        self.students: Dict[str, Student] = {}
        self.courses: Dict[str, Course] = {}
        self.professors: Dict[str, Professor] = {}
        self.users: Dict[str, LoginUser] = {}
        self.load_all()
    def load_all(self):
        self.students = {}
        for r in self.students_store.read_all():
            self.students[r["Email_address"]] = Student(r["Email_address"], r["First_name"], r["Last_name"], r["Course_id"], r["grades"], int(r["Marks"]))
        self.courses = {}
        for r in self.courses_store.read_all():
            self.courses[r["Course_id"]] = Course(r["Course_id"], r["Course_name"], r.get("Description", ""), int(r.get("Credits", "3") or 3))
        self.professors = {}
        for r in self.profs_store.read_all():
            self.professors[r["Professor_id"]] = Professor(r["Professor_id"], r["Professor_Name"], r["Rank"], r["Course_id"])
        self.users = {}
        for r in self.users_store.read_all():
            self.users[r["User_id"]] = LoginUser(r["User_id"], r["Password"], r["Role"])
    def save_students(self):
        self.students_store.write_all([asdict(s) for s in self.students.values()])
    def save_courses(self):
        self.courses_store.write_all([asdict(c) for c in self.courses.values()])
    def save_profs(self):
        self.profs_store.write_all([asdict(p) for p in self.professors.values()])
    def save_users(self):
        self.users_store.write_all([asdict(u) for u in self.users.values()])
    def register_user(self, email: str, password: str, role: str):
        if email in self.users:
            print("User already exists.")
            return
        if role not in ("student", "professor"):
            print("Role must be student or professor.")
            return
        self.users[email] = LoginUser(email, PasswordHasher.hash_password(password), role)
        self.save_users()
        print("Account created successfully.")
    def login(self, email: str, password: str):
        u = self.users.get(email)
        if not u:
            return None
        return u if PasswordHasher.verify_password(password, u.Password) else None
    def change_password(self, email: str):
        oldp = getpass.getpass("Old password: ")
        u = self.login(email, oldp)
        if not u:
            print("Invalid old password.")
            return
        newp = getpass.getpass("New password: ")
        self.users[email].Password = PasswordHasher.hash_password(newp)
        self.save_users()
        print("Password updated.")
    def add_student(self):
        email = input("Student email: ").strip()
        if email in self.students:
            print("Student already exists.")
            return
        first = input("First name: ").strip()
        last  = input("Last name: ").strip()
        cid   = input("Course ID: ").strip()
        try:
            marks = int(input("Marks (0-100): ").strip())
        except ValueError:
            print("Marks must be integers.")
            return
        grade = Grades.letter_for(marks)
        self.students[email] = Student(email, first, last, cid, grade, marks)
        self.save_students()
        print("Student added successfully.")
    def update_student(self):
        email = input("Enter student email to update: ").strip()
        s = self.students.get(email)
        if not s:
            print("Not found.")
            return
        new_first = input(f"First name [{s.First_name}]: ").strip() or s.First_name
        new_last  = input(f"Last name  [{s.Last_name}]: ").strip() or s.Last_name
        new_cid   = input(f"Course ID  [{s.Course_id}]: ").strip() or s.Course_id
        marks_in  = input(f"Marks (0-100) [{s.Marks}]: ").strip()
        if marks_in:
            try:
                m = int(marks_in)
                s.Marks = m
                s.grades = Grades.letter_for(m)
            except ValueError:
                print("Marks must be integers.")
        s.First_name, s.Last_name, s.Course_id = new_first, new_last, new_cid
        self.save_students()
        print("Student updated successfully.")
    def delete_student(self):
        email = input("Enter student email to delete: ").strip()
        if email in self.students:
            del self.students[email]
            self.save_students()
            print("Student deleted successfully.")
        else:
            print("Not found.")
    def add_course(self):
        cid = input("Course ID: ").strip()
        if cid in self.courses:
            print("Course already exists.")
            return
        name = input("Course name: ").strip()
        desc = input("Description of course: ").strip()
        credits_txt = input("Credits (default 3): ").strip()
        credits = int(credits_txt) if credits_txt.isdigit() else 3
        self.courses[cid] = Course(cid, name, desc, credits)
        self.save_courses()
        print("Course added.")
    def update_course(self):
        cid = input("Enter course_id to be update: ").strip()
        c = self.courses.get(cid)
        if not c:
            print("Not found.")
            return
        c.Course_name = input(f"Course name [{c.Course_name}]: ").strip() or c.Course_name
        c.Description = input(f"Description [{c.Description}]: ").strip() or c.Description
        cr = input(f"Credits [{c.Credits}]: ").strip()
        if cr.isdigit():
            c.Credits = int(cr)
        self.save_courses()
        print("Course updated.")
    def delete_course(self):
        cid = input("Enter course_id to be delete: ").strip()
        if cid in self.courses:
            del self.courses[cid]
            self.save_courses()
            print("Course deleted.")
        else:
            print("Not found.")
            
    def list_courses(self):
        if not self.courses:
            print("No courses found.")
            return
        print("Course_id , Course_name , Credits")
        for c in self.courses.values():
            print(f"{c.Course_id} , {c.Course_name} , {c.Credits}")
            
    def add_professor(self):
        pid = input("Professor email: ").strip()
        if pid in self.professors:
            print("Professor exists.")
            return
        pname = input("Professor name: ").strip()
        rank  = input("Rank: ").strip()
        cid   = input("Course ID: ").strip()
        self.professors[pid] = Professor(pid, pname, rank, cid)
        self.save_profs()
        print("Professor added.")
    def update_professor(self):
        pid = input("Professor email to update: ").strip()
        p = self.professors.get(pid)
        if not p:
            print("Not found.")
            return
        p.Professor_Name = input(f"Name [{p.Professor_Name}]: ").strip() or p.Professor_Name
        p.Rank = input(f"Rank [{p.Rank}]: ").strip() or p.Rank
        p.Course_id = input(f"Course ID [{p.Course_id}]: ").strip() or p.Course_id
        self.save_profs()
        print("Professor updated.")
    def delete_professor(self):
        pid = input("Professor email to delete: ").strip()
        if pid in self.professors:
            del self.professors[pid]
            self.save_profs()
            print("Professor deleted.")
        else:
            print("Not found.")
    def report_student(self, email: str):
        s = self.students.get(email)
        if not s:
            return "No record."
        return f"{s.First_name} {s.Last_name} ({s.Email_address}) | {s.Course_id} | {s.Marks} ({s.grades})"
    def course_stats(self, cid: str):
        rows = [s.Marks for s in self.students.values() if s.Course_id == cid]
        if not rows:
            return "0 student(s) in " + cid
        avg = round(sum(rows)/len(rows), 2)
        med = statistics.median(rows)
        mn = min(rows)
        mx = max(rows)
        return f"{len(rows)} student(s) in {cid}\nAvg={avg} , Median={med} , Min={mn} , Max={mx}"
    def report_course_full(self, cid: str):
        rows = [s for s in self.students.values() if s.Course_id == cid]
        out = [f"{len(rows)} student(s) in {cid}"]
        for s in rows:
            out.append(f"- {s.Email_address}\t{s.First_name} {s.Last_name}\t{s.Marks} {s.grades}")
        if rows:
            marks = [s.Marks for s in rows]
            out.append(f"Avg={round(sum(marks)/len(marks),2)} , Median={statistics.median(marks)} , Min={min(marks)} , Max={max(marks)}")
        return "\n".join(out)
    def report_professor(self, pid: str):
        p = self.professors.get(pid)
        if not p:
            return "No record."
        rows = [s for s in self.students.values() if s.Course_id == p.Course_id]
        out = [f"{p.Professor_Name} -> Course {p.Course_id}"]
        for s in rows:
            out.append(f"- {s.Email_address}\t{s.First_name} {s.Last_name}\t{s.Marks} {s.grades}")
        return "\n".join(out)
    def search_students(self, substr: str):
        t0 = time.perf_counter()
        res = [s for s in self.students.values() if substr.lower() in s.Email_address.lower()]
        dt = (time.perf_counter() - t0) * 1000.0
        return res, dt
    def sort_students(self, by: str, descending: bool):
        if by == "marks":
            key = lambda s: (s.Marks, s.Email_address)
        else:
            key = lambda s: s.Email_address.lower()
        t0 = time.perf_counter()
        out = sorted(self.students.values(), key=key, reverse=descending)
        dt = (time.perf_counter() - t0) * 1000.0
        return out, dt

def minimum_info(app: CheckMyGradeApp):
    if "DATA200" not in app.courses:
        app.courses["DATA200"] = Course("DATA200", "Python", "Advanced to basic python", 1)
        app.save_courses()
    if "micheal@mycsu.edu" not in app.professors:
        app.professors["micheal@mycsu.edu"] = Professor("mick@sjsu.edu", "Mick Cena", "Professor", "DATA200")
        app.save_profs()
    if "sam@mycsu.edu" not in app.students:
        app.students["sam@mycsu.edu"] = Student("dean@sjsu.edu", "Dean", "Carpenter", "DATA200", Grades.letter_for(96), 96)
        app.save_students()
    if "prof@mycsu.edu" not in app.users:
        app.users["prof@mycsu.edu"] = LoginUser("prof@mycsu.edu", PasswordHasher.hash_password("Welcome12#_"), "professor")
        app.save_users()

def student_menu(app: CheckMyGradeApp, user: LoginUser):
    while True:
        print("\nStudent Menu")
        print("1) My report")
        print("2) Course stats")
        print("3) Change password")
        print("4) Logout")
        c = input("Enter you choice: ").strip()
        if c == "1":
            print(app.report_student(user.User_id))
        elif c == "2":
            cid = input("Course ID: ").strip()
            print(app.course_stats(cid))
        elif c == "3":
            app.change_password(user.User_id)
        elif c == "4":
            break
        else:
            print("Invalid choice.")

def professor_menu(app: CheckMyGradeApp, user: LoginUser):
    while True:
        print("\nProfessor Menu")
        print("1) Add student")
        print("2) Update student")
        print("3) Delete student")
        print("4) Add course")
        print("5) Update course")
        print("6) Delete course")
        print("7) List courses")
        print("8) Add professor")
        print("9) Update professor")
        print("10) Delete professor")
        print("11) Course report")
        print("12) Professor report")
        print("13) Search students")
        print("14) Sort students")
        print("15) Change password")
        print("16) Logout")
        c = input("Enter your choice: ").strip()
        if c == "1":
            app.add_student()
        elif c == "2":
            app.update_student()
        elif c == "3":
            app.delete_student()
        elif c == "4":
            app.add_course()
        elif c == "5":
            app.update_course()
        elif c == "6":
            app.delete_course()
        elif c == "7":
            app.list_courses()
        elif c == "8":
            app.add_professor()
        elif c == "9":
            app.update_professor()
        elif c == "10":
            app.delete_professor()
        elif c == "11":
            cid = input("Course ID: ").strip()
            print(app.report_course_full(cid))
        elif c == "12":
            pid = input("Professor email: ").strip()
            print(app.report_professor(pid))
        elif c == "13":
            sub = input("Email substring: ").strip()
            res, ms = app.search_students(sub)
            print(f"Found {len(res)} student in {ms:.2f} ms")
            for s in res:
                print(f"- {s.Email_address} , {s.Marks} {s.grades}")
        elif c == "14":
            by = input("Sort by marks/email: ").strip().lower()
            order = input("Order by asc/desc: ").strip().lower()
            desc = order == "desc"
            lst, ms = app.sort_students(by if by in ("marks", "email") else "email", desc)
            print(f"Sorted {len(lst)} records in {ms:.2f} ms")
            for s in lst:
                print(f"- {s.Email_address} , {s.Marks} {s.grades}")
        elif c == "15":
            app.change_password(user.User_id)
        elif c == "16":
            break
        else:
            print("Invalid choice.")

def main_menu(app: CheckMyGradeApp):
    while True:
        print("\nCheckMyGrade")
        print("1) Login")
        print("2) Sign up")
        print("3) Exit")
        c = input("Enter your choice: ").strip()
        if c == "1":
            email = input("Email: ").strip()
            pwd = getpass.getpass("Password: ")
            u = app.login(email, pwd)
            if not u:
                print("Invalid credentials.")
                continue
            if u.Role == "student":
                student_menu(app, u)
            elif u.Role == "professor":
                professor_menu(app, u)
            else:
                print("Role not defined.")
        elif c == "2":
            email = input("Email: ").strip()
            role  = input("Role (student/professor): ").strip().lower()
            pwd1  = getpass.getpass("Password: ")
            pwd2  = getpass.getpass("Confirm: ")
            if pwd1 != pwd2:
                print("Passwords does not match.")
                continue
            app.register_user(email, pwd1, role)
        elif c == "3":
            print("Thank you!")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    app = CheckMyGradeApp("data")
    minimum_info(app)
    main_menu(app)






