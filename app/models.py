from django.db import models
import os
# Create your models here.
class UserModel(models.Model):
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.username
    
    class Meta:
        db_table = "UserModel"  # Specify the table name in the database


class UploadJob(models.Model):
    companyname = models.CharField(max_length=100)
    jobtitle = models.CharField(max_length=100)
    jobdescription = models.TextField()
    joblocation = models.CharField(max_length=100)
    salary = models.IntegerField()
    skills = models.TextField() 
    job_category = models.CharField(max_length=100, null=True)
    jobcreatedat = models.DateTimeField(auto_now_add=True)
    image = models.FileField(upload_to=os.path.join('static/assets', 'Jobs'))
    jobstatus = models.CharField(max_length=100, default="Active")

    def __str__(self):
        return self.jobtitle
    
    class Meta:
        db_table = "UploadJob"  # Specify the table name in the database


class ApplyJob(models.Model):
    jobid = models.ForeignKey(UploadJob, on_delete=models.CASCADE)
    user_id = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    jobappliedat = models.DateTimeField(auto_now_add=True)
    jobstatus = models.CharField(max_length=100, default="Applied")
    resume = models.FileField(upload_to=os.path.join('static/assets', 'Resume'))
    phone = models.IntegerField(null=True)
    textquestion = models.TextField(null=True)
    answer = models.TextField(null=True)

    def __str__(self):
        return self.jobid.jobtitle
    
    class Meta:
        db_table = "ApplyJob"  # Specify the table name in the database

    

