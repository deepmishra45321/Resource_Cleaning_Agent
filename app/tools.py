import psutil
from fastmcp import FastMCP, Client

# Initialize FastMCP Server
mcp = FastMCP("SysOps")

@mcp.tool()
def get_system_metrics() -> str:
    """Returns current CPU and RAM usage percentage."""
    cpu = psutil.cpu_percent(interval=0.1)
    ram = psutil.virtual_memory().percent
    return f"CPU: {cpu}%, RAM: {ram}%"

@mcp.tool()
def get_top_processes(limit: int = 5) -> str:
    """Returns the top processes by RAM usage as a stringified list of dicts."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
        try:
            # Check if process actually exists and we have permissions
            proc_info = proc.info
            processes.append({
                "pid": proc_info['pid'],
                "name": proc_info['name'],
                "ram_mb": proc_info['memory_info'].rss / (1024 * 1024)
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    # Sort safely by RAM
    sorted_procs = sorted(processes, key=lambda x: x['ram_mb'], reverse=True)[:limit]
    return str(sorted_procs)

@mcp.tool()
def kill_process(pid: int, audit_mode: bool = True) -> str:
    """Kills a process by PID. If audit_mode is True, simulates the kill."""
    if audit_mode:
        return f"[AUDIT MODE] Simulated killing process with PID {pid}."
    try:
        proc = psutil.Process(pid)
        proc.terminate()
        proc.wait(timeout=3)
        return f"Process {pid} successfully terminated."
    except psutil.NoSuchProcess:
        return f"Process {pid} not found."
    except psutil.AccessDenied:
        return f"Access denied to terminate process {pid}."
    except Exception as e:
        return f"Error killing process {pid}: {str(e)}"

# Initialize for In-Memory Client usage (e.g. for LangGraph)
mcp_client = Client(mcp)
