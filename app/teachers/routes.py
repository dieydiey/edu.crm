from flask import render_template, request, flash, redirect, url_for
from app.teachers import teachers_bp
from app.teachers.service import (
    add_teacher, list_teachers, delete_teacher, get_teacher_by_id,
    update_teacher, search_teachers, filter_by_speciality
)
from app.auth.decorators import login_required

@teachers_bp.route('/')
@login_required
def list():
    speciality = request.args.get('speciality', '')
    if speciality:
        teachers = filter_by_speciality(speciality)
    else:
        teachers = list_teachers()
    # Récupérer toutes les spécialités pour le filtre
    all_specialities = sorted(set(t['speciality'] for t in list_teachers()))
    return render_template('teachers/list.html', teachers=teachers, speciality=speciality, all_specialities=all_specialities)

@teachers_bp.route('/search')
@login_required
def search():
    query = request.args.get('q', '')
    if query:
        results = search_teachers(query)
    else:
        results = []
    return render_template('teachers/search.html', query=query, results=results)

@teachers_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        speciality = request.form.get('speciality')
        if name and email and speciality:
            add_teacher(name, email, speciality)
            flash('Enseignant ajouté.', 'success')
            return redirect(url_for('teachers.list'))
        else:
            flash('Tous les champs sont requis.', 'danger')
    return render_template('teachers/create.html')

@teachers_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    teacher = get_teacher_by_id(id)
    if not teacher:
        flash('Enseignant introuvable.', 'danger')
        return redirect(url_for('teachers.list'))
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        speciality = request.form.get('speciality')
        if name and email and speciality:
            update_teacher(id, name=name, email=email, speciality=speciality)
            flash('Enseignant modifié.', 'success')
            return redirect(url_for('teachers.list'))
        else:
            flash('Tous les champs sont requis.', 'danger')
    return render_template('teachers/edit.html', teacher=teacher)

@teachers_bp.route('/delete/<int:id>')
@login_required
def delete(id):
    delete_teacher(id)
    flash('Enseignant supprimé.', 'info')
    return redirect(url_for('teachers.list'))