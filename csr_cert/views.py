from hmac import digest
from django.shortcuts import render, HttpResponse
import OpenSSL.crypto as crypto
from .models import CSR
from .forms import CSRForm,CSSRForm
from ca_intermediate.models import RootCAIM
from django.views.static import serve
import os
from Crypto.PublicKey import RSA

# Create your views here.

def CSRView(request):
    form = CSRForm()
    gen_cert = "NaN"
    gen_csr = "NaN"
    gen_key = "NaN"
    download_path = 'http://127.0.0.1:8000/static/cert/certs.pem'
    temp = 0

    if request.method == 'POST':
        form = CSRForm(request.POST)

        if form.is_valid():
            print('Creating CSR and sign using ')
            digest = "sha256"
            req = crypto.X509Req()
            # savin info in req object
            subj = req.get_subject()
            subj.CN = form.cleaned_data['common_name']
            subj.C = form.cleaned_data['country_code']
            subj.ST = form.cleaned_data['state']
            subj.O = form.cleaned_data['org_name']
            subj.OU = form.cleaned_data['org_unit']
            subj.emailAddress = form.cleaned_data['email']
            #generate key 
            #passphrase for key generated
            passphrase = form.cleaned_data['passphrase']
            passphrase_as_bytes = str.encode(passphrase)
            key_rsa = RSA.generate(2048)
            new_key = key_rsa.export_key("PEM",passphrase=passphrase)
            key = crypto.load_privatekey(crypto.FILETYPE_PEM,new_key,passphrase=passphrase_as_bytes)
            
            #below for root ca and im
            password = "password"
            password_as_bytes = str.encode(password)
            
            #generating req csr -> csr field
            req.set_pubkey(key)
            req.sign(key,digest)
            form.instance.csr =  crypto.dump_certificate_request(crypto.FILETYPE_PEM,req).decode()
            # retreving obj using set_issuer field
            obj = RootCAIM.objects.get(name=form.cleaned_data['set_issuer'])
            issuerCert = crypto.load_certificate(crypto.FILETYPE_PEM, obj.certificate)
            issuerKey = crypto.load_privatekey(crypto.FILETYPE_PEM,obj.key,passphrase=password_as_bytes)
            #creatin cert obj and using req to and obj key to sign cert
            cert = crypto.X509()
            cert.gmtime_adj_notBefore(0)
            cert.gmtime_adj_notAfter(form.cleaned_data['validity_time']*365*86400)
            cert.set_subject(req.get_subject())
            cert.set_issuer(issuerCert.get_subject())
            cert.sign(issuerKey,digest)
            #savin cert to certificate field
            form.instance.certificate = crypto.dump_certificate(crypto.FILETYPE_PEM,cert).decode()
            #form.instance.key = crypto.dump_privatekey(crypto.FILETYPE_PEM,key).decode()
            form.instance.key = key_rsa.exportKey("PEM", passphrase=passphrase).decode()
            #form.save
            form.save()

            gen_csr = crypto.dump_certificate_request(crypto.FILETYPE_PEM,req).decode()
            gen_cert = crypto.dump_certificate(crypto.FILETYPE_PEM,cert).decode()
            gen_key =  key_rsa.exportKey("PEM", passphrase=passphrase).decode()

            temp = CSR.objects.get(csr=gen_csr).id

            f = open('./static/cert/certs.pem', 'w')
            f.write('CSR:\n')
            f.write(gen_csr)
            f.close()

            f = open('./static/cert/certs.pem', 'a')
            f.write('\n')
            f.write('CERTIFICATE:\n')
            f.write(gen_cert)
            f.write('\n')
            f.write('KEY:\n')
            f.write(gen_key)
            f.close()

    return render(request,'csr_page.html',{'form':form, 'csr': gen_csr, 'cert': gen_cert, 'key' : gen_key, 'path': download_path, 'id':temp})

def CSSRView(request):
    form = CSSRForm()
    gen_cert = "NaN"
    gen_key = "NaN"
    content = "Nan"

    if request.method == 'POST':
        print(form.is_valid())
        form = CSSRForm(request.POST)

        if request.POST['checkit'] == "upload":
            content = request.FILES['file'].read().decode()

        if form.is_valid():
            print('Creating CSR and sign using ')
            digest = "sha256"

            if request.POST['checkit'] == "paste":
                print("here")
                content = form.cleaned_data['csr']

            print(content)
            print("ok")

            req = crypto.load_certificate_request(crypto.FILETYPE_PEM,content)
            #generate key #the key is already set for the csr no need to sign it
            # key = crypto.PKey()
            # key.generate_key(crypto.TYPE_RSA,2048)
            password = "password"
            password_as_bytes = str.encode(password)
            #generating req csr -> csr field   3 already signed
            # req.set_pubkey(key)
            # req.sign(key,digest)
            # retreving obj using set_issuer field
            obj = RootCAIM.objects.get(name=form.cleaned_data['set_issuer'])
            issuerCert = crypto.load_certificate(crypto.FILETYPE_PEM, obj.certificate)
            issuerKey = crypto.load_privatekey(crypto.FILETYPE_PEM,obj.key,passphrase=password_as_bytes)
            #creatin cert obj and using req to and obj key to sign cert
            cert = crypto.X509()
            cert.gmtime_adj_notBefore(0)
            cert.gmtime_adj_notAfter(form.cleaned_data['validity_time']*365*86400)
            cert.set_subject(req.get_subject())
            cert.set_issuer(issuerCert.get_subject())
            cert.sign(issuerKey,digest)
            #savin cert to certificate field
            form.instance.certificate = crypto.dump_certificate(crypto.FILETYPE_PEM,cert).decode()
            #form.instance.key = crypto.dump_privatekey(crypto.FILETYPE_PEM,key).decode()
            #form.save
            #we dont have key duhh
            form.save()
            gen_cert = crypto.dump_certificate(crypto.FILETYPE_PEM,cert).decode()
            #gen_key =  crypto.dump_privatekey(crypto.FILETYPE_PEM,key).decode()

            print(gen_cert)

    return render(request,'csr_two.html',{'form':form, 'cert': gen_cert})


def getCertChain(request, id):
    if(id == '0'):
        return HttpResponse("Cert not found!")
    
    obj = CSR.objects.get(id=id)
    f = open('./static/certChain/certs.pem', 'w')
    f.write(obj.certificate)
    f.close()

    parent = obj.set_issuer

    while parent != None:
        print(parent)
        temp = RootCAIM.objects.get(name=parent)

        f = open('./static/certChain/certs.pem', 'a')
        f.write('\n')
        f.write(temp.certificate)
        f.close()

        parent = temp.set_issuer

    filepath = './static/certChain/certs.pem'
    return serve(request, os.path.basename(filepath), os.path.dirname(filepath))
