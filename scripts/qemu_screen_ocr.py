import socket
import subprocess
import os

sock_path = '/var/tmp/qemu-monitor.sock'
ppm_path = '/var/tmp/cur-screen.ppm'
png_path = '/var/tmp/cur-screen.png'

s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.connect(sock_path)
s.recv(1024)
s.sendall(f'screendump {ppm_path}\n'.encode())
s.recv(1024)
s.close()

subprocess.run(['ffmpeg', '-y', '-i', ppm_path, png_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
res = subprocess.run(['tesseract', png_path, 'stdout', '--psm', '6'], capture_output=True, text=True)
print("=== OCR SCREEN DUMP ===")
print(res.stdout)
print("=======================")
