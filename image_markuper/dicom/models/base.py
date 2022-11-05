from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from utils.files import media_upload_path

User = get_user_model()


class Project(models.Model):
    class PathologyType(models.IntegerChoices):
        no_pathology = 0, "Без патологий"
        covid_pathology_all = 1, "COVID-19; все доли; многочисленные; размер любой"
        covid_pathology_lung = (
            2,
            "COVID-19; Нижняя доля правого лёгкого, Нижняя доля левого лёгкого",
        )
        few = 3, "Немногочисленные; 10-20 мм"
        lung_cancer_lower_right = (
            4,
            "Рак лёгкого; Нижняя доля правого лёгкого, Единичное; 10-20 мм",
        )
        lung_cancer_middle_right = (
            5,
            "Рак лёгкого; Средняя доля правого лёгкого, Единичное; >20 мм",
        )
        lung_cancer_lower_left = (
            6,
            "Рак лёгкого; Нижняя доля левого лёгкого, Единичное; 10-20 мм",
        )
        lung_cancer_upper_right = (
            7,
            "Рак лёгкого; Верхняя доля правого лёгкого, Единичное; 5-10 мм",
        )
        lung_cancer_upper_left = (
            8,
            "Рак лёгкого; Верхняя доля левого лёгкого, Единичное; 5-10 мм",
        )
        lung_cancer_all_many_small = (
            9,
            "Метастатическое поражение лёгких; Все доли; Многочисленные; 5-10 мм",
        )
        lung_cancer_all_many_big = (
            10,
            "Метастатическое поражение лёгких; Все доли; Многочисленные; 10-20 мм",
        )
        lung_cancer_all_few_small = (
            11,
            "Метастатическое поражение лёгких; Все доли; Немногочисленные; 5-10 мм",
        )

    name = models.CharField(max_length=200)

    pathology_type = models.IntegerField(choices=PathologyType.choices, default=0)

    user = models.ForeignKey(User, related_name="projects", on_delete=models.CASCADE)
    slug = models.SlugField(max_length=10)
    stl = models.FileField(blank=True)

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s project"


class Dicom(models.Model):
    slug = models.SlugField()

    file = models.FileField(upload_to=media_upload_path)
    uploaded = models.DateTimeField(auto_now_add=True)

    project = models.ForeignKey(
        Project, related_name="files", null=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return self.file.name

    def get_absolute_url(self):
        return reverse("get_update_delete_dicom", kwargs={"slug": self.slug})


class Layer(models.Model):
    parent = models.ForeignKey(
        "self", related_name="children", blank=True, null=True, on_delete=models.CASCADE
    )
    dicom = models.ForeignKey(Dicom, related_name="layers", on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=8)

    def __str__(self):
        return f"layer on {self.dicom}"
