import socket
import time
import subprocess

def send_string_to_vm(cmd):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect('/var/tmp/qemu-monitor.sock')
    time.sleep(0.1)
    s.recv(1024)
    for c in cmd:
        if c == ';': s.sendall(b'sendkey semicolon\n')
        elif c == ' ': s.sendall(b'sendkey spc\n')
        elif c == '-': s.sendall(b'sendkey minus\n')
        elif c == '|': s.sendall(b'sendkey shift-backslash\n')
        elif c == '"': s.sendall(b'sendkey shift-apostrophe\n')
        elif c == '.': s.sendall(b'sendkey dot\n')
        elif c == '/': s.sendall(b'sendkey slash\n')
        elif c == '$': s.sendall(b'sendkey shift-4\n')
        elif c == '>': s.sendall(b'sendkey shift-dot\n')
        elif c == '_': s.sendall(b'sendkey shift-minus\n')
        elif c == '=': s.sendall(b'sendkey equal\n')
        elif c == ',': s.sendall(b'sendkey comma\n')
        elif c == ':': s.sendall(b'sendkey shift-semicolon\n')
        elif c == '*': s.sendall(b'sendkey shift-8\n')
        elif c == '&': s.sendall(b'sendkey shift-7\n')
        elif c == '@': s.sendall(b'sendkey shift-2\n')
        elif c.isupper(): s.sendall(f'sendkey shift-{c.lower()}\n'.encode())
        else: s.sendall(f'sendkey {c}\n'.encode())
        time.sleep(0.02)
    s.sendall(b'sendkey ret\n')
    time.sleep(0.5)
    s.close()

def screendump_and_ocr(out_ppm='/tmp/vm_restart_screen.ppm'):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect('/var/tmp/qemu-monitor.sock')
    time.sleep(0.1)
    s.recv(1024)
    s.sendall(f'screendump {out_ppm}\n'.encode())
    time.sleep(0.5)
    s.close()
    png_path = out_ppm.replace('.ppm', '.png')
    subprocess.run(['ffmpeg', '-y', '-i', out_ppm, png_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    res = subprocess.run(['tesseract', png_path, 'stdout', '--psm', '6'], capture_output=True, text=True)
    return res.stdout, png_path

if __name__ == '__main__':
    # Kill quickshell intentionally
    cmd = 'clear; killall -9 quickshell; sleep 2; su - horizon -c "export XDG_RUNTIME_DIR=/run/user/1000; systemctl --user status caelestia-shell --no-pager; pgrep -a kwin_wayland; pgrep -a plasmashell"'
    send_string_to_vm(cmd)
    time.sleep(3.0)

    text, png = screendump_and_ocr('/tmp/caelestia_kill_test.ppm')
    print("=== KILL TEST RESULT ===")
    print(text)
    print("========================")
