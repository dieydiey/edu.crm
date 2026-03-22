from app.data import load_data, save_data
from app.auth.service import create_user, get_user_by_email

STUDENTS_FILE = 'students.json'

def _load_students():
    return load_data(STUDENTS_FILE)

def _save_students(students):
    save_data(STUDENTS_FILE, students)

def add_student(name, email):
    students = _load_students()
    for s in students:
        if s['email'] == email:
            return None
    new_id = max([s['id'] for s in students], default=0) + 1
    student = {'id': new_id, 'name': name, 'email': email}
    students.append(student)
    _save_students(students)
    if not get_user_by_email(email):
        default_password = name.lower().replace(' ', '') + '123'
        create_user(email, default_password, name, role='student')
    return student

def list_students():
    return _load_students()

def get_student_by_id(student_id):
    students = _load_students()
    for s in students:
        if s['id'] == student_id:
            return s
    return None

def update_student(student_id, name=None, email=None):
    students = _load_students()
    for s in students:
        if s['id'] == student_id:
            if name:
                s['name'] = name
            if email:
                s['email'] = email
            _save_students(students)
            return s
    return None

def delete_student(student_id):
    students = _load_students()
    students = [s for s in students if s['id'] != student_id]
    _save_students(students)

def search_students(query):
    students = _load_students()
    query = query.lower()
    return [s for s in students if query in s['name'].lower() or query in s['email'].lower()]