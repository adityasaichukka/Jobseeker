from django.shortcuts import render, redirect
from . models import *
from django.contrib import messages
# Create your views here.
def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm-password']
        if password == confirm_password:
            if UserModel.objects.filter(email=email, username=username).exists():
                messages.error(request, 'Email or username already exists')
                return redirect('register')
            else:
                user = UserModel(username=username, email=email, password=password)
                user.save()
                messages.success(request, 'User created successfully')
                return redirect('login')
        else:
            messages.error(request, 'Passwords do not match')
            return redirect('register')

    return render(request, 'register.html')

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        if email == 'admin@gmail.com' and password == 'admin':
            request.session['email'] = email
            request.session['login'] = 'admin'
            return redirect('home')

        elif UserModel.objects.filter(email=email, password=password).exists():
            request.session['email'] = email
            request.session['login'] = 'user'
            return redirect('home')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('login')
    return render(request, 'login.html')


def home(request):
    login = request.session['login']
    jobs = UploadJob.objects.all()
    return render(request, 'home.html',{'login':login, 'jobs':jobs})

def logout(request):
    return redirect('index')


def addjob(request):
    if request.method == 'POST':
        companyname = request.POST['companyname']
        job_title = request.POST['job_title']
        job_description = request.POST['job_description']
        location = request.POST['location']
        job_category = request.POST['job_category']
        job_salary = request.POST['salary']
        primaryskills = request.POST['primaryskills']
        image = request.FILES['job_file']
        job = UploadJob.objects.create(
            companyname=companyname, jobtitle=job_title, jobdescription=job_description,
         joblocation=location, job_category=job_category, salary=job_salary, skills=primaryskills,
         image=image)
        job.save()
        messages.success(request, 'Job Added Successfully')
        return redirect('addjob')

    return render(request, 'addjob.html')

def jobs(request):
    # ApplyJob.objects.get(id=29).delete()
    login = request.session['login']

    jobs = UploadJob.objects.all()
    return render(request, 'jobs.html',{'jobs':jobs, 'login':login})

def viewjob(request, id):
    login = request.session['login']

    job = UploadJob.objects.filter(id=id)
  
    return render(request, 'viewjob.html',{'job':job, 'login':login})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import UploadJob

def updatejob(request, id):
    login = request.session.get('login', None)
    updatejob = UploadJob.objects.filter(id=id)
    job = UploadJob.objects.get(id=id) # Ensure we get a valid job object or raise 404

    if request.method == 'POST':
        # Fetch updated data from the form
        company_name = request.POST.get('companyname')
        job_title = request.POST.get('job_title')
        job_description = request.POST.get('job_description')
        primary_skills = request.POST.get('primaryskills')
        job_category = request.POST.get('job_category')
        location = request.POST.get('location')
        salary = request.POST.get('salary')
        job_status = request.POST.get('job_status')

        job_file = request.FILES.get('job_file')  # Handle file upload

        # Update job object with new data
        job.companyname = company_name
        job.jobtitle = job_title
        job.jobdescription = job_description  # Stripping whitespace for consistency
        job.skills = primary_skills
        job.job_category = job_category
        job.joblocation = location
        job.salary = salary
        job.jobstatus = job_status

        if job_file:  # Update the file only if a new file is uploaded
            job.job_file = job_file

        job.save()  # Save updated job object to the database
        messages.success(request, "Job details updated successfully!")
        return redirect('updatejob', id)  # Redirect to an appropriate page (e.g., job listing)

    # For GET request, render the update form with the current job details
    return render(request, 'updatejob.html', {'job': updatejob, 'login': login, 'id': id})

def deletejob(request, id):
    job = UploadJob.objects.get(id=id)
    job.delete()
    # messages.success(request, "Job deleted successfully!")
    return redirect('jobs')


import pdfplumber
import re
from difflib import SequenceMatcher
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from .models import UploadJob, UserModel, ApplyJob
from django.core.mail import send_mail
import random
from django.conf import settings
def applyjob(request, id):
    # ApplyJob.objects.all().delete()
    login = request.session.get('login', None)
    email = request.session.get('email', None)

    if not email:
        messages.error(request, "Session expired. Please log in again.")
        return redirect('login')

    job = UploadJob.objects.get(id=id)
    user = UserModel.objects.filter(email=email)

    try:
        user1 = UserModel.objects.get(email=email)
    except ObjectDoesNotExist:
        messages.error(request, "User not found.")
        return redirect('home')

    if request.method == 'POST':
        number = request.POST.get('phone', '').strip()
        resume = request.FILES.get('resume')

        if ApplyJob.objects.filter(jobid=job, user_id = user1).exists():
            messages.error(request, "You have already applied for this job.")
            return redirect('applyjob', id=id)


        if not resume:
            messages.error(request, "Please upload a valid resume.")
            return redirect('applyjob', id=id)

        # Extract text from PDF Resume
        text1 = extract_text_from_pdf(resume)
        # print(text1)
        text2 = job.skills.strip() if job.skills else ""
     

        if not text1 or not text2:
            messages.error(request, "Resume or job skills data is missing.")
            return redirect('applyjob', id=id)

        # Calculate similarity using TF-IDF + Cosine Similarity
        similarity_percentage = calculate_similarity(text2, text1)
        print(f"Similarity Percentage: {similarity_percentage}%")

        job_status = "Rejected" if similarity_percentage < 50  else "Resume Shortlisted"

        # Store job application data
        ApplyJob.objects.create(
            jobid=job,
            user_id=user1,
            phone=number,
            resume=resume,
            jobstatus=job_status
        ).save()

        if job_status == "Resume Shortlisted":
            email_subject = 'Job Application Status - Shortlisted'
            email_message = f"""
            Hello {user1.username},

            Congratulations!

            We are pleased to inform you that your job application has been successfully received, and your resume has been shortlisted for further evaluation.

            Our team will review your profile, and you will receive an update regarding the next steps in the selection process soon.

            Please keep an eye on your email for further communication.

            Best regards,  
            Your Hiring Team
            """

            send_mail(email_subject, email_message, 'connectsjobseeker@gmail.com', [user1.email])


            messages.success(request, f"Application submitted successfully! ")
        else:
            email_subject = 'Job Application Status - Update'
            email_message = f"""
            Hello {user1.username},

            Thank you for your interest in the position and for taking the time to apply.

            After careful review of your application, we regret to inform you that we have decided to move forward with other candidates for this role. Please know that this decision was not an easy one, as we received numerous strong applications.

            We truly appreciate your effort and interest in our company, and we encourage you to apply for future opportunities that align with your skills and experience.

            Wishing you success in your job search.

            Best regards,  
            Your Hiring Team
            """

            send_mail(email_subject, email_message, 'connectsjobseeker@gmail.com', [user1.email])

            messages.error(request, f"Your resume does not meet the required skills for this job.")
        return redirect('applyjob', id=id)

        # return redirect('job_list')

    return render(request, 'applyjob.html', {'login': login, 'user': user, 'position': job.jobtitle, 'id': id})

def extract_text_from_pdf(pdf_file):
    """Extract text from a PDF file."""
    extracted_text = ""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
    
    return clean_text(extracted_text.strip())

def clean_text(text):
    """Clean and preprocess text."""
    text = text.lower()  # Convert to lowercase
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)  # Remove special characters
    return text

def calculate_similarity(text1, text2):
    """Calculate similarity using TF-IDF and Cosine Similarity."""
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([text1, text2])
    cosine_sim = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]
    
    return round(cosine_sim * 1000, 2)  # Convert to percentage


def viewapplications(request):
    login = request.session['login']
    email = request.session['email']
    data = ApplyJob.objects.filter(user_id__email=email)
    return render(request, 'viewapplications.html', {'login': login, 'data': data})

def viewjobapplications(request):
    login = request.session['login']
    data = ApplyJob.objects.all()
    return render(request, 'viewjobapplications.html', {'login': login, 'data': data})


def send(request, id):
    login = request.session['login']
    if request.method == 'POST':
        question = request.POST['question']
        data=ApplyJob.objects.get(id=id)
        data.textquestion = question
        data.jobstatus = "Test Assigned"
        data.save()
        email_subject = 'Test Assignment Notification'
        email_message = f"""
        Hello {data.user_id.username},

        We are pleased to inform you that a test has been assigned to you.

        Please check the website for further details and complete the test within the given timeframe.

        If you have any questions, feel free to reach out to us.

        Best regards,  
        Your Team
        """

        send_mail(email_subject, email_message, 'connectsjobseeker@gmail.com', [data.user_id.email])
        messages.success(request, 'Test is Assigned')

        return redirect('viewjobapplications')
        
    return render(request, 'send.html', {'login':login, 'id':id})

from django.db.models import Q
def testandresponses(request):
    login = request.session['login']
    email = request.session['email']

    data = ApplyJob.objects.filter(Q(user_id__email=email) &
                                    ~Q(jobstatus="Resume Shortlisted"))
    return render(request, 'testandresponses.html',{'data':data,'login':login})


def attempttest(request, id):
    login = request.session['login']
    email = request.session['email']
    data = ApplyJob.objects.get(id=id)
    if request.method == 'POST':
        answer = request.POST['answer']
        data.answer = answer
        data.jobstatus = "Test Submitted Successfully"
        data.save()
        email_subject = 'Test Submission Confirmation'
        email_message = f"""
        Hello {data.user_id.username},

        We have received your completed test. Thank you for submitting your answers.

        Please wait for further communication regarding your results or next steps.

        If you have any questions or concerns, feel free to reach out to us.

        Best regards,  
        Your Team
        """

        send_mail(email_subject, email_message, 'connectsjobseeker@gmail.com', [data.user_id.email])
        messages.success(request, 'Test is Submitted')
        return redirect('testandresponses')


    return render(request, 'answer.html', {'id': id, 'login':login,'question':data.textquestion})



def viewtestresponse(request, id):
    login = request.session['login']
    data = ApplyJob.objects.filter(id=id)
    return render(request, 'viewtestresponse.html',{'data':data,'login':login})


def selectcandidate(request, id):
    login = request.session['login']
    data = ApplyJob.objects.get(id=id)
    data.jobstatus = 'Candidate Selected'

    data.save()
    email_subject = 'Test Results: Congratulations, You’re Qualified!'
    email_message = f"""
    Hello {data.user_id.username},

    We’ve reviewed your submission, and we’re pleased to inform you that you have qualified. Congratulations!

    You can expect to hear from us soon regarding the next steps and details for your interview.

    If you have any questions in the meantime, feel free to reach out.

    Best regards,  
    Your Team
    """

    send_mail(email_subject, email_message, 'connectsjobseeker@gmail.com', [data.user_id.email])
    messages.success(request, 'Candidate Selected')
    return redirect('viewtestresponse', id)


def rejectcandidate(request, id):
    login = request.session['login']
    data = ApplyJob.objects.get(id=id)
    data.jobstatus = 'Candidate Rejected'
    data.save()
    email_subject = 'Test Results: Unfortunately, You Did Not Qualify'
    email_message = f"""
    Hello {data.user_id.username},

    We appreciate your effort and time in taking the test. Unfortunately, after reviewing your submission, we regret to inform you that you did not qualify this time.

    We encourage you to continue improving and apply again in the future. If you have any questions, feel free to reach out.

    Best regards,  
    Your Team
    """

    send_mail(email_subject, email_message, 'connectsjobseeker@gmail.com', [data.user_id.email])
    messages.error(request, 'Candidate Rejected')

    return redirect('viewtestresponse', id)



def reject(request, id):
    login = request.session['login']
    data = ApplyJob.objects.get(id=id)
    data.jobstatus = 'Rejected'
    data.save()
    email_subject = 'Application Update'
    email_message = f"""
    Hello {data.user_id.username},

    Thank you for your interest and for taking the time to go through the application process.

    At this time, we have decided to move forward with another candidate. We truly value the effort you put into your application and encourage you to apply again for future opportunities.

    If you have any questions, feel free to reach out to us.

    Best regards,  
    Your Team
    """

    send_mail(email_subject, email_message, 'connectsjobseeker@gmail.com', [data.user_id.email])
    messages.info(request, 'Candidate moved on from the process')

    return redirect('viewjobapplications')
