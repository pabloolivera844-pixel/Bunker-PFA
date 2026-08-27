import sys
import json
import os
from datetime import datetime

class SistemaDIFOficial:
    def __init__(self):
        self.log_file = "dfi_secops.log"
        self.db_file = "dfi_agentes.json"
        self.cargar_base_datos()

    def cargar_base_datos(self):
        if os.path.exists(self.db_file):
            with open(self.db_file, "r", encoding="utf-8") as f:
                self.base_datos = json.load(f)
        else:
            # Base institucional dividida: Superioridad PFA y Núcleo D.I.F.
            self.base_datos = {
                "oficiales_pfa": [
                    {
                        "id": "PFA-001", 
                        "nombre": "Alexis", 
                        "rango": "Comisario General", 
                        "acceso": "Total_Alto", 
                        "llave": "key_alexis_cg2026",
                        "intentos_fallidos": 0,
                        "bloqueado": False
                    },
                    {
                        "id": "PFA-002", 
                        "nombre": "Joel", 
                        "rango": "Comisario", 
                        "acceso": "Parcial_Jerarquico", 
                        "llave": "key_joel_com2026",
                        "intentos_fallidos": 0,
                        "bloqueado": False
                    },
                    {
                        "id": "DIF-001", 
                        "nombre": "Pablo", 
                        "rango": "Director D.I.F.", 
                        "acceso": "Master_Total", 
                        "llave": "llave_maestra_dfi",
                        "intentos_fallidos": 0,
                        "bloqueado": False
                    }
                ],
                "flota_pfa": [
                    {"unidad": "Móvil PFA-12", "estado": "Patrulla Urbana", "jurisdiccion": "Puerto Madero"}
                ],
                "archivos_desclasificados": [
                    {"doc_id": "EXP-2026-01", "titulo": "Directiva General de Custodia Transversal", "formato": "PDF"}
                ]
            }
            self.guardar_base_datos()

    def guardar_base_datos(self):
        with open(self.db_file, "w", encoding="utf-8") as f:
            json.dump(self.base_datos, f, indent=4, ensure_ascii=False)

    def registrar_log(self, mensaje):
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"{timestamp} {mensaje}\n")

    def autenticar_usuario(self, usuario, token_llave):
        for p in self.base_datos["oficiales_pfa"]:
            if p["nombre"].lower() == usuario.lower():
                if p["bloqueado"]:
                    self.registrar_log(f"[ALERTA INTRUSIÓN] Intento en cuenta BLOQUEADA: {p['nombre']}")
                    print("\n[X] ACCIÓN BLOQUEADA: Cuenta suspendida por seguridad de la Central.")
                    return None
                
                if p["llave"] == token_llave:
                    p["intentos_fallidos"] = 0
                    self.guardar_base_datos()
                    self.registrar_log(f"[LOGIN EXITOSO] {p['rango']} - {p['nombre']}")
                    return p
                else:
                    p["intentos_fallidos"] += 1
                    self.guardar_base_datos()
                    self.registrar_log(f"[FALLO SEGURIDAD] Credencial errónea para {p['nombre']} ({p['intentos_fallidos']}/3)")
                    
                    if p["intentos_fallidos"] >= 3:
                        p["bloqueado"] = True
                        self.guardar_base_datos()
                        print(f"\n[!] ¡ALERTA CENTRAL D.I.F.! Cuenta de {p['nombre']} bloqueada por seguridad.")
                    return None
        self.registrar_log(f"[ALERTA] Usuario no autorizado intentó acceso: '{usuario}'")
        return None

    def mostrar_menu(self, perfil):
        while True:
            print(f"\n==================================================")
            print(f"   DEPARTAMENTO FEDERAL DE INVESTIGACIÓN (D.I.F.)")
            print(f"   Usuario: {perfil['nombre']} | Rango: {perfil['rango']}")
            print(f"==================================================")
            print("1. Consultar legajos y Flota PFA")
            print("2. Repositorio de Archivos y Descargas (PDF)")
            
            if perfil["acceso"] in ["Master_Total", "Total_Alto", "Parcial_Jerarquico"]:
                print("3. Bitácora de Novedades e Incidencias")
                print("4. Rastreador Táctico de Unidades")
            
            if perfil["acceso"] == "Master_Total":
                print("5. Subir Nuevo Expediente / Documento PDF")
                print("6. Panel Maestro de Auditoría Forense (Director)")
                print("7. Cerrar Sesión / Salir")
            else:
                print("5. Cerrar Sesión / Salir")
            
            opcion = input("\nSeleccione una opción táctica: ")
            
            if opcion == "1":
                print("\n--- DIRECTORIO Y FLOTA PFA ---")
                for f in self.base_datos["flota_pfa"]:
                    print(f"- {f['unidad']} | Estado: {f['estado']} | Zona: {f['jurisdiccion']}")
            elif opcion == "2":
                print("\n--- REPOSITORIO DE ARCHIVOS OFICIALES (ESTILO FBI) ---")
                for doc in self.base_datos["archivos_desclasificados"]:
                    print(f"[📄] {doc['doc_id']} - {doc['titulo']} ({doc['formato']})")
                print("\n[i] (En el Paso Web podrá descargarlos directamente con un clic)")
            elif opcion == "3" and perfil["acceso"] in ["Master_Total", "Total_Alto", "Parcial_Jerarquico"]:
                print("\n[+] Abriendo bitácora de novedades...")
            elif opcion == "4" and perfil["acceso"] in ["Master_Total", "Total_Alto", "Parcial_Jerarquico"]:
                print("\n[+] Activando rastreador táctico...")
            elif opcion == "5" and perfil["acceso"] == "Master_Total":
                titulo_doc = input("Ingrese título del nuevo expediente PDF a subir: ")
                nuevo_doc = {"doc_id": f"EXP-2026-{len(self.base_datos['archivos_desclasificados'])+1:02d}", "titulo": titulo_doc, "formato": "PDF"}
                self.base_datos["archivos_desclasificados"].append(nuevo_doc)
                self.guardar_base_datos()
                self.registrar_log(f"[EXPEDIENTE NUEVO] Director subió el documento: {titulo_doc}")
                print(f"\n[✓] Expediente cargado y disponible para descarga en la red.")
            elif opcion == "6" and perfil["acceso"] == "Master_Total":
                print("\n--- AUDITORÍA FORENSE DE REGISTROS ---")
                if os.path.exists(self.log_file):
                    with open(self.log_file, "r", encoding="utf-8") as f:
                        print(f.read())
                else:
                    print("[i] Sin registros de auditoría.")
            elif (opcion == "7" and perfil["acceso"] == "Master_Total") or (opcion == "5" and perfil["acceso"] != "Master_Total"):
                self.registrar_log(f"[LOGOUT] {perfil['nombre']} cerró sesión.")
                print(f"\n[x] Sesión cerrada.")
                break
            else:
                print("\n[!] Opción inválida o privilegios insuficientes.")

if __name__ == "__main__":
    app = SistemaDIFOficial()
    print("=== AUTENTICACIÓN REQUERIDA (CENTRAL D.I.F.) ===")
    ingreso_usuario = input("Ingrese nombre de usuario: ")
    ingreso_llave = input("Ingrese token / llave de seguridad: ")
    
    usuario_actual = app.autenticar_usuario(ingreso_usuario, ingreso_llave)
    
    if usuario_actual:
        print(f"\n[✓] Acceso concedido.")
        app.mostrar_menu(usuario_actual)
    else:
        print("\n[X] ACCESO DENEGADO.")
        sys.exit(1)

