import subprocess

def ping(IPS):
    for ip in IPS:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "1", ip],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        if(result.returncode !=0):
            return False
        
    return True