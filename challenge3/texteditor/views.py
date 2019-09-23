from django.shortcuts import render, redirect, reverse
from .forms import PinForm
from pymongo import MongoClient, ASCENDING, DESCENDING
from rest_framework import status, views
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import serializers
from rest_framework.decorators import api_view
from bson.objectid import ObjectId
import datetime
from pprint import pprint

# Create your views here.
client = MongoClient('localhost', 27017)
db = client.challenge3
documents = db.documents
cursors = db.cursors



def index(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = PinForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            doc = documents.find_one({'pin': form.cleaned_data['pin']})
            #print('pin : ' + str(form.cleaned_data['pin']))
            docID = doc['_id']
            #print(chat_room_collection.find_one({'pin': str(form.cleaned_data['pin'])})['_id'])
            #chatID = chat['_id']
            # redirect to a new URL:
            return redirect(reverse('texteditor:room', kwargs={'id':docID}))
            #return render(request, 'chat/room.html', {'pin': form.cleaned_data['pin']})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = PinForm()

    return render(request, 'texteditor/index.html', {'form': form})


def room(request, id):
    #print(pin)
    document = documents.find_one({'_id': ObjectId(id)})['_id']
    context = {
        #'text':document.text,
        #'messages':messages,
        'id': document,
    }


    return render(request, 'texteditor/doc.html', context)


class Documents(APIView):

    def get(self, request, format=None):
        docNeeded = documents.find_one({'_id': ObjectId(request.GET.get("room"))})
        docNeeded.pop('_id')
        oneMinuteAgo = datetime.datetime.now() - datetime.timedelta(minutes=1)
        # ,"lastUpdate":{"$gt":oneMinuteAgo}
        cursorsNeeded = list(cursors.find({'document': ObjectId(request.GET.get("room")), "lastUpdate":{"$gt":oneMinuteAgo}}, {'_id':0}).sort([("position", ASCENDING)]))
        for cursorNeeded in cursorsNeeded:

            cursorNeeded.pop('document')
        return Response({'docText':docNeeded, 'cursors': cursorsNeeded}, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        myQuery = {'_id': ObjectId(request.POST.get("room"))}
        newValue = { "$set": { "text": request.POST.get("message") } }
        documents.update_one(myQuery, newValue)
        #x = docNeeded.update_one({"text": request.POST.get("message")})
        return Response({'status':"success","message": request.POST.get("message")}, status=status.HTTP_200_OK)

class Cursors(APIView):

    # def get(self, request, format=None):
    #     oneMinuteAgo = datetime.datetime.now() - datetime.timedelta(minutes=1)
    #     # ,"lastUpdate":{"$gt":oneMinuteAgo}
    #     cursorsNeeded = list(cursors.find({'document': ObjectId(request.GET.get("document"))}, {'_id':0}))
    #     for cursorNeeded in cursorsNeeded:
    #
    #         cursorNeeded.pop('document')
    #     return JsonResponse({'thingINeed':cursorsNeeded}, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        query = {
            "document":ObjectId(request.POST['document']),
            "name": request.POST['name'],
            "color": request.POST['color']
        }
        updateVal = {
            "$set":{
                "document":ObjectId(request.POST['document']),
                "name": request.POST['name'],
                "color": request.POST['color'],
                "position": int(request.POST['position']),
                "lastUpdate" : datetime.datetime.now()
            }
        }
        cursors.update(query,updateVal, upsert=True)
        return JsonResponse({'status':"success","message": request.POST.get("position")} , status=status.HTTP_200_OK)
