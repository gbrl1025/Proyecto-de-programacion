"""
Sistema de Gestión Académica para Profesores
Programa para primer año de programación.
Guarda los datos en datos.json
"""

import json
import os
import hashlib

ARCHIVO = "datos.json"

ITERACIONES_HASH = 120000


# ----- Seguridad de contraseñas (hash + salt) -----

def generar_hash_clave(clave):
    """Retorna un string con el hash de la clave (no reversible)."""
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", clave.encode("utf-8"), salt, ITERACIONES_HASH)
    return "pbkdf2$" + str(ITERACIONES_HASH) + "$" + salt.hex() + "$" + dk.hex()


def verificar_clave(clave_ingresada, valor_guardado):
    """
    Verifica una clave contra el valor guardado.
    - Si el valor guardado es viejo (texto plano), compara directo.
    - Si es nuevo (pbkdf2$...), verifica con pbkdf2.
    Retorna True/False.
    """
    if isinstance(valor_guardado, str) and valor_guardado.startswith("pbkdf2$"):
        partes = valor_guardado.split("$")
        if len(partes) != 4:
            return False
        iteraciones = int(partes[1])
        salt = bytes.fromhex(partes[2])
        esperado = bytes.fromhex(partes[3])
        obtenido = hashlib.pbkdf2_hmac("sha256", clave_ingresada.encode("utf-8"), salt, iteraciones)
        return obtenido == esperado
    return clave_ingresada == valor_guardado


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
    datos["teachers"][usuario] = generar_hash_clave(clave)
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
    guardada = datos["teachers"][usuario]
    if not verificar_clave(clave, guardada):
        print("Contraseña incorrecta.")
        return None
    # Migración automática: si estaba en texto plano, se guarda como hash.
    if isinstance(guardada, str) and not guardada.startswith("pbkdf2$"):
        datos["teachers"][usuario] = generar_hash_clave(clave)
        guardar_datos(datos)
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


# ----- Estudiantes -----

def agregar_estudiante(datos, seccion):
    """Agrega un estudiante a la sección."""
    nombre = input("Nombre: ").strip()
    cedula = input("Cédula: ").strip()
    if nombre == "" or cedula == "":
        print("Nombre y cédula son obligatorios.")
        return
    for est in seccion["estudiantes"]:
        if est["cedula"] == cedula:
            print("Ya existe un estudiante con esa cédula.")
            return
    seccion["estudiantes"].append({"nombre": nombre, "cedula": cedula, "notas": []})
    guardar_datos(datos)
    print("Estudiante agregado.")


def listar_estudiantes(seccion):
    """Muestra todos los estudiantes de la sección con sus notas y promedio."""
    if len(seccion["estudiantes"]) == 0:
        print("No hay estudiantes.")
        return
    print("\n--- Estudiantes de", seccion["nombre"], "---")
    for est in seccion["estudiantes"]:
        notas = est["notas"]
        if len(notas) == 0:
            prom = 0
        else:
            prom = sum(notas) / len(notas)
        print(" ", est["nombre"], "| Cédula:", est["cedula"], "| Notas:", notas, "| Promedio:", round(prom, 2))


def buscar_estudiante_por_cedula(datos):
    """Busca un estudiante por cédula en todas las secciones."""
    cedula = input("Cédula a buscar: ").strip()
    if cedula == "":
        return
    for sec in datos["sections"]:
        for est in sec["estudiantes"]:
            if est["cedula"] == cedula:
                print("\nNombre:", est["nombre"])
                print("Cédula:", est["cedula"])
                print("Sección:", sec["nombre"])
                print("Notas:", est["notas"])
                return
    print("No encontrado.")


def gestionar_notas(datos, seccion):
    """Menú para agregar, editar o eliminar notas de un estudiante."""
    cedula = input("Cédula del estudiante: ").strip()
    estudiante = None
    posicion = -1
    for i in range(len(seccion["estudiantes"])):
        if seccion["estudiantes"][i]["cedula"] == cedula:
            estudiante = seccion["estudiantes"][i]
            posicion = i
            break
    if estudiante is None:
        print("Estudiante no encontrado.")
        return
    # Usamos un objeto Estudiante para las operaciones
    est = Estudiante(estudiante["nombre"], estudiante["cedula"])
    est.notas = list(estudiante["notas"])
    while True:
        print("\n--- Notas de", est.nombre, "---")
        print("Actuales:", est.notas)
        print("1. Agregar nota")
        print("2. Editar nota")
        print("3. Eliminar nota")
        print("4. Volver")
        op = input("Opción: ").strip()
        if op == "1":
            nota = input("Nota (0-20): ").strip()
            if est.agregar_nota(nota):
                seccion["estudiantes"][posicion]["notas"] = est.notas
                guardar_datos(datos)
                print("Nota agregada.")
            else:
                print("Nota inválida.")
        elif op == "2":
            if len(est.notas) == 0:
                print("No hay notas.")
                continue
            for i in range(len(est.notas)):
                print(" ", i + 1, ":", est.notas[i])
            try:
                num = int(input("Número de nota a editar: "))
            except:
                print("Entrada inválida.")
                continue
            nueva = input("Nueva nota: ").strip()
            if est.editar_nota(num, nueva):
                seccion["estudiantes"][posicion]["notas"] = est.notas
                guardar_datos(datos)
                print("Nota actualizada.")
            else:
                print("Valor inválido.")
        elif op == "3":
            if len(est.notas) == 0:
                print("No hay notas.")
                continue
            for i in range(len(est.notas)):
                print(" ", i + 1, ":", est.notas[i])
            try:
                num = int(input("Número de nota a eliminar: "))
            except:
                print("Entrada inválida.")
                continue
            if est.eliminar_nota(num):
                seccion["estudiantes"][posicion]["notas"] = est.notas
                guardar_datos(datos)
                print("Nota eliminada.")
            else:
                print("Número inválido.")
        elif op == "4":
            break
        else:
            print("Opción no válida.")


def eliminar_estudiante(datos, seccion):
    """Elimina un estudiante de la sección."""
    cedula = input("Cédula del estudiante a eliminar: ").strip()
    for i in range(len(seccion["estudiantes"])):
        if seccion["estudiantes"][i]["cedula"] == cedula:
            seccion["estudiantes"].pop(i)
            guardar_datos(datos)
            print("Estudiante eliminado.")
            return
    print("No encontrado.")


def eliminar_seccion(datos, seccion, profesor):
    """Elimina la sección actual."""
    r = input("¿Eliminar esta sección? (s/n): ").strip().lower()
    if r != "s":
        return False
    nombre = seccion["nombre"]
    datos["sections"] = [
        sec for sec in datos["sections"]
        if not (sec["teacher"] == profesor and sec["nombre"] == nombre)
    ]
    guardar_datos(datos)
    print("Sección eliminada.")
    return True


# ----- Menú dentro de una sección (no vuelve a pedir la sección) -----

def menu_seccion_activa(datos, profesor, seccion):
    """Gestiona estudiantes y notas usando la sección ya seleccionada."""
    while True:
        print("\n==========", seccion["nombre"], "==========")
        print("1. Agregar estudiante")
        print("2. Listar estudiantes")
        print("3. Gestionar notas")
        print("4. Eliminar estudiante")
        print("5. Cambiar nombre de sección")
        print("6. Eliminar sección")
        print("0. Retroceder")
        op = input("Opción: ").strip()

        if op == "1":
            agregar_estudiante(datos, seccion)
        elif op == "2":
            listar_estudiantes(seccion)
        elif op == "3":
            gestionar_notas(datos, seccion)
        elif op == "4":
            eliminar_estudiante(datos, seccion)
        elif op == "5":
            nuevo = input("Nuevo nombre: ").strip()
            if nuevo != "":
                seccion["nombre"] = nuevo
                guardar_datos(datos)
                print("Nombre actualizado.")
        elif op == "6":
            eliminado = eliminar_seccion(datos, seccion, profesor)
            if eliminado:
                return
        elif op == "0":
            return
        else:
            print("Opción no válida.")


# ----- Menú Mis Secciones -----

def menu_mis_secciones(datos, profesor):
    """Muestra las secciones del profesor y permite seleccionar una."""
    while True:
        secciones = obtener_secciones(datos, profesor)
        print("\n========== MIS SECCIONES ==========")

        if len(secciones) == 0:
            print("No tienes secciones.")
            print("1. Crear sección")
            print("0. Retroceder")
            op = input("Opción: ").strip()
            if op == "1":
                crear_seccion(datos, profesor)
            elif op == "0":
                return
            else:
                print("Opción no válida.")
            continue

        for i in range(len(secciones)):
            print(i + 1, ".", secciones[i]["nombre"])
        print(len(secciones) + 1, ". Crear nueva sección")
        print("0. Retroceder")

        op = input("Opción: ").strip()
        if op == "0":
            return
        if not op.isdigit():
            print("Opción no válida.")
            continue

        num = int(op)
        if 1 <= num <= len(secciones):
            menu_seccion_activa(datos, profesor, secciones[num - 1])
        elif num == len(secciones) + 1:
            crear_seccion(datos, profesor)
        else:
            print("Opción no válida.")


# ----- Menú principal -----

def menu_principal(datos, profesor):
    """Menú principal después de iniciar sesión."""
    while True:
        print("\n========== SISTEMA ACADÉMICO ==========")
        print("1. Mis Secciones")
        print("2. Buscar estudiante por cédula")
        print("3. Crear sección")
        print("4. Cerrar sesión")
        op = input("Opción: ").strip()

        if op == "1":
            menu_mis_secciones(datos, profesor)
        elif op == "2":
            buscar_estudiante_por_cedula(datos)
        elif op == "3":
            crear_seccion(datos, profesor)
        elif op == "4":
            return
        else:
            print("Opción no válida.")


def main():
    """Punto de entrada."""
    print("Sistema de Gestión Académica")
    print("Datos en:", ARCHIVO)
    datos = cargar_datos()

    while True:
        print("\n--- Inicio ---")
        print("1. Iniciar sesión")
        print("2. Registrarse")
        print("3. Salir")
        op = input("Opción: ").strip()

        if op == "1":
            profesor = iniciar_sesion(datos)
            if profesor is not None:
                print("Bienvenido,", profesor)
                menu_principal(datos, profesor)
        elif op == "2":
            registrar(datos)
        elif op == "3":
            print("Hasta pronto.")
            break
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    main()
