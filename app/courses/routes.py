from flask import render_template, request, flash, redirect, url_for, session
from app.courses import courses_bp
from app.courses.service import (
    add_course, list_courses, delete_course, assign_student_to_course,
    get_course_by_id, remove_student_from_course, search_courses, update_course
)
from app.teachers.service import list_teachers
from app.students.service import list_students
from app.auth.decorators import login_required, role_required

def get_student_by_email(email):
    from app.students.service import _load_students
    students = _load_students()
    for s in students:
        if s['email'] == email:
            return s
    return None

def get_teacher_by_email(email):
    from app.teachers.service import _load_teachers
    teachers = _load_teachers()
    for t in teachers:
        if t['email'] == email:
            return t
    return None

@courses_bp.route('/')
@login_required
def list():
    # L'admin voit tous les cours, le prof voit ses cours, l'étudiant voit ses cours (optionnel)
    role = session.get('user_role')
    if role == 'admin':
        q = request.args.get('q', '')
        if q:
            courses = search_courses(q)
        else:
            courses = list_courses()
        return render_template('courses/list.html', courses=courses, query=q)
    elif role == 'teacher':
        teacher = get_teacher_by_email(session['user_email'])
        if teacher:
            all_courses = list_courses()
            my_courses = [c for c in all_courses if c['teacher_id'] == teacher['id']]
            return render_template('courses/teacher_courses.html', courses=my_courses)
        else:
            flash('Enseignant non trouvé.', 'danger')
            return redirect(url_for('dashboard.index'))
    else:
        # student
        student = get_student_by_email(session['user_email'])
        if student:
            all_courses = list_courses()
            my_courses = [c for c in all_courses if student['id'] in c['student_ids']]
            return render_template('courses/student_courses.html', courses=my_courses)
        else:
            flash('Étudiant non trouvé.', 'danger')
            return redirect(url_for('dashboard.index'))

@courses_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def create():
    teachers = list_teachers()
    if request.method == 'POST':
        title = request.form.get('title')
        teacher_id = request.form.get('teacher_id')
        day = request.form.get('day')
        time = request.form.get('time')
        room = request.form.get('room')
        if title and teacher_id:
            try:
                teacher_id = int(teacher_id)
                schedule = {'day': day, 'time': time, 'room': room}
                add_course(title, teacher_id, schedule)
                flash('Cours créé.', 'success')
                return redirect(url_for('courses.list'))
            except ValueError:
                flash('Données invalides.', 'danger')
        else:
            flash('Titre et enseignant requis.', 'danger')
    return render_template('courses/create.html', teachers=teachers)

@courses_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit(id):
    course = get_course_by_id(id)
    if not course:
        flash('Cours introuvable.', 'danger')
        return redirect(url_for('courses.list'))
    teachers = list_teachers()
    if request.method == 'POST':
        title = request.form.get('title')
        teacher_id = request.form.get('teacher_id')
        day = request.form.get('day')
        time = request.form.get('time')
        room = request.form.get('room')
        if title and teacher_id:
            try:
                teacher_id = int(teacher_id)
                schedule = {'day': day, 'time': time, 'room': room}
                update_course(id, title=title, teacher_id=teacher_id, schedule=schedule)
                flash('Cours modifié.', 'success')
                return redirect(url_for('courses.list'))
            except ValueError:
                flash('Données invalides.', 'danger')
        else:
            flash('Titre et enseignant requis.', 'danger')
    return render_template('courses/edit.html', course=course, teachers=teachers)

@courses_bp.route('/delete/<int:id>')
@login_required
@role_required('admin')
def delete(id):
    delete_course(id)
    flash('Cours supprimé.', 'info')
    return redirect(url_for('courses.list'))

@courses_bp.route('/assign/<int:course_id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def assign(course_id):
    course = get_course_by_id(course_id)
    if not course:
        flash('Cours introuvable.', 'danger')
        return redirect(url_for('courses.list'))
    students = list_students()
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        if student_id:
            try:
                student_id = int(student_id)
                if assign_student_to_course(course_id, student_id):
                    flash('Étudiant inscrit au cours.', 'success')
                else:
                    flash('Étudiant déjà inscrit ou erreur.', 'warning')
                return redirect(url_for('courses.list'))
            except ValueError:
                flash('ID invalide.', 'danger')
        else:
            flash('Choisissez un étudiant.', 'danger')
    return render_template('courses/assign.html', course=course, students=students)

@courses_bp.route('/remove/<int:course_id>/<int:student_id>')
@login_required
@role_required('admin')
def remove_student(course_id, student_id):
    if remove_student_from_course(course_id, student_id):
        flash('Étudiant retiré du cours.', 'info')
    else:
        flash('Opération impossible.', 'warning')
    return redirect(url_for('courses.list'))

@courses_bp.route('/schedule')
@login_required
def schedule():
    role = session.get('user_role')
    if role == 'student':
        student = get_student_by_email(session['user_email'])
        if student:
            all_courses = list_courses()
            my_courses = [c for c in all_courses if student['id'] in c['student_ids']]
            return render_template('courses/my_schedule.html', courses=my_courses)
        else:
            flash('Étudiant non trouvé.', 'danger')
            return redirect(url_for('dashboard.index'))
    elif role == 'teacher':
        teacher = get_teacher_by_email(session['user_email'])
        if teacher:
            all_courses = list_courses()
            my_courses = [c for c in all_courses if c['teacher_id'] == teacher['id']]
            return render_template('courses/teacher_schedule.html', courses=my_courses)
        else:
            flash('Enseignant non trouvé.', 'danger')
            return redirect(url_for('dashboard.index'))
    else:
        # admin
        courses = list_courses()
        return render_template('courses/schedule.html', courses=courses)