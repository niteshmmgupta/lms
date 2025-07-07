# Local LMS Platform

This is a lightweight **Learning Management System (LMS)** developed by **Nitesh** for organizing and browsing offline course content stored in a folder structure. It allows you to view and navigate through nested folders containing videos, watch them with progress tracking, and resume from where you left off — all from a beautifully designed interface.

## 🌟 Features

- 📂 Auto-loads course folders and subfolders in a clean hierarchical structure
- 🎬 Video playback with:
  - Resume functionality (even after reopening the app)
  - Speed control slider
- ✅ Tracks watched videos (titles turn green)
- 🌓 Dark mode (default) and light mode toggle
- 🔐 Optional login support via `config.json`

## 📁 Folder Structure

```
lms/
├── courses/              # ← Put your course folders here
├── app/
│   ├── __init__.py       # ← Main Flask backend
│   └── templates/
│       ├── index.html
│       ├── player.html
│       └── login.html
├── config.json           # ← LMS title + optional login credentials
├── progress.json         # ← Watched video tracking data (auto-generated)
├── run.py                # ← Entry point to launch the LMS
└── README.md
```

## 🛠 How to Use

1. **Install dependencies**
   Make sure you have Python 3 installed.

```bash
pip install flask
```

2. **Put your course folders** inside the `courses/` directory. You can use nested folders like:

```
courses/
└── MyCourse/
    ├── 1. Introduction/
    │   └── intro.mp4
    └── 2. Module/
        └── video.mp4
```

3. **Customize LMS title (optional)**  
   Open the `config.json` file and change the `lms_title` key:

```json
{
  "lms_title": "Nitesh's LMS",
  "credentials": {
    "username": "",
    "password": ""
  }
}
```

If you set username and password, login will be required. Leave them empty to disable login.

4. **Run the application**

```bash
python run.py
```

Then visit [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

## 🙌 Why I Built This

Many times, course content is downloaded or organized in folders, making it hard to browse or track progress like a real LMS. This tool bridges that gap - making it easy to study and resume videos with a beautiful interface, all locally.

---

### 🛠 Feel free to contribute or improve this project!