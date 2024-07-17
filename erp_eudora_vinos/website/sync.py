import os
import sys
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
from django.utils import timezone

# Configura el entorno Django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_eudora_vinos.settings')
import django
django.setup()

from website.models import Ventas, Producto, Cliente, Configuracion

def obtener_fecha_ultima_sincronizacion():
    #print("Obteniendo fecha de última sincronización")
    config, created = Configuracion.objects.get_or_create(clave='ultima_sincronizacion')
    if created or not config.valor:
        return timezone.make_aware(datetime(2000, 1, 1, 0, 0, 0))
    return config.valor

def actualizar_fecha_ultima_sincronizacion(fecha):
    config, created = Configuracion.objects.get_or_create(clave='ultima_sincronizacion')
    config.valor = timezone.make_aware(fecha) if timezone.is_naive(fecha) else fecha
    config.save()


def SyncWoocomerce():
    # URL de la API de WooCommerce
    url = "https://erp.eudoravinos.cl/wp-json/wc/v3/orders"

    # Claves proporcionadas por WooCommerce
    consumer_key = "ck_c6f3618108c67d62e512c3cd080284d448ce8ede"
    consumer_secret = "cs_b812402f4fe07c64a061cc6d2489aebc436fdc3d"


    
     # Obtener la fecha de la última sincronización
    ultima_sincronizacion = obtener_fecha_ultima_sincronizacion()
   

    # Convertir la fecha a string para la API
    fecha_ultima_sincronizacion_str = ultima_sincronizacion.isoformat()

    # Realiza una solicitud GET con parámetros para obtener pedidos después de la última sincronización
    params = {'after': fecha_ultima_sincronizacion_str}
    response = requests.get(url, auth=HTTPBasicAuth(consumer_key, consumer_secret), params=params)
    
    if response.status_code == 200:
        
        data = response.json()
        

        for venta in data:
            pedido = venta['id']
            estado = venta['status']
            
            # Verifica si el estado del pedido es "completed" para poder seguir
            if estado != 'completed':
                #print(f"El pedido ID: {pedido} no está completado. Saltando este pedido.")
                continue
            
            # Obtener rut de billing o meta_data
            rut = None
            for meta in venta['meta_data']:
                if meta['key'] == 'additional_rut':
                    rut = meta['value']
                    break

            nombre_completo = venta['billing']['first_name'] + " " + venta['billing']['last_name']
            correo = venta['billing']['email']
            telefono = venta['billing']['phone']
            comuna = venta['billing']['city']
            calle = venta['billing']['address_1']
            numero_de_casa = venta['billing']['address_2']
            
            flete = int(venta['shipping_total'])
            factura = venta['payment_method_title']
            
            #print(f" Rut: {rut}, Pago Total: {flete}, Factura: {factura}")
            
            if factura != "Webpay Plus":
                factura = " "

            # Convertir fecha a objeto datetime.date
            fecha_boleta_str = venta.get('date_completed', None)
            fecha_boleta = None
            if fecha_boleta_str:
                try:
                    fecha_boleta = datetime.fromisoformat(fecha_boleta_str).date()
                except ValueError:
                    fecha_boleta = None

            # Verifica si la venta tiene los datos necesarios
            if not rut:
                continue

            # Busca el cliente basado en el rut
            cliente = Cliente.objects.filter(rut=rut).first()
            if not cliente:
                # Si no se encuentra el rut, crea un nuevo cliente
                cliente = Cliente.objects.create(rut=rut, nombre=nombre_completo, email=correo, telefono=telefono, numero_de_casa=numero_de_casa, comuna=comuna, calle=calle)

            # Verifica que el cliente se haya creado correctamente
            if not cliente:
                #print(f"No se pudo encontrar o crear un cliente para el RUT: {rut}. Saltando este pedido.")
                continue

            # Verifica si el pedido ya existe en Ventas
            if Ventas.objects.filter(pedido=pedido).exists():
                #print(f"El pedido ID: {pedido} ya existe en la base de datos. Saltando este pedido.")
                continue
            
            # Agregar depuración para los ítems de cada pedido
            for idx, item in enumerate(venta['line_items']):
               
                #print(f"Ítem {idx + 1}: {item}")

                precio_unitario = item['price']
                sku = item['sku']
                cantidad = item['quantity']

                # Depuración: Verificar los valores
                #print(f"Procesando ítem - Precio Unitario: {precio_unitario}, SKU: {sku}, Cantidad: {cantidad}")

                # Verifica si el SKU está presente
                if not sku:
                    #print(f"SKU faltante para el pedido ID: {pedido}. Saltando este ítem.")
                    continue

                # Verifica si la cantidad es un número válido
                if not isinstance(cantidad, int) or cantidad <= 0:
                    #print(f"Cantidad inválida para el pedido ID: {pedido}. Saltando este ítem.")
                    continue

                # Busca o crea el producto basado en el SKU
                producto, created = Producto.objects.get_or_create(SKU=sku)
                """if created:
                    print(f"Producto creado: {producto}")
                else:
                    print(f"Producto encontrado: {producto}")

                print(f"Procesando Pedido ID: {pedido}, Precio Unitario: {precio_unitario}, Cantidad: {cantidad}, SKU: {sku}, Fecha Boleta: {fecha_boleta}")
                """
                # Crea un nuevo registro de venta
                venta_total = precio_unitario * cantidad
                pago = precio_unitario * cantidad + flete
                Ventas.objects.create(pedido=pedido, precio_unitario=precio_unitario, cantidad=cantidad, SKU=producto, rut=cliente, venta_total=venta_total, fecha_boleta=fecha_boleta, flete=flete, pago=pago, factura_o_boleta=factura)
                #print(f"Añadido: Pedido ID {pedido}, Precio Unitario: {precio_unitario}, SKU: {sku}, Cantidad: {cantidad}, Venta Total: {venta_total}, Fecha Boleta: {fecha_boleta}")
        # Actualiza la fecha de última sincronización
        actualizar_fecha_ultima_sincronizacion(timezone.now())
        
    else:
        print(f"Error al realizar la solicitud: {response.status_code}")

######## IMPORTANTE ########

# Llama a la función SyncWoocomerce si este archivo es ejecutado directamente
if __name__ == "__main__":
    print("Ejecutando script directamente")
    #SyncWoocomerce()