from django.core.management.base import BaseCommand
from django.utils import timezone
from gestion.models import Tarifa, Pago

class Command(BaseCommand):
    help = 'Configura tarifas de ejemplo y actualiza pagos existentes'

    def handle(self, *args, **options):
        self.stdout.write('Configurando tarifas de ejemplo...')
        
        # Crear tarifas de ejemplo
        tarifas_data = [
            {
                'nombre': 'Matrícula Mensual',
                'precio': 50.00,
                'observaciones': 'Tarifa estándar para matrícula mensual'
            },
            {
                'nombre': 'Matrícula Trimestral',
                'precio': 140.00,
                'observaciones': 'Tarifa con descuento para matrícula trimestral'
            },
            {
                'nombre': 'Matrícula Anual',
                'precio': 500.00,
                'observaciones': 'Tarifa con descuento máximo para matrícula anual'
            },
            {
                'nombre': 'Clase Individual',
                'precio': 25.00,
                'observaciones': 'Tarifa por clase individual'
            },
            {
                'nombre': 'Material Didáctico',
                'precio': 15.00,
                'observaciones': 'Tarifa por material didáctico'
            }
        ]
        
        tarifas_creadas = []
        for tarifa_data in tarifas_data:
            tarifa, created = Tarifa.objects.get_or_create(
                nombre=tarifa_data['nombre'],
                defaults={
                    'precio': tarifa_data['precio'],
                    'observaciones': tarifa_data['observaciones']
                }
            )
            if created:
                self.stdout.write(f'  ✓ Tarifa creada: {tarifa}')
                tarifas_creadas.append(tarifa)
            else:
                self.stdout.write(f'  - Tarifa ya existe: {tarifa}')
        
        # Actualizar pagos existentes
        self.stdout.write('\nActualizando pagos existentes...')
        pagos_sin_tarifa = Pago.objects.filter(tarifa__isnull=True)
        
        if pagos_sin_tarifa.exists():
            # Usar la primera tarifa como predeterminada
            tarifa_default = Tarifa.objects.first()
            
            for pago in pagos_sin_tarifa:
                # Asignar tarifa predeterminada
                pago.tarifa = tarifa_default
                # Establecer importe_original igual al importe_final (sin descuento)
                pago.importe_original = pago.importe_final
                pago.descuento = 0
                pago.save()
                
                self.stdout.write(f'  ✓ Pago actualizado: {pago.numero} - {pago.importe_final}€')
        else:
            self.stdout.write('  - No hay pagos que actualizar')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Configuración completada:\n'
                f'  - {len(tarifas_creadas)} tarifas creadas\n'
                f'  - {pagos_sin_tarifa.count()} pagos actualizados'
            )
        ) 