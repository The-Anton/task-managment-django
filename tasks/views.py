from multiprocessing import AuthenticationError
from re import template
from urllib import request
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db.models import F
from django.forms import ModelForm, ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from bootstrap_datepicker_plus.widgets import DateTimePickerInput

from tasks.models import EmailScheduler, Task


def sessions_storage_view(request):
    total_views = request.session.get("total_views",0)
    request.session['total_views'] = total_views + 1
    return HttpResponse(f"Total Views is {total_views} an the user is {request.user}")

def homepage_view(request):
    return render(request, 'home.html')

def priority_cascade(form, user):
    conflicting_priority = form.cleaned_data["priority"]
    updated_conflicting_task = []

    print("executing priority cascading")
    while True:
        try:
            task = Task.objects.get(user=user, completed=False, deleted=False, priority=conflicting_priority)
            task.priority += 1
            updated_conflicting_task.append(task)
            conflicting_priority += 1
        except:
            break

    Task.objects.bulk_update(updated_conflicting_task, ["priority"])

class UserCreationStyledForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs["class"] = "p-3 my-2 w-full rounded-md bg-slate-100"
        self.fields["password1"].widget.attrs["class"] = "p-3 my-2 w-full rounded-md bg-slate-100"
        self.fields["password2"].widget.attrs["class"] = "p-3 my-2 w-full rounded-md bg-slate-100"
        
class UserLoginStyledForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs["class"] = "p-3 my-2 w-full rounded-md bg-slate-100"
        self.fields["password"].widget.attrs["class"] = "p-3 my-2 w-full rounded-md bg-slate-100"

class TaskCreateFrom(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].widget.attrs["class"] = "p-3 my-2 w-full rounded-md bg-slate-100"
        self.fields["description"].widget.attrs["class"] = "p-3 my-2 w-full rounded-md bg-slate-100"
        self.fields["priority"].widget.attrs["class"] = "p-3 my-2 w-full rounded-md bg-slate-100"

    def clean_title(self):
        title = self.cleaned_data["title"]
        if(len(title) < 10):
            raise ValidationError("Data too small")
        return title.upper()

    class Meta:
        model = Task
        fields = ["title", "description", "priority", "completed"]

class EmailReportForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["mail_time"].widget.attrs["class"] = "p-3 my-2 w-full rounded-md bg-slate-100"
    class Meta:
        model = EmailScheduler
        fields = ('mail_time',)


class UserLoginView(LoginView):
    form_class = UserLoginStyledForm
    template_name = "user_login.html"
class UserCreateView(CreateView):
    form_class = UserCreationStyledForm
    template_name = "user_create.html"
    success_url = "/user/login"

class AuthorisedTaskManager(LoginRequiredMixin):
    def get_queryset(self):
        return Task.objects.filter(deleted=False, user=self.request.user)
class GenericTaskCreateView(AuthorisedTaskManager, CreateView):
    form_class = TaskCreateFrom
    template_name = "task_create.html"
    success_url = "/tasks"

    def form_valid(self, form):
        priority_cascade(form, self.request.user)
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

# CRUD operation views
class GenericTaskDetailView(AuthorisedTaskManager, DetailView):
    model = Task
    template_name = "task_detail.html"
class GenericTaskDeleteView(AuthorisedTaskManager, DeleteView):
    model = Task
    template_name = "task_delete.html"
    success_url = "/tasks"
class GenericTaskUpdateView(AuthorisedTaskManager, UpdateView):
    model = Task
    form_class = TaskCreateFrom
    template_name = "task_update.html"
    success_url = "/tasks"

    def form_valid(self, form):
        if "priority" in form.changed_data:
            priority_cascade(form, self.request.user)
        self.object = form.save(commit=False)
        self.object.save()
        return HttpResponseRedirect("/tasks")

class GenericTaskMarkCompletedView(AuthorisedTaskManager, View):

    def get(self, request, pk):
        Task.objects.filter(id=pk).update(completed=True)
        return HttpResponseRedirect("/tasks")

# List tasks
class GenericTaskView(AuthorisedTaskManager, ListView):
    queryset = Task.objects.filter(deleted=False, completed=False)
    template_name = "tasks.html"
    context_object_name = "tasks"
    paginate_by = 5

    def get_queryset(self):
        search_term = self.request.GET.get("search")
        tasks = Task.objects.filter(deleted=False,  completed=False, user=self.request.user).order_by('priority')

        if search_term:
            tasks = tasks.filter(title__icontains=search_term)
        return tasks

class GenericTaskCompleteView(AuthorisedTaskManager, ListView):
    queryset = Task.objects.filter( completed=True, deleted=False)
    template_name = "completed.html"
    context_object_name = "completed_tasks"
    paginate_by = 5

    def get_queryset(self):
        return Task.objects.filter(completed=True, deleted=False, user=self.request.user).order_by("priority")

class GenericAllTaskView(AuthorisedTaskManager, ListView):
    queryset = Task.objects.filter(deleted=False)
    template_name = "all.html"
    context_object_name = "tasks"
    paginate_by = 5
    

class GenericEmailReportView(AuthorisedTaskManager, CreateView):
    form_class = EmailReportForm
    template_name = "mail_config.html"
    success_url = "/tasks"

    def get_queryset(self):
        return EmailScheduler.objects.filter(user=self.request.user)
    
    def perform_create(self):
        pass
class CreateTaskView(View):

    def get(self, request):
        return render(request, "task_create.html")

    def post(self, request):
        task_value = request.POST.get("task")
        Task(title=task_value).save()
        return HttpResponseRedirect("/tasks")
class TaskView(View):

    def get(self, request):
        tasks = Task.objects.filter(deleted=False)
        search_term = request.GET.get("search")

        if search_term:
            tasks = tasks.filter(title__icontains=search_term)
        return render(request, "tasks.html", {"tasks": tasks})

    def post(self, request):
        pass
