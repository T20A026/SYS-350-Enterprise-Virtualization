import getpass
import ssl
import warnings
from pyVmomi import vim

#ඞ
#Disable Depericiation warning
warnings.filterwarnings("ignore", category=DeprecationWarning)
from pyVim.connect import SmartConnect
passw = getpass.getpass()

#Grab login config from cred file
cred = [line.rstrip() for line in open('/home/super/Documents/SYS350/SYS-350-Enterprise-Virtualization/creds.txt')]

username = cred[0]
hostname = cred[1]

#Set SSL Settings
s=ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
s.verify_mode=ssl.CERT_NONE

#Connect to VCenter Server
si= SmartConnect(host=hostname, user=username, pwd=passw, sslContext=s)

#Gather and report session information
sessionIp = si.content.sessionManager.currentSession.ipAddress
sessionUser = si.content.sessionManager.currentSession.userName
sessionServer = si.content.about.name

print("Current session source Address:", sessionIp)
print("Current session connected User:", sessionUser)
print("Current VCenter Server:", sessionServer)


#Get VM Information Function
def get_vm_info_by_name(vm_name):
    # Get the content of the root folder
    content = si.RetrieveContent()

    # Search for the VM by name
    vm = None
    vm_list = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    for v in vm_list.view:
        if v.name == vm_name:
            vm = v
            break

    # If the VM is found, retrieve its information
    if vm:
        print(f"Name: {vm.name}")
        print(f"Power state: {vm.runtime.powerState}")
        print(f"CPU count: {vm.summary.config.numCpu}")
        print(f"Memory size: {vm.summary.config.memorySizeMB} MB")

    # Ip Address             
        ip_address = None
        for guest in vm.guest.net:
            if guest.ipConfig.ipAddress:
                ip_address = guest.ipConfig.ipAddress[0].ipAddress
                break
        print(f"IP address: {ip_address}")


def powerOnVM():
    vm_name = input("Enter the VM you would like to power on: ")
    # Get the content of the root folder
    content = si.RetrieveContent()

    # Search for the VM by name
    vm = None
    vm_list = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    for v in vm_list.view:
        if v.name == vm_name:
            vm = v
            break

    # If the VM is found, power it on
    if vm:
        try:
            if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOff:
                task = vm.PowerOn()
                print(f"Powering on VM {vm_name}.")
            else:
                print(f"VM {vm_name} is already powered on.")
        except Exception as e:
            print(f"Error powering on VM {vm_name}: {e}")
    else:
        print(f"VM {vm_name} not found.")


def powerOffVM():
    vm_name = input("Enter the VM you would like to power off: ")
    # Get the content of the root folder
    content = si.RetrieveContent()

    # Search for the VM by name
    vm = None
    vm_list = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    for v in vm_list.view:
        if v.name == vm_name:
            vm = v
            break

    # If the VM is found, power it off
    if vm:
        try:
            if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOn:
                task = vm.PowerOff()
                print(f"Powering off VM {vm_name}.")
            else:
                print(f"VM {vm_name} is already powered off.")
        except Exception as e:
            print(f"Error powering off VM {vm_name}: {e}")
    else:
        print(f"VM {vm_name} not found.")


vm_names = []
vm_list = []

#Retrive Vm Uid and Name
def find_by_name():
    vm_names = []

    searchName = input("Enter the name to search for: ")
    # Retrieve Vm Uid and Name
    content = si.RetrieveContent()
    for child in content.rootFolder.childEntity:
        if hasattr(child, 'vmFolder'):
            datacenter = child
            vmfolder = datacenter.vmFolder
            vmlist = vmfolder.childEntity

            for vm in vmlist:
                vm_names.append(vm.name)

    # Retrieve VmContent Via Name
    for vm in vm_names:
        if searchName in vm:
            print("Virtual Machines found: ")
            get_vm_info_by_name(vm)

def exit_program():
    print("Exiting program...")
    quit()

def display_menu():
    print("\nMenu:")
    print("1. Search for VM by name")
    print("2. Power on a VM by name")
    print("3. Power off a VM by name")
    print("4. Exit")

functions = {
    '1': find_by_name,
    '2': powerOnVM,
    '3': powerOffVM,
    '4': exit_program
}

while True:
    display_menu()
    choice = input("Enter your choice: ")

    if choice in functions:
        functions[choice]()
    else:
        print("Invalid choice. Please try again.")
