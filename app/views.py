from django.shortcuts import render

from django.http import HttpResponse

def home_page(reguest):
    return HttpResponse("Home page")
