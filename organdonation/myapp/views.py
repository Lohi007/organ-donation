from django.shortcuts import render, redirect, get_object_or_404
from .models import donorregister, receiverregister
import hashlib
import csv
import os
import json
from AppBC import Blockchain, process_csv_and_update_blockchain
from LoadDB import CSVToSQLite
import random
from django.core.mail import send_mail
from django.contrib import messages

# Constants for file paths
FILE_NAME = "organ_donation.csv"

def otp_process(request):
    if request.method == 'POST':
        if 'send_otp' in request.POST:
            email = request.POST['email']
            otp = str(random.randint(100000, 999999))
            request.session['email'] = email
            request.session['otp'] = otp

            send_mail(
                subject='Your OTP Code',
                message=f'Your OTP is: {otp}',
                from_email='your_email@gmail.com',
                recipient_list=[email],
                fail_silently=False,
            )
            messages.info(request, 'OTP sent to your email.')
            return render(request, 'myapp/otp_page.html', {'email': email, 'otp_sent': True})

        elif 'verify_otp' in request.POST:
            input_otp = request.POST['otp']
            session_otp = request.session.get('otp')
            email = request.session.get('email')

            if input_otp == session_otp:
                messages.success(request, 'OTP verified successfully!')
                return render(request, 'myapp/otp_page.html', {'otp_verified': True, 'email': email})
            else:
                messages.error(request, 'Invalid OTP. Please try again.')
                return render(request, 'myapp/otp_page.html', {'otp_sent': True, 'email': email})

    return render(request, 'myapp/otp_page.html')

def create_csv():
    if not os.path.exists(FILE_NAME):
        with open(FILE_NAME, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["id", "user_type", "name", "age", "blood_type", "organs", "contact_info", "password", "location",
                             "Hospital_Name", "chronic_diseases", "infectious_diseases", "cancer_history", "current_medications"])
create_csv()

def get_donor_data():
    donor_registry = []
    with open(FILE_NAME, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        for row in reader:
            if row[1] == "Donor":  # Only fetch donor records
                donor_registry.append(row)
    return donor_registry

def donor_detail(request, id):
    donor = get_object_or_404(donorregister, id=id)
    organ_needed = request.GET.get('organneed', '')
    requested_blood_type = request.GET.get('rbloodtype', '')
    return render(request, 'myapp/donor_detail.html', {'donor': donor, 'organ_needed': organ_needed, 'requested_blood_type': requested_blood_type})

def index(request):
    return render(request, 'myapp/index.html')

def login(request):
    if request.method == "POST":
        usertype = request.POST['usertype']
        username = request.POST['first']
        password = request.POST['pwd']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        if usertype == "Recipient":
            with open(FILE_NAME, mode='r') as file:
                reader = csv.reader(file)
                next(reader)
                for row in reader:
                    if row[2] == username and row[7] == hashed_password:
                        request.session['logged_in'] = True
                        request.session['user'] = row
                        request.session['user_type'] = row[1]
                        return redirect('homepage')

            return render(request, 'myapp/login.html', {"error": "Invalid Credentials"})

        elif usertype == "Blockchain":
            if username == "admin" and password == "admin":
                with open("blockchain_data.json", "r") as f:
                    blockchain_data = json.load(f)
                return render(request, 'myapp/vieworgan.html', {'data': blockchain_data})

    return render(request, 'myapp/login.html')

def requestorgan(request):
    if request.method == 'POST':
        organneed = request.POST.get('organneed')
        rbloodtype = request.POST.get('rbloodtype')
        minage = int(request.POST.get('minage'))
        maxage = int(request.POST.get('maxage'))

        donor_registry = get_donor_data()

        filtered_data = []
        for entry in donor_registry:
            donor_organ = entry[5].lower()
            donor_blood = entry[4].lower()
            donor_age = int(entry[3])

            if (organneed.lower() in donor_organ and
                    donor_blood == rbloodtype.lower() and
                    minage <= donor_age <= maxage):
                filtered_data.append({
                    'id': entry[0],
                    'role': entry[1],
                    'name': entry[2],
                    'age': entry[3],
                    'bloodgroup': entry[4],
                    'organ': entry[5],
                    'phone': entry[6],
                    'city': entry[8] if entry[8] != "None" else "-",
                    'hospital': entry[9] if entry[9] != "None" else "-"
                })

        return render(request, 'myapp/requestorgan.html', {'data1': filtered_data, 'searched_organ': organneed, 'searched_blood_type': rbloodtype})

    return render(request, 'myapp/requestorgan.html')


# ✅ Donor Registration
def register(request):
    if request.method == "POST":
        user_data = {
            "username": request.POST['uname'],
            "age": request.POST['age'],
            "bloodtype": request.POST['bloodtype'],
            "mobno": request.POST['mobno'],
            "pwd": request.POST['pwd'],
            "locn": request.POST['locn'],
            "hname": request.POST['hname'],
            "organavail": request.POST['organavail'],
            "chronicdisease": request.POST['chronicdisease'],
            "infectious": request.POST['infectious'],
            "cancerhistory": request.POST['cancerhistory'],
            "medications": request.POST['medications']
        }
        hashed_password = hashlib.sha256(user_data["pwd"].encode()).hexdigest()
        user_type = "Donor"

        with open(FILE_NAME, mode='a', newline='') as file:
            writer = csv.writer(file)
            user_id = sum(1 for _ in open(FILE_NAME))
            writer.writerow([user_id, user_type, user_data["username"], user_data["age"], user_data["bloodtype"],
                             user_data["organavail"], user_data["mobno"], hashed_password, user_data["locn"],
                             user_data["hname"], user_data["chronicdisease"], user_data["infectious"],
                             user_data["cancerhistory"], user_data["medications"]])

        blockchain = Blockchain()
        process_csv_and_update_blockchain(FILE_NAME, blockchain)
        CSVToSQLite().upload_csv(FILE_NAME)

        donorregister.objects.create(**user_data)
        return redirect('login')

    return render(request, 'myapp/register.html')

# ✅ Recipient Registration
def registerrept(request):
    if request.method == "POST":
        user_data = {
            "rname": request.POST['rname'],
            "rage": request.POST['rage'],
            "rbloodtype": request.POST['rbloodtype'],
            "rmobno": request.POST['rmobno'],
            "rpwd": request.POST['rpwd'],
            "rlocn": request.POST['rlocn'],
            "rhname": request.POST['rhname'],
            "organneed": request.POST['organneed']
        }
        hashed_password = hashlib.sha256(user_data["rpwd"].encode()).hexdigest()
        user_type = "Recipient"

        with open(FILE_NAME, mode='a', newline='') as file:
            writer = csv.writer(file)
            user_id = sum(1 for _ in open(FILE_NAME))
            writer.writerow([user_id, user_type, user_data["rname"], user_data["rage"], user_data["rbloodtype"],
                             user_data["organneed"], user_data["rmobno"], hashed_password, user_data["rlocn"],
                             user_data["rhname"], "N/A", "N/A", "N/A", "N/A"])

        blockchain = Blockchain()
        process_csv_and_update_blockchain(FILE_NAME, blockchain)
        CSVToSQLite().upload_csv(FILE_NAME)

        receiverregister.objects.create(
            rname=user_data["rname"], rage=user_data["rage"], rbloodtype=user_data["rbloodtype"],
            rmobno=user_data["rmobno"], rpwd=user_data["rpwd"], rlocn=user_data["rlocn"],
            rhname=user_data["rhname"], organneed=user_data["organneed"]
        )
        return redirect('login')

    return render(request, 'myapp/registerrept.html')

# ✅ Homepage
def homepage(request):
    return render(request, 'myapp/homepage.html')

# ✅ View Organ Blockchain Data
def vieworgan(request):
    return render(request, 'myapp/vieworgan.html')

# ✅ About Us Page
def about_us(request):
    return render(request, 'myapp/aboutus.html')




# from django.shortcuts import render
# from .models import donorregister, receiverregister
# import hashlib
# import csv
# import os
# from AppBC import Blockchain, process_csv_and_update_blockchain
# from LoadDB import CSVToSQLite
# from EDA import ExploratoryDataAnalysis
# import json
# # Create your views here.
# # Constants for file paths
# FILE_NAME = "organ_donation.csv"
#
#
# def create_csv():
#     if not os.path.exists(FILE_NAME):
#         with open(FILE_NAME, mode='w', newline='') as file:
#             writer = csv.writer(file)
#             writer.writerow(["id", "name", "age", "blood_type", "organs", "contact_info", "password", "location","Hospital_Name",
#                              "chronic_diseases", "infectious_diseases", "cancer_history", "current_medications"])
# create_csv()
#
# def index(requests):
#     return render(requests,'myapp/index.html')
#
# def login(requests):
#     if requests.method == "POST":
#         print("hi")
#         usertype= requests.POST['usertype']
#         username = requests.POST['first']
#         password = requests.POST['pwd']
#         if usertype=="Recipient":
#
#             hashed_password = hashlib.sha256(password.encode()).hexdigest()
#             print(hashed_password)
#             # Search for user in CSV
#             with open(FILE_NAME, mode='r') as file:
#                 print("ki")
#                 reader = csv.reader(file)
#                 next(reader)  # Skip header row
#                 user_found = False
#                 for row in reader:
#                     if row[2] == username and row[7] == hashed_password:  # Match name and hashed password
#                         requests.session['logged_in'] = True
#                         requests.session['user'] = row
#                         requests.session['user_type'] = row[1]
#                         # st.session_state.logged_in = True
#                         # st.session_state.user = row  # Store user data in session state
#                         # st.session_state.user_type = row[1]  # Store user type (Donor or Recipient)
#                         user_found = True
#                         break
#             try:
#                 if user_found:
#                     return render(requests, 'myapp/homepage.html')
#                 else:
#                     return render(requests, 'myapp/login.html')
#             except:
#                 pass
#         elif usertype=="Blockchain":
#             if username=="admin" and password=="admin":
#                 with open("blockchain_data.json", "r") as f:
#                     blockchain_data = json.load(f)
#                     print(blockchain_data)
#                 content={
#                     'data':blockchain_data,
#                 }
#                 return render(requests, 'myapp/vieworgan.html',content)
#     return render(requests,'myapp/login.html')
#
# import csv
# from django.shortcuts import render
#
# FILE_NAME = "organ_donation.csv"  # Ensure the correct file path
#
#
# def requestorgan(request):
#     if request.method == "POST":
#         organneed = request.POST['organneed']
#         rbloodtype = request.POST['rbloodtype']
#         minage = int(request.POST['minage'])
#         maxage = int(request.POST['maxage'])
#         matches = []
#
#         # Read CSV file
#         with open(FILE_NAME, mode='r') as file:
#             reader = csv.reader(file)
#             next(reader)  # Skip header row
#             for row in reader:
#                 if (
#                         row[1] == "Donor" and
#                         any(organ in row[5] for organ in organneed) and
#                         row[4] == rbloodtype and
#                         minage <= int(row[3]) <= maxage and
#                         row[0] != str(request.session.get('user', [])[0])  # Ensure user[0] is used properly
#                 ):
#                     matches.append(row)
#
#         # ✅ Fix user session issue
#         user_data = request.session.get('user', [])
#         if len(user_data) > 3:
#             user_value = int(user_data[3])
#         else:
#             user_value = 0  # Default value if user data is missing
#
#         print(matches)
#
#         content = {"data1": matches}
#         return render(request, 'myapp/requestorgan.html', content)
#
#     return render(request, 'myapp/requestorgan.html')
#
#
# def register(request):
#     if request.method == "POST":
#         username = request.POST['uname']
#         age = request.POST['age']
#         bloodtype = request.POST['bloodtype']
#         mobno = request.POST['mobno']
#         pwd = request.POST['pwd']
#         locn = request.POST['locn']
#         hname = request.POST['hname']
#         organavail = request.POST['organavail']
#         chronicdisease = request.POST['chronicdisease']
#         infectious = request.POST['infectious']
#         cancerhistory = request.POST['cancerhistory']
#         medications = request.POST['medications']
#
# #CSV
#         hashed_password = hashlib.sha256(pwd.encode()).hexdigest()
#         user_type="Donor"
#         # Open CSV and append user data
#         with open(FILE_NAME, mode='a', newline='') as file:
#             writer = csv.writer(file)
#             user_id = sum(1 for _ in open(FILE_NAME))  # Simple ID generation by counting rows
#             writer.writerow([user_id, user_type, username, age, bloodtype,organavail, mobno, hashed_password,
#                              locn, hname, chronicdisease, infectious, cancerhistory, medications])
#
#             blockchain = Blockchain()
#
#             # Process the CSV file and update the blockchain once
#             process_csv_and_update_blockchain(FILE_NAME, blockchain)
#             csv_to_sqlite = CSVToSQLite()
#             csv_to_sqlite.upload_csv(FILE_NAME)
#
#         newuser = donorregister(username=username, age=age, bloodtype=bloodtype, mobno=mobno, pwd=pwd,locn=locn,hname=hname,organavail=organavail,chronicdisease=chronicdisease,infectious=infectious,cancerhistory=cancerhistory,medications=medications)
#         newuser.save()
#         return render(request, 'myapp/login.html')
#     return render(request,'myapp/register.html')
#
# def registerrept(request):
#     if request.method == "POST":
#         rname = request.POST['rname']
#         rage = request.POST['rage']
#         rbloodtype = request.POST['rbloodtype']
#         rmobno = request.POST['rmobno']
#         rpwd = request.POST['rpwd']
#         rlocn = request.POST['rlocn']
#         rhname = request.POST['rhname']
#         organneed = request.POST['organneed']
#         chronicdisease = "N/A"
#         infectious = "N/A"
#         cancerhistory = "N/A"
#         medications = "N/A"
#         user_type = "Recipient"
#         # CSV
#         hashed_password = hashlib.sha256(rpwd.encode()).hexdigest()
#
#         # Open CSV and append user data
#         with open(FILE_NAME, mode='a', newline='') as file:
#             writer = csv.writer(file)
#             user_id = sum(1 for _ in open(FILE_NAME))  # Simple ID generation by counting rows
#             writer.writerow([user_id, user_type, rname, rage, rbloodtype, organneed, rmobno, hashed_password,
#                              rlocn, rhname, chronicdisease, infectious, cancerhistory, medications])
#
#             blockchain = Blockchain()
#
#             # Process the CSV file and update the blockchain once
#             process_csv_and_update_blockchain(FILE_NAME, blockchain)
#             csv_to_sqlite = CSVToSQLite()
#             csv_to_sqlite.upload_csv(FILE_NAME)
#
#         newuser = receiverregister(rname=rname, rage=rage, rbloodtype=rbloodtype, rmobno=rmobno, rpwd=rpwd, rlocn=rlocn,
#                                 rhname=rhname, organneed=organneed)
#         newuser.save()
#         return render(request,'myapp/login.html')
#     return render(request,'myapp/registerrept.html')
#
# def homepage(request):
#     return render(request,'myapp/homepage.html')
#
# def vieworgan(request):
#     return render(request,'myapp/vieworgan.html')
# def about_us(request):
#     """
#     View function for the 'About Us' page.
#     """
#     return render(request, 'myapp/aboutus.html')

