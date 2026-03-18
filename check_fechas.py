from app.models import RegistroAsunto


# este modulo se encarga de revisar las fechas de los registros para ver si hay algun problema con ellas, como fechas futuras o inconsistentes
registros = RegistroAsunto.objects.all()[:15]
print("=== Primeros 15 registros - Análisis de fechas ===\n")
for i, r in enumerate(registros, 1):
    print(f"{i:2}. {r.asunto.nombre[:35]:35} | Fecha: {r.fecha}")
