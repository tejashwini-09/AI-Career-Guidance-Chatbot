import streamlit as st
import os
import json
import time
from dotenv import load_dotenv
from google import genai
from auth import initialize_db, create_user, verify_user
# Load API key from .env
st.set_page_config(
    page_title="AI Career Guidance Chatbot",
    page_icon="🎓",
    layout="wide"
)
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
# Login and Signup System

initialize_db()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:

    st.title("🔐 Student Login")

    choice = st.radio(
        "Choose an option",
        ["Login", "Signup"]
    )

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )

    if choice == "Signup":

        if st.button("Create Account"):

            if username.strip() and password:

                if create_user(username, password):
                    st.success("Account created! Please login.")
                else:
                    st.error("Username already exists.")

            else:
                st.warning("Enter username and password.")

    else:

        if st.button("Login"):

            if verify_user(username, password):

                st.session_state.logged_in = True
                st.session_state.username = username

                st.success("Login successful!")
                st.rerun()

            else:
                st.error("Invalid username or password.")

    st.stop()


# Logout Button

if st.session_state.logged_in:

    st.sidebar.write(
        f"Welcome, {st.session_state.username}!"
    )

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.pop("username", None)
        st.rerun()
# Custom Website Design
st.markdown("""
<style>
.stApp {
    background-color: #fff5f8;
    color: #333333;
}

[data-testid="stSidebar"] {
    background-color: #ffe4ec;
}

h1, h2, h3, h4 {
    color: #c44d7a !important;
}

.stButton > button {
    background-color: #e88bab;
    color: white;
    border-radius: 12px;
    border: none;
    padding: 10px 20px;
}

.stButton > button:hover {
    background-color: #d96d91;
    color: white;
}

input, textarea {
    background-color: white !important;
    color: #333333 !important;
}

div[style*="background:#1e293b"] {
    background-color: #ffe4ec !important;
    color: #333333 !important;
}

div[style*="linear-gradient"] {
    background: linear-gradient(135deg, #f7b6d2, #e8b8f0) !important;
}

</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>
[data-testid="stChatMessage"] {
    background-color: #ffffff;
    border-radius: 15px;
    padding: 15px;
    margin-bottom: 10px;
    border: 1px solid #f2d6e0;
}

[data-testid="stChatInput"] {
    border-radius: 20px;
}

</style>
""", unsafe_allow_html=True)
st.title("🎓 AI Career Guidance Chatbot")
st.markdown("""
<div style="
    background: linear-gradient(135deg, #1e3a8a, #6d28d9);
    padding: 35px;
    border-radius: 18px;
    text-align: center;
    margin-bottom: 25px;
">
    <h1 style="color: white;">
        Welcome to AI Career Assistant 🎓
    </h1>
    <h3 style="color: #e0e7ff;">
        Discover your career. Build your skills. Achieve your goals.
    </h3>
    <p style="color: white;">
        Your personal AI assistant for career guidance,
        learning and job preparation.
    </p>
</div>
""", unsafe_allow_html=True)
# Quick Access Cards

st.markdown("### ✨ Explore Your Career Tools")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style="background:#1e293b;padding:20px;
    border-radius:15px;text-align:center;">
    <h2>🎯</h2>
    <h4>Career Guidance</h4>
    <p>Find your suitable career path</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background:#1e293b;padding:20px;
    border-radius:15px;text-align:center;">
    <h2>📄</h2>
    <h4>Resume Analyzer</h4>
    <p>Improve your resume with AI</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="background:#1e293b;padding:20px;
    border-radius:15px;text-align:center;">
    <h2>💼</h2>
    <h4>Job Guidance</h4>
    <p>Prepare for jobs and internships</p>
    </div>
    """, unsafe_allow_html=True)
st.write(
    "Welcome! Get personalized career guidance "
    "based on your education, interests and skills."
)

# Connect to Gemini
if API_KEY:
    client = genai.Client(api_key=API_KEY)
else:
    client = None
    st.error("API key not found. Please check your .env file.")
# Common AI Function with Retry
def generate_ai_response(prompt):

    last_error = None

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt
            )
            return response

        except Exception as e:
            last_error = e

            if "503" in str(e) and attempt < 2:
                time.sleep(3 * (attempt + 1))
            else:
                raise

    raise last_error
# Sidebar
st.sidebar.title("Career Assistant")
st.sidebar.caption("Your personal AI career companion ")
mode = st.sidebar.selectbox(
    "Select your learning level",
    ["Beginner", "Advanced"]
)

st.sidebar.success("Selected: " + mode)
page = st.sidebar.radio(
    "Menu",
    [
        "Chat",
        "Student Profile",
        "Career Guidance",
        "Resume Analyzer",
        "AI Interview Preparation",
        "AI Project Ideas Generator",
        "Course Recommendations",
        " Student Progress Tracker",
        "Completed Courses",
        "Job & Internship Guidance"
    ]
)
# Store conversation

CHAT_FILE = "chat_history.json"

if os.path.exists(CHAT_FILE):
    with open(CHAT_FILE, "r", encoding="utf-8") as f:
        saved_chats = json.load(f)
else:
    saved_chats = []

# Convert old chat into a chat session
if saved_chats and "role" in saved_chats[0]:

    first_question = next(
        (m["content"] for m in saved_chats if m["role"] == "user"),
        "Previous Chat"
    )

    saved_chats = [{
        "id": "chat_1",
        "title": first_question[:40],
        "messages": saved_chats
    }]

if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = saved_chats

if "active_chat_id" not in st.session_state:
    st.session_state.active_chat_id = (
        saved_chats[-1]["id"] if saved_chats else None
    )

if "chat_history" not in st.session_state:
    st.session_state.chat_history = (
        saved_chats[-1]["messages"] if saved_chats else []
    )

    
if page == "Chat":
    with st.sidebar:
        st.subheader("💬 Chat History")

        for i, chat in enumerate(st.session_state.chat_sessions):
            if st.button(chat["title"], key=f"chat_{i}"):
                st.session_state.chat_history = chat["messages"]
                st.session_state.active_chat_id = chat["id"]
                st.rerun()

        if st.button("➕ New Chat"):
            st.session_state.chat_history = []
            st.session_state.active_chat_id = None
            st.rerun()




st.markdown('<div id="career-guidance"></div>', unsafe_allow_html=True)
# Student profile
if page == "Student Profile":
    st.header("👩‍🎓 Student Profile")

    with st.form("student_form"):

        name = st.text_input("Enter your name")

        education = st.selectbox(
            "Select your education",
            ["PUC", "Diploma", "B.E/B.Tech",
            "BCA", "B.Sc", "B.Com", "MBA", "Other"]
        )

        branch = st.text_input("Enter your branch")

        interests = st.multiselect(
            "Choose your interests",
            ["Data Analytics",
            "Software Development",
            "Artificial Intelligence",
            "Web Development",
            "Cybersecurity",
            "Cloud Computing"]
        )

        skills = st.text_input(
            "Enter your skills (Python, Java, SQL...)"
        )

        submit = st.form_submit_button("Get Career Guidance")

    if submit:

        if name.strip() and branch.strip() and interests:

            st.success("Profile submitted successfully!")

            st.subheader("🎯 Your Career Recommendations")

            if client:

                prompt = f"""
                You are an AI Career Guidance Assistant.

                Give personalized career guidance to this student.

                Name: {name}
                Education: {education}
                Branch: {branch}
                Interests: {interests}
                Skills: {skills}
                Learning level: {mode}

                Provide:
                1. Three suitable career options.
                2. Why each career suits this student.
                3. Skills the student should learn.
                4. A step-by-step learning roadmap.
                5. Suggested projects.
                6. Job opportunities.

                Explain in simple language.
                Make the answer clear and useful for a college student.
                """

                try:

                    response = generate_ai_response(prompt)

                    st.markdown(response.text)

                except Exception as e:

                    st.error("AI error: " + str(e))

            else:
                st.error("Gemini API is not connected.")

        else:

            st.warning(
                "Please enter your name, branch "
                "and select at least one interest."
            )

# Chatbot section
st.divider()

st.header("💬 AI Career Assistant")

st.write(
    "Ask questions about careers, skills, courses "
    "and job opportunities."
)

# Chat input
if page == "Chat":

    if st.button("🗑️ Clear Chat"):

        st.session_state.chat_history = []

        if st.session_state.active_chat_id is not None:

            current_chat = next(
                (
                    chat for chat in st.session_state.chat_sessions
                    if chat["id"] == st.session_state.active_chat_id
                ),
                None
            )

            if current_chat is not None:
                current_chat["messages"] = []

                with open(CHAT_FILE, "w", encoding="utf-8") as f:
                    json.dump(
                        st.session_state.chat_sessions,
                        f,
                        ensure_ascii=False,
                        indent=4
                    )

        st.rerun()

    if not st.session_state.chat_history:
        st.markdown("""
        <div style="text-align:center; padding:30px;">
            <h2>👋 Hello!</h2>
            <p>Welcome to your AI Career Assistant.</p>
            <p>Ask me about careers, skills, internships, projects or interviews.</p>
        </div>
        """, unsafe_allow_html=True)

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Ask anything about your career...")

    if question:

        if client:

            # Display user question
            st.session_state.chat_history.append(
                {"role": "user", "content": question}
            )
            # Create new chat session
            if st.session_state.active_chat_id is None:

                chat_id = f"chat_{len(st.session_state.chat_sessions) + 1}"

                new_chat = {
                    "id": chat_id,
                    "title": question[:40],
                    "messages": []
                }

                st.session_state.chat_sessions.append(new_chat)
                st.session_state.active_chat_id = chat_id

            # Save user message to current chat
            current_chat = next(
                (
                    chat for chat in st.session_state.chat_sessions
                    if chat["id"] == st.session_state.active_chat_id
                ),
                None
            )

            if current_chat is None:
                chat_id = f"chat_{len(st.session_state.chat_sessions) + 1}"

                current_chat = {
                    "id": chat_id,
                    "title": question[:40],
                    "messages": []
                }

                st.session_state.chat_sessions.append(current_chat)
                st.session_state.active_chat_id = chat_id

            current_chat["messages"].append(
                {"role": "user", "content": question}
            )
            with open(CHAT_FILE, "w", encoding="utf-8") as f:
                json.dump(
                  st.session_state.chat_sessions,
                    f,
                    ensure_ascii=False,
                    indent=4
                )
            

            with st.chat_message("user"):
                st.markdown(question)

            # Build conversation context
            conversation = ""

            for message in st.session_state.chat_history[-10:]:

                conversation += (
                    message["role"] + ": "
                    + message["content"] + "\n"
                )

            prompt = f"""
            You are an AI Career Guidance Chatbot for college students.

            Learning level: {mode}

            Answer questions about:
            careers, courses, skills, internships,
            projects, resumes, interviews and jobs.

            Use simple language for beginners.
            For advanced students, provide technical details.

            Conversation:
            {conversation}

            Give a helpful answer to the latest question.
            """

            with st.chat_message("assistant"):
                st.markdown("### 🎓 Career Assistant")

                with st.spinner("Gemini is thinking..."):
                    try:
                        response = None
                        last_error = None

                        response = generate_ai_response(prompt)

                        if response is None:
                            raise last_error

                        answer = response.text

                        st.markdown(answer)

                        st.session_state.chat_history.append(
                            {"role": "assistant", "content": answer}
                        )

                        current_chat["messages"].append(
                            {"role": "assistant", "content": answer}
                        )

                        with open(CHAT_FILE, "w", encoding="utf-8") as f:
                            json.dump(
                                st.session_state.chat_sessions,
                                f,
                                ensure_ascii=False,
                                indent=4
                            )

                    except Exception as e:
                        st.error("AI error: " + str(e))


        else:

            st.error("Please check your Gemini API key.")

        # Skill Gap Analyzer
if page == "Career Guidance":        
    st.divider()

    st.header("📊 AI Skill Gap Analyzer")

    st.write(
        "Find which skills you need to learn "
        "for your dream career."
    )

    career_goal = st.selectbox(
        "Choose your dream career",
        [
            "Data Analyst",
            "Data Scientist",
            "AI Engineer",
            "Software Developer",
            "Web Developer",
            "Cybersecurity Analyst",
            "Cloud Engineer"
        ],
        key="skill_gap_career"
    )

    current_skills = st.text_input(
        "Enter your current skills",
        placeholder="Example: Python, Java, SQL",
        key="skill_gap_skills"
    )

    if st.button("Analyze My Skill Gap"):

        if current_skills.strip():

            if client:

                prompt = f"""
                You are an AI career and skill gap analyzer.

                Student's dream career: {career_goal}
                Current skills: {current_skills}
                Learning level: {mode}

                Analyze this student's skill gap.

                Give the result in these sections:

                1. Skills the student already has.
                2. Missing skills required for this career.
                3. Learning priority (Beginner to Advanced).
                4. A 3-month learning roadmap.
                5. Three practical project ideas.
                6. Recommended free learning resources.

                Use simple, clear language.
                Make the guidance practical for a college student.
                """

                try:

                    with st.spinner("Analyzing your skills..."):

                        response = generate_ai_response(prompt)
                    st.subheader("🎯 Your Skill Gap Analysis")

                    st.markdown(response.text)

                except Exception as e:

                    st.error("Analysis error: " + str(e))

            else:

                st.error("Gemini API is not connected.")

        else:

            st.warning("Please enter your current skills.")
if page == "Resume Analyzer":
            # AI Resume Analyzer
    st.divider()

    st.header("📄 AI Resume Analyzer")

    st.write(
        "Upload your resume and get AI-powered feedback "
        "to improve your career opportunities."
    )

    uploaded_resume = st.file_uploader(
        "Upload your Resume (PDF)",
        type=["pdf"],
        key="resume_upload"
    )

    if st.button("Analyze My Resume"):

        if uploaded_resume is not None:

            if client:

                try:

                    from pypdf import PdfReader
                    import io

                    pdf_reader = PdfReader(
                        io.BytesIO(uploaded_resume.getvalue())
                    )

                    resume_text = ""

                    for page in pdf_reader.pages:
                        resume_text += page.extract_text() or ""

                    if not resume_text.strip():

                        st.warning(
                            "Could not extract text from this PDF. "
                            "Please upload a text-based PDF."
                        )

                    else:

                        prompt = f"""
                        You are an AI Resume Analyzer
                        for college students and job seekers.

                        Analyze the following resume.

                        Give feedback in these sections:

                        1. Resume Strengths
                        2. Missing Skills
                        3. Weaknesses and Improvements
                        4. Suitable Career Roles
                        5. Recommended Projects
                        6. Resume Improvement Tips
                        7. Interview Preparation Suggestions

                        Use simple and clear language.

                        Resume content:
                        {resume_text}
                        """

                        with st.spinner("Analyzing your resume..."):

                          response = generate_ai_response(prompt)

                        st.subheader("🎯 Resume Analysis Report")

                        st.markdown(response.text)

                except Exception as e:

                    st.error("Resume analysis error: " + str(e))

            else:

                st.error("Gemini API is not connected.")

        else:

            st.warning("Please upload your resume PDF first.")
if page == "AI Interview Preparation":
        # AI Interview Preparation

    st.divider()

    st.header("🎤 AI Interview Preparation")

    st.write("Practice interview questions with AI.")

    interview_role = st.selectbox(
        "Choose your career role",
        [
            "Data Analyst",
            "Software Developer",
            "Python Developer",
            "Web Developer",
            "AI Engineer",
            "Cybersecurity Analyst"
        ],
        key="interview_role"
    )

    interview_level = st.selectbox(
        "Choose your level",
        ["Beginner", "Intermediate", "Advanced"],
        key="interview_level"
    )

    if st.button("Generate Interview Questions"):

        if client:

            prompt = f"""
            Prepare interview questions for a student.

            Career Role: {interview_role}
            Level: {interview_level}

            Give:
            1. 10 interview questions
            2. Simple sample answers
            3. 3 HR interview questions
            4. Interview tips

            Use easy English.
            """

            try:
                with st.spinner("Preparing interview questions..."):

                   response = generate_ai_response(prompt)

                st.subheader("📝 Your Interview Practice")
                st.markdown(response.text)

            except Exception:
                st.warning(
                    "Gemini is temporarily busy. "
                    "Please wait a few minutes and try again."
                )

        else:
            st.error("Gemini API is not connected.")
if page == "AI Project Ideas Generator":
            # AI Project Ideas Generator

    st.divider()

    st.header("💡 AI Project Ideas Generator")

    st.write("Generate project ideas based on your interests.")

    project_domain = st.selectbox(
        "Choose your domain",
        [
            "Python",
            "Artificial Intelligence",
            "Machine Learning",
            "Data Analytics",
            "Web Development",
            "IoT",
            "Cybersecurity",
            "Cloud Computing"
        ],
        key="project_domain"
    )

    project_level = st.selectbox(
        "Choose project level",
        ["Beginner", "Intermediate", "Advanced"],
        key="project_level"
    )

    if st.button("Generate Project Ideas"):

        if client:

            prompt = f"""
            Suggest 5 college student projects.

            Domain: {project_domain}
            Level: {project_level}

            For each project provide:
            1. Project title
            2. Problem statement
            3. Technologies used
            4. Main features
            5. Short explanation

            Use simple English.
            """

            try:
                with st.spinner("Generating project ideas..."):

                  response = generate_ai_response(prompt)

                st.subheader("🚀 Recommended Project Ideas")
                st.markdown(response.text)

            except Exception:
                st.warning(
                    "AI is temporarily busy. Please try again later."
                )

        else:
            st.error("Gemini API is not connected.")
if page == "Course Recommendations":
            # AI Course Recommendation

    st.divider()

    st.header("📚 AI Course Recommendation")

    course_career = st.selectbox(
        "Choose your career goal",
        [
            "Data Analyst",
            "Data Scientist",
            "AI Engineer",
            "Software Developer",
            "Web Developer",
            "Cybersecurity",
            "Cloud Engineer"
        ],
        key="course_career"
    )

    if st.button("Recommend Courses"):

        if client:

            prompt = f"""
            Recommend free courses for a college student.

            Career Goal: {course_career}

            Give:
            1. 5 free courses
            2. Course platform
            3. Topics covered
            4. Skills learned
            5. Learning order
            6. A 3-month learning roadmap

            Prefer free resources such as YouTube,
            freeCodeCamp, Coursera free courses,
            NPTEL and Google learning resources.

            Use simple English.
            """

            try:
                with st.spinner("Finding suitable courses..."):

                 response = generate_ai_response(prompt)

                st.subheader("🎓 Recommended Learning Path")
                st.markdown(response.text)

            except Exception:
                st.warning(
                    "AI is temporarily busy. Please try again later."
                )

        else:
            st.error("Gemini API is not connected.")
if page == " Student Progress Tracker":
            # Student Progress Tracker

    st.divider()

    st.header("📈 Student Progress Tracker")

    st.write("Track your learning progress and completed skills.")

    skills_list = [
        "Python",
        "Java",
        "C",
        "SQL",
        "Excel",
        "Power BI",
        "HTML & CSS",
        "Machine Learning"
    ]

    completed_skills = st.multiselect(
        "Select skills you have learned",
        skills_list,
        key="completed_skills"
    )

    total_skills = len(skills_list)
    learned_count = len(completed_skills)

    progress = learned_count / total_skills

    st.write(f"Skills completed: {learned_count}/{total_skills}")

    st.progress(progress)

    st.write(f"Your learning progress: {int(progress * 100)}%")
if page == "Completed Courses":
    st.subheader("📚 Completed Courses")

    if "completed_courses" not in st.session_state:
        st.session_state.completed_courses = []

    course_name = st.text_input(
        "Enter completed course name",
        key="course_name_input"
    )

    if st.button("Add Completed Course"):

        if course_name.strip():

            st.session_state.completed_courses.append(
                course_name.strip()
            )

            st.success("Course added successfully!")

    if st.session_state.completed_courses:

        for course in st.session_state.completed_courses:
            st.write("✅", course)

    else:

        st.info("No completed courses added yet.")
if page == "Job & Internship Guidance":
        # AI Job & Internship Guidance

    st.divider()

    st.header("💼 AI Job & Internship Guidance")

    st.write(
        "Get guidance to prepare for jobs and internships."
    )

    job_role = st.selectbox(
        "Choose your career role",
        [
            "Data Analyst",
            "Software Developer",
            "Web Developer",
            "AI Engineer",
            "Python Developer",
            "Cybersecurity Analyst",
            "Cloud Engineer"
        ]
    )

    job_type = st.selectbox(
        "What are you looking for?",
        ["Internship", "Fresher Job", "Work From Home"]
    )

    job_location = st.text_input(
        "Preferred location",
        placeholder="Bengaluru, Remote, etc."
    )

    if st.button("Get Job Guidance"):

        if client:

            prompt = f"""
            You are an AI career and job guidance assistant.

            Career role: {job_role}
            Job type: {job_type}
            Preferred location: {job_location}

            Give the student:
            1. Required technical skills.
            2. Required soft skills.
            3. How to prepare a resume.
            4. Interview preparation tips.
            5. Project ideas to improve their resume.
            6. Websites to search for jobs and internships.
            7. A simple preparation plan.

            Explain in simple English.
            Give practical advice for college students.
            Do not invent actual job openings.
            """

            try:

                response = generate_ai_response(prompt)

                st.markdown(response.text)

            except Exception:

                st.warning(
                    "AI service is temporarily busy. "
                    "Please try again later."
                )

        else:

            st.error("Gemini API is not connected.")
        