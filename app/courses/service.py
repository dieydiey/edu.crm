from app.data import load_data, save_data
from app.teachers.service import get_teacher_by_id
from app.students.service import get_student_by_id

COURSES_FILE = 'courses.json'

def _load_courses():
    return load_data(COURSES_FILE)

def _save_courses(courses):
    save_data(COURSES_FILE, courses)

def add_course(title, teacher_id, schedule=None):
    courses = _load_courses()
    new_id = max([c['id'] for c in courses], default=0) + 1
    course = {
        'id': new_id,
        'title': title,
        'teacher_id': teacher_id,
        'student_ids': [],
        'schedule': schedule or {'day': 'Non défini', 'time': 'Non défini', 'room': 'Non définie'}
    }
    courses.append(course)
    _save_courses(courses)
    return course

def update_course(course_id, title=None, teacher_id=None, schedule=None):
    courses = _load_courses()
    for c in courses:
        if c['id'] == course_id:
            if title:
                c['title'] = title
            if teacher_id:
                c['teacher_id'] = teacher_id
            if schedule:
                c['schedule'] = schedule
            _save_courses(courses)
            return c
    return None

def delete_course(course_id):
    courses = _load_courses()
    courses = [c for c in courses if c['id'] != course_id]
    _save_courses(courses)

def list_courses():
    courses = _load_courses()
    enriched = []
    for c in courses:
        teacher = get_teacher_by_id(c['teacher_id'])
        teacher_name = teacher['name'] if teacher else 'Inconnu'
        students_names = []
        for sid in c['student_ids']:
            s = get_student_by_id(sid)
            if s:
                students_names.append(s['name'])
        enriched.append({
            'id': c['id'],
            'title': c['title'],
            'teacher_name': teacher_name,
            'teacher_id': c['teacher_id'],
            'student_ids': c['student_ids'],
            'students_names': students_names,
            'schedule': c.get('schedule', {'day': 'Non défini', 'time': 'Non défini', 'room': 'Non définie'})
        })
    return enriched

def get_course_by_id(course_id):
    courses = _load_courses()
    for c in courses:
        if c['id'] == course_id:
            return c
    return None

def assign_student_to_course(course_id, student_id):
    courses = _load_courses()
    for c in courses:
        if c['id'] == course_id and student_id not in c['student_ids']:
            c['student_ids'].append(student_id)
            _save_courses(courses)
            return True
    return False

def remove_student_from_course(course_id, student_id):
    courses = _load_courses()
    for c in courses:
        if c['id'] == course_id and student_id in c['student_ids']:
            c['student_ids'].remove(student_id)
            _save_courses(courses)
            return True
    return False

def search_courses(title):
    courses = list_courses()
    if not title:
        return courses
    title = title.lower()
    return [c for c in courses if title in c['title'].lower()]