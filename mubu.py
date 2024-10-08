import pygame as pg
import numpy as np
from time import sleep
from random import randint, choice
import tkinter as tk
from tkinter.filedialog import asksaveasfilename, askopenfilename
import customtkinter as ctk
import pandas as pd
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

app = ctk.CTk()
app.geometry("720x480")
app.title("Musipy")

# Inicialización de Pygame
pg.init()
pg.mixer.init()

# Definición de escalas y estilos
notas = np.round(130.813 * np.power(2 ** (1 / 12), np.arange(36)),3)
nombres_notas = ("C","C#","D","D#","E","F","F#","G","G#","A","A#","B","C","C#","D","D#","E","F","F#","G","G#","A","A#","B","C","C#","D","D#","E","F","F#","G","G#","A","A#","B")
dict_clav_frec = {notas[i] : nombres_notas[i]for i in range(len(notas))}
dict_clav_nombre = {nombres_notas[i] :notas[i] for i in range(12)}

i_escal_may = [0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19, 21, 23, 24, 26, 28, 29, 31, 33, 34, 36]
i_escal_men = [0, 2, 3, 5, 7, 8, 10, 12, 14, 15, 17, 19, 20, 22, 24, 26, 27, 29, 31, 32, 34, 36]

estilos = ("Sine", "Piano", "Sawtooth", "Square", "Triangle", "Organ")
estilos_percusion = ("Bombo","Caja")

notas_pantalla_global = []
base_global = []
mel_global = []
perc_global = []
son_global = ["Aleatoria", "Aleatoria"]
esc_global = ""
tip_esc_global = ""
df_global = pd.DataFrame()
continuar_cancion_global = False


def chance(porcentaje):
    return randint(1, 100) <= porcentaje


def crear_acordes(esc_nota,esc_tipo,largo = 64):
    if esc_nota == "Aleatoria":
        esc_nota = choice(nombres_notas[:11])
    if esc_tipo == "Aleatoria":
        esc_tipo = choice(["Mayor","Menor"])

    if esc_tipo == "Mayor":
        escala = i_escal_may
    else:
        escala = i_escal_men

    nota_base = dict_clav_nombre[esc_nota]
    i_nota_base = np.where(notas == nota_base)[0][0]
    notas_cortadas = notas[i_nota_base:]

    notas_usables = notas_cortadas[escala[:len(escala)-i_nota_base-1]]

    acordes = []
    notas_pantalla_global = []
    for _ in range(largo):
        indice = randint(0, 6)
        mostrar = dict_clav_frec[notas_usables[indice]]
        if (escala[indice+2] - escala[indice]) < 4 and (escala[indice+4] - escala[indice+2]) >= 4:
            mostrar= mostrar + "m"
        elif (escala[indice+2] - escala[indice]) < 4 and (escala[indice+4] - escala[indice+2]) < 4:
            mostrar = mostrar + "dim"
        acorde = [notas_usables[indice], notas_usables[indice + 2], notas_usables[indice + 4]]
        acordes.append(acorde)
        notas_pantalla_global.append(mostrar)

    return acordes,esc_nota,esc_tipo,notas_pantalla_global


def crear_base(acordes, p_empezar=None, p_parar=None):
    if p_empezar is None:
        p_empezar = randint(4, 100)

    if p_parar is None:
        p_parar = randint(0, 2)

    continuar = chance(p_empezar)
    base_global = [
        (acorde if continuar else [0, 0, 0, 0]) for acorde in acordes
    ]

    for i in range(len(acordes)):
        if continuar:
            continuar = not chance(p_parar)
        else:
            continuar = chance(p_empezar)
        base_global[i] = (acordes[i] if continuar else [0, 0, 0, 0])

    return base_global


def crear_melodia(acordes, probabilidad=None):
    if probabilidad is None:
        probabilidad = randint(0, 100)

    melodia = [
        choice(acorde) if chance(probabilidad) else 0
        for acorde in acordes
        for _ in range(3)
    ]

    return melodia


def crear_percusion(p_empezar = None,p_parar=None,largo = 64):
    if p_empezar is None:
        p_empezar = randint(0, 40)
    if p_parar is None:
        p_parar = randint(0, 40)

    empezar = chance(p_empezar)
    sonido_bombo, sonido_caja = estilos_percusion[:2]

    percusion = []
    for i in range(largo):
        if empezar:
            percusion.extend([sonido_bombo, sonido_caja, sonido_bombo, sonido_caja])
            empezar = chance(100 - p_parar)
        else:
            percusion.extend(["", "", "", ""])
            empezar = chance(p_empezar)
    
    return percusion


def crear_cancion():
    global base_global, mel_global, son_global, esc_global,notas_pantalla_global,tem_global,tip_esc_global,perc_global,continuar_cancion_global
    continuar_cancion_global = False
    esc_global = esc_variable.get()
    tip_esc_global = tipo_esc_variable.get()
    acordes,esc_global,tip_esc_global,notas_pantalla_global = crear_acordes(esc_global,tip_esc_global)
    base_global = crear_base(acordes)
    mel_global = crear_melodia(acordes)
    perc_global = crear_percusion()
    tem_global = tem_entrada_menu.get()
    
    if not tem_global.isdigit():
        tem_global = randint(70, 140)
    else:
        tem_global = int(tem_global)
    
    if mel_variable.get() == "Aleatoria":
        son_global[1] = choice(estilos)
    else:
        son_global[1] = mel_variable.get()

    if bas_variable.get() == "Aleatoria":
        son_global[0] = choice(estilos)
    else:
        son_global[0] = bas_variable.get()
    
    label_base.configure(text = "Base: "+son_global[0])
    label_melodia.configure(text = "Melodia: "+son_global[1])
    label_tempo.configure(text = "BPM: "+str(tem_global))
    label_escala.configure(text = "Escala: "+ tip_esc_global +" de " + esc_global)
    boton_reproducir.configure(state = "normal")
    boton_ventana_guardar.configure(state = "normal")


def reproducir_nota(frecuencia, duracion, estilo, sampling_rate=44100):
    if frecuencia == 0:
        return

    if not pg.mixer.get_init():
        pg.mixer.init(frequency=sampling_rate, size=-16, channels=2)

    frames = int(duracion*1.01 * sampling_rate)
    tiempo = np.linspace(0, duracion*1.01, frames)

    if estilo == "Sine":
        arr = np.sin(2 * np.pi * frecuencia * tiempo)
    elif estilo == "Piano":
        arr = np.sin(2 * np.pi * frecuencia * tiempo) * np.exp(-tiempo * 1.2)
    elif estilo == "Sawtooth":
        arr = 2 * (tiempo * frecuencia - np.floor(0.5 + tiempo * frecuencia))
    elif estilo == "Organ":
        arr = np.cos(2 * np.pi * frecuencia * tiempo) \
              + np.cos(4 * np.pi * frecuencia * tiempo) \
              + np.cos(6 * np.pi * frecuencia * tiempo)
    elif estilo == "Square":
        arr = np.sign(np.sin(2 * np.pi * frecuencia * tiempo))
    elif estilo == "Triangle":
        arr = 2 * np.abs(np.sin(2 * np.pi * frecuencia * tiempo)) - 1

    else:
        print("No existe el estilo "+ estilo)
        return


    arr /= np.max(np.abs(arr))
    arr *= (frecuencia ** -0.2)

    sonido = np.array([32767 * arr, 32767 * arr], dtype=np.int16).T
    sonido = pg.sndarray.make_sound(sonido.copy())
    
    if estilo == "Piano":sonido.set_volume(0.1)
    else:sonido.set_volume(0.04)
    sonido.play()


def reproducir_percusion(sonido):
    
    if sonido != "":
        if not pg.mixer.get_init():
            frecuencia = 50
            tiempo = np.linspace(0, 0.05, 44100)
            arr = np.sin(2 * np.pi * frecuencia * tiempo)
        
        if sonido == "Bombo":
            tiempo = np.linspace(0, 1, 44100)
            arr = np.sin(2 * np.pi * 60 * tiempo) * np.exp(-8)


        elif sonido == "Caja":
            tiempo = np.linspace(0, 1, 44100)
            frecuencia = 120
            ruido_blanco = np.random.uniform(-0.0001, 0.0001, 44100)
            envolvente = np.exp(-tiempo * 8)
            arr = ruido_blanco * envolvente
            
            
        else:
            print("No existe el sonido"+sonido)
            return
    else:
        return

    arr /= np.max(np.abs(arr)) * 0.5
    arr *= (90 ** -0.2)
    
    

    sonido = np.array([32767 * arr, 32767 * arr], dtype=np.int16).T
    sonido = pg.sndarray.make_sound(sonido.copy())

    if sonido == "Bombo":
        sonido.set_volume(1)
    else:
        sonido.set_volume(0.04)
    
    sonido.play()


def reproducir_cancion():
    boton_reproducir.configure(state = "disabled")
    global base_global, mel_global, son_global, tem_global,perc_global,continuar_cancion_global
    continuar_cancion_global = True

    bps = 60 / tem_global
    t_entre_compases = bps * 4
    largo_melodia = len(mel_global)
    largo_base = len(base_global)

    sonido_acordes, sonido_melodia = son_global
    i = 0
    while continuar_cancion_global and i<largo_base:
        label_nota_iz.configure(text = notas_pantalla_global[i])
            
        if i < largo_base - 2:
            label_nota_cen.configure(text = notas_pantalla_global[i + 1])
            label_nota_der.configure(text = notas_pantalla_global[i + 2])  
        elif i == largo_base - 2:
            label_nota_cen.configure(text = notas_pantalla_global[i + 1])
            label_nota_der.configure(text = " ")

        for nota in base_global[i]:
            reproducir_nota(nota, t_entre_compases, estilo=sonido_acordes)
        
        for x in range(4):
            indice = i * 4 + x

            if indice < largo_melodia and continuar_cancion_global:
                reproducir_nota(mel_global[indice], bps, estilo=sonido_melodia)
                reproducir_percusion(perc_global[indice])
                for z in range(10):
                    app.update()
                    sleep(bps/10)
        i+=1    
    pg.mixer.fadeout(800)
    label_nota_iz.configure(text = " ")
    label_nota_cen.configure(text = " ")
    label_nota_der.configure(text = " ")  


def guardar_cancion():
    if len(entrada_nombre.get())>0 and len(entrada_nombre.get())<=14:
        global base_global, mel_global, son_global, tem_global,perc_global,notas_pantalla_global,esc_global,tip_esc_global
        son_base, son_melodia = son_global
        base_procesada = ""
        mel_procesada = ""

        for acorde in base_global:
            for nota in acorde:
                base_procesada += str(nota)+"|"

        for nota in mel_global:
            mel_procesada += str(nota)+"|"
        
        perc_procesada = "|".join(perc_global)
        n_pant_procesada = "|".join(notas_pantalla_global)
        
        datos = {"Nombre":entrada_nombre.get(),
                "Base":[base_procesada],
                "Melodia":[mel_procesada],
                "Percusion":[perc_procesada],
                "Sonido Base":[son_base],
                "Sonido Melodia":[son_melodia],
                "BPM":[str(tem_global)],
                "Notas En Pantalla":[n_pant_procesada],
                "Escala": [esc_global],
                "Tipo De Escala": [tip_esc_global]}
        
        nuevo_df = pd.DataFrame(datos)

        ruta_archivo = asksaveasfilename(defaultextension=".csv",filetypes=[("CSV files","*.csv")])

        if os.path.exists(ruta_archivo):
            viejo_df = pd.read_csv(ruta_archivo)
            final_df = pd.concat([viejo_df,nuevo_df])
        else:
            final_df = nuevo_df


        try:
            final_df.to_csv(ruta_archivo,index=False)
            mostrar_mensaje("Datos guardados en " + ruta_archivo)
            abrir_ventana_principal()
        except Exception as error:
            mostrar_mensaje(f"Error al guardar el archivo CSV: {error}")
        
    elif len(entrada_nombre.get())>14:
        mostrar_mensaje("El nombre es demasiado largo")
    else:
        mostrar_mensaje("Escriba un nombre")


def abrir_ventana_principal():
    frame5.place_forget()
    frame6.place_forget()
    boton_cancelar_carga.place_forget()
    boton_seleccionar_archivo.place_forget()

    frame1.place(relx=0.05, rely=0.05, anchor=tk.NW)
    frame2.place(relx=0.95, rely=0.05, anchor=tk.NE)
    frame3.place(relx=0.50, rely=0.95, anchor=tk.S)
    frame4.place(relx=0.95, rely=0.6, anchor=tk.E)


def abrir_ventana_guardar():
    frame1.place_forget()
    frame2.place_forget()
    frame3.place_forget()
    frame4.place_forget()

    frame6.place(relx=0.5, rely=0.5, anchor=tk.CENTER)


def cargar_archivo():
    palabras = ["Nombre","Sonido Base", "Sonido Melodia"]
    ruta_archivo = askopenfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    
    if ruta_archivo != "":
        global df_global
        df_global = pd.read_csv(ruta_archivo)
        

        for i in range(len(df_global)):
            fila = df_global.iloc[i]

            for x in range(len(palabras)):
                frame = ctk.CTkFrame(master=frame5, fg_color="transparent",border_color="gray50", border_width=1,corner_radius=0)
                frame.grid(column=x, row=i+1,pady = 10)
                
                ctk.CTkLabel(master=frame, font=fuente_fixedsys, text=fila[palabras[x]], anchor="center",width=125).pack(padx=30, pady=5)

                if x == len(palabras)-1:
                    frame = ctk.CTkFrame(master=frame5, fg_color="transparent",border_color="gray50", border_width=1,corner_radius=0)
                    frame.grid(column=x+1, row=i+1,pady = 10)
                    ctk.CTkButton(master=frame,font=fuente_fixedsys, command=lambda indice = i:cargar_cancion(indice), width=20,corner_radius=80, text=">").pack(padx=5, pady=5)
    else:
        mostrar_mensaje("No se selecciono una ruta")


def abrir_ventana_cargar():
    frame1.place_forget()
    frame2.place_forget()
    frame3.place_forget()
    frame4.place_forget()

    frame5.place(relx=0.5, rely=0.4, anchor=tk.CENTER)
    boton_cancelar_carga.place(anchor = "sw",relx=0.10, rely=0.93)
    boton_seleccionar_archivo.place(anchor = "se",relx=0.90, rely=0.93)

    palabras = ["Nombre","Sonido Base", "Sonido Melodia"]
    for i in range(len(palabras)):
        frame = ctk.CTkFrame(master=frame5, fg_color="transparent",border_color="gray50", border_width=1,corner_radius=0)
        frame.grid(column=i, row=0,pady = 10)
        ctk.CTkLabel(frame, font=fuente_fixedsys, text=palabras[i], anchor="center",width=125).pack(padx=30, pady=5)
    

def cargar_cancion(indice):
    abrir_ventana_principal()
    
    fila = df_global.iloc[indice]
    base_cargada = fila["Base"]
    base_cargada = base_cargada.split("|")
    base_cargada.pop()
    base_final = []
    indice = 0

    for i in range(len(base_cargada)//3):
        base_final.append([float(base_cargada[indice]),float(base_cargada[indice+1]),float(base_cargada[indice+2])])
        indice +=3
    
    melodia_cargada = fila["Melodia"]
    melodia_cargada = melodia_cargada.split("|")
    melodia_cargada.pop()
    melodia_final = []

    for nota in melodia_cargada:
        melodia_final.append(float(nota))

    
    percusion_final = fila["Percusion"]
    percusion_final = percusion_final.split("|")

    sonidos = [fila["Sonido Base"],fila["Sonido Melodia"]]
    bpm = fila["BPM"]
    tipo_de_escala_cargada = fila["Tipo De Escala"]
    escala_cargada = fila["Escala"]

    notas_pant_cargada = fila["Notas En Pantalla"]
    notas_pant_cargada = notas_pant_cargada.split("|")

    global base_global, mel_global, son_global,notas_pantalla_global,tem_global,perc_global,esc_global,tip_esc_global
    esc_global = str(escala_cargada)
    tip_esc_global = str(tipo_de_escala_cargada)
    son_global = sonidos
    notas_pantalla_global = notas_pant_cargada
    base_global = base_final
    mel_global = melodia_final
    perc_global = percusion_final
    tem_global = bpm


    label_base.configure(text = "Base: "+son_global[0])
    label_melodia.configure(text = "Melodia: "+son_global[1])
    label_tempo.configure(text = "BPM: "+str(tem_global))
    label_escala.configure(text = "Escala: "+ tip_esc_global +" de " + esc_global)
    boton_reproducir.configure(state = "normal")
    boton_ventana_guardar.configure(state = "disabled")

    reproducir_cancion()

def mostrar_mensaje(mensaje):
    def ocultar_mensaje():
        frame_mensaje.place_forget()
        label_mensaje.configure(text = "")   

    label_mensaje.configure(text = mensaje)
    frame_mensaje.place(anchor = "n",rely = 0.03,relx = .5)
    app.after(5000,ocultar_mensaje)
        
# Interfaz
fuente_fixedsys = ctk.CTkFont(family="Fixedsys",size=20)
fuente_fixedsys2 = ctk.CTkFont(family="Fixedsys",size=35)
fuente_fixedsys3 = ctk.CTkFont(family="Fixedsys",size=50)


#FRAME 1
frame1 = ctk.CTkFrame(master=app,height=150,width=500)
frame1.place(relx=0.05, rely=0.05, anchor=tk.NW)

frame_base = ctk.CTkFrame(master=frame1)
frame_base.pack(padx = 10,pady = 5,anchor = "e")
ctk.CTkLabel(frame_base, text="Base:",font=fuente_fixedsys).grid(column = 0, row = 0,padx =5)
bas_variable = tk.StringVar(app,value="Aleatoria")
bas_tipo_menu = ctk.CTkOptionMenu(master=frame_base,font=fuente_fixedsys,variable=bas_variable,values=estilos)
bas_tipo_menu.grid(column = 1, row = 0)


frame_mel = ctk.CTkFrame(master=frame1)
frame_mel.pack(padx = 10,pady = 5,anchor = "e")
ctk.CTkLabel(frame_mel, text="Melodía:",font=fuente_fixedsys).grid(column = 0, row = 0,padx =5)
mel_variable = tk.StringVar(app,value="Aleatoria")
mel_tipo_menu = ctk.CTkOptionMenu(master=frame_mel,font=fuente_fixedsys,variable=mel_variable,values=estilos)
mel_tipo_menu.grid(column = 1, row = 0)


frame_esc = ctk.CTkFrame(master=frame1)
frame_esc.pack(padx = 10,pady = 5,anchor = "e")
ctk.CTkLabel(frame_esc, text="Escala:",font=fuente_fixedsys).grid(column = 0, row = 0,padx =5)
esc_variable = tk.StringVar(app,value="Aleatoria")
esc_menu = ctk.CTkOptionMenu(master=frame_esc,font=fuente_fixedsys,variable=esc_variable,values=nombres_notas[:11])
esc_menu.grid(column = 1, row = 0)


frame_tipo_esc = ctk.CTkFrame(master=frame1)
frame_tipo_esc.pack(padx = 10,pady = 5,anchor = "e")
ctk.CTkLabel(frame_tipo_esc, text="Tipo:",font=fuente_fixedsys).grid(column = 0, row = 0,padx =5)
tipo_esc_variable = tk.StringVar(app,value="Aleatoria")
esc_tipo_menu = ctk.CTkOptionMenu(master=frame_tipo_esc,font=fuente_fixedsys,variable=tipo_esc_variable,values=["Mayor","Menor"])
esc_tipo_menu.grid(column = 1, row = 0)


frame_tem = ctk.CTkFrame(master=frame1)
frame_tem.pack(padx = 10,pady = 5,anchor = "e")
ctk.CTkLabel(frame_tem, text="BPM:",font=fuente_fixedsys).grid(column = 0, row = 0,padx =5)
tem_entrada_menu = ctk.CTkEntry(master=frame_tem,font=fuente_fixedsys,width=100,placeholder_text="Aleatorio")
tem_entrada_menu.grid(column = 1, row = 0)


#FRAME 2
frame2 = ctk.CTkFrame(master=app)
frame2.place(relx=0.95, rely=0.05, anchor=tk.NE)

label_base = ctk.CTkLabel(frame2,font=fuente_fixedsys, text="Base:",width=155,anchor="w")
label_base.pack(padx = 10,pady = 5)

label_melodia = ctk.CTkLabel(frame2,font=fuente_fixedsys, text="Melodia:",width=155,anchor="w")
label_melodia.pack(padx = 10,pady = 0)

label_tempo = ctk.CTkLabel(frame2,font=fuente_fixedsys, text="BPM:",width=155,anchor="w")
label_tempo.pack(padx = 10,pady = 5)

label_escala = ctk.CTkLabel(frame2,font=fuente_fixedsys, text="Escala:",width=155,anchor="w")
label_escala.pack(padx = 10,pady = 5)

#FRAME 3
frame3 = ctk.CTkFrame(master=app)
frame3.place(relx=0.50, rely=0.95, anchor=tk.S)

boton_generar = ctk.CTkButton(master=frame3, text="Generar Canción",font=fuente_fixedsys, command=crear_cancion)
boton_generar.grid(column = 0,row = 0,padx = 10,pady = 10)

boton_reproducir = ctk.CTkButton(master=frame3, text="Reproducir Canción",font=fuente_fixedsys, command=reproducir_cancion,state="disabled")
boton_reproducir.grid(column = 1,row = 0,padx = 10,pady = 10)

boton_ventana_guardar = ctk.CTkButton(master=frame3, text="Guardar Canción",font=fuente_fixedsys,state="disabled",command=abrir_ventana_guardar)
boton_ventana_guardar.grid(column = 2,row = 0,padx = 10,pady = 10)

boton_cargar = ctk.CTkButton(master=frame3, text="Cargar Canción",font=fuente_fixedsys,command=abrir_ventana_cargar)
boton_cargar.grid(column = 3,row = 0,padx = 10,pady = 10)

#FRAME 4
frame4 = ctk.CTkFrame(master=app)#,border_width=2,border_color=("black","gray25")
frame4.place(relx=0.95, rely=0.6, anchor=tk.E)

label_nota_iz = ctk.CTkLabel(frame4,font=fuente_fixedsys3, text=" ",anchor="w", width=130)
label_nota_iz.grid(column = 0,row = 0,padx = 20,pady = 30)

label_nota_cen = ctk.CTkLabel(frame4,font=fuente_fixedsys2, text=" ",text_color="gray40",anchor="center", width=92)
label_nota_cen.grid(column = 1,row = 0,pady = 30)

label_nota_der = ctk.CTkLabel(frame4,font=fuente_fixedsys2, text=" ",text_color="gray20",anchor="e", width=92)
label_nota_der.grid(column = 2,row = 0,padx = 20,pady = 30)


#VENTANA CARGAR
#FRAME 5
frame5 = ctk.CTkScrollableFrame(master=app,height=300,width=620)

boton_cancelar_carga = ctk.CTkButton(master=app, text="Cancelar",font=fuente_fixedsys,command=abrir_ventana_principal)
boton_seleccionar_archivo = ctk.CTkButton(master=app, text="Abrir Archivo",font=fuente_fixedsys,command=cargar_archivo)

#VENTANA GUARDAR
#FRAME 6
frame6 = ctk.CTkFrame(master=app)
entrada_nombre = ctk.CTkEntry(master=frame6,width=300,justify = "center",placeholder_text="Nombre de la cancion")
entrada_nombre.grid(column = 0,row = 0,columnspan = 2,padx = 10,pady = 10)

boton_cancelar_nombre = ctk.CTkButton(master=frame6, text="Cancelar",font=fuente_fixedsys,command=abrir_ventana_principal)
boton_cancelar_nombre.grid(column = 0,row = 1,padx = 10,pady = 10)

boton_guardar_nombre = ctk.CTkButton(master=frame6, text="Guardar",font=fuente_fixedsys,command=guardar_cancion)
boton_guardar_nombre.grid(column = 1,row = 1,padx = 10,pady = 10)

#FRAME MENSAJE
frame_mensaje = ctk.CTkFrame(master=app,corner_radius=100)
label_mensaje = ctk.CTkLabel(frame_mensaje,font=fuente_fixedsys)
label_mensaje.pack(padx = 10, pady = 3)

app.mainloop()
pg.quit()