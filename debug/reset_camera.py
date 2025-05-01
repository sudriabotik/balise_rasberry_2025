import os
import subprocess
import signal

def list_video_devices():
    result = subprocess.run(['ls', '/dev/video*'], capture_output=True, text=True, shell=True)
    print("Caméras détectées :", result.stdout.strip())

def find_processes_using_cameras():
    result = subprocess.run("lsof /dev/video* 2>/dev/null", capture_output=True, text=True, shell=True)
    lines = result.stdout.strip().split('\n')[1:]  # ignore header
    pids = set()
    for line in lines:
        parts = line.split()
        if len(parts) >= 2:
            pid = parts[1]
            pids.add(pid)
    return pids

def kill_processes(pids):
    for pid in pids:
        try:
            os.kill(int(pid), signal.SIGKILL)
            print(f"Processus {pid} tué")
        except Exception as e:
            print(f"Erreur en tuant {pid} : {e}")

def reload_udev():
    subprocess.run(["sudo", "udevadm", "control", "--reload"])
    subprocess.run(["sudo", "udevadm", "trigger"])
    print("udev rechargé")

if __name__ == "__main__":
    print("🔍 Détection des caméras...")
    list_video_devices()

    print("🔍 Recherche des processus utilisant les caméras...")
    pids = find_processes_using_cameras()

    if pids:
        print("⚠️ Processus trouvés : ", pids)
        kill_processes(pids)
    else:
        print("✅ Aucun processus ne bloque les caméras")

    print("🔁 Rechargement des règles udev...")
    reload_udev()

    print("✅ Caméras potentiellement débloquées. Tu peux relancer ton script principal.")
