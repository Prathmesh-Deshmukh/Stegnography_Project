import os
import re
from django.conf import settings
from django.shortcuts import render
import stepic
from PIL import Image # importing the Image module from the PIL library.
import io
from django.http import FileResponse
import tempfile
from django.http import HttpResponse
from django.core.files import File



# Create your views here.

def index(request):
    return render(request, 'index.html')

def hide_text_in_image(image, text):
    text = encrypt(text, 5)
    data = text.encode('utf-8')
    '''encode('utf-8') on a string, it translates the human-readable 
    characters into a sequence of bytes using the UTF-8 encoding.
     The result is a bytes object in Python.'''
    return stepic.encode(image, data)




from django.http import HttpResponse

def about_us(request):
    return render(request, "about.html")

def encryption_view(request):
    if request.method == 'POST':
        text = request.POST['text']
        password = request.POST['pass']
        image_file = request.FILES['image']
        image = Image.open(image_file)

        modtext = text + '"[*]"' + password

        if image.format != 'PNG':
            image = image.convert('RGBA')
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            image = Image.open(buffer)


        new_image = hide_text_in_image(image, modtext) #used to hid text

        response = HttpResponse(content_type='image/png')

        original_filename = image_file.name.split('.')[0]
        encrypted_filename = f'{original_filename}_encrypted.png'
        response['Content-Disposition'] = f'attachment; filename="{encrypted_filename}"'


        new_image.save(response, 'PNG')

        return response

    return render(request, 'encryption.html')



def decryption_view(request):
    text=''
    cla = ''
    if request.method == 'POST':
        image_file = request.FILES['image']
        image = Image.open(image_file)
        password = request.POST['pass']

        if image.format != 'PNG':#checks whether the image format is not PNG.
            image = image.convert('RGBA')

            buffer = io.BytesIO()

            image.save(buffer, format="PNG")
            image = Image.open(buffer)

        modtext = extract_text_from_image(image)
        modtext = decrypt(modtext, 5)
        arr = modtext.split('"[*]"')
        text = arr[0]
        if arr[1] == password:
            text = arr[0]
            cla = 'alert-success'
        elif arr[1] != password:
            text = 'Incorrect Password, Please Try Again!'
            cla = 'alert-danger'

    return render(request, 'decryption.html', {'text': text, 'cla' : cla})

def extract_text_from_image(image):
    data = stepic.decode(image)

    if isinstance(data, bytes):
        return data.decode('utf-8')
    return data

def encrypt(text, shift):
    encrypted_text = ""
    for char in text:
        # Encrypt uppercase letters
        if char.isupper():
            encrypted_text += chr((ord(char) + shift - 65) % 26 + 65)
        # Encrypt lowercase letters
        elif char.islower():
            encrypted_text += chr((ord(char) + shift - 97) % 26 + 97)
        else:
            encrypted_text += char  # Keep non-alphabetic characters unchanged
    return encrypted_text


def decrypt(text, shift):
    decrypted_text = ""
    for char in text:
        # Decrypt uppercase letters
        if char.isupper():
            decrypted_text += chr((ord(char) - shift - 65) % 26 + 65)
        # Decrypt lowercase letters
        elif char.islower():
            decrypted_text += chr((ord(char) - shift - 97) % 26 + 97)
        else:
            decrypted_text += char  # Keep non-alphabetic characters unchanged
    return decrypted_text
