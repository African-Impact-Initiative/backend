# Venture Build Setup Guide

## Summary

This document guides the setup for the Venture Build Backend application.

## Team

| Name | Role | Contact |
|---|---|---|
| Jessica | Product Owner | <jessica@africanimpactinitiative.com> |
| Saad | SWE | <saad.makrod@mail.utoronto.ca> |
| Man Hei | SWE | <man.ho@mail.utoronto.ca> |
| Alykhan | SWE | <alykhan.versi@mail.utoronto.ca> |

## Development Guide

Currently we have general project tracking on [Notion](https://www.notion.so/8ba829f8b0dd48e8a17ebd28df4d2d9a?v=81c9ee79dec94beda40c150972ceff65). Please make sure you have access to the link. We will track specific tasks and tickets using GitHub Projects. Navigate to the project tab in the repository to view the task plan.

On Notion, you should also add comments at least once a week. Jessica (the project manager) reviews the comments for the latest status every Friday.

Furthuremore for the sake of consistency we will have a branch naming convention as follows `[fea/hotfix/chore]/change-description`.

- `[fea/hotfix/chore]` indicates whether a full feature is being done, a chore update, or a hotfix on the develop branch for a bug
- `change-description` is a small desciption of the change based on the ticket assigned in the project

Upon completion of a feature please open a pull request and add those who you would like to review. Once approved the branch can be merged and deleted.

Some additional resources:

- **Meeting notes**: [Google Docs Link](https://docs.google.com/document/d/14ANfxa0CUgF6XR9H8Xx3c1zYaqNO5UxUAivhAaCX-ww/edit?usp=sharing)

## Background

What is Venture Build?

Venture Build is a entrepreneurship platform developed to aid African startups begin their ventures as part of the African Impact Challenge. The platform is currently in development with the goal of completing a MVP by April 2024.

The backend of this application has been developed using Django with a heavy reliance on the Django Rest Framework.

To learn more about setting up the application for local development, please continue reading below.

## Preliminary Steps

Git will need to be installed please see the official documentation at <https://github.com/git-guides/install-git>. Once git is installed navigate to the directory of your choosing and execute `git clone https://github.com/African-Impact-Initiative/backend.git`.

## Backend

The setup steps for the backend.

### Installation Steps

This guide will assume that you already have Python installed. To install Python please see <https://wiki.python.org/moin/BeginnersGuide/Download>. At the time of development the Python version being used is 3.9.12, the Django version is 4.2.3, and the Django Rest Framework version is 3.14.0.

Note that you will need a Python virtual environment. Below is a hierarchical representation of the suggested file directory structure where:

- `venture-build-backend` is a general parent folder
- `venv` is the folder containing the virtual environement
- `backend` is the actual repository

```txt
.
|-- venture-build-backend/
    |-- backend/
        |-- ...repository contents
    |-- venv/
```

To setup a Python virtual environment run the following command in the directory you would like to keep the project: `python -m venv venv`. Note that this names the virtual environment as `venv` feel free to rename it to your preference.

Activate the virtual environment with the following command `.\venv\Scripts\activate` on Windows and `source venv/bin/activate` on Mac. Now the virtual environment is active. In the root of the repository you will find a requirements.txt with the following contents:

```powershell
# Django
Django==4.2.3
# Used in development to allow port 3000 (react frontend) to communicate with server
django-cors-headers==4.2.0
# rest framework
djangorestframework==3.14.0
# used for user authentication (not just social auth)
drf-social-oauth2==2.1.3
# swagger framework
drf-yasg==1.21.7
# for files on backend (temporary)
Pillow=10.0.0
```

You can install all the packages by running `pip install -r requirements.txt`. Now you should have all the project dependencies.

Make sure to create the migrations if necessary by navigating to the backend folder and running the commands: `python manage.py makemigrations` and then `python manage.py migrate`.

**NOTE:** If at any point you run into an error along the lines of `'No module named pkg_resources'` you may need to install the `setuptools` package, so run `pip install setuptools`.

To start the API run `python manage.py runserver` in the backend folder. If there are no issues the server will start at <http://127.0.0.1:8000/>.

Now we must set up the **authentication backend**. Note that currently these steps specify the setup for user credentials (username and passwords); this will be updated when OAuth is implemented. To set up authentication perform the following steps:

1. First a superuser must be created. In the terminal (in the directory with `manage.py`) run the command `python manage.py createsuperuser` and follow the necessary steps.
2. Now make sure the server is running and navigate to <http://127.0.0.1:8000/admin> and log in.
3. You will see a section that says **DJANGO OAUTH TOOLKIT**, click on applications.
4. Once you click on applications you will have to create a new app for password-based authentication. The resource type is **Resource owner password based** and client type is **public**. Name is not important you can include it if you would like. To do this, click on add application in the top right corner. Make sure to copy down the `client ID` and `secret` before saving them since you cannot find them again.
5. Save the new app.
6. Now the corresponding values that need to be updated in the env file in the `frontend` folder are `VITE_APP_REGULAR_LOGIN_CLIENT_ID`, and `VITE_APP_REGULAR_LOGIN_CLIENT_SECRET`. To do this please create a file called `.env` and copy the contents of `.env.example` into it. Fill out the necessary information. **This step is only required for frontend developers.**

Now the frontend and backend should be able to communicate with each other. You will have to restart the app for the new changes to apply.

### Project Structure

The project structure is straight-forward, each main API endpoint has its own folder. The home folder with `settings.py` and main URLs is `venturebuild`. The contents of the folder should be familiar, as all Django Rest Framework projects consist of similar file contents. Below is a description of what each folder contains.

- **models.py**: Contains the database schema relating to the resource managed by the folder (e.g. `organizations`’ `models.py` manages the `Organization` schema)
- **views.py**: Contains the logic required to generate a response to the client, heavily relies on the Django Rest Framework. It is recommended to see the video below to completely understand this
- **serializers.py**: Data sent to and from the server must be serialized in some way, this specifies the serializers needed for the resource. Again this heavily relies on the Django Rest Framework
- **urls.py**: Specifies the routes of the API (i.e. connects a view `views.py` to a URL)
- **apps.py**: Basic app metadata
- **admin.py**: Registers resources to admin dashboard

### **Useful Resources**

- Django Docs: <https://docs.djangoproject.com/en/4.2/>
- Django Rest Framework Docs: <https://www.django-rest-framework.org/>
- Django Rest Framework Tutorial (long but good): <https://www.youtube.com/watch?v=c708Nf0cHrs>
- DRF Social Auth Docs: <https://github.com/wagnerdelima/drf-social-oauth2>
- Note that the DRF social auth docs are quite weak (imo) so this video may be better <https://www.youtube.com/watch?v=wlcCvzOLL8w>
- Django CORS Headers Docs: <https://pypi.org/project/django-cors-headers/>

## Swagger

The API for venture build also supports both a Swagger and Redoc. To access the docs ensure that you are logged in at <http://127.0.0.1:8000/admin>. To access the docs in Swagger format navigate to <http://127.0.0.1:8000/swagger/> and to access the docs in Redoc format navigate to <http://127.0.0.1:8000/redoc/>. Note that the docs are managed by the `drf-yasg` package so they may not be perfect; any questions can be directed to the backend development team.
