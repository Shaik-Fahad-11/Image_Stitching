# NeonStitch - AI Image Stitching Web Application

NeonStitch is a modern, full-stack web application that allows users to seamlessly stitch overlapping images into high-quality panoramas. Built with Flask, OpenCV, and PostgreSQL, it features a stunning Glassmorphism UI with neon aesthetics, secure user authentication, and persistent session history.

## 🚀 Features

### 🔹 Core Functionality

* **AI-Powered Stitching**: Utilizes OpenCV's advanced stitching algorithms to combine multiple images into a single panorama.
* **Smart Auto-Cropping**: Includes a custom post-processing pipeline that removes black borders and irregularities using contour detection and erosion.
* **Session Persistence**: Saves stitching history (images and session data) using PostgreSQL (via Neon) or SQLite.
* **Secure Authentication**: Complete Login and Signup system with password hashing (pbkdf2:sha256) and session management.

### 🔹 UI/UX Design

* **Glassmorphism Interface**: Frosted glass cards, glowing neon borders, and smooth gradients.
* **Interactive Dashboard**: 
  * Drag-and-drop style file selection with Image Preview Grid.
  * Sidebar navigation to revisit previous stitching sessions.
* **Dynamic Feedback**: Live loading animations, custom modal popups for errors, and delete confirmations (no browser alerts).
* **Responsive Layout**: Fully optimized for desktop and mobile devices.

## 🛠️ Tech Stack

* **Backend**: Python 3, Flask, Flask-SQLAlchemy, Flask-Login
* **Computer Vision**: OpenCV (cv2), NumPy, Imutils
* **Database**: Neon PostgreSQL (Production) / SQLite (Local Dev)
* **Frontend**: HTML5, CSS3 (Custom Glassmorphism), JavaScript (Fetch API)
* **Deployment**: Ready for Docker or Cloud Platforms (Render/Heroku/Vercel)

## 📂 Project Structure

```
NeonStitch/
│
├── app.py                 # Main Flask Application & Route Logic
├── stitcher.py            # Computer Vision Logic (Stitching & Cropping)
├── requirements.txt       # Python Dependencies
├── .env                   # Environment Variables (DB Connection)
│
├── static/
│   ├── css/
│   │   └── style.css      # Main Stylesheet (Neon/Glass theme)
│   ├── js/
│   │   └── script.js      # Frontend Logic (AJAX, Modals, Previews)
│   └── uploads/           # Stores user images & results (Git ignored)
│
└── templates/
    ├── base.html          # Base Layout (Nav, Footer, Flash messages)
    ├── landing.html       # Animated Landing Page
    ├── login.html         # Login Form
    ├── signup.html        # Registration Form
    └── dashboard.html     # Main Workspace & Modals
```

## ⚡ Installation & Setup

### Prerequisites

* Python 3.8+ installed
* pip (Python Package Manager)

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/neonstitch.git
cd neonstitch
```

### 2. Create a Virtual Environment

It is highly recommended to use a virtual environment to manage dependencies.

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory.

* **For Local Development**: You can skip this step (it will default to SQLite).
* **For Production (Neon PostgreSQL)**: Get your connection string from the Neon Console.

```env
# .env file content
DATABASE_URL=postgresql://user:password@ep-url.aws.neon.tech/dbname?sslmode=require
SECRET_KEY=your_super_secret_key
```

### 5. Run the Application

```bash
python app.py
```

The application will start at `http://127.0.0.1:5000`.

## 📖 Usage Guide

1. **Register**: Create a new account on the Signup page. You will be redirected to Login.

2. **Dashboard**: Once logged in, you will see the main dashboard.

3. **Upload**: 
   * Click "Click to Upload Images".
   * Select multiple overlapping images (e.g., a landscape panned from left to right).
   * Verify your selection in the Image Preview Grid.

4. **Stitch**: 
   * Click the Stitch Images button.
   * Wait for the loader to finish.

5. **Result**: 
   * The stitched image will appear in the main view.
   * Click Download Image to save it.
   * The session is automatically saved to the sidebar history.

6. **Manage**: Click the X icon on any sidebar item to delete that session.

## 🔧 Troubleshooting

### "Stitching Failed / Not enough keypoints"

* **Cause**: The images do not overlap enough, or the subject has too little texture (e.g., a clear blue sky or white wall).
* **Fix**: Ensure images have at least 30-50% overlap and distinct features.

### Database Connection Error

* **Cause**: Incorrect `.env` configuration.
* **Fix**: Ensure your `DATABASE_URL` starts with `postgresql://` (some providers give `postgres://` which SQLAlchemy doesn't like—change it manually if needed) and includes `sslmode=require`.

## 📜 License

This project is open-source and available under the MIT License.

## ✨ Acknowledgements

* **OpenCV** for the stitching pipeline.
* **Neon** for serverless database hosting.
* **Flask** for the backend framework.
