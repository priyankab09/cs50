from django.shortcuts import render
from django.http import HttpResponseRedirect
from . import util
from django import forms
from django.core.exceptions import ValidationError
from django.urls import reverse
from random import randint


class EntryForm(forms.Form):
    title = forms.CharField(label="Title", min_length=3, max_length=100, widget=forms.TextInput(attrs={'class': 'myfieldclass'}))
    content = forms.CharField(widget=forms.Textarea, label="Content", min_length=20)

    def clean_title(self):
        title = self.cleaned_data['title']
        if util.get_entry(title) is not None:
            raise ValidationError ("Title already exists")
        
        return title


class EditEntryForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea, label="", min_length=20)

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    }
)

def entry(request, title): 
     return render (request, "encyclopedia/content.html", {
        "content": util.get_entry_markdown(title), "title":title
        }
)

def search(request): 
     title = request.GET["q"]
     matches = []
     entries = util.list_entries()
     for item in entries:
         
         if title in item:
             matches.append(item)

         if title == item:
             return render (request, "encyclopedia/content.html", {
                "content": util.get_entry_markdown(title), "title":title
                }
             )

     return render (request, "encyclopedia/search.html", {
        "matches": matches, "searched_title": title
        }
     )

def add(request):
    if request.method == "POST":
        form = EntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            util.save_entry(title, content)
            return HttpResponseRedirect(reverse("encyclopedia:entry", args=(title,)))

        else:
            return render (request, "encyclopedia/addcontent.html", {
                "form": form
                })
        # formContent.save_entry(title, content)


    return render(request, "encyclopedia/addcontent.html", {
         "form": EntryForm()
         })
    # if request.method == "POST":

def edit(request, title):
     if request.method == "GET":
        # title = request.GET["title"]
        content = util.get_entry(title)
        return render (request, "encyclopedia/editcontent.html", {
         "form": EditEntryForm(initial={"content": content}), "title":title
        })

     if request.method == "POST":
        form = EditEntryForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data["content"]
            util.save_entry(title, content)
            return HttpResponseRedirect(reverse("encyclopedia:entry", args=(title,)))
        else:
            return render (request, "encyclopedia/editcontent.html", {
                "form": form
                })

def randomPage(request):
    entries = util.list_entries()
    NumberOfEntries = len(entries)
    RndVal = randint(0, NumberOfEntries-1)
    title = entries[RndVal]
    return render (request, "encyclopedia/content.html", {
        "content": util.get_entry_markdown(title), "title":title
        })
