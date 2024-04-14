import psutil
process = psutil.Process()
print(f"VMS (Virtual Memory Size): {process.memory_info().vms / (1024 * 1024):.2f} MB")
