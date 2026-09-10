# ============================================================
#  PROGRENTIS — Windows Local User Generator Script
#  Translated from Python to PowerShell by Claude
# ============================================================

if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    # Added -NoExit here to keep the new elevated window open
    Start-Process powershell.exe "-NoExit -NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    Exit
}

$PassBaseKeywords = @(
    # Kitchen & Dining
    "mesa", "silla", "plato", "vaso", "taza",
    "tenedor", "cuchara", "cuchillo", "sarten", "botella",

    # Living Room & Bedroom
    "cama", "almohada", "saba", "espejo", "reloj",
    "lampara", "sofa", "alfombra", "cortina", "cuadro",

    # Electronics & Office
    "telefono", "computadora", "pantalla", "teclado", "camara",
    "audifonos", "television", "cable", "papel", "boligrafo",

    # Clothing & Personal Items
    "camisa", "pantalon", "zapatos", "calcetines", "chaqueta",
    "sombrero", "bolso", "billetera", "llave", "gafas",

    # Bathroom & Cleaning
    "toalla", "jabon", "cepillo", "esponja", "esoba",
    "basura", "puerta", "ventana", "mochila", "maleta"
)

$UserList = @()

function Get-GeneratedPassword {
    $Base   = $PassBaseKeywords | Get-Random
    $Digits = Get-Random -Minimum 100 -Maximum 1000
    return "$Base$Digits"
}

function Get-GradeDesignator {
    param([int]$GradeNumber)
    switch ($GradeNumber) {
        1 { return "${GradeNumber}ro" }
        2 { return "${GradeNumber}do" }
        3 { return "${GradeNumber}ro" }
        4 { return "${GradeNumber}to" }
        5 { return "${GradeNumber}to" }
        6 { return "${GradeNumber}to" }
    }
}

function Get-UserName {
    param([int]$Count)

    if ($Count -le 0 -or $Count -ge 13) {
        Write-Host "ERROR: Grade level out of range.`n || Grade level given: $Count, whilst range is 1-12 (Pri. & Sec.)."
        return "ERROR USER"
    }

    $Secondary = $false
    if ($Count -ge 7) {
        $Secondary = $true
        $Count -= 6
    }

    $GradeLevel = Get-GradeDesignator -GradeNumber $Count
    $Division   = if ($Secondary) { "Secundaria" } else { "Primaria" }
    return "$GradeLevel $Division"
}

function New-WindowsLocalUser {
    param(
        [string]$Username,
        [string]$Password
    )

    try {
        # 1. Create the secure password string
        $SecurePassword = ConvertTo-SecureString $Password -AsPlainText -Force

        # 2. Create the local Windows user account
        New-LocalUser -Name $Username -Password $SecurePassword -FullName $Username -Description "Created via script" -ErrorAction Stop

        # 3. Explicitly add the user to the local 'Users' group (Standard User)
        Add-LocalGroupMember -Group "Users" -Member $Username -ErrorAction SilentlyContinue

        # 4. Create the credential object for the profile initialization
        $Credentials = New-Object System.Management.Automation.PSCredential($Username, $SecurePassword)

        # 5. Trigger the hidden background process to build C:\Users\<Username>
        Start-Process `
            -FilePath      "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" `
            -WorkingDirectory "C:\Windows\System32" `
            -Credential    $Credentials `
            -ArgumentList  "-Command `& {Write-Host 'Initializing Profile...'}" `
            -WindowStyle   Hidden

        # 6. Disable the "Hi" first logon animation globally
        Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -Name "EnableFirstLogonAnimation" -Value 0 -ErrorAction SilentlyContinue

        # 7. Safe creation of the OOBE key (checks if it exists first to prevent errors)
        if (-not (Test-Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\OOBE")) {
            New-Item -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows" -Name "OOBE" -Force | Out-Null
        }

        # 8. Disable the OOBE privacy experience prompts globally
        Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\OOBE" -Name "DisablePrivacyExperience" -Value 1 -ErrorAction SilentlyContinue

        Write-Host "User created, profile initialized in background, and OOBE blocks applied successfully!"

    } catch {
        Write-Host "An error occurred while executing the script:"
        Write-Host $_.Exception.Message
    }
}

function Invoke-Tests {
    New-WindowsLocalUser -Username "Test User" -Password "123"
}

# ── Main ─────────────────────────────────────────────────────

# Uncomment to run tests instead:
# Invoke-Tests

$IterationCount = 4   # PROGRENTIS laptop classes start at 4to Primaria

while ($IterationCount -le 12) {
    $UName = Get-UserName -Count $IterationCount
    $UPass = Get-GeneratedPassword

    $UserList += ,@($UName, $UPass)
    New-WindowsLocalUser -Username $UName -Password $UPass

    $IterationCount++
}

Write-Host "User Generation Report:"
foreach ($Entry in $UserList) {
    Write-Host "  Username: $($Entry[0])  |  Password: $($Entry[1])"
}

Write-Host "Script finished."
