import socket
import time
import subprocess

def send_keys_to_vm(keys, delay=0.03):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect('/var/tmp/qemu-monitor.sock')
    time.sleep(0.1)
    s.recv(1024)
    for k in keys:
        s.sendall(f'sendkey {k}\n'.encode())
        time.sleep(delay)
    time.sleep(0.5)
    s.close()

def screendump_and_save(out_ppm='/tmp/vm_screen.ppm', dest_png=None):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect('/var/tmp/qemu-monitor.sock')
    time.sleep(0.1)
    s.recv(1024)
    s.sendall(f'screendump {out_ppm}\n'.encode())
    time.sleep(0.5)
    s.close()
    if dest_png:
        subprocess.run(['ffmpeg', '-y', '-i', out_ppm, dest_png], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Saved {dest_png}")

if __name__ == '__main__':
    send_keys_to_vm(['ctrl-alt-f1'], delay=0.2)
    time.sleep(1.0)
    screendump_and_save('/tmp/desktop_after_restart.ppm', '/mnt/c/Users/gaumi/.gemini/antigravity/brain/d5ddc0d8-4760-40cc-9d68-0284d41cf543/desktop_after_restart.png')
