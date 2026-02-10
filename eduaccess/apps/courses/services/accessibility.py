from pathlib import Path


def analyze_material_accessibility(material):
    """
    Analiza problemas básicos de accesibilidad según tipo de material.
    Retorna un dict con flags.
    """

    result = {
        "has_text": False,
        "has_alt_text": False,
        "has_captions": False,
    }

    file_path = Path(material.file.path)
    material_type = material.material_type

    # PDFs
    if material_type == "PDF":
        # Por ahora asumimos que NO tiene texto
        # (luego OCR actualizará esto)
        result["has_text"] = False

    # Imágenes
    elif material_type == "IMAGE":
        # Las imágenes necesitan descripción (alt text)
        result["has_alt_text"] = False

    # Videos
    elif material_type == "VIDEO":
        # Videos accesibles requieren subtítulos
        result["has_captions"] = False

    return result
