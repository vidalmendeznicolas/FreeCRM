from django.core.management.base import BaseCommand
from django.utils import timezone
from gestion.models import Gasto
from datetime import date, timedelta
from django.db import models

class Command(BaseCommand):
    help = 'Configura gastos de ejemplo para el sistema'

    def handle(self, *args, **options):
        self.stdout.write('Configurando gastos de ejemplo...')
        
        # Gastos de ejemplo
        gastos_data = [
            {
                'concepto': 'Factura de electricidad - Enero 2025',
                'importe': 85.50,
                'categoria': 'suministros',
                'observaciones': 'Factura mensual de electricidad del local',
                'fecha_gasto': date(2025, 1, 15)
            },
            {
                'concepto': 'Factura de internet - Enero 2025',
                'importe': 45.00,
                'categoria': 'suministros',
                'observaciones': 'Servicio de internet de alta velocidad',
                'fecha_gasto': date(2025, 1, 20)
            },
            {
                'concepto': 'Factura de agua - Enero 2025',
                'importe': 35.20,
                'categoria': 'suministros',
                'observaciones': 'Consumo de agua del mes',
                'fecha_gasto': date(2025, 1, 25)
            },
            {
                'concepto': 'Material de oficina',
                'importe': 120.00,
                'categoria': 'administrativo',
                'observaciones': 'Papel, bolígrafos, carpetas y otros materiales',
                'fecha_gasto': date(2025, 1, 10)
            },
            {
                'concepto': 'Servicio de limpieza',
                'importe': 200.00,
                'categoria': 'limpieza',
                'observaciones': 'Limpieza mensual del local',
                'fecha_gasto': date(2025, 1, 5)
            },
            {
                'concepto': 'Mantenimiento de equipos',
                'importe': 150.00,
                'categoria': 'equipamiento',
                'observaciones': 'Revisión y mantenimiento de ordenadores',
                'fecha_gasto': date(2025, 1, 12)
            },
            {
                'concepto': 'Publicidad en redes sociales',
                'importe': 80.00,
                'categoria': 'marketing',
                'observaciones': 'Campaña publicitaria en Facebook e Instagram',
                'fecha_gasto': date(2025, 1, 18)
            },
            {
                'concepto': 'Seguro del local',
                'importe': 300.00,
                'categoria': 'inmobiliario',
                'observaciones': 'Póliza de seguro anual del local',
                'fecha_gasto': date(2025, 1, 1)
            }
        ]
        
        for gasto_data in gastos_data:
            gasto, created = Gasto.objects.get_or_create(
                concepto=gasto_data['concepto'],
                defaults={
                    'importe': gasto_data['importe'],
                    'categoria': gasto_data['categoria'],
                    'observaciones': gasto_data['observaciones'],
                    'fecha_gasto': gasto_data['fecha_gasto']
                    # Nota: factura se puede añadir manualmente después
                }
            )
            if created:
                self.stdout.write(f'  ✓ Gasto creado: {gasto.concepto} - {gasto.importe}€')
            else:
                self.stdout.write(f'  - Gasto ya existe: {gasto.concepto}')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Configuración de gastos completada.'))
        
        # Mostrar estadísticas
        total_gastos = Gasto.objects.aggregate(total=models.Sum('importe'))['total'] or 0
        self.stdout.write(f'\n📊 Estadísticas:')
        self.stdout.write(f'  - Total de gastos: {Gasto.objects.count()}')
        self.stdout.write(f'  - Importe total: {total_gastos}€') 