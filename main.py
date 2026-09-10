# ============================================================
#  PROGRENTIS — Windows Local User Generator Script
#  Python script made and written entirely by Joshua Colell
# ============================================================

import random
import subprocess

pass_base_keyword = [
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
]

user_list = []

### This function generates a pseudo-pseudo-random string of characters
### that would be assigned as the User's password.
###
### Returns randomly-generated string "password"; Example -> "camara574".
def pass_gen():
    pass_base = random.choice(pass_base_keyword)
    pass_sequential_digits = random.randint(100, 999)

    password = f"{pass_base}{pass_sequential_digits}"
    return password

### This function provides the correct designator (or ending) that each grande
### level should have.
###
### Made due to the nature of the input being an integer,
### and the fact that the User's username has to display everything
### without any flaws.
###
### Returns string "grade"; Example -> "1ro".
def grade_designator(grade_number):
    match grade_number:
        case 1: return f"{grade_number}ro"
        case 2: return f"{grade_number}do"
        case 3: return f"{grade_number}ro"
        case 4: return f"{grade_number}to"
        case 5: return f"{grade_number}to"
        case 6: return f"{grade_number}to"

### Generates the User's respective username provided that the iteration
### is being counted upon. This is the final layer within the User's username
### is held.
###
### Returns string "username," if held within 1-12 range;
### otherwise, returns Error and string "username" as "ERROR USER".
### Example -> "2do Secundaria".
def user_name_gen(count):
    if count >= 13 or count <= 0:
        print(f"ERROR: Grade level out of range.\n || Grade level given: {count}, whilst range is 1-12 (Pri. & Sec.).")
        return "ERROR USER"

    secondary = False
    if count >= 7:
        secondary = True
        count -= 6

    grade_level = grade_designator(count)
    return f"{grade_level} {"Secundaria" if secondary else "Primaria"}"

### The 'true' main function of this script. This generates, initializes, and sets up the generated user
### silently in the background. Uses PowerShell as the main shell to commit said changes on the Windows computer.
###
### Returns either celebratory string or an error-containing string along with the Error string.
def windows_user_gen(username, password, group):
    powershell_script = f"""
    # 1. Create the secure password string
    $SecurePassword = ConvertTo-SecureString "{password}" -AsPlainText -Force

    # 2. Create the local Windows user account
    New-LocalUser -Name "{username}" -FullName "{username}" -Password $SecurePassword -Description "Created via script" -ErrorAction Stop

    # 3. Explicitly add the user to the local 'Users' group (Standard User)
    # NOTE: The local group name changes depending on the user machine's language.
    #  || Change accordingly to the language of the system.
    Add-LocalGroupMember -Group "{group}" -Member "{username}"

    # 4. Create the credential object for the profile initialization
    $Credentials = New-Object System.Management.Automation.PSCredential("{username}", $SecurePassword)

    # 5. Trigger the hidden background process to build C:\\Users\\{username}
    Start-Process -FilePath "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -WorkingDirectory "C:\\Windows\\System32" -Credential $Credentials -ArgumentList "-Command `& {{Write-Host 'Initializing Profile...'}}" -WindowStyle Hidden

    # 6. Disable the "Hi" first logon animation globally
    Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" -Name "EnableFirstLogonAnimation" -Value 0 -ErrorAction SilentlyContinue

    # 7. Safe creation of the OOBE key (checks if it exists first to prevent errors)
    if (-not (Test-Path "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\OOBE")) {{
        New-Item -Path "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows" -Name "OOBE" -Force | Out-Null
    }}

    # 8. Disable the OOBE privacy experience prompts globally
    Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\OOBE" -Name "DisablePrivacyExperience" -Value 1 -ErrorAction SilentlyContinue
    """

    try:
        subprocess.run(
            ["powershell", "-Command", powershell_script],
            text=True,
            check=True,
            capture_output=True # Captures stdout/stderr for debugging
        )
        print("User created, profile initialized in background, and OOBE blocks applied successfully!")

    except subprocess.CalledProcessError as e:
        print("An error occurred while executing the script:")
        print(e.stderr)

### As the name suggests, this function runs some tests to see if the theorized code truly works.
###
### Returns nothing.
def run_tests():
    windows_user_gen("Test User", "123", "Usuarios")

def main():
    # Uncomment to run some tests.
    #run_tests()

    iteration_count = 1 # Laptop classes which would use PROGRENTIS start at 4to Pri., hence why it's 4 and not 1.
    while iteration_count <= 270:
        username = user_name_gen(iteration_count)
        password = pass_gen()

        user_list.append([username, password])
        windows_user_gen(username, password, "Usuarios")

        iteration_count += 1

    print(f"User Generation Report:\n{user_list}")

if __name__ == "__main__":
    main()
