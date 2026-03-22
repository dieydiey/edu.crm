from app.data import load_data, save_data
from app.teachers.service import get_teacher_by_id
from app.classes.service import get_class_by_id

COURSES_FILE = 'courses.json'

def _load_courses():
    return load_data(COURSES_FILE)

def _save_courses(courses):
    save_data(COURSES_FILE, courses)

def add_course(title, teacher_id, class_id, schedule=None, is_canceled=False):
    courses = _load_courses()
    new_id = max([c['id'] for c in courses], default=0) + 1
    course = {
        'id': new_id,
        'title': title,
        'teacher_id': teacher_id,
        'class_id': class_id,
        'schedule': schedule or {'day': 'Non défini', 'time': 'Non défini', 'room': 'Non définie', 'mode': 'Présentiel'},
        'is_canceled': is_canceled
    }
    courses.append(course)
    _save_courses(courses)
    return course

def update_course(course_id, title=None, teacher_id=None, class_id=None, schedule=None, is_canceled=None):
    courses = _load_courses()
    for c in courses:
        if c['id'] == course_id:
            if title:
                c['title'] = title
            if teacher_id:
                c['teacher_id'] = teacher_id
            if class_id:
                c['class_id'] = class_id
            if schedule:
                c['schedule'] = schedule
            if is_canceled is not None:
                c['is_canceled'] = is_canceled
            _save_courses(courses)
            return c
    return None

def list_courses():
    courses = _load_courses()
    enriched = []
    for c in courses:
        teacher = get_teacher_by_id(c['teacher_id'])
        teacher_name = teacher['name'] if teacher else 'Inconnu'
        class_obj = get_class_by_id(c['class_id'])
        class_name = class_obj['name'] if class_obj else 'Non définie'
        enriched.append({
            'id': c['id'],
            'title': c['title'],
            'teacher_name': teacher_name,
            'teacher_id': c['teacher_id'],
            'class_name': class_name,
            'class_id': c['class_id'],
            'schedule': c.get('schedule', {'day': 'Non défini', 'time': 'Non défini', 'room': 'Non définie', 'mode': 'Présentiel'}),
            'is_canceled': c.get('is_canceled', False)
        })
    return enriched

def get_course_by_id(course_id):
    courses = _load_courses()
    for c in courses:
        if c['id'] == course_id:
            return c
    return None

def cancel_course(course_id):
    return update_course(course_id, is_canceled=True)

def delete_course(course_id):
    courses = _load_courses()
    courses = [c for c in courses if c['id'] != course_id]
    _save_courses(courses)

def search_courses(title):
    courses = list_courses()
    if not title:
        return courses
    title = title.lower()
    return [c for c in courses if title in c['title'].lower()]