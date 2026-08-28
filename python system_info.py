import os
import platform
import socket
import subprocess
import sys
import psutil

def run_powershell(cmd):
    """Runs a PowerShell command and returns the cleaned text output."""
    try:
        command = f'powershell -NoProfile -Command "{cmd}"'
        output = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.DEVNULL).strip()
        return output if output else 'N/A'
    except Exception:
        return 'N/A'

def bytes_to_gb(bytes_value):
    """Converts bytes to gigabytes formatted to 2 decimal places."""
    return f"{bytes_value / (1024 ** 3):.2f} GB"

def build_full_report():
    lines = []
    
    def log(text=""):
        lines.append(text)

    log("=" * 65)
    log("         COMPLETE HARDWARE & SYSTEM COMPONENT REPORT         ")
    log("=" * 65)

    # 1. OPERATING SYSTEM & BUILD
    log("\n[ OPERATING SYSTEM & BUILD ]")
    log(f"  OS Name           : {platform.system()} {platform.release()}")
    
    if platform.system() == "Windows":
        build_num = run_powershell('(Get-ItemProperty "HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion").CurrentBuildNumber')
        ubr = run_powershell('(Get-ItemProperty "HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion").UBR')
        display_version = run_powershell('(Get-ItemProperty "HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion").DisplayVersion')
        log(f"  Version / Edition : {display_version}")
        log(f"  OS Build Number   : {build_num}.{ubr}")
    else:
        log(f"  OS Build Number   : {platform.version()}")

    log(f"  Architecture      : {platform.machine()} ({platform.architecture()[0]})")
    log(f"  Hostname          : {socket.gethostname()}")

    # 2. MOTHERBOARD, BIOS & SYSTEM SERIAL
    log("\n[ MOTHERBOARD, BIOS & SERIAL NUMBERS ]")
    if platform.system() == "Windows":
        mb_vendor = run_powershell('(Get-CimInstance Win32_BaseBoard).Manufacturer')
        mb_model = run_powershell('(Get-CimInstance Win32_BaseBoard).Product')
        mb_serial = run_powershell('(Get-CimInstance Win32_BaseBoard).SerialNumber')
        bios_ver = run_powershell('(Get-CimInstance Win32_BIOS).SMBIOSBIOSVersion')
        sys_serial = run_powershell('(Get-CimInstance Win32_BIOS).SerialNumber')
        
        log(f"  Motherboard       : {mb_vendor} {mb_model}")
        log(f"  Motherboard Serial: {mb_serial}")
        log(f"  BIOS Version      : {bios_ver}")
        log(f"  System Serial No. : {sys_serial}")

    # 3. PROCESSOR (CPU)
    log("\n[ PROCESSOR (CPU) ]")
    log(f"  CPU Model         : {platform.processor()}")
    log(f"  Physical Cores    : {psutil.cpu_count(logical=False)}")
    log(f"  Logical Threads   : {psutil.cpu_count(logical=True)}")

    # 4. GRAPHICS CARD (GPU)
    log("\n[ GRAPHICS CARD (GPU) ]")
    if platform.system() == "Windows":
        gpu_name = run_powershell('(Get-CimInstance Win32_VideoController).Name')
        log(f"  GPU Controller    : {gpu_name}")

    # 5. MEMORY (RAM)
    log("\n[ MEMORY (RAM) ]")
    virtual_mem = psutil.virtual_memory()
    log(f"  Total Capacity    : {bytes_to_gb(virtual_mem.total)}")
    log(f"  Available Memory  : {bytes_to_gb(virtual_mem.available)}")
    log(f"  Current Usage     : {virtual_mem.percent}%")
    
    if platform.system() == "Windows":
        ram_serials = run_powershell('(Get-CimInstance Win32_PhysicalMemory).SerialNumber')
        ram_parts = run_powershell('(Get-CimInstance Win32_PhysicalMemory).PartNumber')
        log(f"  RAM Serial No(s)  : {ram_serials}")
        log(f"  RAM Part No(s)    : {ram_parts}")

    # 6. STORAGE & DISK DRIVES
    log("\n[ STORAGE & DISK DRIVES ]")
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            log(f"  Drive {partition.device} (Mount: {partition.mountpoint})")
            log(f"    - Type         : {partition.fstype}")
            log(f"    - Total Size   : {bytes_to_gb(usage.total)}")
            log(f"    - Free Space   : {bytes_to_gb(usage.free)}")
            log(f"    - Usage        : {usage.percent}%")
        except PermissionError:
            continue

    # 7. NETWORK ADAPTERS
    log("\n[ NETWORK ADAPTERS ]")
    addrs = psutil.net_if_addrs()
    for interface_name, interface_addresses in addrs.items():
        log(f"  Adapter: {interface_name}")
        for addr in interface_addresses:
            if addr.family == socket.AF_INET:
                log(f"    - IPv4 Address : {addr.address}")
            elif hasattr(psutil, 'AF_LINK') and addr.family == psutil.AF_LINK:
                log(f"    - MAC Address  : {addr.address}")

    log("\n" + "=" * 65)

    full_output = "\n".join(lines)
    
    # Print to Terminal
    print(full_output)
    
    # Save Report to File
    report_filename = "system_report.txt"
    try:
        with open(report_filename, "w", encoding="utf-8") as f:
            f.write(full_output)
        print(f"\n[+] Full report saved to: {os.path.abspath(report_filename)}")
    except Exception as e:
        print(f"\n[-] Could not save text file: {e}")

if __name__ == "__main__":
    build_full_report()