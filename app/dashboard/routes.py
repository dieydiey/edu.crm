from flask import render_template
from app.dashboard import dashboard_bp
from app.students.service import list_students
from app.teachers.service import list_teachers
from app.courses.service import list_courses,_load_courses
from app.auth.decorators import login_required

@dashboard_bp.route('/')
@login_required
def index():
    students = list_students()
    teachers = list_teachers()
    courses = list_courses()

    # Statistiques de base
    total_students = len(students)
    total_teachers = len(teachers)
    total_courses = len(courses)

    # Nombre d'étudiants par cours (pour graphique)
    courses_stats = []
    for c in courses:
        courses_stats.append({
            'title': c['title'],
            'students_count': len(c['student_ids'])
        })

    # Moyenne étudiants par cours
    avg_students = 0
    if total_courses > 0:
        avg_students = sum(sc['students_count'] for sc in courses_stats) / total_courses

    # Derniers étudiants ajoutés (les 5 plus récents, supposons que l'id le plus grand = dernier)
    latest_students = sorted(students, key=lambda s: s['id'], reverse=True)[:5]

    # Derniers cours créés
    latest_courses = []
    for c in courses:
        # On récupère le cours complet depuis le fichier pour avoir l'id
        # On va plutôt utiliser la liste des cours bruts (non enrichie) pour l'ordre
        pass
    # Pour avoir l'ordre, on charge les cours bruts
    from app.courses.service import _load_courses
    raw_courses = _load_courses()
    latest_raw_courses = sorted(raw_courses, key=lambda c: c['id'], reverse=True)[:5]
    # Enrichir ces derniers avec nom du prof
    latest_courses_info = []
    for rc in latest_raw_courses:
        teacher = next((t for t in teachers if t['id'] == rc['teacher_id']), None)
        teacher_name = teacher['name'] if teacher else 'Inconnu'
        latest_courses_info.append({
            'title': rc['title'],
            'teacher_name': teacher_name
        })

    return render_template(
        'dashboard/index.html',
        total_students=total_students,
        total_teachers=total_teachers,
        total_courses=total_courses,
        courses_stats=courses_stats,
        avg_students=round(avg_students, 1),
        latest_students=latest_students,
        latest_courses=latest_courses_info
    )