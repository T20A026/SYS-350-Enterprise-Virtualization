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
    vm_names = input("Enter the names of the VMs to power on (separated by commas): ").split(',')

    # For loop to work through the inputted list of VM's
    for vm_name in vm_names:
        vm_name = vm_name.strip()  # Remove spaces

        # Get VM list from host
        content = si.RetrieveContent()

        # Search for the VM in the list
        vm = None
        vm_list = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
        for v in vm_list.view:
            if v.name == vm_name:
                vm = v
                break

        # If the VM is there power it on
        if vm:
            try:
                if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOff:
                    task = vm.PowerOn()
                    print(f"Powering on VM {vm_name}.")
                else:
                    print(f"VM {vm_name} is already powered on.")
            except Exception as e:
                print(f"Oops, something went wrong while powering on VM {vm_name}: {e}")
        else:
            print(f"VM {vm_name} not found.")


'''Powers off a list of VM's by name, seperated with a comma'''
def powerOffVM():
    vm_names = input("Enter the names of the VMs to power off (separated by commas): ").split(',')

    #For loop to work for the list of names provided in the input
    for vm_name in vm_names:
        vm_name = vm_name.strip()  # Remove spaces from the CSV style input (Works wihtout spaces)

        # Get the VM names from the host
        content = si.RetrieveContent()

        # Search for the VM in the list of names
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
                print(f"Oops, something went wrong while powering off VM {vm_name}: {e}")
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

'''Takes a list of Guest's and creates snapshots for each, allowing specific nameing and descriptions'''
def create_snapshots():
    vm_names = input("Enter the names of the VMs (separated by commas): ").split(',')

    for vm_name in vm_names:
        vm_name = vm_name.strip()  # Remove leading/trailing spaces

        # Get the content of the root folder
        content = si.RetrieveContent()

        # Search for the VM by name
        vm = None
        vm_list = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
        for v in vm_list.view:
            if v.name == vm_name:
                vm = v
                break

        # If the VM is found, create a snapshot
        if vm:
            snapshot_name = input(f"Enter a name for the snapshot of {vm_name}: ")
            description = input(f"Enter a description for the snapshot of {vm_name} (optional): ")

            try:
                vm.CreateSnapshot_Task(
                name=snapshot_name,
                description=description,
                memory=False,
                quiesce=False
                )
                print(f"Creating snapshot {snapshot_name} for VM {vm_name}...")

                print(f"Snapshot {snapshot_name} created successfully for VM {vm_name}.")
            except Exception as e:
                print(f"Error creating snapshot for VM {vm_name}: {e}")
        else:
            print(f"VM {vm_name} not found.")

'''Takes a list of Guests in CSV format and allows bulk updating of CPU and RAM'''

def update_guest_resources():
    vm_names = input("Enter the names of the VMs (separated by commas): ").split(',')

    new_cpu = input("Enter the updated CPU count (or press Enter to skip): ")
    new_memory_mb = input("Enter the updated memory size in MB (or press Enter to skip): ")

    if new_cpu and new_cpu.isdigit() and int(new_cpu) > 0:
        new_cpu = int(new_cpu)
    else:
        new_cpu = None

    if new_memory_mb and new_memory_mb.isdigit() and int(new_memory_mb) > 0:
        new_memory_mb = int(new_memory_mb)
    else:
        new_memory_mb = None

    for vm_name in vm_names:
        vm_name = vm_name.strip()  # Remove leading/trailing spaces

        # Get the VM list
        content = si.RetrieveContent()

        # Search for the VM
        vm = None
        vm_list = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
        for v in vm_list.view:
            if v.name == vm_name:
                vm = v
                break

        # If the VM is found, update CPU and memory
        if vm:
            try:
                if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOff:
                    # Update CPU count and memory
                    config_spec = vim.vm.ConfigSpec()
                    if new_cpu is not None:
                        config_spec.numCPUs = new_cpu
                    if new_memory_mb is not None:
                        config_spec.memoryMB = new_memory_mb

                    vm.Reconfigure(config_spec)
                    print(f"VM {vm_name} configuration updated successfully.")
                else:
                    print(f"VM {vm_name} must be powered off to update configuration.")
            except Exception as e:
                print(f"Oops, something went wrong while updating VM {vm_name} configuration: {e}")
        else:
            print(f"VM {vm_name} not found.")



''' Begin the menu system, and end of the functions'''

def exit_program():
    print("Exiting program...")
    quit()

def display_menu():
    print("\nMenu:")
    print("1. Search for VM by name")
    print("2. Power on a VM by name")
    print("3. Power off a VM by name")
    print("4. Create VM Snapshot by name")
    print("5. Update CPU and Memory by name")
    print("6. Exit")

functions = {
    '1': find_by_name,
    '2': powerOnVM,
    '3': powerOffVM,
    '4': create_snapshots,
    '5': update_guest_resources,
    '6': exit_program
}

while True:
    display_menu()
    choice = input("Enter your choice: ")

    if choice in functions:
        functions[choice]()
    else:
        print("Invalid choice. Please try again.")
