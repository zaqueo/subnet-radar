from flask import Flask, render_template_string, jsonify, request
import platform
import subprocess
import concurrent.futures
import ipaddress

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ixtanet - Escaner de Red</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f4f7f6; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .navbar { background-color: #0d6efd; }
        .card { box-shadow: 0 4px 12px rgba(0,0,0,0.1); border-radius: 12px; border: none; }
        .badge-activo { background-color: #ff8c00; }
        .info-badge { font-size: 0.85rem; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark mb-5 shadow-sm">
        <div class="container">
            <span class="navbar-brand mb-0 h1 fw-bold">Herramientas de Red - Ixtanet</span>
        </div>
    </nav>

    <div class="container">
        <div class="card p-4 mx-auto" style="max-width: 640px;">
            <h4 class="text-center mb-4 text-secondary">Escaner de Subred Remota</h4>

            <div class="mb-3">
                <label class="form-label fw-bold">Direccion de Red Base:</label>
                <input type="text" class="form-control form-control-lg text-center" id="ipBase" value="192.168.1.0" placeholder="Ej: 192.168.1.0">
            </div>

            <div class="mb-3">
                <label class="form-label fw-bold">Mascara de subred (CIDR):</label>
                <select class="form-select form-select-lg" id="mascara" onchange="actualizarInfo()">
                    <option value="30">/30 - 2 hosts</option>
                    <option value="29">/29 - 6 hosts</option>
                    <option value="28">/28 - 14 hosts</option>
                    <option value="27">/27 - 30 hosts</option>
                    <option value="26">/26 - 62 hosts</option>
                    <option value="25">/25 - 126 hosts</option>
                    <option value="24" selected>/24 - 254 hosts</option>
                    <option value="23">/23 - 510 hosts</option>
                    <option value="22">/22 - 1.022 hosts</option>
                    <option value="21">/21 - 2.046 hosts</option>
                    <option value="20">/20 - 4.094 hosts</option>
                    <option value="19">/19 - 8.190 hosts</option>
                    <option value="18">/18 - 16.382 hosts</option>
                    <option value="17">/17 - 32.766 hosts</option>
                    <option value="16">/16 - 65.534 hosts</option>
                </select>
            </div>

            <div id="infoSubred" class="alert alert-info py-2 text-center info-badge mb-3">
                Se escanearan <strong>254 IPs</strong> - tiempo estimado: <strong>~15 seg</strong>
            </div>

            <div id="alertaGrande" class="alert alert-warning py-2 text-center info-badge mb-3 d-none">
                Redes grandes pueden tardar varios minutos. Asegurate de estar conectado a la red local.
            </div>

            <button id="btnEscanear" class="btn btn-primary btn-lg w-100 mb-4" onclick="iniciarEscaneo()">
                Escanear Red Ahora
            </button>

            <div id="loading" class="text-center d-none mb-4">
                <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;"></div>
                <p id="loadingMsg" class="mt-3 text-muted fw-bold">Escaneando, por favor espera...</p>
            </div>

            <ul id="resultados" class="list-group list-group-flush"></ul>
        </div>
    </div>

    <script>
        const hostsXMascara = {
            30: 2, 29: 6, 28: 14, 27: 30, 26: 62, 25: 126,
            24: 254, 23: 510, 22: 1022, 21: 2046, 20: 4094,
            19: 8190, 18: 16382, 17: 32766, 16: 65534
        };

        function actualizarInfo() {
            const mascara = parseInt(document.getElementById('mascara').value);
            const hosts = hostsXMascara[mascara];
            const segs = Math.max(5, Math.round(hosts / 17));
            const tiempo = segs >= 60 ? '~' + Math.round(segs / 60) + ' min' : '~' + segs + ' seg';
            document.getElementById('infoSubred').innerHTML =
                'Se escanearan <strong>' + hosts.toLocaleString('es') + ' IPs</strong> - tiempo estimado: <strong>' + tiempo + '</strong>';
            document.getElementById('alertaGrande').classList.toggle('d-none', mascara >= 22);
        }

        async function iniciarEscaneo() {
            const ipBase = document.getElementById('ipBase').value.trim();
            const mascara = document.getElementById('mascara').value;
            const subred = ipBase + '/' + mascara;
            const btn = document.getElementById('btnEscanear');
            const loading = document.getElementById('loading');
            const resultados = document.getElementById('resultados');
            const hosts = hostsXMascara[parseInt(mascara)];

            document.getElementById('loadingMsg').textContent =
                'Haciendo ping a ' + hosts.toLocaleString('es') + ' IPs, por favor espera...';

            btn.disabled = true;
            loading.classList.remove('d-none');
            resultados.innerHTML = '';

            try {
                const response = await fetch('/escanear', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ subred: subred })
                });
                const data = await response.json();

                if (data.error) {
                    resultados.innerHTML = '<li class="list-group-item text-danger text-center fw-bold">' + data.error + '</li>';
                } else if (data.ips.length === 0) {
                    resultados.innerHTML = '<li class="list-group-item text-danger text-center fw-bold">No se encontraron equipos activos.</li>';
                } else {
                    resultados.innerHTML = '<li class="list-group-item text-success text-center fw-bold mb-1">' +
                        data.ips.length + ' equipo(s) detectado(s) en ' + subred + '</li>';
                    data.ips.forEach(ip => {
                        resultados.innerHTML +=
                            '<li class="list-group-item d-flex justify-content-between align-items-center fs-5">' +
                            '<a href="http://' + ip + '" target="_blank" class="text-decoration-none text-dark">' + ip + '</a>' +
                            '<span class="badge badge-activo rounded-pill">Detectado</span></li>';
                    });
                }
            } catch (error) {
                resultados.innerHTML = '<li class="list-group-item text-danger text-center">Error de conexion con el servidor local.</li>';
            } finally {
                btn.disabled = false;
                loading.classList.add('d-none');
            }
        }

        actualizarInfo();
    </script>
</body>
</html>
"""

def hacer_ping(ip_str):
    parametro = '-n' if platform.system().lower() == 'windows' else '-c'
    param_timeout = '-w' if platform.system().lower() == 'windows' else '-W'
    val_timeout = '1000' if platform.system().lower() == 'windows' else '1'
    comando = ['ping', parametro, '1', param_timeout, val_timeout, ip_str]
    try:
        salida = subprocess.run(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=2)
        if salida.returncode == 0:
            return ip_str, True
    except subprocess.TimeoutExpired:
        pass
    return ip_str, False

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/escanear', methods=['POST'])
def escanear():
    datos = request.get_json()
    subred = datos.get('subred', '192.168.1.0/24')
    ips_activas = []
    try:
        red = ipaddress.IPv4Network(subred, strict=False)
        ips_a_escanear = [str(ip) for ip in red.hosts()]
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as ejecutor:
            resultados = ejecutor.map(hacer_ping, ips_a_escanear)
            for ip, activa in resultados:
                if activa:
                    ips_activas.append(ip)
    except ValueError:
        return jsonify({'error': 'Subred invalida'}), 400
    return jsonify({'ips': ips_activas})

if __name__ == '__main__':
    print("Servidor iniciado. Abre: http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000)