# Project README

## About the Project

This project is a robust and completely functional Online Judge web application built with Django, it has all the features required to utilize it right now as  a full scale app.
Currently it is deployed on AWS, you can <a href="www.bonsaicode.software">visit here!</a>
- It has a fully functional online compiler with syntax highlighting and multiple language support along with custom input & output, also accompanied by AI Review of there code if needed.
  
 - Test case matching is done to give out verdicts for submission. It provides an intuitive interface for users to manage, view, and interact with various problem sets and their associated test cases, making it ideal for online judge coding platforms.


### Built Using the Following Technologies

- **Django**: For backend logic, database management, and security.
- **Python**: The core programming language used throughout the project.
- **AWS:** For hosting the project.
- **Docker**: For containerized development, building images.
- **CodeMirror5**: For better code editing experience, having syntax highlighting and indentation.
- **CSS**: For styling and responsive design.
- **Javascript:** To handle IDE logic.
- **Static File Management**: Efficient handling of static assets like images, CSS, and JavaScript.

### Functionalities
##### Core:
- Two types of users to implement complete functionality of an online judge.
- **Login/Signup:** Complete user authentication setup.
- **Online Compiler:** Available to everyone regardless of logged or not.
- **URL Configuration**: Flexible routing and clean URL design for easy navigation.
- **Docker Support**: Easy setup and deployment using Docker for consistent development environments.

##### Problem Solver:
- **Multi-language Support:** Solve in your favourite language.
- **Heatmaps:** Users can see the their progress for by heatmaps based on their submissions.
- **A.I. Review:** Get AI to review your code, in context to the problem with just a click.
- **Sorting:** Navigate problems based on your preffered difficulty.
##### Problem Setter
-  **Problem Management**: Create, update, and manage problems with detailed descriptions and metadata.
- **Test Case Management**: Add, edit, and organize test cases for each problem, supporting automated grading or manual review.


---

## How to Build the Project

Follow these steps to build and run the project locally:

1. **Clone the Repository**

```
git clone <repository_url>
cd <project_directory>
```

2. **Set Up Python Environment**

- Ensure you have Python 3.x installed.
- Create and activate a virtual environment.
- I used CMD as my terminal, the command below is to activate the Virtual ENV works for CMD in windows. Figure out on your own if you use PS (-_-).

```
python -m venv myenv
myenv\Scripts\activate.bat # Linux/MacOS source myenv/bin/activate  
```

3. **Install Dependencies**
```
pip install -r requirements.txt
````

4. **Set Up Django Environment Variables**

- Create a `.env` file in your project root.
- Add required environment variables, you'll only need one while development which is your API key for Together AI(the one I used) the variable name is `TOGETHER_API_KEY`.
- And when you dockerize, you'll need to add a few more, see below in docker part.

5. **Migrate the Database**

```
python manage.py makemigrations
python manage.py migrate
````


6. **Run the Development Server**
- Access the application at `http://127.0.0.1:8000/`.
```
python manage.py runserver
````

7. **Optional: Use Docker**

- Ensure Docker is  installed.
- Build and run the project using Docker :

```
docker image build -t <imgname> . #when you are in root directory
docker container run -d -p 8000:8000 --name <containername> <imagename>
```
- Set the ports accordingly.
- The application will be available at the same local address.
- Also when you dockerize without the database(as you should(i think)), and don't want to create a superuser everytime, use the shell script I included, and run that in the docker file.
- For that add the following to the env file.
```
DJANGO_SUPERUSER_USERNAME=username
DJANGO_SUPERUSER_EMAIL=username@mail.com
DJANGO_SUPERUSER_PASSWORD=you password
````
- If you ever need the exact docker file hit me up, I'll help(i know i needed it).
- Also you can look up how to utilize .env while spinning the container, or again hit me up.
---

## About Me :)
- This project was my first attempt at building robust, user-friendly, and scalable web applications. Which I think I achieved pretty well (for the most part).
- I am a developer skilled in Django and Python, with a focus on backend development, database setup, and web application security.
- I had prior experience in Bash, Linux, and AWS so that helped me quite a lot while debugging.
- Also, I love to make UI beautiful, cause most people prefer  form  over functionality:)
- I also have experience using Docker for development and deployment, also I utilised AWS to host this project which was a blast, AWS really it great!
- <a href="https://www.linkedin.com/in/singh-abhay175">Come say Hi!</a>