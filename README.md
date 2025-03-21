# Quiz Application (QuizzKaroo)

## Overview

The Quiz Application is a web-based platform built using the Flask framework and Python. It allows users to create, take, and manage quizzes. The application leverages AI-powered quiz generation using the Gemini API and features authentication for users.

## Features

- User authentication with secure login/logout (Flask-Login, Flask-Bcrypt)
- AI-powered quiz generation using the Gemini API
- CRUD functionality for quizzes and questions
- Responsive UI for desktop, laptops, tablets, and mobile devices
- Uses Bootstrap, FontAwesome icons, and Google Fonts for an enhanced UI
- SQLite database for data storage
- Secure form handling with Flask-WTF

## Technologies Used

- **Backend:** Flask, Python
- **Frontend:** Bootstrap, FontAwesome, Google Fonts
- **Database:** SQLite
- **AI Integration:** Gemini API

## Installation

### Prerequisites

Ensure you have Python installed on your system. You can download it from [python.org](https://www.python.org/downloads/).

### Steps to Install

1. Clone the repository:

   ```sh
   git clone https://github.com/yourusername/quiz-application.git
   cd quiz-application
   ```

2. Create and activate a virtual environment:

   ```sh
   python -m venv venv
   source venv/bin/activate   # On macOS/Linux
   venv\Scripts\activate      # On Windows
   ```

3. Install dependencies:

   ```sh
   pip install -r requirements.txt
   ```

4. Set up environment variables:

   - Create a `.env` file in the root directory and add necessary configurations.

5. Run the application:

   ```sh
   flask run
   ```

6. Open your browser and navigate to `http://127.0.0.1:5000/`

## Dependencies

This application uses the following libraries:

```
annotated-types==0.7.0
anyio==4.8.0
bcrypt==4.2.1
blinker==1.9.0
cachetools==5.5.1
certifi==2025.1.31
charset-normalizer==3.4.1
click==8.1.8
colorama==0.4.6
distro==1.9.0
dnspython==2.7.0
email_validator==2.2.0
Flask==3.1.0
Flask-Bcrypt==1.0.1
Flask-Login==0.6.3
Flask-SQLAlchemy==3.1.1
Flask-WTF==1.2.2
google-ai-generativelanguage==0.6.15
google-api-core==2.24.1
google-api-python-client==2.161.0
google-auth==2.38.0
google-auth-httplib2==0.2.0
google-genai==1.7.0
google-generativeai==0.8.4
googleapis-common-protos==1.67.0
greenlet==3.1.1
grpcio==1.70.0
grpcio-status==1.70.0
h11==0.14.0
httpcore==1.0.7
httplib2==0.22.0
httpx==0.28.1
idna==3.10
itsdangerous==2.2.0
Jinja2==3.1.5
jiter==0.8.2
MarkupSafe==3.0.2
openai==1.63.2
proto-plus==1.26.0
protobuf==5.29.3
pyasn1==0.6.1
pyasn1_modules==0.4.1
pydantic==2.10.6
pydantic_core==2.27.2
pyparsing==3.2.1
python-dotenv==1.0.1
requests==2.32.3
rsa==4.9
sniffio==1.3.1
SQLAlchemy==2.0.38
tqdm==4.67.1
typing_extensions==4.12.2
uritemplate==4.1.1
urllib3==2.3.0
websockets==15.0.1
Werkzeug==3.1.3
WTForms==3.2.1
```

## Contributing

Contributions are welcome! Feel free to fork the repository and submit pull requests.

## License

This project is licensed under the MIT License.

---

### Author

Developed by @Vishesh2305


Linkedin: https://www.linkedin.com/in/onlyvishesh/
