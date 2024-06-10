from django.core import serializers
from django.http import JsonResponse
from  django.views.decorators.csrf import csrf_exempt

from .models import Producto
from .models import Proveedores
from .models import Cliente

# api para obtener todos los productos

# PRODUCTOS

@csrf_exempt
def guardarproducto(request):
    sku = request.POST.get('SKU', '')
    type = request.POST.get('type', '')
    value = request.POST.get('value', '')

    try:
        producto = Producto.objects.get(SKU=sku)
        if type == 'tipo_producto':
            producto.tipo_producto = value
        elif type == 'viña':
            producto.viña = value
        elif type == 'cepa':
            producto.cepa = value
        elif type == 'nombre_producto':
            producto.nombre_producto = value
        elif type == 'cosecha':
            producto.cosecha = value

        producto.save()
        return JsonResponse({'status': 'Updated'})
    except Producto.DoesNotExist:
        return JsonResponse({'status': 'Product not found'}, status=404)
    

# PROVEEDORES

@csrf_exempt
def guardarproveedor(request):
    rut_empresa = request.POST.get('rut_empresa', '')
    type = request.POST.get('type', '')
    value = request.POST.get('value', '')

    try:
        proveedor = Proveedores.objects.get(rut_empresa=rut_empresa)
        if type == 'nombre_prov':
            proveedor.nombre_prov = value
        elif type == 'email_empresa':
            proveedor.email_empresa = value
        elif type == 'telefono_empresa':
            proveedor.telefono_empresa = value

        proveedor.save()
        return JsonResponse({'status': 'Updated'})
    except Proveedores.DoesNotExist:
        return JsonResponse({'status': 'Provider not found'}, status=404)
    
def guardarcliente(request):
    rut=request.POST.get('rut','')
    type = request.POST.get('type', '')
    value = request.POST.get('value', '')

    try:
        cliente = Cliente.objects.get(rut=rut)
        if type == 'nombre':
            cliente.nombre = value
        elif type == 'apellido':
            cliente.apellido = value
        elif type == 'email':
            cliente.email = value
        elif type == 'comuna':
            cliente.comuna = value
        elif type == 'calle':
            cliente.calle = value
        elif type == 'numero_de_casa':
            cliente.numero_de_casa = value
        elif type == 'telefono':
            cliente.telefono = value

        cliente.save()
        return JsonResponse({'status': 'Updated'})
    except Cliente.DoesNotExist:
        return JsonResponse({'status': 'Client not found'}, status=404)