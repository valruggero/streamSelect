

def name():
    return "streamSelect"
def description():
    return "Dockable widget for downward stream selection"
def version():
    return "Version 0.0.1"
def icon():
    return "icon.png"
def qgisMinimumVersion():
    return "1.8"
def classFactory(iface):
    from streamSelect import StreamSelect
    return StreamSelect(iface)
