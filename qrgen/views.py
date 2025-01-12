from django.shortcuts import render
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.http import HttpResponse
import qrcode
from pyzbar.pyzbar import decode
from PIL import Image
from pathlib import Path
from .models import Gen


# Create your views here.
def gen_qr(request):
    image_url = None
    if request.method == 'POST':
        data = request.POST['data']
        number = request.POST['number']
     
        
        # checking the validity of number
        if not number or not number.isnumeric() or  len(number) > 10:
             return render(request, 'qrgen/scan.html', {'result': 'Invalid number. Check the length.'})

   
        
        qr_content = f'{data} {number}'

        qr_code = qrcode.make(qr_content)

        buffer = BytesIO()

        filename =f'{data}_{number}.png'
        # saving the qr code in buffer
        qr_code.save( buffer, format='PNG' ) 
        buffer.seek(0)

        file = ContentFile(buffer.read())
        # defining the path where the qr image will save
        qr_path = FileSystemStorage(location=settings.MEDIA_ROOT / 'qr_codes', base_url='/media/qr_codes/')
        # saving the qr image
        qr_path.save(filename, file)
        image_url = qr_path.url(filename)

        # saving the qr data in the database
        Gen.objects.create(data=data, number=number)





        return render(request, 'qrgen/gen.html', {'image_url': image_url})

    return render(request, 'qrgen/gen.html', )



def scan_qr(request):
    result = None
    if request.method == 'POST' and  request.FILES['qr_image']:
        qr_image = request.FILES['qr_image']
        number = request.POST.get('number')

        # Validate the number
        if not number or not number.isnumeric() or len(number) > 10:
            return render(request, 'qrgen/scan.html', {'result': 'Invalid number. Check the length.'})

        fs = FileSystemStorage()
        filename = fs.save(qr_image.name, qr_image)
        image_path = Path(fs.location) / filename

        try:
            # Open and decode the QR image
            image = Image.open(image_path)
            decode_img = decode(image)

            if not decode_img:
                raise ValueError("No QR code found in the image.")

            decoded_data = decode_img[0].data.decode('utf-8').strip()
            print(decoded_data)
            data, qr_number = decoded_data.split(' ')
            print(f'Decoded data: {data} {qr_number}')

            # Validate QR code data with the database
            qr_entry = Gen.objects.filter(data=data, number=qr_number).first()
            print(qr_entry.data, qr_entry.number)
            if qr_entry:
                result = f'{data} {qr_number} is valid'
                qr_entry.delete()

                # Delete the saved QR code image
                qr_path = settings.MEDIA_ROOT / f'qr_codes/{filename}'
                if qr_path.exists():
                    qr_path.unlink()

                # Delete the uploaded image
                if image_path.exists():
                    image_path.unlink()
            else:
                result = "Invalid QR code data or number mismatch."
        except Exception as e:
            result = f'Error: Invalid QR code. Details: {e}'

        return render(request, 'qrgen/scan.html', {'result': result})

    return render(request, 'qrgen/scan.html')



# Scaning the qr code
def scan_qr(request):
    result = None
    if request.method == 'POST' and 'qr_image' in request.FILES:
        qr_image = request.FILES['qr_image']
        number = request.POST.get('number')

        # Validate the number
        if not number or not number.isnumeric() or len(number) > 10:
            return render(request, 'qrgen/scan.html', {'result': 'Invalid number. Check the length.'})

        fs = FileSystemStorage()
        filename = fs.save(qr_image.name, qr_image)
        image_path = Path(fs.location) / filename

        try:
            # Open and decode the QR image
            image = Image.open(image_path)
            decode_img = decode(image)

            if not decode_img:
                raise ValueError("No QR code found in the uploaded image.")

            # Extract data from the QR code
            decoded_data = decode_img[0].data.decode('utf-8').strip()
            if ' ' not in decoded_data:
                raise ValueError("Invalid QR code format. Expected 'data number' format.")

            data, qr_number = decoded_data.split(' ', 1)

            # Validate QR code data with the database
            qr_entry = Gen.objects.filter(data=data, number=qr_number).first()
            if qr_entry:
                result = f'{data} {qr_number} is valid'
                qr_entry.delete()

                # Delete the saved QR code image
                qr_path = settings.MEDIA_ROOT / f'qr_codes/{filename}'
                if qr_path.exists():
                    qr_path.unlink()

                # Delete the uploaded image
                if image_path.exists():
                    image_path.unlink()
            else:
                result = "Invalid QR code data or number mismatch."

        except Exception as e:
            result = f'Error: Invalid QR code. Details: {e}'

        return render(request, 'qrgen/scan.html', {'result': result})

    return render(request, 'qrgen/scan.html')
