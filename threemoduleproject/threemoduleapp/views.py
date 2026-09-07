from django.shortcuts import render, redirect
from .models import CustomUser, Teacher, Student
from django.contrib import messages
from django.contrib.auth.models import auth
from django.contrib.auth import login
from django.db.models import Q
import random
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash


# Create your views here.
def homepage(request):
    return render(request, 'homepage.html')

def loginpage(request):
    return render(request, 'loginpage.html')

def tsignup(request):
    return render(request, 'teachersignup.html')

def stusignup(request):
    return render(request, 'studentsignup.html')

def addteacher(request):
    if request.method == "POST":
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        uname = request.POST.get('uname')
        age = request.POST.get('age')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        utype = request.POST.get('utype')
        imag = request.FILES.get('img')
        sel = request.POST.get('sel')

        if CustomUser.objects.filter(username=uname).exists():
            messages.success(request, "UserName already Exists")
            return redirect('tsignup')
        
        if CustomUser.objects.filter(email=email).exists():
            messages.success(request, "Email already Exists")
            return redirect('tsignup')
        
        user = CustomUser.objects.create_user(first_name=fname, last_name=lname, username=uname, email=email, user_type=utype)
        user.save()

        teacher = Teacher(course=sel, user=user, Age=age, contact=contact, image=imag)
        teacher.save()
        messages.success(request, "Register Sucessfully. Please wait for admin approval!")
        return redirect('tsignup')
    return render(request, 'teachersignup.html')

def addstudent(request):
    if request.method == "POST":
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        uname = request.POST.get('uname')
        age = request.POST.get('age')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        utype = request.POST.get('utype')
        imag = request.FILES.get('img')
        sel = request.POST.get('sel')

        if CustomUser.objects.filter(username=uname).exists():
            messages.success(request, "UserName already Exists")
            return redirect('stusignup')
        
        if CustomUser.objects.filter(email=email).exists():
            messages.success(request, "Email already Exists")
            return redirect('stusignup')
        
        user = CustomUser.objects.create_user(first_name=fname, last_name=lname, username=uname, email=email, user_type=utype)
        user.save()

        student = Student(course=sel, user=user, Age=age, contact=contact, image=imag)
        student.save()
        messages.success(request, "Register Sucessfully. Please wait for admin approval!")
        return redirect('stusignup')
    return render(request, 'studentsignup.html')

def loginauth(request):
    username = request.POST.get('uname')
    password = request.POST.get('pwd')
    user = auth.authenticate(username=username, password=password)
    if user is not None:
        if user.user_type == "1":
            login(request, user)
            return redirect('adminhome')
        elif user.user_type == "2":
            auth.login(request, user)
            return redirect('tadmin')
        elif user.user_type == "3":
            auth.login(request, user)
            return redirect('sadmin')

def adminhome(request):
    disapprovecount = CustomUser.objects.filter(status=0).count()
    count = disapprovecount - 1
    total_teachers = Teacher.objects.count()
    total_students = Student.objects.count()
    return render(request, 'admin.html', {'count': count, 'total_teachers': total_teachers, 'total_students': total_students})

def tadmin(request):
    return render(request, 'tadmin.html')

def sadmin(request):
    return render(request, 'sadmin.html')

def approvedisapprove(request):
    user = CustomUser.objects.filter(~Q(user_type="1"))
    teacher = Teacher.objects.filter(user__in=user)
    student = Student.objects.filter(user__in=user)
    disapprovecount = CustomUser.objects.filter(status=0).count()
    count = disapprovecount - 1
    return render(request, 'approvedisapprove.html', {'user_data': user, 'teachers': teacher, 'students': student, 'count': count})

def approve(request, id):
    usr = CustomUser.objects.get(id=id)
    usr.status = 1
    usr.save()

    if usr.user_type == "2":
        teach = Teacher.objects.get(user=id)
        password = str(random.randint(100000, 999999))
        usr.set_password(password)
        usr.save()

        send_mail(
            'Admin Approved',
            f'UserName:{teach.user.username}\nPassword:{password}\nEmail:{teach.user.email}',
            settings.EMAIL_HOST_USER,
            [usr.email]
        )
        messages.info(request, 'Teacher Approved')    
    elif usr.user_type == "3":
        stu = Student.objects.get(user=id)
        password = str(random.randint(100000, 999999))
        usr.set_password(password)
        usr.save()

        send_mail(
            'Admin Approved',
            f'UserName:{stu.user.username}\nPassword:{password}\nEmail:{stu.user.email}',
            settings.EMAIL_HOST_USER,
            [usr.email]
        )
        messages.info(request, 'Student Approved')
    
    return redirect('approvedisapprove')

def disapprove(request, id):
    usr = CustomUser.objects.get(id=id)

    # Delete the user data based on their user type
    if usr.user_type == "2":
        Teacher.objects.filter(user=id).delete()  # Delete teacher record
    elif usr.user_type == "3":
        Student.objects.filter(user=id).delete()  # Delete student record
    
    usr.delete()  # Delete the user

    # Send disapproval email to the user
    send_mail(
        'Admin Disapproved Your Account',
        f'Hello {usr.first_name},\n\nYour account has been disapproved by the admin.',
        settings.EMAIL_HOST_USER,  # From email
        [usr.email],  # Recipient email
        fail_silently=False,
    )

    messages.info(request, "User disapproved and email sent.")
    return redirect('approvedisapprove')

@login_required
def reset(request):
    if request.method == "POST":
        # Retrieve form data
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        user = request.user

        # Check if the current password is correct
        if not user.check_password(current_password):
            messages.error(request, "Your current password is incorrect.")
            return redirect('reset')

        # Check if the new passwords match
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('reset')

        # Validate the new password for strength
        if (len(new_password) < 6 or
            not any(char.isupper() for char in new_password) or
            not any(char.isdigit() for char in new_password) or
            not any(char in '!@#$%^&*()_+-[]{}|;:,.<>?/' for char in new_password)):
            messages.error(
                request,
                "Password must be at least 6 characters long, contain an uppercase letter, a number, and a special character."
            )
            return redirect('reset')

        # Set the new password
        user.set_password(new_password)
        user.save()

        # Update session to keep the user logged in
        update_session_auth_hash(request, user)

        # Display success message
        messages.success(request, "Your password has been successfully updated.")
        return redirect('reset')  # Optionally, redirect to a dashboard or profile page

    # Render the reset password page for GET requests
    return render(request, 'reset_password.html')

def logout(request):
    auth.logout(request)
    return redirect('loginpage')
