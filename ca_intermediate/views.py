from django.shortcuts import render, HttpResponse

# Create your views here.
from unicodedata import name
from wsgiref.util import request_uri
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
import pkg_resources
from .forms import RootCAIMForm
from .models import RootCAIM
import OpenSSL.crypto as crypto
from Crypto.PublicKey import RSA

# Create your views here.
class IndexView(TemplateView):
    template_name = 'index.html'

def RootCAIMView(request):
    allCas = RootCAIM.objects.all()

    form = RootCAIMForm()
    gen_cert = "NaN"
    download_path = 'http://127.0.0.1:8000/static/ca/certificate.pem'

    if request.method == 'POST':
        form = RootCAIMForm(request.POST)
        
        if form.is_valid():
            print('Setting up Root CA/IM!!')
            #initially
            # key = crypto.PKey()
            # key.generate_key(crypto.TYPE_RSA,2048)
            #Improvements
            key_rsa = RSA.generate(2048)
            password = "password"
            password_as_bytes = str.encode(password)
            new_key = key_rsa.export_key("PEM",passphrase=password)
            key = crypto.load_privatekey(crypto.FILETYPE_PEM,new_key,passphrase=password_as_bytes)

            cert = crypto.X509()
            cert.get_subject().CN = form.cleaned_data['common_name']
            cert.gmtime_adj_notBefore(0)
            cert.gmtime_adj_notAfter(form.cleaned_data['validity_time']*365*86400)
            cert.get_subject().C = form.cleaned_data['country_code']
            cert.get_subject().ST = form.cleaned_data['state']
            cert.get_subject().O = form.cleaned_data['org_name']
            cert.get_subject().OU = form.cleaned_data['org_unit']
            cert.set_pubkey(key)

            if form.cleaned_data['set_issuer'] == None:
                # if len(allCas) > 0:
                #     return HttpResponse("Error Root CA already exists!")
                cert.set_issuer(cert.get_subject())
                cert.sign(key,"sha256")
            else:
                obj = RootCAIM.objects.get(name=form.cleaned_data['set_issuer'])
                issuerCert = crypto.load_certificate(crypto.FILETYPE_PEM, obj.certificate)
                issuerKey = crypto.load_privatekey(crypto.FILETYPE_PEM,obj.key,passphrase=password_as_bytes)
                cert.set_issuer(issuerCert.get_subject())
                cert.sign(issuerKey,"sha256")
            form.instance.certificate = crypto.dump_certificate(crypto.FILETYPE_PEM,cert).decode()
            # form.instance.key = crypto.dump_privatekey(crypto.FILETYPE_PEM,key).decode()
            form.instance.key = key_rsa.exportKey("PEM", passphrase=password).decode()
            form.save()
            
            gen_cert = crypto.dump_certificate(crypto.FILETYPE_PEM,cert).decode()
            print(gen_cert)

            f = open('./static/ca/certificate.pem', 'w')
            f.write(gen_cert)
            f.close()

    return render(request, 'caim_page.html', {'form':form, 'cert': gen_cert, 'size': len(allCas), 'path': download_path})