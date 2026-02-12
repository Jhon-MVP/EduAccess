# 🎓 EduAccess LMS - Accessibility-First Platform

![Django](https://img.shields.io/badge/Django-4.2-092E20?style=for-the-badge&logo=django&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Accessibility](https://img.shields.io/badge/a11y-100%25-success?style=for-the-badge)

**EduAccess** es una plataforma de gestión del aprendizaje (LMS) desarrollada en Django, diseñada desde cero con una filosofía **"Accessibility-First"**. Su objetivo es romper las barreras tecnológicas y brindar una experiencia educativa inmersiva, inclusiva y profesional para todos los estudiantes, adaptándose a necesidades visuales, cognitivas y motoras mediante el uso de Inteligencia Artificial.

---

## ✨ Características Principales

### ♿ Accesibilidad Integral (a11y)
- **Navegación 100% por Teclado:** Integración de *Skip-Links*, anillos de enfoque semánticos (Focus Rings) y menús desplegables operables sin ratón.
- **Text-to-Speech Nativo:** Lectura en voz alta de descripciones y documentos a través de la API `SpeechSynthesis` del navegador.
- **Modo Alto Contraste y Tipografía:** Panel de preferencias del estudiante (`student_profile`) para escalar fuentes y cambiar el contraste en tiempo real.
- **Adaptación IA Automática:** Uso de *signals* de Django para procesar imágenes y PDFs en segundo plano, generando textos descriptivos (OCR inclusivo) automáticamente.

### 📚 Experiencia del Estudiante
- **Course Player Inmersivo:** Reproductor de lecciones limpio, con sidebar de navegación fija y soporte para jerarquía visual rica (Rich Content).
- **Formatos Dinámicos:** Soporte para video, descargas de material original y transcripciones en formato `.txt` generadas al vuelo.
- **Tracking de Progreso:** Lógica para guardar el último acceso del estudiante y marcar módulos completados.

### 👨‍🏫 Herramientas Docentes
- **Gestión de Módulos:** Creación estructurada de lecciones y subida de archivos multimedia.
- **Dashboard de Accesibilidad:** Métricas para que el profesor sepa si el contenido que sube cumple con los estándares para los alumnos con discapacidad.

---

## 📂 Arquitectura del Proyecto

El proyecto sigue una estructura modular para facilitar la escalabilidad:

```text
eduaccess/
│
├── apps/
│   ├── accessibility/  # Lógica de IA (OCR), procesamiento y preferencias (A11y)
│   ├── core/           # Dashboards principales (student_home, teacher_home)
│   ├── courses/        # Modelos (Course, Module, Content) y Course Player
│   └── users/          # Perfiles de usuario personalizados, roles y Auth
│
├── static/             # Assets globales (CSS compilado de Tailwind, fuentes)
├── media/              # Archivos de usuario (course_materials, perfiles)
├── templates/          # Plantillas de Django (Modulares y accesibles)
│
├── manage.py           # Entry-point del framework
└── requirements.txt    # Dependencias del proyecto