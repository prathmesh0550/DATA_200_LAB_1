import os
import unittest
import tempfile
from unittest.mock import patch
from time import perf_counter


from DATA_200_LAB_1 import (
    CheckMyGradeApp,
    Student,
    Course,
    Professor,
    Grades,
    minimum_info,
)

def make_input_side_effect(values):
    it = iter(values)
    return lambda prompt="": next(it)

class TestCheckMyGrade(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.app = CheckMyGradeApp(self.tmpdir.name)
        minimum_info(self.app)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_bulk_students_load_search_and_sort(self):
        for i in range(1000):
            email = f"user{i}@x.com"
            first = f"F{i}"
            last = f"L{i}"
            cid = "DATA200"
            marks = (i * 7) % 101
            grade = Grades.letter_for(marks)
            self.app.students[email] = Student(email, first, last, cid, grade, marks)
        self.app.save_students()

        app2 = CheckMyGradeApp(self.tmpdir.name)
        self.assertGreaterEqual(len(app2.students), 1000)

        res, ms = app2.search_students("user500")
        print(f"[SEARCH] {len(res)} result(s) in {ms:.2f} ms")
        self.assertTrue(ms >= 0)
        self.assertTrue(any(s.Email_address == "user500@x.com" for s in res))

        lst_asc, ms_asc = app2.sort_students("marks", False)
        print(f"[SORT marks asc] {len(lst_asc)} records in {ms_asc:.2f} ms")
        self.assertTrue(ms_asc >= 0)
        self.assertLessEqual(lst_asc[0].Marks, lst_asc[-1].Marks)

        lst_desc, ms_desc = app2.sort_students("email", True)
        print(f"[SORT email desc] {len(lst_desc)} records in {ms_desc:.2f} ms")
        self.assertTrue(ms_desc >= 0)
        self.assertGreaterEqual(lst_desc[0].Email_address, lst_desc[-1].Email_address)

    def test_student_add_update_delete(self):
        with patch("builtins.input", side_effect=make_input_side_effect([
            "stud1@x.com", "Ana", "Bell", "DATA200", "88"
        ])):
            self.app.add_student()
        self.assertIn("stud1@x.com", self.app.students)
        self.assertEqual(self.app.students["stud1@x.com"].Marks, 88)

        with patch("builtins.input", side_effect=make_input_side_effect([
            "stud1@x.com",
            "Ann",         
            "",           
            "",            
            "91"     
        ])):
            self.app.update_student()
        s = self.app.students["stud1@x.com"]
        self.assertEqual(s.First_name, "Ann")
        self.assertEqual(s.Marks, 91)

        with patch("builtins.input", side_effect=make_input_side_effect(["stud1@x.com"])):
            self.app.delete_student()
        self.assertNotIn("stud1@x.com", self.app.students)

    def test_course_crud(self):
        with patch("builtins.input", side_effect=make_input_side_effect([
            "CS101", "Intro CS", "Basics", "4"
        ])):
            self.app.add_course()
        self.assertIn("CS101", self.app.courses)
        self.assertEqual(self.app.courses["CS101"].Credits, 4)

        with patch("builtins.input", side_effect=make_input_side_effect([
            "CS101", "Intro to CS", "Foundations", "5"
        ])):
            self.app.update_course()
        c = self.app.courses["CS101"]
        self.assertEqual(c.Course_name, "Intro to CS")
        self.assertEqual(c.Description, "Foundations")
        self.assertEqual(c.Credits, 5)

        with patch("builtins.input", side_effect=make_input_side_effect(["CS101"])):
            self.app.delete_course()
        self.assertNotIn("CS101", self.app.courses)

    def test_professor_crud(self):
        with patch("builtins.input", side_effect=make_input_side_effect([
            "prof1@x.com", "Prof One", "Assistant", "DATA200"
        ])):
            self.app.add_professor()
        self.assertIn("prof1@x.com", self.app.professors)
        self.assertEqual(self.app.professors["prof1@x.com"].Rank, "Assistant")

        with patch("builtins.input", side_effect=make_input_side_effect([
            "prof1@x.com", "Professor Uno", "Associate", "DATA200"
        ])):
            self.app.update_professor()
        p = self.app.professors["prof1@x.com"]
        self.assertEqual(p.Professor_Name, "Professor Uno")
        self.assertEqual(p.Rank, "Associate")

        with patch("builtins.input", side_effect=make_input_side_effect(["prof1@x.com"])):
            self.app.delete_professor()
        self.assertNotIn("prof1@x.com", self.app.professors)

    def test_timed_search_reports_time(self):
        for i in range(200):
            email = f"find{i}@u.edu"
            self.app.students[email] = Student(email, "A", "B", "DATA200", Grades.letter_for(70), 70)
        self.app.save_students()

        t0 = perf_counter()
        res, ms = self.app.search_students("find1")
        t1 = perf_counter()
        wall_ms = (t1 - t0) * 1000.0
        print(f"[SEARCH (function)] {ms:.2f} ms, [wall] {wall_ms:.2f} ms, found={len(res)}")
        self.assertTrue(ms >= 0)
        self.assertTrue(wall_ms >= 0)

    def test_timed_sort_reports_time(self):
        for i in range(300):
            email = f"s{i:04d}@u.edu"
            marks = (i * 11) % 100
            self.app.students[email] = Student(email, "X", "Y", "DATA200", Grades.letter_for(marks), marks)
        self.app.save_students()

        lst, ms = self.app.sort_students("marks", False)
        print(f"[SORT marks asc] {ms:.2f} ms")
        self.assertTrue(ms >= 0)
        self.assertLessEqual(lst[0].Marks, lst[-1].Marks)

        lst2, ms2 = self.app.sort_students("email", True)
        print(f"[SORT email desc] {ms2:.2f} ms")
        self.assertTrue(ms2 >= 0)
        self.assertGreaterEqual(lst2[0].Email_address, lst2[-1].Email_address)

if __name__ == "__main__":
    unittest.main(verbosity=2)






