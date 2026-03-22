from flask import render_template, request, flash, redirect, url_for
from app.students import students_bp
from app.students.service import (
    add_student, list_students, delete_student, get_student_by_id,
    update_student, search_students
)
from app.auth.decorators import login_required, role_required

@students_bp.route('/')
@login_required
@role_required('admin')
def list():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    students = list_students()
    total = len(students)
    start = (page - 1) * per_page
    end = start + per_page
    paginated = students[start:end]
    return render_template('students/list.html', students=paginated, page=page, total=total, per_page=per_page)

@students_bp.route('/search')
@login_required
@role_required('admin')
def search():
    query = request.args.get('q', '')
    if query:
        results = search_students(query)
    else:
        results = []
    return render_template('students/search.html', query=query, results=results)

@students_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def create():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        if name and email:
            student = add_student(name, email)
            if student:
                flash(f'Étudiant ajouté. Un compte a été créé avec le mot de passe : {name.lower().replace(" ", "")}123', 'success')
            else:
                flash('Un étudiant avec cet email existe déjà.', 'danger')
            return redirect(url_for('students.list'))
        else:
            flash('Tous les champs sont requis.', 'danger')
    return render_template('students/create.html')

@students_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit(id):
    student = get_student_by_id(id)
    if not student:
        flash('Étudiant introuvable.', 'danger')
        return redirect(url_for('students.list'))
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        if name and email:
            update_student(id, name=name, email=email)
            # Mettre à jour le compte utilisateur associé
            from app.auth.service import get_user_by_email, update_user
            user = get_user_by_email(student['email'])
            if user:
                update_user(user['id'], name=name, email=email)
            flash('Étudiant modifié.', 'success')
            return redirect(url_for('students.list'))
        else:
            flash('Tous les champs sont requis.', 'danger')
    return render_template('students/edit.html', student=student)

@students_bp.route('/delete/<int:id>')
@login_required
@role_required('admin')
def delete(id):
    delete_student(id)
    flash('Étudiant supprimé.', 'info')
    return redirect(url_for('students.list'))