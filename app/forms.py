from flask_wtf import FlaskForm
from wtforms import StringField,DateField, PasswordField, SelectField, SubmitField, IntegerField, TextAreaField ,FloatField
from wtforms.validators import DataRequired, Email, Length,NumberRange
from flask_wtf.file import FileField, FileAllowed , FileRequired


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])

    role = SelectField(
        "Role",
        choices=[
            ("Admin", "Admin"),
            ("Teacher", "Teacher"),
            ("Student", "Student")
        ]
    )

    submit = SubmitField("Login")


class StudentForm(FlaskForm):

    register_no = StringField("Register Number", validators=[DataRequired()])

    name = StringField("Student Name", validators=[DataRequired()])

    department = StringField("Department", validators=[DataRequired()])

    year = IntegerField("Year", validators=[DataRequired()])

    section = StringField("Section", validators=[DataRequired()])

    email = StringField("Email", validators=[DataRequired(), Email()])

    phone = StringField("Phone", validators=[DataRequired()])

    submit = SubmitField("Add Student")
    photo = FileField(
    "Student Photo",
        validators=[
            FileRequired(message="Please upload a student photo."),
            FileAllowed(["jpg", "jpeg", "png"], "Images only!")
    ]
    )

    password = PasswordField(
    "Password",
    validators=[DataRequired()]
)
    
    
class TeacherForm(FlaskForm):

    employee_id = StringField("Employee ID", validators=[DataRequired()])

    name = StringField("Teacher Name", validators=[DataRequired()])

    department = StringField("Department", validators=[DataRequired()])

    subject = StringField("Subject", validators=[DataRequired()])

    email = StringField("Email", validators=[
        DataRequired(),
        Email()
    ])

    phone = StringField("Phone", validators=[DataRequired()])

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=6)
        ]
    )

    submit = SubmitField("Add Teacher")
class DepartmentForm(FlaskForm):

    name = StringField(
        "Department Name",
        validators=[DataRequired()]
    )

    hod = StringField(
        "Head of Department"
    )

    description = TextAreaField(
        "Description"
    )

    submit = SubmitField("Save Department")

class SubjectForm(FlaskForm):

    subject_code = StringField(
        "Subject Code",
        validators=[DataRequired()]
    )

    subject_name = StringField(
        "Subject Name",
        validators=[DataRequired()]
    )

    semester = IntegerField(
        "Semester",
        validators=[DataRequired()]
    )

    credits = IntegerField(
        "Credits",
        validators=[DataRequired()]
    )

    department = StringField(
        "Department",
        validators=[DataRequired()]
    )

    submit = SubmitField("Save Subject")

class AttendanceForm(FlaskForm):

    subject = SelectField(
        "Subject",
        coerce=int
    )

    attendance_date = DateField(
        "Date"
    )

    submit = SubmitField("Save Attendance")

class CourseForm(FlaskForm):

    course_code = StringField(
        "Course Code",
        validators=[DataRequired()]
    )

    course_name = StringField(
        "Course Name",
        validators=[DataRequired()]
    )

    duration = IntegerField(
        "Duration (Years)",
        validators=[DataRequired()]
    )

    description = TextAreaField(
        "Description"
    )

    submit = SubmitField(
        "Save Course"
    )

class MarkForm(FlaskForm):

    student = SelectField(
        "Student",
        coerce=int,
        validators=[DataRequired()]
    )

    subject = SelectField(
        "Subject",
        coerce=int,
        validators=[DataRequired()]
    )

    internal = IntegerField(
        "Internal Marks",
        validators=[
            DataRequired(),
            NumberRange(min=0, max=40)
        ]
    )

    external = IntegerField(
        "External Marks",
        validators=[
            DataRequired(),
            NumberRange(min=0, max=60)
        ]
    )

    submit = SubmitField("Save Marks")

class FeeForm(FlaskForm):

    student = SelectField(
        "Student",
        coerce=int,
        validators=[DataRequired()]
    )

    amount = FloatField(
        "Total Fee",
        validators=[DataRequired()]
    )

    paid = FloatField(
        "Paid Amount",
        validators=[DataRequired()]
    )

    submit = SubmitField("Save Fee")


class TimetableForm(FlaskForm):

    day = SelectField(
        "Day",
        choices=[
            ("Monday","Monday"),
            ("Tuesday","Tuesday"),
            ("Wednesday","Wednesday"),
            ("Thursday","Thursday"),
            ("Friday","Friday")
        ]
    )

    period = SelectField(
        "Period",
        choices=[
            ("1","Period 1"),
            ("2","Period 2"),
            ("3","Period 3"),
            ("4","Period 4"),
            ("5","Period 5"),
            ("6","Period 6")
        ]
    )

    subject = SelectField(
        "Subject",
        coerce=int
    )

    teacher = SelectField(
        "Teacher",
        coerce=int
    )

    classroom = StringField("Classroom")

    submit = SubmitField("Save Timetable")

class NoticeForm(FlaskForm):

    title = StringField(
        "Title",
        validators=[DataRequired()]
    )

    description = TextAreaField(
        "Description",
        validators=[DataRequired()]
    )

    notice_date = DateField(
        "Date",
        format="%Y-%m-%d",
        validators=[DataRequired()]
    )

    submit = SubmitField("Publish Notice")

class LibraryForm(FlaskForm):

    book_code = StringField(
        "Book Code",
        validators=[DataRequired()]
    )

    book_name = StringField(
        "Book Name",
        validators=[DataRequired()]
    )

    author = StringField(
        "Author",
        validators=[DataRequired()]
    )

    quantity = IntegerField(
        "Quantity",
        validators=[DataRequired()]
    )

    submit = SubmitField("Save Book")


class BookIssueForm(FlaskForm):

    student = SelectField(
        "Student",
        coerce=int
    )

    book = SelectField(
        "Book",
        coerce=int
    )

    issue_date = DateField(
        "Issue Date",
        format="%Y-%m-%d",
        validators=[DataRequired()]
    )

    submit = SubmitField("Issue Book")