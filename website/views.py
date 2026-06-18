from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import SignUpForm, AddRecordForm
from .models import Record
from django.db.models import Q
from django.core.paginator import Paginator
import csv
from django.http import HttpResponse
from reportlab.pdfgen import canvas


def home(request):

	query = request.GET.get('q')
	sort = request.GET.get('sort', 'first_name')

	if query:
		records = Record.objects.filter(
			Q(first_name__icontains=query) |
			Q(last_name__icontains=query) |
			Q(email__icontains=query) |
			Q(phone__icontains=query)
		)
	else:
		records = Record.objects.all()

		allowed_sorts = ['first_name', 'email', 'city']
		if sort not in allowed_sorts:
			sort = 'first_name'

		records = records.order_by(sort)

	paginator = Paginator(records, 10)
	page = request.GET.get('page')
	records = paginator.get_page(page)
	total_customers = Record.objects.count()

	# Check to see if logging in
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']

		user = authenticate(request, username=username, password=password)

		if user is not None:
			login(request, user)
			messages.success(request, "You Have Been Logged In!")
			return redirect('home')
		else:
			messages.success(request, "There Was An Error Logging In, Please Try Again...")
			return redirect('home')

	return render(request, 'home.html', {
		'records': records,
		'total_customers': total_customers,
	})


def logout_user(request):
	logout(request)
	messages.success(request, "You Have Been Logged Out...")
	return redirect('home')


def register_user(request):
	if request.method == 'POST':
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			# Authenticate and login
			username = form.cleaned_data['username']
			password = form.cleaned_data['password1']
			user = authenticate(username=username, password=password)
			login(request, user)
			messages.success(request, "You Have Successfully Registered! Welcome!")
			return redirect('home')
	else:
		form = SignUpForm()
		return render(request, 'register.html', {'form':form})

	return render(request, 'register.html', {'form':form})



def customer_record(request, pk):
	if request.user.is_authenticated:
		# Look Up Records
		customer_record = Record.objects.get(id=pk)
		return render(request, 'record.html', {'customer_record':customer_record})
	else:
		messages.success(request, "You Must Be Logged In To View That Page...")
		return redirect('home')



def delete_record(request, pk):
	if request.user.is_authenticated:
		delete_it = Record.objects.get(id=pk)
		delete_it.delete()
		messages.success(request, "Record Deleted Successfully...")
		return redirect('home')
	else:
		messages.success(request, "You Must Be Logged In To Do That...")
		return redirect('home')


def add_record(request):
	form = AddRecordForm(request.POST or None)
	if request.user.is_authenticated:
		if request.method == "POST":
			if form.is_valid():
				add_record = form.save()
				messages.success(request, "Record Added...")
				return redirect('home')
		return render(request, 'add_record.html', {'form':form})
	else:
		messages.success(request, "You Must Be Logged In...")
		return redirect('home')


def update_record(request, pk):
	if request.user.is_authenticated:
		current_record = Record.objects.get(id=pk)
		form = AddRecordForm(request.POST or None, instance=current_record)
		if form.is_valid():
			form.save()
			messages.success(request, "Record Has Been Updated!")
			return redirect('home')
		return render(request, 'update_record.html', {'form':form})
	else:
		messages.success(request, "You Must Be Logged In...")
		return redirect('home')
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="customers.csv"'

    writer = csv.writer(response)

    writer.writerow([
        'First Name',
        'Last Name',
        'Email',
        'Phone',
        'City',
        'State'
    ])

    records = Record.objects.all()

    for record in records:
        writer.writerow([
            record.first_name,
            record.last_name,
            record.email,
            record.phone,
            record.city,
            record.state
        ])

    return response


def export_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="customers.pdf"'

    p = canvas.Canvas(response)

    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, 800, "Customer Report")

    y = 760

    records = Record.objects.all()

    for record in records:
        line = f"{record.first_name} {record.last_name} | {record.email} | {record.phone}"
        p.setFont("Helvetica", 10)
        p.drawString(40, y, line)

        y -= 20

        if y < 50:
            p.showPage()
            y = 800

    p.save()
    return response