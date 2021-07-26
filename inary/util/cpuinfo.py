import os


def get_cpuinfo(section=""):
    if os.path.exists("/proc/cpuinfo"):
        cpuinfo = open("/proc/cpuinfo", "r").read()
        for line in cpuinfo.split("\n"):
            if section in line:
                return line.split(":")[1].strip()
    return ""


cpupath = "/sys/devices/system/cpu/cpu"


def get_cpu_governor(core=0):
    if os.path.exists(cpupath+str(core)+"/cpufreq/scaling_governor"):
        return open(cpupath+str(core)+"/cpufreq/scaling_governor", "r").read().strip()
    else:
        return ""


def change_cpu_governor(core, governor):
    if os.path.exists(cpupath+str(core)+"/cpufreq/scaling_governor"):
        open(cpupath+str(core)+"/cpufreq/scaling_governor", "w").write(governor)
    else:
        return
