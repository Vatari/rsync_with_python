import subprocess
import os
from datetime import datetime

# ДАННИ ЗА HOST, USER, PASSWORD, PORT AND REMOTE RSYNC PATH
local_folder = ""
remote_folder = ""
remote_host = ""
username = ""
password = ""
port = 22
rsync_path = "/usr/bin/rsync" # Това е важно за различните дистрибуции, но обикновено е в /usr/bin/rsync
keep_last_n = 2

# sshpass трябва да се инсталира предварително
# БЕКЪП С ВЕРСИИ
def create_versioned_backup(local_folder, remote_folder, remote_host, username, password, port=22,
                            rsync_path="/usr/bin/rsync", keep_last_n=5):
    if not local_folder.endswith('/'): # Ако OS е Windows
        local_folder += '/'

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    versioned_remote_folder = os.path.join(remote_folder, f"backup_{timestamp}")

    rsync_command = [
        "sshpass", "-p", password,
        "rsync",
        "-avz",
        "--rsync-path", rsync_path,
        "-e", f"ssh -p {port}",
        local_folder,
        f"{username}@{remote_host}:{versioned_remote_folder}"
    ]

    try:
        result = subprocess.run(rsync_command, check=True, text=True, capture_output=True)
        print("Backup completed successfully.")
        print(result.stdout)

        cleanup_old_backups(remote_folder, remote_host, username, password, port, keep_last_n)

    except subprocess.CalledProcessError as e:
        print("An error occurred during the rsync backup:")
        print(e.stderr)

# ИЗТРИВАНЕ НА СТАРИТЕ БЕКЪПИ
def cleanup_old_backups(remote_folder, remote_host, username, password, port, keep_last_n):
    ssh_command = [
        "sshpass", "-p", password,
        "ssh", f"{username}@{remote_host}", "-p", str(port),
        f"ls -1dt {remote_folder}/backup_* | tail -n +{keep_last_n + 1} | xargs rm -rf"
    ]

    try:
        result = subprocess.run(ssh_command, check=True, text=True, capture_output=True)
        print(f"Old backups cleaned up, keeping only the last {keep_last_n} versions.")
        print(result.stdout)

    except subprocess.CalledProcessError as e:
        print("An error occurred during cleanup of old backups:")
        print(e.stderr)

# EXECUTION
create_versioned_backup(local_folder, remote_folder, remote_host, username, password, port, rsync_path, keep_last_n)
