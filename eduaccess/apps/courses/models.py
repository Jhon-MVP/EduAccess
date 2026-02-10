from django.conf import settings
from django.db import models
from .services.accessibility import analyze_material_accessibility

User = settings.AUTH_USER_MODEL


class Course(models.Model):
    """
    Curso institucional (no depende de docente ni período)
    """
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    credits = models.PositiveSmallIntegerField()
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class AcademicTerm(models.Model):
    """
    Período académico (ej: 2025-1)
    """
    name = models.CharField(max_length=50, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    active = models.BooleanField(default=False)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return self.name


class CourseOffering(models.Model):
    """
    Curso impartido en un período específico
    """
    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name="offerings"
    )
    term = models.ForeignKey(
        AcademicTerm,
        on_delete=models.PROTECT,
        related_name="offerings"
    )
    teachers = models.ManyToManyField(
        User,
        related_name="teaching_offerings"
    )
    published = models.BooleanField(default=False)

    class Meta:
        unique_together = ("course", "term")  # CORRECCIÓN: singular

    def __str__(self):
        return f"{self.course.code} ({self.term})"


class Enrollment(models.Model):
    """
    Inscripción del estudiante a un curso impartido
    """
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )
    offering = models.ForeignKey(
        CourseOffering,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("student", "offering")

    def __str__(self):
        return f"{self.student} → {self.offering}"


class Module(models.Model):
    """
    Unidad o módulo de un curso impartido
    """
    offering = models.ForeignKey(
        CourseOffering,
        on_delete=models.CASCADE,
        related_name="modules"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ["order"]
        unique_together = ("offering", "order")

    def __str__(self):
        return f"{self.offering} | Módulo {self.order}: {self.title}"

    def accessibility_summary(self):
        """
        Devuelve un diccionario con el porcentaje de materiales accesibles
        """
        materials = self.materials.all()
        total = materials.count()
        if total == 0:
            return {
                "has_text": None,
                "has_alt_text": None,
                "has_captions": None,
                "overall_accessible": None,
            }

        has_text_pct = sum(m.has_text for m in materials) / total * 100
        has_alt_text_pct = sum(m.has_alt_text for m in materials) / total * 100
        has_captions_pct = sum(m.has_captions for m in materials) / total * 100

        overall_accessible = all(
            m.has_text and m.has_alt_text and m.has_captions for m in materials
        )

        return {
            "has_text": has_text_pct,
            "has_alt_text": has_alt_text_pct,
            "has_captions": has_captions_pct,
            "overall_accessible": overall_accessible,
        }


class Material(models.Model):
    MATERIAL_TYPES = (
        ("PDF", "PDF"),
        ("IMAGE", "Imagen"),
        ("VIDEO", "Video"),
    )

    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name="materials"
    )
    title = models.CharField(max_length=255)
    material_type = models.CharField(
        max_length=10,
        choices=MATERIAL_TYPES
    )
    file = models.FileField(upload_to="materials/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # Metadatos de accesibilidad
    has_text = models.BooleanField(default=False)
    has_alt_text = models.BooleanField(default=False)
    has_captions = models.BooleanField(default=False)

    class Meta:
        ordering = ["uploaded_at"]

    def __str__(self):
        return f"{self.title} ({self.material_type})"

    def analyze_accessibility(self):
        """
        Analiza el material y guarda los resultados
        """
        analysis = analyze_material_accessibility(self)

        self.has_text = analysis["has_text"]
        self.has_alt_text = analysis["has_alt_text"]
        self.has_captions = analysis["has_captions"]

        self.save(update_fields=[
            "has_text",
            "has_alt_text",
            "has_captions",
        ])

class ModuleProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)

    completed = models.BooleanField(default=False)

    # 🔥 ESTE CAMPO FALTABA
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "module")

    def __str__(self):
        return f"{self.user} - {self.module}"