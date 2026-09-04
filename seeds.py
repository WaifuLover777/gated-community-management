from datetime import datetime, date, timedelta
from extensions import db
from models import Usuario, Casa, Residente, Vehiculo, Cuota, Visita, Comunicado

def seed_datos():
    if Usuario.query.first():
        print("Ya existen datos. Se aborta el seed para no duplicar.")
        return

    casas_def = [
        ("A-01", "A", 120.0, 45.00, "villa", "Blanco"),
        ("A-02", "A", 110.0, 42.00, "casa", "Beige"),
        ("A-03", "A", 130.0, 50.00, "villa", "Terracota"),
        ("B-01", "B", 150.0, 58.00, "adosada", "Gris"),
        ("B-02", "B", 140.0, 54.00, "casa", "Celeste"),
        ("B-03", "B", 125.0, 48.00, "departamento", "Arena"),
    ]
    casas = []
    for numero, manzana, area, alicuota, tipo, color in casas_def:
        c = Casa(numero=numero, manzana=manzana, area_m2=area, alicuota=alicuota,
                 tipo=tipo, color=color, capacidad=5, personas=3)
        db.session.add(c)
        casas.append(c)
    db.session.flush()

    casas[5].pin_registro = "654321"

    admin = Usuario(nombre="Administrador", email="admin@urb.com", rol="admin")
    admin.set_password("admin123")
    guardia = Usuario(nombre="Guardia Principal", email="guardia@urb.com", rol="guardia")
    guardia.set_password("guardia123")
    db.session.add_all([admin, guardia])

    residentes_def = [
        ("María Cevallos", "0912345678", "0991111111", "propietario", 0),
        ("Carlos Andrade", "0923456789", "0992222222", "propietario", 1),
        ("Lucía Mendoza", "0934567890", "0993333333", "propietario", 2),
        ("Jorge Vera", "0945678901", "0994444444", "propietario", 3),
        ("Ana Suárez", "0956789012", "0995555555", "propietario", 4),

    ]
    residentes = []
    for nombre, cedula, tel, tipo, idx in residentes_def:
        r = Residente(
            casa_id=casas[idx].id, nombre=nombre, cedula=cedula, telefono=tel,
            email=nombre.lower().replace(" ", ".") + "@correo.com",
            tipo=tipo, fecha_ingreso=date.today() - timedelta(days=200),
        )
        db.session.add(r)
        residentes.append(r)
    db.session.flush()

    u_res = Usuario(nombre=residentes[0].nombre, email="residente@urb.com",
                    rol="residente", residente_id=residentes[0].id)
    u_res.set_password("residente123")
    db.session.add(u_res)

    vehiculos_def = [
        (0, "GYA-1234", "Toyota", "Corolla", "Blanco"),
        (1, "GSB-5678", "Chevrolet", "Aveo", "Gris"),
        (2, "GTC-9012", "Kia", "Sportage", "Negro"),
        (3, "GYD-3456", "Hyundai", "Tucson", "Rojo"),
        (4, "GSE-7890", "Mazda", "CX-5", "Azul"),
    ]
    for idx, placa, marca, modelo, color in vehiculos_def:
        db.session.add(Vehiculo(residente_id=residentes[idx].id, placa=placa,
                                marca=marca, modelo=modelo, color=color))

    hoy = date.today()
    for casa in casas:
        db.session.add(Cuota(casa_id=casa.id, mes=2, anio=2026, monto=casa.alicuota,
                             estado="pagado", fecha_pago=str(hoy - timedelta(days=88)),
                             metodo_pago="transferencia"))

        db.session.add(Cuota(casa_id=casa.id, mes=3, anio=2026, monto=casa.alicuota,
                             estado="pagado", fecha_pago=str(hoy - timedelta(days=58)),
                             metodo_pago="transferencia"))

        estado_abril = "pagado" if casa.id % 2 == 0 else "vencido"
        if estado_abril == "pagado":
            db.session.add(Cuota(casa_id=casa.id, mes=4, anio=2026, monto=casa.alicuota,
                                 estado="pagado", fecha_pago=str(hoy - timedelta(days=28)),
                                 metodo_pago="efectivo"))
        else:
            db.session.add(Cuota(casa_id=casa.id, mes=4, anio=2026, monto=casa.alicuota,
                                 estado="vencido"))

        if casa.id <= 2:
            db.session.add(Cuota(casa_id=casa.id, mes=5, anio=2026, monto=casa.alicuota,
                                 estado="pagado", fecha_pago=str(hoy - timedelta(days=5)),
                                 metodo_pago="efectivo"))
        elif casa.id == 3:
            db.session.add(Cuota(casa_id=casa.id, mes=5, anio=2026, monto=casa.alicuota,
                                 estado="en_revision", metodo_pago="transferencia"))
        else:
            db.session.add(Cuota(casa_id=casa.id, mes=5, anio=2026, monto=casa.alicuota,
                                 estado="pendiente"))

        db.session.add(Cuota(casa_id=casa.id, mes=6, anio=2026, monto=casa.alicuota,
                             estado="pendiente"))

        db.session.add(Cuota(casa_id=casa.id, mes=7, anio=2026, monto=casa.alicuota,
                             estado="pendiente"))

        db.session.add(Cuota(casa_id=casa.id, mes=6, anio=2026, monto=25.00,
                             tipo="extraordinaria", concepto="Reparación de piscina",
                             estado="pendiente"))

    visitas_def = [
        (0, "Roberto Paz", "0911111111", "Familiar", "PQR-1122", "111111", residentes[0].nombre),
        (1, "Sofía Loor", "0922222222", "Delivery", "", "222222", residentes[1].nombre),
        (3, "Técnico Claro", "0933333333", "Mantenimiento", "XYZ-9988", "333333", residentes[3].nombre),
    ]
    for idx, nombre, cedula, motivo, placa, pin, autorizado_por in visitas_def:
        db.session.add(Visita(
            casa_id=casas[idx].id, nombre_visitante=nombre, cedula_visitante=cedula,
            motivo=motivo, placa_vehiculo=placa, estado="pendiente",
            autorizado_por=autorizado_por, pin=pin,
        ))

    comunicados_def = [
        ("Corte de agua programado", "El día sábado habrá corte de agua de 8h00 a 12h00.", "urgente"),
        ("Asamblea de copropietarios", "Se convoca a asamblea general el próximo viernes.", "circular"),
        ("Mantenimiento de áreas verdes", "Esta semana se realizará poda de jardines.", "anuncio"),
    ]
    for titulo, contenido, tipo in comunicados_def:
        db.session.add(Comunicado(titulo=titulo, contenido=contenido, tipo=tipo,
                                  publicado_por="Administrador"))

    db.session.commit()
    print(f"   Casas: {len(casas)} | Residentes: {len(residentes)} | "
          f"Vehículos: {len(vehiculos_def)} | Comunicados: {len(comunicados_def)}")
