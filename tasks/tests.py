from django.contrib.auth.models import User
from django.core import mail
from django.test import RequestFactory, TestCase
from task_manager.celery import every_30_seconds

from tasks import views
from tasks.models import EmailScheduler, Task

from .models import Task
from .views import GenericTaskCreateView, GenericTaskView

task = {
            "title": "Task1",
            "description": "Task1 description",
            "priority": 1,
            "completed": False,
            "status": "PENDING",
        }

second_task = {
                "title": "Task2",
                "description": "Task2 description",
                "priority": 1,
                "completed": False,
                "status": "COMPLETED",
            }
class ViewsTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="admin", email="admin@gmail.com", password="thisisa31!@")

    def test_login(self):
        response = self.client.get("/user/login")
        self.assertEqual(response.status_code, 200)

    def test_signup(self):
        response = self.client.get("/user/signup")
        self.assertEqual(response.status_code, 200)

    def test_home(self):
        response = self.client.get("")
        self.assertEqual(response.status_code, 200)

    def test_is_TaskView_authenticated(self):
        request = self.factory.get("/tasks")
        request.user = self.user
        response = views.GenericTaskView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_CreateView_authenticated(self):
        request = self.factory.get("/create-task/")
        request.user = self.user
        response = views.GenericTaskCreateView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_create_task(self):
        self.client.login(username="admin", password="thisisa31!@")
        self.client.post("/create-task/",task)
        try:
            title = Task.objects.get(priority=1).title
        except:
            title = None

        self.assertEqual(title, "Task1")

    def test_check_priority(self):
        self.client.login(username="admin", password="thisisa31!@")
        self.client.post("/create-task/",task)
        self.client.post("/create-task/",second_task)
        try:
            title = Task.objects.get(priority=2).title
        except:
            title = None
        self.assertEqual(title, "Task2")

    def test_updateView(self):
        self.client.login(username="admin", password="thisisa31!@")
        createtask = Task.objects.create(
            title="Task3",
            description="Task3 description",
            priority=1,
            completed=False,
            status="PENDING",
            user=self.user,
        )
        self.client.post(f"/update-task/{createtask.id}/",
                         {
                             "title": "Task3",
                             "description": "Updated Task3 description",
                             "priority": 1,
                             "completed": True,
                             "status": "PENDING",
                         },
                         )
        self.assertEqual(Task.objects.get(id=createtask.id).description, "Updated Task3 description")

    def test_status_integrity(self):
        completed = Task.objects.filter(status="COMPLETED").count()
        cancelled = Task.objects.filter(status="CANCELLED").count()
        in_progress = Task.objects.filter(status="IN_PROGRESS").count()
        pending = Task.objects.filter(status="PENDING").count()
        all_obj = Task.objects.all().count()

        self.assertEqual(completed + cancelled + in_progress + pending, all_obj)

class ApiTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="admin", email="admin@wgmail.com", password="thisisa31!@")

    def test_acsessapi(self):
        self.client.login(username="admin", password="thisisa31!@")
        response = self.client.get(f"/api/task/")
        self.assertEqual(response.status_code, 200)