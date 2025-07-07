from flask import Flask, render_template, send_from_directory, request, redirect, url_for, session, flash, jsonify
import os
import json
import re
import shutil

app = Flask(__name__)
app.secret_key = 'supersecretkey@#69'  # Change to a strong key in production
# Load LMS title from config
CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config.json"))
with open(CONFIG_PATH) as f:
    config = json.load(f)
LMS_TITLE = config.get("lms_title", "My LMS")

# Set base and course directories
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
COURSES_DIR = os.path.join(BASE_DIR, "courses")
PROGRESS_FILE = os.path.join(BASE_DIR, "progress.json")
IMPORTED_FILE = os.path.join(BASE_DIR, "imported_courses.json")

# Load progress and imported courses with error handling
if os.path.exists(PROGRESS_FILE):
    with open(PROGRESS_FILE) as f:
        try:
            progress_data = json.load(f)
        except json.JSONDecodeError:
            progress_data = {}
else:
    progress_data = {}

if os.path.exists(IMPORTED_FILE):
    with open(IMPORTED_FILE) as f:
        try:
            imported_courses = json.load(f)
        except json.JSONDecodeError:
            imported_courses = []
else:
    imported_courses = []

# Sorting helper
def sort_key(name):
    match = re.match(r'^\[?(\d+(?:\.\d+)*)(?=[\]\s\.-])?', name)
    if match:
        try:
            return [float(x) for x in match.group(1).split('.')]
        except:
            pass
    return [float('inf')]

# Recursively build course tree
def get_course_structure(course_path):
    items = []
    for entry in sorted(os.listdir(course_path), key=sort_key):
        full_path = os.path.join(course_path, entry)
        rel_path = os.path.relpath(full_path, COURSES_DIR).replace("\\", "/")
        if os.path.isdir(full_path):
            children = get_course_structure(full_path)
            items.append({
                "type": "folder",
                "name": entry,
                "children": children
            })
        elif entry.lower().endswith((".mp4", ".mkv", ".avi", ".mov", ".m4v", ".webm", ".flv", ".wmv", ".mpeg", ".mpg")):
            items.append({
                "type": "video",
                "name": entry,
                "path": rel_path
            })
    return items

@app.route('/login', methods=['GET', 'POST'])
def login():
    credentials = config.get("credentials", {})
    valid_user = credentials.get("username")
    valid_pass = credentials.get("password")

    # If credentials are missing, disable login
    if not valid_user or not valid_pass:
        session['user'] = "public"
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == valid_user and password == valid_pass:
            session['user'] = username
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials', 'danger')

    return render_template('login.html')

# Homepage
@app.route('/')
def home():
    credentials = config.get("credentials", {})
    valid_user = credentials.get("username")
    valid_pass = credentials.get("password")

    # If login is required and user not logged in
    if (valid_user and valid_pass) and 'user' not in session:
        return redirect(url_for('login'))

    if not os.path.exists(COURSES_DIR):
        os.makedirs(COURSES_DIR)

    course_folders = [
        name for name in os.listdir(COURSES_DIR)
        if os.path.isdir(os.path.join(COURSES_DIR, name))
    ]
    return render_template("index.html", courses=course_folders, imported=imported_courses, lms_title=LMS_TITLE)

# Course view
@app.route('/course/<path:course_name>')
def course_page(course_name):
    credentials = config.get("credentials", {})
    valid_user = credentials.get("username")
    valid_pass = credentials.get("password")

    if (valid_user and valid_pass) and 'user' not in session:
        return redirect(url_for('login'))

    folder_path = os.path.join(COURSES_DIR, course_name)
    course_structure = get_course_structure(folder_path)

    def find_first_video(items):
        for item in items:
            if item['type'] == 'video':
                return item['path']
            elif item['type'] == 'folder':
                nested = find_first_video(item['children'])
                if nested:
                    return nested
        return None

    first_video = find_first_video(course_structure)
    return render_template(
        "player.html",
        course=course_structure,
        first_video_path=first_video,
        first_video_title=os.path.basename(first_video) if first_video else "",
        progress=progress_data,
        course_name=course_name,
        lms_title=LMS_TITLE
    )

# Serve video
@app.route("/video/<path:filepath>")
def serve_video(filepath):
    full_path = os.path.join(COURSES_DIR, filepath)
    return send_from_directory(os.path.dirname(full_path), os.path.basename(full_path))

# Track watched
@app.route('/mark_watched', methods=['POST'])
def mark_watched():
    data = request.get_json()
    path = data.get('path')
    course = data.get('course')

    if path:
        progress_data[path] = True
        if course:
            progress_data[f"last:{course}"] = path

    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress_data, f, indent=2)

    return jsonify({'status': 'success'})

@app.route('/last_watched/<course>')
def last_watched(course):
    path = progress_data.get(f"last:{course}")
    return jsonify({'path': path})

if __name__ == "__main__":
    app.run(debug=True)
