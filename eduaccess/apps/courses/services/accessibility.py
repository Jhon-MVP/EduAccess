import google.generativeai as genai
from django.conf import settings


def process_content_with_ia(instance):
    # Configuración de tu llave
    genai.configure(api_key=settings.GEMINI_API_KEY)

    try:
        # ¡EL SECRETO ESTABA AQUÍ! Usamos el modelo que SÍ existe en tu lista
        model = genai.GenerativeModel('models/gemini-2.5-flash')

        if not instance.file_upload:
            return "Error: No se encontró el archivo físico."

        # Lectura de la imagen
        instance.file_upload.open('rb')
        image_data = instance.file_upload.read()
        instance.file_upload.close()

        # Generación de la descripción
        response = model.generate_content([
            "Eres un experto en accesibilidad. Describe esta imagen detalladamente "
            "para un estudiante con discapacidad visual. Si hay logos de lenguajes "
            "de programación o texto, extráelos y organízalos. Pero omite mencionar que es para un estudiante discapacitado",
            {'mime_type': 'image/jpeg', 'data': image_data}
        ])

        return response.text

    except Exception as e:
        return f"Error en procesamiento: {str(e)}"


def analyze_material_accessibility(material):
    return {
        "has_text": True,
        "has_alt_text": True,
        "has_captions": False,
    }