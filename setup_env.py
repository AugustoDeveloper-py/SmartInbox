import os
import subprocess
import sys

def create_and_setup_env():
    # Nombre del entorno virtual
    env_name = "env"
    
    # Crear el entorno virtual
    print("Creando entorno virtual...")
    subprocess.run([sys.executable, "-m", "venv", env_name], check=True)

    # Identificar el ejecutable de Python dentro del entorno
    python_executable = os.path.join(env_name, "Scripts", "python.exe") if os.name == "nt" else os.path.join(env_name, "bin", "python")
    
    # Instalar dependencias desde requirements.txt
    print("Instalando dependencias...")
    subprocess.run([python_executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
    subprocess.run([python_executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    
    print(f"¡Entorno virtual '{env_name}' creado y configurado exitosamente!")
    print(f"Para activarlo, usa:")
    if os.name == "nt":
        print(f"{env_name}\\Scripts\\activate")
    else:
        print(f"source {env_name}/bin/activate")

if __name__ == "__main__":
    create_and_setup_env()
