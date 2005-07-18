# all package operation interfaces are here

def remove(package_name):
    """Remove a goddamn package"""
    ui.info('Removing package ' + package_name)
    if not installdb.is_installed(package_name):
        raise InstallError('Trying to remove nonexistent package '
                           + package_name)
    for fileinfo in installdb.files(package_name):
        os.unlink(fileinfo.path)
    installdb.remove(package_name)


from install import Installer

def install(package_name):
    Installer 
