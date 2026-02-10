from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from courses.models import Enrollment, ModuleProgress, CourseOffering, AcademicTerm
from users.models import UserProfile

@login_required
def student_home(request):

    enrollments = (
        Enrollment.objects
        .filter(student=request.user, active=True)
        .select_related("offering__course", "offering__term")
        .prefetch_related("offering__modules")
    )

    courses_data = []

    for enrollment in enrollments:
        offering = enrollment.offering
        modules = offering.modules.all()
        total_modules = modules.count()

        # 🔥 PROGRESO REAL usando ModuleProgress
        completed_modules = ModuleProgress.objects.filter(
            user=request.user,
            module__offering=offering,
            completed=True
        ).count()

        progress = int((completed_modules / total_modules) * 100) if total_modules else 0

        courses_data.append({
            "course": offering.course,
            "offering": offering,
            "modules": modules,
            "completed_modules": completed_modules,
            "total_modules": total_modules,
            "progress": progress,
        })

    context = {
        "student": request.user,
        "courses_data": courses_data,
    }

    return render(request, "core/student_home.html", context)

@login_required
def teacher_home(request):
    user = request.user

    # 🔥 cursos donde este usuario es docente
    offerings = CourseOffering.objects.filter(
        teachers=user
    ).select_related("course", "term").prefetch_related("enrollments")

    courses_data = []

    for offering in offerings:
        students_count = offering.enrollments.count()

        courses_data.append({
            "offering": offering,
            "course": offering.course,
            "students_count": students_count,
        })

    return render(request, "core/teacher_home.html", {
        "courses_data": courses_data
    })