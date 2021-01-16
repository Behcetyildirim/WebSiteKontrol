import urllib.request
import socket
import subprocess
import pandas as pd
import os
from tkinter import *
import threading
import time
import requests


class Form():
    def __init__(self):
        self.form = Tk()
        self.form.title("Site Sorgulama")
        self.form.config(bg="papaya whip")
        self.form.geometry("600x600")
        self.form.minsize(300,300)
        self.form.maxsize(800,800)
        self.form.state("normal")

        self.entry = Entry(width=30)
        self.entry.pack(side="top")

        
        self.button = Button(self.form, text="Tarama Yap" , bg="white", command=self.th)
        self.button.pack()
        
        self.form.mainloop()

    def telegram_bot_sendtext(self, bot_message):
        
        bot_token = "1280244692:AAFGO4U9tkHZE4nDD9GPJPeTURaZ-bQQIUQ"
        bot_chatID = '1322517481'
        send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

        response = requests.get(send_text)

        return response.json()  

    def kodKiyasla(self,fp,tp):

        f = open(fp,"r")
        kod = f.readlines()
        t = open(tp,"r")
        temp = t.readlines()
        f.close()
        t.close()

        c = True
        
        for i in range(0,len(kod)):
            if kod[i] != temp[i]:
                c = False

        return c

    def sorgu(self,site):
        while True:
            dataFrame = pd.DataFrame()
            port = []
            state = []
            service = []

            url = site.split(".")
            url = "www." + url[1] + "." + url[2] + "." + url[3] # www.google.com.tr

            siteName = site.split(".")
            kaynakKod = [] 
            ipAddress = socket.gethostbyname(url)

            ## Port Sorgusu
            try:
                si = subprocess.STARTUPINFO()
                si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                a = subprocess.check_output(['nmap ','-F', ipAddress], startupinfo=si) 
                b = a.split(b'\r\n')
            except:
                print("NMAP ile ilgili sorun gerçekleşti.")

            if b == None:
                pass
            else:
                for index, i in enumerate(b):
                    if index>3 and index<21:
                        ports = str(i)
                        ports = ports[2:-1]
                        elements = ports.split()
                        port.append(elements[0])
                        state.append(elements[1])
                        service.append(elements[2])

                dataFrame["PORT"] = port[1:]
                dataFrame["STATE"] = state[1:]
                dataFrame["SERVICE"] = service[1:]

                kontrol = False
                portPath = "portBilgileri/" + siteName[1] + "-portlar.csv"

                if os.path.exists(portPath): ## Daha önce tarama yapıldı mı?
                    yerel_port_bilgisi = pd.read_csv(portPath)
                    
                    for i in range(0,len(yerel_port_bilgisi)):
                        if yerel_port_bilgisi["STATE"].iloc[i] != dataFrame["STATE"].iloc[i]:
                            self.telegram_bot_sendtext("{name} portunda değişiklik mevcut".format(name=dataFrame["PORT"].iloc[i]))
                            kontrol = True

                    
                else:
                    dataFrame.to_csv(portPath) ## İlk sorguysa kaydet


               
            ## Kaynak Kod Çekme İşlemi
            try:
                htm = urllib.request.urlopen(site) 
                html = htm.read()   
                codes = html.decode().split(" ") 
                for code in codes:
                    kaynakKod.append(code) 
            except UnicodeDecodeError:
                print("Site kodları çözümlenemedi..") 
                

            if len(kaynakKod) == 0:  
                print("Bir Hatayla Karşılaşıldı.")
                exit()
            else:
                fileName ="kaynakKodlar/" + siteName[1] + "-kaynakKodu.txt"
                if os.path.exists(fileName):
                    
                    tempPath = "kaynakKodlar/" + siteName[1] + "temp.txt"
                    tf = open(tempPath,"w",encoding="utf-8")
                    for item in kaynakKod:
                        tf.write(item)
                    tf.close()
                    check = self.kodKiyasla(fileName,tempPath)
                    
                    
                    if check==False:
                        self.telegram_bot_sendtext("Kaynak Kodlarda bir değişiklik saptandı.")
                    os.remove(tempPath) ## Geçici dosyanın silinmesi
                            
                else:
                    file = open(fileName,"w",encoding="utf-8") 
                    for item in kaynakKod:
                        file.write(item) 
                    file.close() 

    def th(self):
        self.s = self.entry.get()
        print(self.s)
        x = threading.Thread(target=self.sorgu,args=(self.s,))
        x.start()
        

app = Form()



