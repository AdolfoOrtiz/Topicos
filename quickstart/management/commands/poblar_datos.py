import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from quickstart.models import Carrera, Materia, Alumno, Inscripcion, Publicacion


class Command(BaseCommand):
    help = 'Puebla la base de datos con carreras, materias, alumnos e inscripciones (excluyendo publicaciones).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limpiar',
            action='store_true',
            help='Elimina los registros existentes de carreras, materias, alumnos e inscripciones antes de poblar.',
        )

    def handle(self, *args, **options):
        limpiar = options['limpiar']

        with transaction.atomic():
            if limpiar:
                self.stdout.write(self.style.WARNING('Eliminando registros previos (excepto publicaciones)...'))
                Inscripcion.objects.all().delete()
                Alumno.objects.all().delete()
                Materia.objects.all().delete()
                Carrera.objects.all().delete()
                self.stdout.write(self.style.SUCCESS('Registros eliminados correctamente.\n'))

            self.stdout.write('Iniciando carga de datos de prueba...')

            # 1. Crear Carreras
            datos_carreras = [
                {
                    'nombre': 'Ingeniería en Sistemas Computacionales',
                    'clave': 'ISC',
                    'descripcion': 'Formación integral en desarrollo de software, redes, bases de datos y arquitectura de cómputo.'
                },
                {
                    'nombre': 'Ingeniería Industrial',
                    'clave': 'IND',
                    'descripcion': 'Optimización de procesos productivos, logística, calidad y gestión de operaciones.'
                },
                {
                    'nombre': 'Ingeniería Mecatrónica',
                    'clave': 'MCT',
                    'descripcion': 'Integración de mecánica, electrónica, robótica y sistemas computarizados de control.'
                },
                {
                    'nombre': 'Licenciatura en Administración',
                    'clave': 'LAD',
                    'descripcion': 'Gestión estratégica empresarial, finanzas, mercadotecnia y recursos humanos.'
                },
            ]

            carreras_creadas = {}
            for c_data in datos_carreras:
                carrera, created = Carrera.objects.get_or_create(
                    clave=c_data['clave'],
                    defaults={
                        'nombre': c_data['nombre'],
                        'descripcion': c_data['descripcion']
                    }
                )
                carreras_creadas[c_data['clave']] = carrera
                status = 'Creada' if created else 'Ya existía'
                self.stdout.write(f'  [Carrera] {status}: {carrera.nombre} ({carrera.clave})')

            # 2. Crear Materias
            datos_materias = [
                # ISC
                {'nombre': 'Bases de Datos', 'clave': 'ISC-BD', 'creditos': 5, 'carrera': 'ISC'},
                {'nombre': 'Programación Web', 'clave': 'ISC-PW', 'creditos': 5, 'carrera': 'ISC'},
                {'nombre': 'Estructuras de Datos', 'clave': 'ISC-ED', 'creditos': 5, 'carrera': 'ISC'},
                {'nombre': 'Redes de Computadoras', 'clave': 'ISC-RC', 'creditos': 4, 'carrera': 'ISC'},
                # IND
                {'nombre': 'Investigación de Operaciones', 'clave': 'IND-IO', 'creditos': 5, 'carrera': 'IND'},
                {'nombre': 'Control Estadístico de la Calidad', 'clave': 'IND-CC', 'creditos': 5, 'carrera': 'IND'},
                {'nombre': 'Gestión de la Cadena de Suministro', 'clave': 'IND-CS', 'creditos': 4, 'carrera': 'IND'},
                # MCT
                {'nombre': 'Circuitos Eléctricos y Electrónicos', 'clave': 'MCT-CE', 'creditos': 5, 'carrera': 'MCT'},
                {'nombre': 'Robótica Industrial', 'clave': 'MCT-RI', 'creditos': 5, 'carrera': 'MCT'},
                {'nombre': 'Sistemas de Control', 'clave': 'MCT-SC', 'creditos': 4, 'carrera': 'MCT'},
                # LAD
                {'nombre': 'Contabilidad Financiera', 'clave': 'LAD-CF', 'creditos': 5, 'carrera': 'LAD'},
                {'nombre': 'Comportamiento Organizacional', 'clave': 'LAD-CO', 'creditos': 4, 'carrera': 'LAD'},
                {'nombre': 'Mercadotecnia Estratégica', 'clave': 'LAD-ME', 'creditos': 4, 'carrera': 'LAD'},
            ]

            materias_creadas = []
            for m_data in datos_materias:
                carrera_obj = carreras_creadas[m_data['carrera']]
                materia, created = Materia.objects.get_or_create(
                    clave=m_data['clave'],
                    defaults={
                        'nombre': m_data['nombre'],
                        'creditos': m_data['creditos'],
                        'carrera': carrera_obj
                    }
                )
                materias_creadas.append(materia)
                status = 'Creada' if created else 'Ya existía'
                self.stdout.write(f'  [Materia] {status}: {materia.nombre} ({materia.clave})')

            # 3. Crear Alumnos
            datos_alumnos = [
                {
                    'nombre': 'Carlos',
                    'apellido_paterno': 'Hernández',
                    'apellido_materno': 'López',
                    'numero_control': '26010001',
                    'email': 'carlos.hernandez@instituto.edu.mx',
                    'carrera': 'ISC'
                },
                {
                    'nombre': 'María Fernanda',
                    'apellido_paterno': 'González',
                    'apellido_materno': 'Torres',
                    'numero_control': '26010002',
                    'email': 'maria.gonzalez@instituto.edu.mx',
                    'carrera': 'ISC'
                },
                {
                    'nombre': 'Alejandro',
                    'apellido_paterno': 'Ramírez',
                    'apellido_materno': 'Sánchez',
                    'numero_control': '26010003',
                    'email': 'alejandro.ramirez@instituto.edu.mx',
                    'carrera': 'IND'
                },
                {
                    'nombre': 'Valeria',
                    'apellido_paterno': 'Morales',
                    'apellido_materno': 'Castillo',
                    'numero_control': '26010004',
                    'email': 'valeria.morales@instituto.edu.mx',
                    'carrera': 'IND'
                },
                {
                    'nombre': 'Diego',
                    'apellido_paterno': 'Vargas',
                    'apellido_materno': 'Mendoza',
                    'numero_control': '26010005',
                    'email': 'diego.vargas@instituto.edu.mx',
                    'carrera': 'MCT'
                },
                {
                    'nombre': 'Sofía',
                    'apellido_paterno': 'Navarro',
                    'apellido_materno': 'Reyes',
                    'numero_control': '26010006',
                    'email': 'sofia.navarro@instituto.edu.mx',
                    'carrera': 'MCT'
                },
                {
                    'nombre': 'Luis Fernando',
                    'apellido_paterno': 'Castro',
                    'apellido_materno': 'Ortiz',
                    'numero_control': '26010007',
                    'email': 'luis.castro@instituto.edu.mx',
                    'carrera': 'LAD'
                },
                {
                    'nombre': 'Ana Paula',
                    'apellido_paterno': 'Flores',
                    'apellido_materno': 'Gutiérrez',
                    'numero_control': '26010008',
                    'email': 'ana.flores@instituto.edu.mx',
                    'carrera': 'LAD'
                },
            ]

            alumnos_creados = []
            for a_data in datos_alumnos:
                carrera_obj = carreras_creadas.get(a_data['carrera'])
                alumno, created = Alumno.objects.get_or_create(
                    numero_control=a_data['numero_control'],
                    defaults={
                        'nombre': a_data['nombre'],
                        'apellido_paterno': a_data['apellido_paterno'],
                        'apellido_materno': a_data['apellido_materno'],
                        'email': a_data['email'],
                        'carrera': carrera_obj
                    }
                )
                alumnos_creados.append(alumno)
                status = 'Creado' if created else 'Ya existía'
                self.stdout.write(f'  [Alumno] {status}: {alumno.nombre} {alumno.apellido_paterno} ({alumno.numero_control})')

            # 4. Crear Inscripciones
            # Se inscriben alumnos en materias correspondientes a su carrera con calificación y ciclo
            calificaciones_posibles = [Decimal('75.00'), Decimal('82.50'), Decimal('88.00'), Decimal('91.50'), Decimal('95.00'), Decimal('100.00')]
            ciclos = ['2026-1', '2026-2']

            inscripciones_count = 0
            for alumno in alumnos_creados:
                if not alumno.carrera:
                    continue
                # Materias de la carrera del alumno
                materias_de_su_carrera = Materia.objects.filter(carrera=alumno.carrera)
                for materia in materias_de_su_carrera:
                    calif = random.choice(calificaciones_posibles)
                    ciclo = random.choice(ciclos)
                    inscripcion, created = Inscripcion.objects.get_or_create(
                        alumno=alumno,
                        materia=materia,
                        defaults={
                            'calificacion': calif,
                            'ciclo': ciclo
                        }
                    )
                    if created:
                        inscripciones_count += 1

            self.stdout.write(f'  [Inscripciones] Creadas: {inscripciones_count}')

            self.stdout.write(self.style.SUCCESS('\n¡Base de datos poblada exitosamente!'))
            self.stdout.write(f'Total Carreras: {Carrera.objects.count()}')
            self.stdout.write(f'Total Materias: {Materia.objects.count()}')
            self.stdout.write(f'Total Alumnos: {Alumno.objects.count()}')
            self.stdout.write(f'Total Inscripciones: {Inscripcion.objects.count()}')
            self.stdout.write(self.style.NOTICE(f'Total Publicaciones (sin modificar): {Publicacion.objects.count()}'))
