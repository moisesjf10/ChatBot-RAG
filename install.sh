#!/bin/bash

# --- CONFIGURACIÓN DE COLORES PARA QUE SE VEA PROFESIONAL ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# --- CABECERA ---
echo -e "${BLUE}=================================================${NC}"
echo -e "${BLUE}    INSTALADOR AUTOMÁTICO - RAG CHATBOT AI       ${NC}"
echo -e "${BLUE}=================================================${NC}"
echo ""

# 1. VERIFICAR SI DOCKER ESTÁ INSTALADO
echo -e "${YELLOW}[1/5] Verificando requisitos del sistema...${NC}"
if ! [ -x "$(command -v docker)" ]; then
  echo -e "${RED}Error: Docker no está instalado.${NC}"
  echo "Por favor, instala Docker Desktop antes de continuar."
  exit 1
fi
echo -e "${GREEN}✓ Docker detectado.${NC}"

# 2. VERIFICAR ARCHIVOS NECESARIOS
echo -e "${YELLOW}[2/5] Buscando archivos de instalación...${NC}"
if [ ! -f "instalador_chatbot.tar" ]; then
    echo -e "${RED}Error: No encuentro el archivo 'instalador_chatbot.tar'.${NC}"
    exit 1
fi

if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}Error: No encuentro el archivo 'docker-compose.yml'.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Archivos encontrados.${NC}"

# 3. CARGAR LA IMAGEN DOCKER (Esto puede tardar)
echo -e "${YELLOW}[3/5] Cargando la imagen del Chatbot (esto puede tardar unos segundos)...${NC}"
# Nota: Redirigimos la salida para que no ensucie la pantalla, a menos que haya error
docker load -i instalador_chatbot.tar
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Imagen cargada correctamente en Docker.${NC}"
else
    echo -e "${RED}Error al cargar la imagen. Verifica que el archivo .tar no esté corrupto.${NC}"
    exit 1
fi

# 4. GESTIÓN DEL ARCHIVO .ENV (API KEY)
echo -e "${YELLOW}[4/5] Configurando entorno...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${BLUE}No se detectó archivo .env.${NC}"
    echo -e "Por favor, introduce tu GOOGLE_API_KEY para Gemini:"
    read -p "API Key: " USER_KEY
    
    # Crear el archivo .env
    echo "GOOGLE_API_KEY=$USER_KEY" > .env
    echo -e "${GREEN}✓ Archivo .env creado.${NC}"
else
    echo -e "${GREEN}✓ Archivo .env existente detectado. Usando configuración actual.${NC}"
fi

# 5. LANZAR LA APLICACIÓN
echo -e "${YELLOW}[5/5] Iniciando el Chatbot...${NC}"

# Detener contenedores antiguos si existen
docker-compose down > /dev/null 2>&1

# Arrancar en modo 'detached' (segundo plano)
docker-compose up -d

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}==============================================${NC}"
    echo -e "${GREEN}   ¡INSTALACIÓN COMPLETADA CON ÉXITO! 🚀      ${NC}"
    echo -e "${GREEN}==============================================${NC}"
    echo ""
    echo -e "Accede a tu Chatbot aquí: ${BLUE}http://localhost:8501${NC}"
    echo ""
    echo "Para detener el bot, ejecuta: docker-compose down"
    echo ""
else
    echo -e "${RED}Hubo un error al iniciar los contenedores.${NC}"
    echo "Verifica que el puerto 8501 no esté ocupado."
fi
