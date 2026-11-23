import hashlib
import hmac
import os
import re

from .errores import error_validacion
from .tabla_hash import tabla_hash

rol_estudiante = "estudiante"
rol_monitor = "monitor"
rol_administrador = "administrador"
roles = [rol_estudiante, rol_monitor, rol_administrador]
iteraciones = 120000
maximo_intentos = 3
largo_minimo_clave = 8


def normalizar_usuario(usuario):
    if not isinstance(usuario, str) or re.fullmatch(r"[A-Za-z0-9._-]{3,20}", usuario.strip()) is None:
        raise error_validacion("el usuario debe tener de 3 a 20 caracteres: letras, numeros, punto, guion o guion bajo")
    return usuario.strip().lower()


def revisar_clave(contrasena):
    if not isinstance(contrasena, str) or len(contrasena) < largo_minimo_clave:
        raise error_validacion(f"la contrasena debe tener al menos {largo_minimo_clave} caracteres")
    if contrasena.strip() != contrasena or " " in contrasena:
        raise error_validacion("la contrasena no puede tener espacios")
    return contrasena


def calcular_hash(contrasena, sal_hex):
    return hashlib.pbkdf2_hmac("sha256", contrasena.encode("utf-8"), bytes.fromhex(sal_hex), iteraciones).hex()


class clase_cuenta:

    def __init__(self, usuario, nombre, rol, codigo_persona, sal, clave_hash, intentos=0, bloqueada=False):
        if rol not in roles:
            raise error_validacion("rol invalido: '" + str(rol) + "'")
        self.usuario = usuario
        self.nombre = nombre
        self.rol = rol
        self.codigo_persona = codigo_persona
        self.sal = sal
        self.clave_hash = clave_hash
        self.intentos = intentos
        self.bloqueada = bloqueada

    def poner_clave(self, contrasena):
        self.sal = os.urandom(16).hex()
        self.clave_hash = calcular_hash(revisar_clave(contrasena), self.sal)
        self.intentos = 0
        self.bloqueada = False

    def clave_correcta(self, contrasena):
        if not isinstance(contrasena, str):
            return False
        return hmac.compare_digest(calcular_hash(contrasena, self.sal), self.clave_hash)


class registro_cuentas:

    def __init__(self):
        self.tabla = tabla_hash()

    def __len__(self):
        return len(self.tabla)

    def existe(self, usuario):
        return self.tabla.contiene(normalizar_usuario(usuario))

    def obtener(self, usuario):
        return self.tabla.obtener(normalizar_usuario(usuario))

    def revisar_disponible(self, usuario, contrasena):
        clave = normalizar_usuario(usuario)
        if self.tabla.contiene(clave):
            raise error_validacion("el usuario '" + clave + "' ya existe")
        revisar_clave(contrasena)
        return clave

    def crear(self, usuario, contrasena, nombre, rol, codigo_persona=None):
        clave = self.revisar_disponible(usuario, contrasena)
        if rol != rol_administrador and codigo_persona is None:
            raise error_validacion("la cuenta de " + rol + " debe estar ligada a una persona registrada")
        cuenta = clase_cuenta(clave, nombre, rol, codigo_persona, "00", "")
        cuenta.poner_clave(contrasena)
        self.tabla.poner(clave, cuenta)
        return cuenta

    def agregar_existente(self, cuenta):
        self.tabla.poner(cuenta.usuario, cuenta)

    def iniciar_sesion(self, usuario, contrasena):
        mensaje = "usuario o contrasena incorrectos"
        try:
            cuenta = self.obtener(usuario)
        except error_validacion:
            raise error_validacion(mensaje)
        if cuenta is None:
            raise error_validacion(mensaje)
        if cuenta.bloqueada:
            raise error_validacion("la cuenta esta bloqueada por intentos fallidos; pida al administrador que la desbloquee")
        if not cuenta.clave_correcta(contrasena):
            cuenta.intentos += 1
            if cuenta.intentos >= maximo_intentos:
                cuenta.bloqueada = True
                raise error_validacion("demasiados intentos fallidos: la cuenta quedo bloqueada")
            raise error_validacion(mensaje + f" (le quedan {maximo_intentos - cuenta.intentos} intentos)")
        cuenta.intentos = 0
        return cuenta

    def cambiar_clave(self, usuario, actual, nueva):
        cuenta = self.obtener(usuario)
        if cuenta is None or not cuenta.clave_correcta(actual):
            raise error_validacion("la contrasena actual no es correcta")
        cuenta.poner_clave(nueva)

    def restablecer_clave(self, usuario, nueva):
        cuenta = self.obtener(usuario)
        if cuenta is None:
            raise error_validacion("no existe el usuario '" + str(usuario) + "'")
        cuenta.poner_clave(nueva)

    def desbloquear(self, usuario):
        cuenta = self.obtener(usuario)
        if cuenta is None:
            raise error_validacion("no existe el usuario '" + str(usuario) + "'")
        cuenta.bloqueada = False
        cuenta.intentos = 0

    def de_persona(self, codigo_persona):
        for cuenta in self.tabla.valores():
            if cuenta.codigo_persona == codigo_persona:
                return cuenta
        return None

    def contar_administradores(self):
        return len([c for c in self.tabla.valores() if c.rol == rol_administrador])

    def todas(self):
        return sorted(self.tabla.valores(), key=lambda c: (roles.index(c.rol), c.usuario))
