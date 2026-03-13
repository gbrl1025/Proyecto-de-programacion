"""
Sistema de Gestión Académica para Profesores
Programa para primer año de programación.
Guarda los datos en datos.json
"""

import json
import os

ARCHIVO = "datos.json"


# ----- Cargar y guardar datos -----

def cargar_datos():
    """Lee el archivo JSON. Si no existe, retorna datos vacíos."""
    if not os.path.exists(ARCHIVO):
        return {"teachers": {}, "sections": []}
    archivo = open(ARCHIVO, "r", encoding="utf-8")
    datos = json.load(archivo)
    archivo.close()
    return datos


def guardar_datos(datos):
    """Guarda los datos en el archivo JSON."""
    archivo = open(ARCHIVO, "w", encoding="utf-8")
    json.dump(datos, archivo, indent=2, ensure_ascii=False)
    archivo.close()


# ----- Clase Estudiante -----

class Estudiante:
    """Un estudiante tiene nombre, cédula y una lista de notas."""

    def __init__(self, nombre, cedula):
        self.nombre = nombre
        self.cedula = str(cedula)
        self.notas = []

    def agregar_nota(self, nota):
        """Agrega una nota si está entre 0 y 100."""
        try:
            n = float(nota)
            if 0 <= n <= 20:
                self.notas.append(n)
                return True
        except:
            pass
        return False

    def editar_nota(self, posicion, nueva_nota):
        """Cambia la nota en la posición indicada (1, 2, 3...)."""
        try:
            n = float(nueva_nota)
            if 0 <= n <= 20 and 1 <= posicion <= len(self.notas):
                self.notas[posicion - 1] = n
                return True
        except:
            pass
        return False

    def eliminar_nota(self, posicion):
        """Elimina la nota en la posición indicada (1, 2, 3...)."""
        if posicion < 1 or posicion > len(self.notas):
            return False
        self.notas.pop(posicion - 1)
        return True

    def promedio(self):
        """Calcula el promedio de las notas."""
        if len(self.notas) == 0:
            return 0
        return sum(self.notas) / len(self.notas)


# ----- Login y registro -----

def registrar(datos):
    """Registra un nuevo profesor."""
    usuario = input("Usuario: ").strip()
    if usuario == "":
        print("El usuario no puede estar vacío.")
        return
    if usuario in datos["teachers"]:
        print("Ese usuario ya existe.")
        return
    clave = input("Contraseña: ")
    if clave == "":
        print("La contraseña no puede estar vacía.")
        return
    datos["teachers"][usuario] = clave
    guardar_datos(datos)
    print("Registrado correctamente.")


def iniciar_sesion(datos):
    """Pide usuario y contraseña. Retorna el usuario si es correcto, o None."""
    if len(datos["teachers"]) == 0:
        print("No hay profesores. Regístrate primero.")
        return None
    usuario = input("Usuario: ").strip()
    if usuario not in datos["teachers"]:
        print("Usuario no encontrado.")
        return None
    clave = input("Contraseña: ")
    if datos["teachers"][usuario] != clave:
        print("Contraseña incorrecta.")
        return None
    return usuario


# ----- Secciones del profesor -----

def obtener_secciones(datos, profesor):
    """Retorna la lista de secciones del profesor."""
    lista = []
    for sec in datos["sections"]:
        if sec["teacher"] == profesor:
            lista.append(sec)
    return lista


def crear_seccion(datos, profesor):
    """Crea una nueva sección."""
    nombre = input("Nombre de la sección: ").strip()
    if nombre == "":
        print("El nombre no puede estar vacío.")
        return
    nueva = {"nombre": nombre, "teacher": profesor, "estudiantes": []}
    datos["sections"].append(nueva)
    guardar_datos(datos)
    print("Sección creada.")