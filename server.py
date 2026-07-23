import http.server
import socketserver
import urllib.request
import csv
import json
import io

PORT = 8000
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ0vxe6GbEKkdwiHAHtg0pPBFO2aZqvo7Yki_ZSe0RxtDEeBHTYgRXzRgGhRHyUGfZZsNrDjHFmzDdu/pub?gid=0&single=true&output=csv"

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/datos':
            try:
                # 1. Petición directa desde Python a Google Sheets
                req = urllib.request.Request(
                    SHEET_CSV_URL, 
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                with urllib.request.urlopen(req) as response:
                    csv_text = response.read().decode('utf-8')
                
                # 2. Convertir CSV a JSON estructurado
                f = io.StringIO(csv_text)
                reader = csv.DictReader(f)
                filas = [row for row in reader]

                # 3. Responder al navegador sin bloqueos ni CORS
                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(filas, ensure_ascii=False).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode('utf-8'))
        else:
            # Servir archivos HTML/imágenes normles
            super().do_GET()

print(f"Servidor corriendo en http://localhost:{PORT}")
with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
    httpd.serve_forever()