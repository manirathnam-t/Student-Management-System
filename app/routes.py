from flask import Blueprint, redirect, url_for, render_template, flash
from flask_login import login_required, current_user
from flask import request
from .models import Student
from .forms import StudentForm
from .extensions import db
from .models import Teacher
from .forms import TeacherForm
from .models import Subject
from .forms import SubjectForm
from .models import Student, Teacher, Subject, Attendance, Department, Course, Mark, Fee
from .forms import AttendanceForm
from datetime import date
from sqlalchemy import func
from .models import Department
from .forms import DepartmentForm
from .models import Course
from .forms import CourseForm
from .forms import MarkForm
from .forms import FeeForm
from .models import Timetable
from .forms import TimetableForm
from .models import Notice
from .forms import NoticeForm
from .models import Library
from .forms import LibraryForm
from .models import BookIssue
from .forms import BookIssueForm
import os
from werkzeug.utils import secure_filename
from flask import current_app
from .extensions import bcrypt
from .models import User
from .models import Student, Teacher, Subject
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from flask import send_file
from datetime import datetime
from app.models import Department, Course
from flask import jsonify



main = Blueprint("main", __name__)


@main.route("/")
def home():
    return redirect(url_for("auth.login"))


@main.route("/admin/dashboard")
@login_required
def admin_dashboard():

    total_students = Student.query.count()
    total_teachers = Teacher.query.count()
    total_subjects = Subject.query.count()
    total_departments = Department.query.count()

    latest_notices = Notice.query.order_by(
        Notice.notice_date.desc()
    ).limit(5).all()

    return render_template(
        "admin/dashboard.html",
        total_students=total_students,
        total_teachers=total_teachers,
        total_subjects=total_subjects,
        total_departments=total_departments,
        latest_notices=latest_notices
    )

@main.route("/teacher/dashboard")
@login_required
def teacher_dashboard():

    total_students = Student.query.count()

    total_subjects = Subject.query.count()

    total_teachers = Teacher.query.count()

    return render_template(
        "teacher/dashboard.html",
        total_students=total_students,
        total_subjects=total_subjects,
        total_teachers=total_teachers
    )

@main.route("/teacher/students")
@login_required
def teacher_students():

    students = Student.query.all()

    return render_template(
        "teacher/students.html",
        students=students
    )

@main.route("/teacher/attendance", methods=["GET", "POST"])
@login_required
def teacher_attendance():

    students = Student.query.order_by(Student.name).all()
    subjects = Subject.query.order_by(Subject.subject_name).all()

    if request.method == "POST":

        subject_id = request.form.get("subject_id")

        present_students = request.form.getlist("present_students")

        # Remove today's attendance for this subject
        Attendance.query.filter_by(
            subject_id=subject_id,
            attendance_date=date.today()
        ).delete()

        # Save attendance for all students
        for student in students:

            status = "Present" if str(student.id) in present_students else "Absent"

            attendance = Attendance(
                student_id=student.id,
                subject_id=subject_id,
                attendance_date=date.today(),
                status=status
            )

            db.session.add(attendance)

        db.session.commit()

        flash("Attendance saved successfully!", "success")

        return redirect(url_for("main.teacher_attendance"))

    return render_template(
        "teacher/attendance.html",
        students=students,
        subjects=subjects,
        today=date.today()
    )
@main.route("/students/add", methods=["GET", "POST"])
@login_required
def add_student():

    form = StudentForm()

    print("\n==============================")
    print("Request Method:", request.method)

    # -------------------------------
    # Load Departments
    # -------------------------------
    departments = Department.query.order_by(Department.name).all()

    form.department.choices = [
        (d.id, d.name)
        for d in departments
    ]

    # -------------------------------
    # Load Courses
    # -------------------------------
    form.course.choices = []

    if form.department.data:
        courses = Course.query.filter_by(
            department_id=form.department.data
        ).order_by(Course.course_name).all()

        form.course.choices = [
            (c.id, c.course_name)
            for c in courses
        ]

    # -------------------------------
    # Debug POST
    # -------------------------------
    if request.method == "POST":
        print("POST RECEIVED")
        print("Form Errors:", form.errors)
        print("Department:", form.department.data)
        print("Course:", form.course.data)

    # -------------------------------
    # Validate Form
    # -------------------------------
    if form.validate_on_submit():

        print("FORM VALIDATED")

        # Reload Courses
        courses = Course.query.filter_by(
            department_id=form.department.data
        ).order_by(Course.course_name).all()

        form.course.choices = [
            (c.id, c.course_name)
            for c in courses
        ]

        # Check Register Number
        existing_student = Student.query.filter_by(
            register_no=form.register_no.data
        ).first()

        if existing_student:
            flash("Register Number already exists!", "danger")
            return redirect(url_for("main.add_student"))

        # Check Email
        existing_user = User.query.filter_by(
            email=form.email.data
        ).first()

        if existing_user:
            flash("Email already exists!", "danger")
            return redirect(url_for("main.add_student"))

        # Upload Photo
        filename = "default.png"

        if form.photo.data:

            photo = form.photo.data

            filename = secure_filename(photo.filename)

            photo.save(
                os.path.join(
                    current_app.config["UPLOAD_FOLDER"],
                    filename
                )
            )

        # -------------------------------
        # Create Student
        # -------------------------------
        student = Student(
            register_no=form.register_no.data,
            name=form.name.data,
            gender=form.gender.data,
            dob=form.dob.data,
            department_id=int(form.department.data),
            course_id=int(form.course.data),
            year=int(form.year.data),
            section=form.section.data,
            email=form.email.data,
            phone=form.phone.data,
            address=form.address.data,
            photo=filename
        )

        print("Saving Student...")

        db.session.add(student)

        # -------------------------------
        # Create Login
        # -------------------------------
        hashed_password = bcrypt.generate_password_hash(
            form.password.data
        ).decode("utf-8")

        user = User(
            name=form.name.data,
            email=form.email.data,
            password=hashed_password,
            role="Student"
        )

        db.session.add(user)

        try:
            db.session.commit()
            print("STUDENT SAVED SUCCESSFULLY")
            flash("Student Added Successfully!", "success")
            return redirect(url_for("main.view_students"))

        except Exception as e:
            db.session.rollback()
            print("DATABASE ERROR:")
            print(e)
            flash(str(e), "danger")

    else:
        if request.method == "POST":
            print("FORM VALIDATION FAILED")
            print(form.errors)

    return render_template(
        "students/add_student.html",
        form=form
    )


@main.route("/students")
@login_required
def view_students():

    search = request.args.get("search", "")

    if search:
        students = Student.query.filter(
            (Student.name.contains(search)) |
            (Student.register_no.contains(search))
        ).all()
    else:
        students = Student.query.order_by(Student.id).all()

    return render_template(
        "students/view_students.html",
        students=students,
        search=search
    )


@main.route("/students/delete/<int:id>")
@login_required
def delete_student(id):

    student = Student.query.get_or_404(id)

    db.session.delete(student)
    db.session.commit()

    flash("Student deleted successfully!", "success")

    return redirect(url_for("main.view_students"))
@main.route("/students/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_student(id):

    student = Student.query.get_or_404(id)

    form = StudentForm(obj=student)

    if form.validate_on_submit():

        student.register_no = form.register_no.data
        student.name = form.name.data
        student.gender = form.gender.data
        student.dob = form.dob.data
        student.department = form.department.data
        student.course = form.course.data
        student.year = form.year.data
        student.section = form.section.data
        student.email = form.email.data
        student.phone = form.phone.data
        student.address = form.address.data

        # Update photo if a new one is uploaded
        if form.photo.data:

            photo = form.photo.data

            filename = secure_filename(photo.filename)

            photo.save(
                os.path.join(
                    current_app.config["UPLOAD_FOLDER"],
                    filename
                )
            )

            student.photo = filename

        db.session.commit()

        flash("Student Updated Successfully!", "success")

        return redirect(url_for("main.view_students"))

    return render_template(
        "students/add_student.html",
        form=form
    )
@main.route("/students/view/<int:id>")
@login_required
def view_student(id):

    student = Student.query.get_or_404(id)

    attendance_records = Attendance.query.filter_by(
        student_id=id
    ).all()

    total_present = Attendance.query.filter_by(
        student_id=id,
        status="Present"
    ).count()

    total_absent = Attendance.query.filter_by(
        student_id=id,
        status="Absent"
    ).count()

    total_classes = total_present + total_absent

    percentage = 0

    if total_classes > 0:
        percentage = round(
            (total_present / total_classes) * 100,
            2
        )

    return render_template(
        "students/view_student.html",
        student=student,
        attendance_records=attendance_records,
        total_present=total_present,
        total_absent=total_absent,
        percentage=percentage
    )


@main.route("/students/profile/<int:id>")
@login_required
def view_student_profile(id):

    student = Student.query.get_or_404(id)

    return render_template(
        "students/profile.html",
        student=student
    )

@main.route("/teachers/add", methods=["GET", "POST"])
@login_required
def add_teacher():

    form = TeacherForm()

    if form.validate_on_submit():

        # ----------------------------------
        # Check Employee ID
        # ----------------------------------
        existing_teacher = Teacher.query.filter_by(
            employee_id=form.employee_id.data
        ).first()

        if existing_teacher:
            flash("Employee ID already exists!", "danger")
            return redirect(url_for("main.add_teacher"))

        # ----------------------------------
        # Check Email
        # ----------------------------------
        existing_user = User.query.filter_by(
            email=form.email.data
        ).first()

        if existing_user:
            flash("Email already exists!", "danger")
            return redirect(url_for("main.add_teacher"))

        # ----------------------------------
        # Create Teacher
        # ----------------------------------
        teacher = Teacher(
            employee_id=form.employee_id.data,
            name=form.name.data,
            department=form.department.data,
            subject=form.subject.data,
            email=form.email.data,
            phone=form.phone.data
        )

        db.session.add(teacher)

        # ----------------------------------
        # Create Login Account
        # ----------------------------------
        hashed_password = bcrypt.generate_password_hash(
            form.password.data
        ).decode("utf-8")

        user = User(
            name=form.name.data,
            email=form.email.data,
            password=hashed_password,
            role="Teacher"
        )

        db.session.add(user)

        # ----------------------------------
        # Save Database
        # ----------------------------------
        db.session.commit()

        flash("Teacher Added Successfully!", "success")

        return redirect(url_for("main.view_teachers"))

    return render_template(
        "teachers/add_teacher.html",
        form=form
    )



@main.route("/teachers")
@login_required
def view_teachers():

    search = request.args.get("search", "")

    if search:

        teachers = Teacher.query.filter(
            Teacher.name.contains(search)
        ).all()

    else:

        teachers = Teacher.query.order_by(Teacher.id).all()

    return render_template(
        "teachers/view_teachers.html",
        teachers=teachers,
        search=search
    )


@main.route("/teachers/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_teacher(id):

    teacher = Teacher.query.get_or_404(id)

    form = TeacherForm(obj=teacher)

    if form.validate_on_submit():

        teacher.employee_id = form.employee_id.data
        teacher.name = form.name.data
        teacher.department = form.department.data
        teacher.subject = form.subject.data
        teacher.email = form.email.data
        teacher.phone = form.phone.data

        db.session.commit()

        flash(
            "Teacher Updated Successfully!",
            "success"
        )

        return redirect(url_for("main.view_teachers"))

    return render_template(
        "teachers/add_teacher.html",
        form=form
    )


@main.route("/teachers/delete/<int:id>")
@login_required
def delete_teacher(id):

    teacher = Teacher.query.get_or_404(id)

    db.session.delete(teacher)

    db.session.commit()

    flash(
        "Teacher Deleted Successfully!",
        "success"
    )

    return redirect(
        url_for("main.view_teachers")
    )


@main.route("/teachers/view/<int:id>")
@login_required
def view_teacher(id):

    teacher = Teacher.query.get_or_404(id)

    return render_template(
        "teachers/view_teacher.html",
        teacher=teacher
    )


@main.route("/subjects/add", methods=["GET", "POST"])
@login_required
def add_subject():

    form = SubjectForm()

    if form.validate_on_submit():

        subject = Subject(
            subject_code=form.subject_code.data,
            subject_name=form.subject_name.data,
            semester=form.semester.data,
            credits=form.credits.data,
            department=form.department.data
        )

        db.session.add(subject)
        db.session.commit()

        flash("Subject Added Successfully!", "success")

        return redirect(url_for("main.view_subjects"))

    return render_template(
        "subjects/add_subject.html",
        form=form
    )


@main.route("/courses/add", methods=["GET", "POST"])
@login_required
def add_course():

    form = CourseForm()

    if form.validate_on_submit():

        course = Course(

            course_code=form.course_code.data,

            course_name=form.course_name.data,

            duration=form.duration.data,

            description=form.description.data

        )

        db.session.add(course)

        db.session.commit()

        flash(
            "Course Added Successfully!",
            "success"
        )

        return redirect(
            url_for("main.view_courses")
        )

    return render_template(
        "courses/add_course.html",
        form=form
    )

@main.route("/courses")
@login_required
def view_courses():

    courses = Course.query.order_by(Course.id).all()

    return render_template(
        "courses/view_courses.html",
        courses=courses
    )

@main.route("/courses/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_course(id):

    course = Course.query.get_or_404(id)

    form = CourseForm(obj=course)

    if form.validate_on_submit():

        course.course_code = form.course_code.data
        course.course_name = form.course_name.data
        course.duration = form.duration.data
        course.description = form.description.data

        db.session.commit()

        flash(
            "Course Updated Successfully!",
            "success"
        )

        return redirect(
            url_for("main.view_courses")
        )

    return render_template(
        "courses/add_course.html",
        form=form
    )


@main.route("/subjects")
@login_required
def view_subjects():

    search = request.args.get("search", "")

    if search:

        subjects = Subject.query.filter(
            Subject.subject_name.contains(search)
        ).all()

    else:

        subjects = Subject.query.order_by(Subject.id).all()

    return render_template(
        "subjects/view_subjects.html",
        subjects=subjects,
        search=search
    )



@main.route("/attendance", methods=["GET", "POST"])
@login_required
def attendance():

    form = AttendanceForm()

    form.subject.choices = [

        (subject.id, subject.subject_name)

        for subject in Subject.query.all()

    ]

    students = Student.query.order_by(Student.name).all()

    form.attendance_date.data = date.today()

    if form.validate_on_submit():

        print("Selected Subject:", form.subject.data)
        print("Selected Date:", form.attendance_date.data)

        for student in students:

            status = request.form.get(
                f"student_{student.id}"
            )

            existing = Attendance.query.filter_by(
                student_id=student.id,
                subject_id=form.subject.data,
                attendance_date=form.attendance_date.data
            ).first()

            if existing:
                continue

            attendance = Attendance(

                student_id=student.id,

                subject_id=form.subject.data,

                attendance_date=form.attendance_date.data,

                status=status

            )

            db.session.add(attendance)

        db.session.commit()

        flash(
            "Attendance Saved Successfully!",
            "success"
        )

        return redirect(
            url_for("main.attendance")
        )

    return render_template(

        "attendance/attendance.html",

        form=form,

        students=students

    )

@main.route("/attendance/view")
@login_required
def view_attendance():

    search = request.args.get("search", "")
    subject = request.args.get("subject", "")
    attendance_date = request.args.get("date", "")

    query = Attendance.query

    if search:
        query = query.join(Student).filter(
            Student.name.contains(search)
        )

    if subject:
        query = query.join(Subject).filter(
            Subject.subject_name == subject
        )

    if attendance_date:
        query = query.filter(
            Attendance.attendance_date == attendance_date
        )

    records = query.order_by(
        Attendance.attendance_date.desc()
    ).all()

    subjects = Subject.query.order_by(
        Subject.subject_name
    ).all()

    return render_template(
        "attendance/view_attendance.html",
        records=records,
        subjects=subjects,
        search=search,
        subject=subject,
        attendance_date=attendance_date
    )


@main.route("/reports")
@login_required
def reports():

    total_students = Student.query.count()

    total_teachers = Teacher.query.count()

    total_subjects = Subject.query.count()

    total_attendance = Attendance.query.count()

    present_count = Attendance.query.filter_by(
        status="Present"
    ).count()

    absent_count = Attendance.query.filter_by(
        status="Absent"
    ).count()

    percentage = 0

    if total_attendance > 0:

        percentage = round(
            (present_count / total_attendance) * 100,
            2
        )

    return render_template(

        "reports/dashboard.html",

        total_students=total_students,

        total_teachers=total_teachers,

        total_subjects=total_subjects,

        total_attendance=total_attendance,

        present_count=present_count,

        absent_count=absent_count,

        percentage=percentage
    )

@main.route("/departments/add", methods=["GET", "POST"])
@login_required
def add_department():

    form = DepartmentForm()

    if form.validate_on_submit():

        department = Department(
            name=form.name.data,
            hod=form.hod.data,
            description=form.description.data
        )

        db.session.add(department)
        db.session.commit()

        flash(
            "Department Added Successfully!",
            "success"
        )

        return redirect(
            url_for("main.view_departments")
        )

    return render_template(
        "departments/add_department.html",
        form=form
    )


@main.route("/departments")
@login_required
def view_departments():

    search = request.args.get("search", "")

    if search:

        departments = Department.query.filter(
            Department.name.contains(search)
        ).all()

    else:

        departments = Department.query.order_by(
            Department.id
        ).all()

    return render_template(
        "departments/view_departments.html",
        departments=departments,
        search=search
    )

@main.route("/departments/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_department(id):

    department = Department.query.get_or_404(id)

    form = DepartmentForm(obj=department)

    if form.validate_on_submit():

        department.name = form.name.data
        department.hod = form.hod.data
        department.description = form.description.data

        db.session.commit()

        flash("Department Updated Successfully!", "success")

        return redirect(url_for("main.view_departments"))

    return render_template(
        "departments/add_department.html",
        form=form
    )

@main.route("/departments/delete/<int:id>")
@login_required
def delete_department(id):

    department = Department.query.get_or_404(id)

    db.session.delete(department)
    db.session.commit()

    flash(
        "Department Deleted Successfully!",
        "success"
    )

    return redirect(
        url_for("main.view_departments")
    )

@main.route("/courses/delete/<int:id>")
@login_required
def delete_course(id):

    course = Course.query.get_or_404(id)

    db.session.delete(course)
    db.session.commit()

    flash("Course Deleted Successfully!", "success")

    return redirect(url_for("main.view_courses"))


@main.route("/student")
@login_required
def student_dashboard():

    student = Student.query.filter_by(
        email=current_user.email
    ).first()

    attendance = []
    attendance_percentage = 0
    total_subjects = Subject.query.count()

    if student:

        attendance = Attendance.query.filter_by(
            student_id=student.id
        ).order_by(
            Attendance.attendance_date.desc()
        ).limit(10).all()

        total = Attendance.query.filter_by(
            student_id=student.id
        ).count()

        present = Attendance.query.filter_by(
            student_id=student.id,
            status="Present"
        ).count()

        if total > 0:
            attendance_percentage = round(
                (present / total) * 100,
                2
            )

    return render_template(
        "student/dashboard.html",
        student=student,
        attendance=attendance,
        attendance_percentage=attendance_percentage,
        total_subjects=total_subjects
    )
@main.route("/marks/add", methods=["GET", "POST"])
@login_required
def add_marks():

    form = MarkForm()

    form.student.choices = [
        (student.id, student.name)
        for student in Student.query.order_by(Student.name).all()
    ]

    form.subject.choices = [
        (subject.id, subject.subject_name)
        for subject in Subject.query.order_by(Subject.subject_name).all()
    ]

    if form.validate_on_submit():

        total = form.internal.data + form.external.data

        if total >= 90:
            grade = "A+"
        elif total >= 80:
            grade = "A"
        elif total >= 70:
            grade = "B"
        elif total >= 60:
            grade = "C"
        elif total >= 50:
            grade = "D"
        else:
            grade = "F"

        mark = Mark(
            student_id=form.student.data,
            subject_id=form.subject.data,
            internal=form.internal.data,
            external=form.external.data,
            total=total,
            grade=grade
        )

        db.session.add(mark)
        db.session.commit()

        flash("Marks Added Successfully!", "success")

        return redirect(url_for("main.view_marks"))

    return render_template(
        "marks/add_marks.html",
        form=form
    )


@main.route("/result/<int:student_id>")
@login_required
def student_result(student_id):

    student = Student.query.get_or_404(student_id)

    marks = Mark.query.filter_by(student_id=student.id).all()

    total_marks = sum(mark.total for mark in marks)

    percentage = total_marks / len(marks) if marks else 0

    result = "PASS"

    for mark in marks:
        if mark.grade == "F":
            result = "FAIL"
            break

    return render_template(
        "marks/result.html",
        student=student,
        marks=marks,
        percentage=percentage,
        result=result
    )


@main.route("/result/pdf/<int:student_id>")
@login_required
def download_result_pdf(student_id):

    student = Student.query.get_or_404(student_id)

    marks = Mark.query.filter_by(student_id=student.id).all()

    filename = f"Marksheet_{student.register_no}.pdf"

    filepath = os.path.join(
        current_app.root_path,
        filename
    )

    doc = SimpleDocTemplate(filepath)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph(
            "<b>SMART STUDENT MANAGEMENT SYSTEM</b>",
            styles["Title"]
        )
    )

    elements.append(
        Paragraph(f"Name : {student.name}", styles["Normal"])
    )

    elements.append(
        Paragraph(f"Register No : {student.register_no}", styles["Normal"])
    )

    elements.append(
        Paragraph(f"Department : {student.department}", styles["Normal"])
    )

    elements.append(
        Paragraph("<br/>", styles["Normal"])
    )

    data = [
        [
            "Subject",
            "Internal",
            "External",
            "Total",
            "Grade"
        ]
    ]

    total_marks = 0

    for mark in marks:

        data.append([
            mark.subject.subject_name,
            mark.internal,
            mark.external,
            mark.total,
            mark.grade
        ])

        total_marks += mark.total

    table = Table(data)

    table.setStyle(TableStyle([

        ("BACKGROUND", (0,0), (-1,0), colors.darkblue),

        ("TEXTCOLOR", (0,0), (-1,0), colors.white),

        ("GRID", (0,0), (-1,-1), 1, colors.black),

        ("ALIGN", (0,0), (-1,-1), "CENTER"),

        ("BACKGROUND", (0,1), (-1,-1), colors.beige)

    ]))

    elements.append(table)

    percentage = total_marks / len(marks) if marks else 0

    result = "PASS"

    for mark in marks:
        if mark.grade == "F":
            result = "FAIL"

    elements.append(
        Paragraph(f"<br/>Percentage : {percentage:.2f}%", styles["Heading2"])
    )

    elements.append(
        Paragraph(f"Result : {result}", styles["Heading2"])
    )

    doc.build(elements)

    return send_file(
        filepath,
        as_attachment=True
    )

@main.route("/marks")
@login_required
def view_marks():

    search = request.args.get("search", "")

    query = Mark.query

    if search:
        query = query.join(Student).filter(
            Student.name.ilike(f"%{search}%")
        )

    marks = query.order_by(Mark.id.desc()).all()

    return render_template(
        "marks/view_marks.html",
        marks=marks,
        search=search,
        teacher=False
    )
@main.route("/marks/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_marks(id):

    mark = Mark.query.get_or_404(id)

    form = MarkForm()

    form.student.choices = [
        (s.id, s.name)
        for s in Student.query.order_by(Student.name).all()
    ]

    form.subject.choices = [
        (s.id, s.subject_name)
        for s in Subject.query.order_by(Subject.subject_name).all()
    ]

    if form.validate_on_submit():

        mark.student_id = form.student.data
        mark.subject_id = form.subject.data

        mark.internal = form.internal.data
        mark.external = form.external.data

        # Calculate Total
        mark.total = mark.internal + mark.external

        # Grade & Result
        if mark.total >= 90:
            mark.grade = "A+"
            mark.result = "Pass"

        elif mark.total >= 80:
            mark.grade = "A"
            mark.result = "Pass"

        elif mark.total >= 70:
            mark.grade = "B"
            mark.result = "Pass"

        elif mark.total >= 60:
            mark.grade = "C"
            mark.result = "Pass"

        elif mark.total >= 50:
            mark.grade = "D"
            mark.result = "Pass"

        else:
            mark.grade = "F"
            mark.result = "Fail"

        db.session.commit()

        flash("✅ Marks Updated Successfully!", "success")

        return redirect(url_for("main.view_marks"))

    # Pre-fill form
    form.student.data = mark.student_id
    form.subject.data = mark.subject_id
    form.internal.data = mark.internal
    form.external.data = mark.external

    return render_template(
        "marks/add_marks.html",
        form=form,
        edit=True
    )


@main.route("/marks/delete/<int:id>")
@login_required
def delete_marks(id):

    mark = Mark.query.get_or_404(id)

    db.session.delete(mark)
    db.session.commit()

    flash("Marks Deleted Successfully!", "success")

    return redirect(url_for("main.view_marks"))

@main.route("/fees/add", methods=["GET", "POST"])
@login_required
def add_fee():

    form = FeeForm()

    form.student.choices = [
        (student.id, student.name)
        for student in Student.query.order_by(Student.name).all()
    ]

    if form.validate_on_submit():

        balance = form.amount.data - form.paid.data

        if balance <= 0:
            status = "Paid"
        else:
            status = "Pending"

        fee = Fee(
            student_id=form.student.data,
            amount=form.amount.data,
            paid=form.paid.data,
            balance=balance,
            status=status
        )

        db.session.add(fee)
        db.session.commit()

        flash("Fee Added Successfully!", "success")

        return redirect(url_for("main.view_fees"))

    return render_template(
        "fees/add_fee.html",
        form=form
    )

@main.route("/fees")
@login_required
def view_fees():

    fees = Fee.query.order_by(Fee.id.desc()).all()

    return render_template(
        "fees/view_fees.html",
        fees=fees
    )

@main.route("/fees/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_fee(id):

    fee = Fee.query.get_or_404(id)

    form = FeeForm()

    form.student.choices = [
        (student.id, student.name)
        for student in Student.query.order_by(Student.name).all()
    ]

    if form.validate_on_submit():

        fee.student_id = form.student.data
        fee.amount = form.amount.data
        fee.paid = form.paid.data

        fee.balance = fee.amount - fee.paid

        if fee.balance <= 0:
            fee.status = "Paid"
        else:
            fee.status = "Pending"

        db.session.commit()

        flash("Fee Updated Successfully!", "success")

        return redirect(url_for("main.view_fees"))

    form.student.data = fee.student_id
    form.amount.data = fee.amount
    form.paid.data = fee.paid

    return render_template(
        "fees/add_fee.html",
        form=form
    )

@main.route("/fees/delete/<int:id>")
@login_required
def delete_fee(id):

    fee = Fee.query.get_or_404(id)

    db.session.delete(fee)

    db.session.commit()

    flash("Fee Deleted Successfully!", "success")

    return redirect(url_for("main.view_fees"))

@main.route("/timetable/add", methods=["GET", "POST"])
@login_required
def add_timetable():

    form = TimetableForm()

    form.department.choices = [
        (d.id, d.name)
        for d in Department.query.order_by(Department.name).all()
    ]

    form.course.choices = [
        (c.id, c.course_name)
        for c in Course.query.order_by(Course.course_name).all()
    ]

    form.subject.choices = [
        (s.id, s.subject_name)
        for s in Subject.query.order_by(Subject.subject_name).all()
    ]

    form.teacher.choices = [
        (t.id, t.name)
        for t in Teacher.query.order_by(Teacher.name).all()
    ]

    if form.validate_on_submit():

        timetable = Timetable(
            day=form.day.data,
            period=form.period.data,
            department_id=form.department.data,
            course_id=form.course.data,
            year=form.year.data,
            section=form.section.data,
            subject_id=form.subject.data,
            teacher_id=form.teacher.data,
            classroom=form.classroom.data
        )

        db.session.add(timetable)
        db.session.commit()

        flash("Timetable Added Successfully!", "success")

        return redirect(url_for("main.view_timetable"))

    return render_template(
        "timetable/add_timetable.html",
        form=form
    )


@main.route("/teacher/timetable")
@login_required
def teacher_timetable():

    timetable = Timetable.query.order_by(
        Timetable.day,
        Timetable.period
    ).all()

    return render_template(
        "teacher/timetable.html",
        timetable=timetable
    )

@main.route("/timetable")
@login_required
def view_timetable():

    timetable = Timetable.query.all()

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

    timetable_data = {}

    for day in days:
        timetable_data[day] = {}

    for row in timetable:

        timetable_data[row.day][str(row.period)] = row

    return render_template(
        "timetable/view_timetable.html",
        timetable_data=timetable_data,
        days=days
    )
@main.route("/timetable/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_timetable(id):

    timetable = Timetable.query.get_or_404(id)

    form = TimetableForm()

    form.department.choices = [
        (d.id, d.name)
        for d in Department.query.order_by(Department.name).all()
    ]

    form.course.choices = [
        (c.id, c.course_name)
        for c in Course.query.order_by(Course.course_name).all()
    ]

    form.subject.choices = [
        (s.id, s.subject_name)
        for s in Subject.query.order_by(Subject.subject_name).all()
    ]

    form.teacher.choices = [
        (t.id, t.name)
        for t in Teacher.query.order_by(Teacher.name).all()
    ]

    if form.validate_on_submit():

        timetable.day = form.day.data
        timetable.period = form.period.data
        timetable.department_id = form.department.data
        timetable.course_id = form.course.data
        timetable.year = form.year.data
        timetable.section = form.section.data
        timetable.subject_id = form.subject.data
        timetable.teacher_id = form.teacher.data
        timetable.classroom = form.classroom.data

        db.session.commit()

        flash("Timetable Updated Successfully!", "success")

        return redirect(url_for("main.view_timetable"))

    form.day.data = timetable.day
    form.period.data = timetable.period
    form.department.data = timetable.department_id
    form.course.data = timetable.course_id
    form.year.data = timetable.year
    form.section.data = timetable.section
    form.subject.data = timetable.subject_id
    form.teacher.data = timetable.teacher_id
    form.classroom.data = timetable.classroom

    return render_template(
        "timetable/add_timetable.html",
        form=form
    )


@main.route("/timetable/delete/<int:id>")
@login_required
def delete_timetable(id):

    timetable = Timetable.query.get_or_404(id)

    db.session.delete(timetable)
    db.session.commit()

    flash("Timetable Deleted Successfully!", "success")

    return redirect(url_for("main.view_timetable"))


@main.route("/notice/add", methods=["GET", "POST"])
@login_required
def add_notice():

    form = NoticeForm()

    if form.validate_on_submit():

        notice = Notice(
            title=form.title.data,
            description=form.description.data,
            notice_date=form.notice_date.data
        )

        db.session.add(notice)
        db.session.commit()

        flash("Notice Published Successfully!", "success")

        return redirect(url_for("main.view_notice"))

    return render_template(
        "notice/add_notice.html",
        form=form
    )

@main.route("/notice")
@login_required
def view_notice():

    notices = Notice.query.order_by(
        Notice.notice_date.desc()
    ).all()

    return render_template(
        "notice/view_notice.html",
        notices=notices
    )


@main.route("/notice/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_notice(id):

    notice = Notice.query.get_or_404(id)

    form = NoticeForm()

    if form.validate_on_submit():

        notice.title = form.title.data
        notice.description = form.description.data
        notice.notice_date = form.notice_date.data

        db.session.commit()

        flash("Notice Updated Successfully!", "success")

        return redirect(url_for("main.view_notice"))

    form.title.data = notice.title
    form.description.data = notice.description
    form.notice_date.data = notice.notice_date

    return render_template(
        "notice/add_notice.html",
        form=form
    )


@main.route("/notice/delete/<int:id>")
@login_required
def delete_notice(id):

    notice = Notice.query.get_or_404(id)

    db.session.delete(notice)

    db.session.commit()

    flash("Notice Deleted Successfully!", "success")

    return redirect(url_for("main.view_notice"))

@main.route("/library/add", methods=["GET", "POST"])
@login_required
def add_book():

    form = LibraryForm()

    if form.validate_on_submit():

        book = Library(
            book_code=form.book_code.data,
            book_name=form.book_name.data,
            author=form.author.data,
            quantity=form.quantity.data,
            available=form.quantity.data
        )

        db.session.add(book)
        db.session.commit()

        flash("Book Added Successfully!", "success")

        return redirect(url_for("main.view_books"))

    return render_template(
        "library/add_book.html",
        form=form
    )

@main.route("/library")
@login_required
def view_books():

    books = Library.query.order_by(
        Library.book_name
    ).all()

    return render_template(
        "library/view_books.html",
        books=books
    )

@main.route("/library/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_book(id):

    book = Library.query.get_or_404(id)

    form = LibraryForm()

    if form.validate_on_submit():

        book.book_code = form.book_code.data
        book.book_name = form.book_name.data
        book.author = form.author.data

        old_quantity = book.quantity
        new_quantity = form.quantity.data

        difference = new_quantity - old_quantity

        book.quantity = new_quantity
        book.available += difference

        if book.available < 0:
            book.available = 0

        db.session.commit()

        flash("Book Updated Successfully!", "success")

        return redirect(url_for("main.view_books"))

    form.book_code.data = book.book_code
    form.book_name.data = book.book_name
    form.author.data = book.author
    form.quantity.data = book.quantity

    return render_template(
        "library/add_book.html",
        form=form
    )

@main.route("/library/delete/<int:id>")
@login_required
def delete_book(id):

    book = Library.query.get_or_404(id)

    db.session.delete(book)

    db.session.commit()

    flash("Book Deleted Successfully!", "success")

    return redirect(url_for("main.view_books"))


@main.route("/library/issue", methods=["GET", "POST"])
@login_required
def issue_book():

    form = BookIssueForm()

    form.student.choices = [
        (student.id, student.name)
        for student in Student.query.order_by(Student.name).all()
    ]

    form.book.choices = [
        (book.id, book.book_name)
        for book in Library.query.order_by(Library.book_name).all()
    ]

    if form.validate_on_submit():

        book = Library.query.get(form.book.data)

        if book.available <= 0:

            flash("Book is not available!", "danger")

            return redirect(url_for("main.issue_book"))

        issue = BookIssue(
            student_id=form.student.data,
            book_id=form.book.data,
            issue_date=form.issue_date.data
        )

        book.available -= 1

        db.session.add(issue)

        db.session.commit()

        flash("Book Issued Successfully!", "success")

        return redirect(url_for("main.view_issued_books"))

    return render_template(
        "library/issue_book.html",
        form=form
    )


@main.route("/library/issued")
@login_required
def view_issued_books():

    books = BookIssue.query.order_by(
        BookIssue.issue_date.desc()
    ).all()

    return render_template(
        "library/view_issued_books.html",
        books=books
    )

@main.route("/library/return/<int:id>")
@login_required
def return_book(id):

    issue = BookIssue.query.get_or_404(id)

    if issue.status == "Returned":

        flash("Book already returned!", "warning")

        return redirect(url_for("main.view_issued_books"))

    issue.status = "Returned"

    issue.return_date = date.today()

    issue.book.available += 1

    db.session.commit()

    flash("Book Returned Successfully!", "success")

    return redirect(url_for("main.view_issued_books"))



@main.route("/create-teacher")
def create_teacher():

    teacher = User(
    name="Abi",
    email="teacher@gmail.com",
    password=bcrypt.generate_password_hash("teacher123").decode("utf-8"),
    role="Teacher"
)

    db.session.add(teacher)
    db.session.commit()

    return "Teacher Created Successfully!"
@main.route("/teacher/marks", methods=["GET", "POST"])
@login_required
def teacher_marks():

    students = Student.query.order_by(Student.name).all()
    subjects = Subject.query.order_by(Subject.subject_name).all()

    if request.method == "POST":

        student_id = request.form.get("student_id")
        subject_id = request.form.get("subject_id")

        internal = int(request.form.get("internal"))
        external = int(request.form.get("external"))

        total = internal + external

        # Grade Calculation
        if total >= 90:
            grade = "A+"
        elif total >= 80:
            grade = "A"
        elif total >= 70:
            grade = "B"
        elif total >= 60:
            grade = "C"
        elif total >= 50:
            grade = "D"
        else:
            grade = "F"

        # Pass / Fail
        if total >= 50:
            result = "Pass"
        else:
            result = "Fail"

        # Check existing marks
        existing_mark = Mark.query.filter_by(
            student_id=student_id,
            subject_id=subject_id
        ).first()

        if existing_mark:

            existing_mark.internal = internal
            existing_mark.external = external
            existing_mark.total = total
            existing_mark.grade = grade
            existing_mark.result = result

        else:

            mark = Mark(
                student_id=student_id,
                subject_id=subject_id,
                internal=internal,
                external=external,
                total=total,
                grade=grade,
                result=result
            )

            db.session.add(mark)

        db.session.commit()

        flash("Marks saved successfully!", "success")

        return redirect(url_for("main.teacher_marks"))

    return render_template(
        "teacher/marks.html",
        students=students,
        subjects=subjects
    )


@main.route("/teacher/view-marks")
@login_required
def teacher_view_marks():

    search = request.args.get("search", "")

    query = Mark.query

    if search:
        query = query.join(Student).filter(
            Student.name.ilike(f"%{search}%")
        )

    marks = query.order_by(Mark.id.desc()).all()

    return render_template(
        "marks/view_marks.html",   # use the existing template
        marks=marks,
        search=search,
        teacher=True
    )

@main.route("/student/marks")
@login_required
def student_marks():

    student = Student.query.filter_by(
        email=current_user.email
    ).first()

    marks = []

    if student:

        marks = Mark.query.filter_by(
            student_id=student.id
        ).all()

    return render_template(
        "student/marks.html",
        student=student,
        marks=marks
    )


@main.route("/student/attendance")
@login_required
def student_attendance():

    student = Student.query.filter_by(
        email=current_user.email
    ).first()

    attendance = []

    attendance_percentage = 0

    if student:

        attendance = Attendance.query.filter_by(
            student_id=student.id
        ).order_by(
            Attendance.attendance_date.desc()
        ).all()

        total = len(attendance)

        present = Attendance.query.filter_by(
            student_id=student.id,
            status="Present"
        ).count()

        if total > 0:
            attendance_percentage = round(
                (present / total) * 100,
                2
            )

    return render_template(
        "student/attendance.html",
        attendance=attendance,
        attendance_percentage=attendance_percentage
    )

@main.route("/student/result")
@login_required
def student_my_result():

    student = Student.query.filter_by(
        email=current_user.email
    ).first_or_404()

    marks = Mark.query.filter_by(
        student_id=student.id
    ).all()

    total_marks = sum(mark.total for mark in marks)

    percentage = total_marks / len(marks) if marks else 0

    result = "PASS"

    for mark in marks:
        if mark.grade == "F":
            result = "FAIL"
            break

    return render_template(
        "marks/result.html",
        student=student,
        marks=marks,
        percentage=percentage,
        result=result
    )

@main.route("/student/profile", methods=["GET", "POST"])
@login_required
def student_profile():

    student = Student.query.filter_by(
        email=current_user.email
    ).first_or_404()

    if request.method == "POST":

        student.phone = request.form.get("phone")
        student.email = request.form.get("email")

        db.session.commit()

        flash("Profile updated successfully!", "success")

        return redirect(url_for("main.student_profile"))

    return render_template(
        "student/profile.html",
        student=student
    )


@main.route("/students/profile/<int:id>")
@login_required
def student_profile_admin(id):

    student = Student.query.get_or_404(id)

    return render_template(
        "students/profile.html",
        student=student
    )


@main.route("/student/change-password", methods=["GET", "POST"])
@login_required
def change_student_password():

    student = Student.query.filter_by(
        email=current_user.email
    ).first_or_404()

    user = User.query.filter_by(
        email=student.email
    ).first_or_404()

    if request.method == "POST":

        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        # Check current password
        if not bcrypt.check_password_hash(
            user.password,
            current_password
        ):
            flash("Current password is incorrect.", "danger")
            return redirect(url_for("main.change_student_password"))

        # Check confirmation
        if new_password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("main.change_student_password"))

        # Update password
        user.password = bcrypt.generate_password_hash(
            new_password
        ).decode("utf-8")

        db.session.commit()

        flash("Password changed successfully!", "success")

        return redirect(url_for("main.student_dashboard"))

    return render_template("student/change_password.html")@main.route("/admin/notices", methods=["GET", "POST"])
@login_required
def admin_notice():

    if request.method == "POST":

        notice = Notice(
            title=request.form.get("title"),
            description=request.form.get("description"),
            notice_date=date.today()
        )

        db.session.add(notice)
        db.session.commit()

        flash("Notice Posted Successfully!", "success")

        return redirect(url_for("main.admin_notice"))

    notices = Notice.query.order_by(
        Notice.notice_date.desc()
    ).all()

    return render_template(
        "admin/notice.html",
        notices=notices
    )
@main.route("/student/notices")
@login_required
def student_notice():

    notices = Notice.query.order_by(
    Notice.notice_date.desc()
).all()

    return render_template(
        "student/notices.html",
        notices=notices
    )

@main.route("/admin/timetable", methods=["GET", "POST"])
@login_required
def admin_timetable():

    form = TimetableForm()

    # Load Subjects
    form.subject.choices = [
        (s.id, s.subject_name)
        for s in Subject.query.all()
    ]

    # Load Teachers
    form.teacher.choices = [
        (t.id, t.name)
        for t in Teacher.query.all()
    ]

    if form.validate_on_submit():

        timetable = Timetable(
            day=form.day.data,
            period=form.period.data,
            subject_id=form.subject.data,
            teacher_id=form.teacher.data,
            classroom=form.classroom.data
        )

        db.session.add(timetable)
        db.session.commit()

        flash("Timetable Added Successfully!", "success")

        return redirect(url_for("main.admin_timetable"))

    timetables = Timetable.query.order_by(
        Timetable.day,
        Timetable.period
    ).all()

    return render_template(
        "admin/timetable.html",
        form=form,
        timetables=timetables
    )


@main.route("/admin/change-password", methods=["GET", "POST"])
@login_required
def change_admin_password():

    user = User.query.filter_by(
        email=current_user.email,
        role="Admin"
    ).first_or_404()

    if request.method == "POST":

        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if not bcrypt.check_password_hash(
            user.password,
            current_password
        ):
            flash("Current password is incorrect.", "danger")
            return redirect(url_for("main.change_admin_password"))

        if new_password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("main.change_admin_password"))

        user.password = bcrypt.generate_password_hash(
            new_password
        ).decode("utf-8")

        db.session.commit()

        flash("Password changed successfully!", "success")

        return redirect(url_for("main.admin_dashboard"))

    return render_template("admin/change_password.html")



@main.route("/teacher/change-password", methods=["GET", "POST"])
@login_required
def change_teacher_password():

    user = User.query.filter_by(
        email=current_user.email,
        role="Teacher"
    ).first_or_404()

    if request.method == "POST":

        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if not bcrypt.check_password_hash(
            user.password,
            current_password
        ):
            flash("Current password is incorrect.", "danger")
            return redirect(url_for("main.change_teacher_password"))

        if new_password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("main.change_teacher_password"))

        user.password = bcrypt.generate_password_hash(
            new_password
        ).decode("utf-8")

        db.session.commit()

        flash("Password changed successfully!", "success")

        return redirect(url_for("main.teacher_dashboard"))

    return render_template("teacher/change_password.html")

@main.route("/teacher/view-attendance", methods=["GET", "POST"])
@login_required
def teacher_view_attendance():

    subjects = Subject.query.all()

    attendance_list = []

    if request.method == "POST":

        subject_id = request.form.get("subject_id")
        attendance_date = request.form.get("attendance_date")

        from datetime import datetime

        attendance_date = datetime.strptime(
            attendance_date,
            "%Y-%m-%d"
        ).date()

        attendance_list = Attendance.query.filter_by(
            subject_id=subject_id,
            attendance_date=attendance_date
        ).all()

    return render_template(
        "teacher/view_attendance.html",
        subjects=subjects,
        attendance_list=attendance_list
    )

@main.route("/teacher/edit-attendance", methods=["GET", "POST"])
@login_required
def teacher_edit_attendance():

    subjects = Subject.query.all()

    attendance_list = []

    if request.method == "POST":

        action = request.form.get("action")

        subject_id = request.form.get("subject_id")

        attendance_date = datetime.strptime(
            request.form.get("attendance_date"),
            "%Y-%m-%d"
        ).date()

        attendance_list = Attendance.query.filter_by(
            subject_id=subject_id,
            attendance_date=attendance_date
        ).all()

        if action == "update":

            for attendance in attendance_list:

                attendance.status = request.form.get(
                    f"status_{attendance.id}"
                )

            db.session.commit()

            flash(
                "Attendance updated successfully!",
                "success"
            )

    return render_template(
        "teacher/edit_attendance.html",
        subjects=subjects,
        attendance_list=attendance_list
    )

@main.route("/admin/profile", methods=["GET", "POST"])
@login_required
def admin_profile():

    user = User.query.filter_by(
        email=current_user.email,
        role="Admin"
    ).first_or_404()

    if request.method == "POST":

        user.name = request.form.get("name")
        user.email = request.form.get("email")

        db.session.commit()

        flash("Profile updated successfully!", "success")

        return redirect(url_for("main.admin_profile"))

    return render_template(
        "admin/profile.html",
        user=user
    )

@main.route("/teacher/profile", methods=["GET", "POST"])
@login_required
def teacher_profile():

    user = User.query.filter_by(
        email=current_user.email,
        role="Teacher"
    ).first_or_404()

    if request.method == "POST":

        user.name = request.form.get("name")
        user.email = request.form.get("email")

        db.session.commit()

        flash("Profile updated successfully!", "success")

        return redirect(url_for("main.teacher_profile"))

    return render_template(
        "teacher/profile.html",
        user=user
    )
@main.route("/get_courses/<int:department_id>")
@login_required
def get_courses(department_id):

    courses = Course.query.filter_by(
        department_id=department_id
    ).order_by(Course.course_name).all()

    data = []

    for course in courses:
        data.append({
            "id": course.id,
            "name": course.course_name
        })

    return jsonify(data)