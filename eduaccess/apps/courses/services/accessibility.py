import google.generativeai as genai
from django.conf import settings
import mimetypes


def process_content_with_ia(instance):
    genai.configure(api_key=settings.GEMINI_API_KEY)

    try:
        model = genai.GenerativeModel('models/gemini-2.5-flash')

        if not instance.file_upload:
            return "Error: No se encontró el archivo físico."

        # 1. Detectar automáticamente si es PDF o Imagen
        file_name = instance.file_upload.name.lower()
        mime_type, _ = mimetypes.guess_type(file_name)

        # Respaldo por si mimetypes falla
        if not mime_type:
            if file_name.endswith('.pdf'):
                mime_type = 'application/pdf'
            else:
                mime_type = 'image/jpeg'

        # 2. Lectura del archivo
        instance.file_upload.open('rb')
        file_data = instance.file_upload.read()
        instance.file_upload.close()

        # 3. Instrucción dinámica (Sirve para ambos casos)
        prompt = (
            "Eres un motor de accesibilidad y OCR. "
            "Si es una imagen, describe visualmente todo para una persona ciega. "
            "Si es un documento (PDF), compórtate como un software de OCR: "
            "extrae TODO EL TEXTO íntegramente tal cual aparece, respetando "
            "los saltos de línea, párrafos y estructura original. No resumas, "
            "solo transcribe el documento completo para que pueda ser descargado."
        )

        # 4. Enviar a Gemini con el mime_type correcto
        response = model.generate_content([
            prompt,
            {'mime_type': mime_type, 'data': file_data}
        ])

        return response.text

    except Exception as e:
        return f"Error en procesamiento de IA: {str(e)}"


def analyze_material_accessibility(material):
    return {
        "has_text": True,
        "has_alt_text": True,
        "has_captions": False,
    }