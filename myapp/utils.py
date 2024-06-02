import easyocr

# Inicializar el lector de EasyOCR
reader = easyocr.Reader(['en'])

def read_license_plate(license_plate_crop):
    detections = reader.readtext(license_plate_crop)
    for detection in detections:
        bbox, text, score = detection
        text = text.upper().replace(' ', '')
        if True:  # Aquí puedes agregar más lógica si es necesario
            return text, score
    return None, None
