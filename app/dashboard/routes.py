from flask import render_template, session
from app.dashboard import dashboard_bp
from app.students.service import list_students, get_student_by_id
from app.teachers.service import list_teachers
from app.courses.service import list_courses, _load_courses
from app.auth.decorators import login_required

def get_teacher_by_email(email):
    from app.teachers.service import _load_teachers
    teachers = _load_teachers()
    for t in teachers:
        if t['email'] == email:
            return t
    return None

def get_student_by_email(email):
    from app.students.service import _load_students
    students = _load_students()
    for s in students:
        if s['email'] == email:
            return s
    return None

@dashboard_bp.route('/')
@login_required
def index():
    role = session.get('user_role')
    if role == 'admin':
        students = list_students()
        teachers = list_teachers()
        courses = list_courses()
        total_students = len(students)
        total_teachers = len(teachers)
        total_courses = len(courses)
        courses_stats = [{'title': c['title'], 'students_count': len(c['student_ids'])} for c in courses]
        avg_students = 0
        if total_courses:
            avg_students = sum(sc['students_count'] for sc in courses_stats) / total_courses
        latest_students = sorted(students, key=lambda s: s['id'], reverse=True)[:5]
        raw_courses = _load_courses()
        latest_raw = sorted(raw_courses, key=lambda c: c['id'], reverse=True)[:5]
        latest_courses_info = []
        teachers_list = list_teachers()
        for rc in latest_raw:
            teacher = next((t for t in teachers_list if t['id'] == rc['teacher_id']), None)
            latest_courses_info.append({
                'title': rc['title'],
                'teacher_name': teacher['name'] if teacher else 'Inconnu'
            })
        return render_template('dashboard/admin.html',
                               total_students=total_students,
                               total_teachers=total_teachers,
                               total_courses=total_courses,
                               courses_stats=courses_stats,
                               avg_students=round(avg_students, 1),
                               latest_students=latest_students,
                               latest_courses=latest_courses_info)
    elif role == 'teacher':
        teacher = get_teacher_by_email(session['user_email'])
        if teacher:
            all_courses = list_courses()
            my_courses = [c for c in all_courses if c['teacher_id'] == teacher['id']]
            return render_template('dashboard/teacher.html', teacher=teacher, courses=my_courses)
        else:
            return render_template('dashboard/teacher.html', teacher=None, courses=[])
    else:  # student
        student = get_student_by_email(session['user_email'])
        if student:
            all_courses = list_courses()
            my_courses = [c for c in all_courses if student['id'] in c['student_ids']]
            return render_template('dashboard/student.html', student=student, courses=my_courses)
        else:
            return render_template('dashboard/student.html', student=None, courses=[])