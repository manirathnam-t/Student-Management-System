from flask_login import UserMixin
from .extensions import db, login_manager
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    password = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(20), nullable=False)
class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    register_no = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    phone = db.Column(
        db.String(15),
        nullable=False
    )

    gender = db.Column(
        db.String(20),
        nullable=False
    )

    dob = db.Column(
        db.Date
    )

    department_id = db.Column(
        db.Integer,
        db.ForeignKey("department.id"),
        nullable=False
    )

    course_id = db.Column(
        db.Integer,
        db.ForeignKey("courses.id"),
        nullable=False
    )

    department = db.relationship(
        "Department",
        back_populates="students"
    )

    course = db.relationship(
        "Course",
        back_populates="students"
    )

    year = db.Column(
        db.Integer,
        nullable=False
    )

    section = db.Column(
        db.String(10),
        nullable=False
    )

    address = db.Column(
        db.Text
    )

    photo = db.Column(
        db.String(200),
        default="default.png"
    )

    def __repr__(self):
        return f"<Student {self.name}>"

class Teacher(db.Model):
    __tablename__ = "teachers"

    id = db.Column(db.Integer, primary_key=True)

    employee_id = db.Column(db.String(20), unique=True, nullable=False)

    name = db.Column(db.String(100), nullable=False)

    department = db.Column(db.String(100), nullable=False)

    subject = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    phone = db.Column(db.String(15), nullable=False)

    def __repr__(self):
        return f"<Teacher {self.name}>"
    



class Subject(db.Model):
    __tablename__ = "subjects"

    id = db.Column(db.Integer, primary_key=True)

    subject_code = db.Column(db.String(20), unique=True, nullable=False)

    subject_name = db.Column(db.String(100), nullable=False)

    semester = db.Column(db.Integer, nullable=False)

    credits = db.Column(db.Integer, default=3)

    department = db.Column(db.String(100), nullable=False)

class Attendance(db.Model):
    __tablename__ = "attendance"

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.id"),
        nullable=False
    )

    subject_id = db.Column(
        db.Integer,
        db.ForeignKey("subjects.id"),
        nullable=False
    )

    attendance_date = db.Column(
        db.Date,
        nullable=False
    )

    status = db.Column(
        db.String(10),
        nullable=False
    )

    student = db.relationship(
        "Student",
        backref="attendance_records"
    )

    subject = db.relationship(
        "Subject",
        backref="attendance_records"
    )


class Department(db.Model):
    __tablename__ = "department"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    hod = db.Column(
        db.String(100)
    )

    description = db.Column(
        db.Text
    )

    courses = db.relationship(
        "Course",
        back_populates="department",
        cascade="all, delete",
        lazy=True
    )

    students = db.relationship(
        "Student",
        back_populates="department",
        cascade="all, delete",
        lazy=True
    )

    def __repr__(self):
        return f"<Department {self.name}>"

class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    course_code = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    course_name = db.Column(
        db.String(100),
        nullable=False
    )

    department_id = db.Column(
        db.Integer,
        db.ForeignKey("department.id"),
        nullable=False
    )

    duration = db.Column(
        db.Integer,
        nullable=False
    )

    description = db.Column(
        db.Text
    )

    department = db.relationship(
        "Department",
        back_populates="courses"
    )

    students = db.relationship(
        "Student",
        back_populates="course",
        cascade="all, delete",
        lazy=True
    )

    def __repr__(self):
        return f"<Course {self.course_name}>"

    
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class Mark(db.Model):
    __tablename__ = "marks"

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.id"),
        nullable=False
    )

    subject_id = db.Column(
        db.Integer,
        db.ForeignKey("subjects.id"),
        nullable=False
    )

    internal = db.Column(
        db.Integer,
        nullable=False
    )

    external = db.Column(
        db.Integer,
        nullable=False
    )

    total = db.Column(
        db.Integer,
        nullable=False
    )

    grade = db.Column(
        db.String(5),
        nullable=False
    )

    result = db.Column(
        db.String(20),
        nullable=False
    )

    student = db.relationship(
        "Student",
        backref="marks"
    )

    subject = db.relationship(
        "Subject",
        backref="marks"
    )

    def __repr__(self):
        return f"<Mark {self.student_id} - {self.subject_id}>"
class Fee(db.Model):
    __tablename__ = "fees"

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.id"),
        nullable=False
    )

    amount = db.Column(db.Float, nullable=False)

    paid = db.Column(db.Float, nullable=False)

    balance = db.Column(db.Float)

    status = db.Column(db.String(20))

    student = db.relationship("Student")


class Timetable(db.Model):
    __tablename__ = "timetable"

    id = db.Column(db.Integer, primary_key=True)

    day = db.Column(
        db.String(20),
        nullable=False
    )

    period = db.Column(
        db.String(20),
        nullable=False
    )

    department_id = db.Column(
        db.Integer,
        db.ForeignKey("department.id"),
        nullable=False
    )

    course_id = db.Column(
        db.Integer,
        db.ForeignKey("courses.id"),
        nullable=False
    )

    year = db.Column(
        db.Integer,
        nullable=False
    )

    section = db.Column(
        db.String(10),
        nullable=False
    )

    subject_id = db.Column(
        db.Integer,
        db.ForeignKey("subjects.id"),
        nullable=False
    )

    teacher_id = db.Column(
        db.Integer,
        db.ForeignKey("teachers.id"),
        nullable=False
    )

    # Store classroom name directly
    classroom = db.Column(
        db.String(50),
        nullable=False
    )

    department = db.relationship("Department")
    course = db.relationship("Course")
    subject = db.relationship("Subject")
    teacher = db.relationship("Teacher")


class Notice(db.Model):
    __tablename__ = "notices"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)

    description = db.Column(db.Text, nullable=False)

    notice_date = db.Column(db.Date, nullable=False)

class Library(db.Model):
    __tablename__ = "library"

    id = db.Column(db.Integer, primary_key=True)

    book_code = db.Column(db.String(20), unique=True, nullable=False)

    book_name = db.Column(db.String(150), nullable=False)

    author = db.Column(db.String(100), nullable=False)

    quantity = db.Column(db.Integer, default=1)

    available = db.Column(db.Integer, default=1)


class BookIssue(db.Model):
    __tablename__ = "book_issues"

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.id"),
        nullable=False
    )

    book_id = db.Column(
        db.Integer,
        db.ForeignKey("library.id"),
        nullable=False
    )

    issue_date = db.Column(
        db.Date,
        nullable=False
    )

    return_date = db.Column(
        db.Date
    )

    status = db.Column(
        db.String(20),
        default="Issued"
    )

    student = db.relationship("Student")

    book = db.relationship("Library")

class Classroom(db.Model):
    __tablename__ = "classrooms"

    id = db.Column(db.Integer, primary_key=True)

    room_no = db.Column(db.String(30), unique=True, nullable=False)

    block = db.Column(db.String(50))

    capacity = db.Column(db.Integer)

    def __repr__(self):
        return f"<Classroom {self.room_no}>"