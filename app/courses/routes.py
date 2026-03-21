from flask import render_template, request, flash, redirect, url_for
from app.courses import courses_bp
from app.courses.service import (
    add_course, list_courses, delete_course, assign_student_to_course,
    get_course_by_id, remove_student_from_course, search_courses, get_schedule
)
from app.teachers.service import list_teachers
from app.students.service import list_students
from app.auth.decorators import login_required

@courses_bp.route('/')
@login_required
def list():
    q = request.args.get('q', '')
    if q:
        courses = search_courses(q)
    else:
        courses = list_courses()
    return render_template('courses/list.html', courses=courses, query=q)

@courses_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    teachers = list_teachers()
    if request.method == 'POST':
        title = request.form.get('title')
        teacher_id = request.form.get('teacher_id')
        if title and teacher_id:
            try:
                teacher_id = int(teacher_id)
                add_course(title, teacher_id)
                flash('Cours créé.', 'success')
                return redirect(url_for('courses.list'))
            except ValueError:
                flash('Données invalides.', 'danger')
        else:
            flash('Titre et enseignant requis.', 'danger')
    return render_template('courses/create.html', teachers=teachers)

@courses_bp.route('/delete/<int:id>')
@login_required
def delete(id):
    delete_course(id)
    flash('Cours supprimé.', 'info')
    return redirect(url_for('courses.list'))

@courses_bp.route('/assign/<int:course_id>', methods=['GET', 'POST'])
@login_required
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
def remove_student(course_id, student_id):
    if remove_student_from_course(course_id, student_id):
        flash('Étudiant retiré du cours.', 'info')
    else:
        flash('Opération impossible.', 'warning')
    return redirect(url_for('courses.list'))

@courses_bp.route('/schedule')
@login_required
def schedule():
    courses = list_courses()
    for c in courses:
        c['schedule'] = get_schedule(c['id'])
    return render_template('courses/schedule.html', courses=courses)