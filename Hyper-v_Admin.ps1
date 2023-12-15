function GeneralInfo {
    # General Info
    Get-VM | ForEach-Object {
		
        $_ | Select-Object -Property Name, State, 
        @{Name='IPAddresses'; Expression={($_.NetworkAdapters).IPAddresses}},
        HardDrives,
        @{Name='MemoryAssignedMB'; Expression={$_.MemoryAssigned / 1MB}},
        Uptime, 
        Status
        Write-Host "----------------------"
    }
}

# Gets info for specific Vm
function VMInfo {
    $vmName = read-host "Enter VM Name: "

    # Get specific VM information with a search for VM name
    Get-VM -Name $VMName | ForEach-Object {
        $_ | Select-Object -Property Name, State, 
        @{Name='IPAddresses'; Expression={($_.NetworkAdapters).IPAddresses}},
        HardDrives,
        @{Name='MemoryAssignedMB'; Expression={$_.MemoryAssigned / 1MB}},
        Uptime, 
        Status
        Write-Host "----------------------"
    }
}
# Start VM from name
function StartVM {
    $GuestName = read-host "Enter VM to start: "
    Start-VM -Name $GuestName
}
# Stop VM from name
function StopVM{
    $GuestName = read-host "Enter VM to stop: "
    Get-VM $GuestName | Stop-VM
}
# New Checkpoint
function NewCheck{
    $GuestName = read-host "Enter VM name: "
    $vm = Get-VM $GuestName
    $CheckName = read-host "Enter checkpoint name: "
    $vm | Checkpoint-VM -SnapshotName $CheckName
}
# Revert Checkpoint by name
function RevertCheck {
    $GuestName = Read-Host "Enter VM name: "
    $vm = Get-VM $GuestName

    if ($vm) {
        $Checkpoints = Get-VMSnapshot -VM $vm
        if ($Checkpoints.Count -gt 0) {
            Write-Host "Available checkpoints for VM '$GuestName':"
            $Checkpoints | Select-Object -Property Name, CreationTime | Format-Table -AutoSize

            $CheckName = Read-Host "Enter the name of the checkpoint to revert to: "
            $SelectedCheckpoint = $Checkpoints | Where-Object { $_.Name -eq $CheckName }

            if ($SelectedCheckpoint) {
                Restore-VMSnapshot -Name $CheckName -VMName $GuestName
            } else {
                Write-Host "Checkpoint '$CheckName' not found for VM '$GuestName'."
            }
        } else {
            Write-Host "No checkpoints found for VM '$GuestName'."
        }
    } else {
        Write-Host "VM '$GuestName' not found."
    }
}



# New Linked Clone
function LinkedClone {
    $ParentVM = Read-Host "Enter VM to clone: "
    $ChildName = Read-Host "Enter Child VM Name: "

    $Path = "C:\Users\Public\Documents\Hyper-V\Virtual hard disks\"
    $ParentVHD = $Path + $ParentVM + ".vhdx"
    $ChildVHD = $Path + $ChildName + ".vhdx"
    New-VHD -ParentPath $ParentVHD -Path $ChildVHD -Differencing

    New-VM -Name $ChildName -MemoryStartupBytes 2GB -VHDPath $ChildVHD -Generation 2 -SwitchName "LAN-INTERNAL"
    Set-VMFirmware -VMName $ChildName -EnableSecureBoot Off
    Checkpoint-VM -Name $ChildName -SnapshotName "Base"

    Write-Host "Would you like to turn on the VM? (Y/N): "
    $choice = Read-Host
    if ($choice -eq "Y") {
        Start-VM -Name $ChildName
    }
}


# Remove VM
function RemoveVM{
    $vmName = read-host "Enter VM name to delete: "
    $vm = Get-VM $vmName
    if ($vm.state -eq "Running") {
        $ans = read-host "VM is running, stop VM? (y/n)"
        if ($ans -eq "y") {
            Stop-VM $vmName -Force
        }
        else{
            write-host "Aborted"
            return
        }
    }

    $confirm = read-host "**Delete $vmName???** (y/n)"
    if ($confirm -eq "y") {
        $vm | Remove-VM -Force
    }
}


function menu{
    # Menu
    Write-Host "1. Get all VMs"
    Write-Host "2. Search for a specific VM"
    Write-Host "3. Power on a VM"
    Write-Host "4. Power off a VM"
    Write-Host "5. Create a snapshot"
    Write-Host "6. Revert to a snapshot"
    Write-Host "7. Create a linked clone"
    Write-Host "8. Delete a VM"
    Write-Host "9. Exit"
    $choice = Read-Host "Enter your choice"
    switch ($choice) {
        1 {GeneralInfo}
        2 {VMInfo}
        3 {StartVM}
        4 {StopVM}
        5 {NewCheck}
        6 {RevertCheck}
        7 {LinkedClone}
        8 {RemoveVM}
        9 {exit}
    }
}

while ($true) {
    menu
}
