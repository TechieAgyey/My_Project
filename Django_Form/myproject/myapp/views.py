from django.shortcuts import render
from .models import Person
from django.http import JsonResponse
# Create your views here.

def index(request):
    return render(request,"index.html")

def reteriveData(request):
    data=list(Person.objects.values())

    return JsonResponse(data,safe=False)

def registerPerson(request):
    
    name=request.POST.get('name')
    mobile=request.POST.get('mobile')
    age=request.POST.get('age')

    data=Person.objects.filter(name=name).first()

    if data:
        print("validation")
        return JsonResponse(False,safe=False)
        
    else:

        try:
            Person.objects.create(name=name,age=age,mobile=mobile)
        except:
            print("Exception")
            return JsonResponse(False,safe=False)
        else:
            return JsonResponse(True,safe=False)

