from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from tasks.models import Task


def IsDiff(obj1, obj2):
    str_rep1: str = str(obj1)
    str_rep2: str = str(obj2)

    return str_rep1 != str_rep2


class AuthMixin(LoginRequiredMixin):
    login_url = "/user/login"
    success_url = "/tasks"
    model = Task

    def get_success_url(self):
        return "/tasks/"


class ListViewWithSearch(ListView):
    def get_queryset(self):
        search_term = self.request.GET.get("search")
        tasks = self.queryset.filter(user=self.request.user).order_by("id")

        if search_term:
            tasks = self.queryset.filter(
                title__icontains=search_term, user=self.request.user
            ).order_by("id")

        return tasks