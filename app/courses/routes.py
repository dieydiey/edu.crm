from flask import render_template, request, flash, redirect, url_for, session
from app.courses import courses_bp
from app.courses.service import (
    add_course, list_courses, delete_course, get_course_by_id,
    update_course, search_courses, cancel_course
)
from app.teachers.service import list_teachers
from app.classes.service import list_classes
from app.auth.decorators import login_required, role_required

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
    role = session.get('user_role')
    q = request.args.get('q', '')
    if q:
        courses = search_courses(q)
    else:
        courses = list_courses()
    if role == 'admin':
        return render_template('courses/list.html', courses=courses, query=q)
    elif role == 'teacher':
        teacher = get_teacher_by_email(session['user_email'])
        if teacher:
            my_courses = [c for c in courses if c['teacher_id'] == teacher['id']]
            return render_template('courses/teacher_courses.html', courses=my_courses)
        else:
            flash('Enseignant non trouvé.', 'danger')
            return redirect(url_for('dashboard.index'))
    else:
        # student
        from app.students.service import get_student_by_email
        student = get_student_by_email(session['user_email'])
        if student and student.get('class_id'):
            my_courses = [c for c in courses if c['class_id'] == student['class_id']]
            return render_template('courses/student_courses.html', courses=my_courses)
        else:
            flash('Aucune classe affectée.', 'info')
            return render_template('courses/student_courses.html', courses=[])

@courses_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def create():
    teachers = list_teachers()
    classes = list_classes()
    if request.method == 'POST':
        title = request.form.get('title')
        teacher_id = request.form.get('teacher_id')
        class_id = request.form.get('class_id')
        day = request.form.get('day')
        time = request.form.get('time')
        room = request.form.get('room')
        mode = request.form.get('mode', 'Présentiel')
        if title and teacher_id and class_id:
            try:
                teacher_id = int(teacher_id)
                class_id = int(class_id)
                schedule = {'day': day, 'time': time, 'room': room, 'mode': mode}
                add_course(title, teacher_id, class_id, schedule)
                flash('Cours créé.', 'success')
                return redirect(url_for('courses.list'))
            except ValueError:
                flash('Données invalides.', 'danger')
        else:
            flash('Titre, enseignant et classe requis.', 'danger')
    return render_template('courses/create.html', teachers=teachers, classes=classes)

@courses_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit(id):
    course = get_course_by_id(id)
    if not course:
        flash('Cours introuvable.', 'danger')
        return redirect(url_for('courses.list'))
    teachers = list_teachers()
    classes = list_classes()
    if request.method == 'POST':
        title = request.form.get('title')
        teacher_id = request.form.get('teacher_id')
        class_id = request.form.get('class_id')
        day = request.form.get('day')
        time = request.form.get('time')
        room = request.form.get('room')
        mode = request.form.get('mode', 'Présentiel')
        if title and teacher_id and class_id:
            try:
                teacher_id = int(teacher_id)
                class_id = int(class_id)
                schedule = {'day': day, 'time': time, 'room': room, 'mode': mode}
                update_course(id, title=title, teacher_id=teacher_id, class_id=class_id, schedule=schedule)
                flash('Cours modifié.', 'success')
                return redirect(url_for('courses.list'))
            except ValueError:
                flash('Données invalides.', 'danger')
        else:
            flash('Titre, enseignant et classe requis.', 'danger')
    return render_template('courses/edit.html', course=course, teachers=teachers, classes=classes)

@courses_bp.route('/delete/<int:id>')
@login_required
@role_required('admin')
def delete(id):
    delete_course(id)
    flash('Cours supprimé.', 'info')
    return redirect(url_for('courses.list'))

@courses_bp.route('/cancel/<int:id>')
@login_required
def cancel(id):
    role = session.get('user_role')
    course = get_course_by_id(id)
    if not course:
        flash('Cours introuvable.', 'danger')
        return redirect(url_for('courses.list'))
    if role == 'admin':
        cancel_course(id)
        flash('Cours annulé.', 'warning')
    elif role == 'teacher':
        teacher = get_teacher_by_email(session['user_email'])
        if teacher and course['teacher_id'] == teacher['id']:
            cancel_course(id)
            flash('Cours annulé.', 'warning')
        else:
            flash('Vous ne pouvez pas annuler ce cours.', 'danger')
    else:
        flash('Vous n\'avez pas le droit d\'annuler un cours.', 'danger')
    return redirect(url_for('courses.list'))

@courses_bp.route('/schedule')
@login_required
def schedule():
    role = session.get('user_role')
    courses = list_courses()
    if role == 'admin':
        return render_template('courses/schedule.html', courses=courses)
    elif role == 'teacher':
        teacher = get_teacher_by_email(session['user_email'])
        if teacher:
            my_courses = [c for c in courses if c['teacher_id'] == teacher['id']]
            return render_template('courses/teacher_schedule.html', courses=my_courses)
        else:
            flash('Enseignant non trouvé.', 'danger')
            return redirect(url_for('dashboard.index'))
    else:
        from app.students.service import get_student_by_email
        student = get_student_by_email(session['user_email'])
        if student and student.get('class_id'):
            my_courses = [c for c in courses if c['class_id'] == student['class_id']]
            return render_template('courses/my_schedule.html', courses=my_courses)
        else:
            flash('Aucune classe affectée.', 'info')
            return render_template('courses/my_schedule.html', courses=[])