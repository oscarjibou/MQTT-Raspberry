# 📡 MQTT to InfluxDB Bridge - Sistema de Monitoreo IoT

[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.12-green.svg)](https://www.python.org/)
[![InfluxDB](https://img.shields.io/badge/InfluxDB-2.7-orange.svg)](https://www.influxdata.com/)
[![Grafana](https://img.shields.io/badge/Grafana-Latest-red.svg)](https://grafana.com/)

Sistema completo de recolección, almacenamiento y visualización de datos IoT en tiempo real. Este proyecto actúa como puente entre dispositivos LoRa (ESP32) y sistemas de visualización, procesando datos GPS, estado de sensores y métricas de red a través de MQTT.

---

## 🎯 Descripción del Proyecto

Este sistema forma parte de una red mesh LoRa que permite:

- **Recepción de datos** desde dispositivos ESP32 vía LoRa → Raspberry Pi → MQTT
- **Almacenamiento temporal** en InfluxDB (base de datos de series temporales)
- **Visualización en tiempo real** mediante Grafana
- **Procesamiento automático** de datos GPS, estados de sensores y métricas de red

### Flujo de Datos

```
┌─────────┐      ┌──────────────┐      ┌─────────────┐      ┌──────────────┐
│  ESP32  │ LoRa │  Raspberry   │ MQTT │   MacBook   │      │  InfluxDB    │
│ (Nodos) │─────▶│      Pi      │─────▶│  (Docker)   │─────▶│  (Storage)   │
│         │      │ (Mosquitto)  │      │             │      │              │
└─────────┘      └──────────────┘      └─────────────┘      └──────────────┘
                                                                    │
                                                                    ▼
                                                              ┌──────────┐
                                                              │ Grafana  │
                                                              │ (Viz)    │
                                                              └──────────┘
```

---

## ✨ Características Principales

- 🔄 **Procesamiento en tiempo real** de mensajes MQTT
- 📊 **Almacenamiento eficiente** en InfluxDB (optimizado para series temporales)
- 📈 **Visualización interactiva** con Grafana
- 🐳 **Containerización completa** con Docker Compose
- 🔌 **Reconexión automática** a MQTT e InfluxDB
- 🏷️ **Tagging inteligente** por nodo y topic
- 📍 **Soporte GPS** (latitud/longitud)
- 📡 **Métricas de red** (RSSI, TTL, secuencia)

---

## 📋 Requisitos Previos

### Software Necesario

- **Docker** (versión 20.10 o superior)
- **Docker Compose** (versión 2.0 o superior)
- **Git** (para clonar el repositorio)

### Hardware/Red

- Acceso a un **broker MQTT** (ej: Mosquitto en Raspberry Pi)
- Conexión de red entre el MacBook y la Raspberry Pi

### Verificación de Requisitos

```bash
# Verificar Docker
docker --version

# Verificar Docker Compose
docker compose version

# Verificar acceso a MQTT (opcional, antes de iniciar)
docker run --rm -it eclipse-mosquitto:2 \
  mosquitto_sub -h <IP_RASPBERRY> -p 1883 -t 'test/ejemplo/json' -v
```

---

## 🚀 Instalación Rápida

### 1️⃣ Preparación Inicial (Solo Primera Vez)

```bash
# Crear directorios para volúmenes persistentes
mkdir -p influxdb/data influxdb/config grafana/data

# Dar permisos necesarios
chmod -R 777 influxdb grafana
```

### 2️⃣ Configuración de Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```bash
# ===== InfluxDB Configuration =====
DOCKER_INFLUXDB_INIT_MODE=setup
DOCKER_INFLUXDB_INIT_USERNAME=admin
DOCKER_INFLUXDB_INIT_PASSWORD=tu_password_seguro
DOCKER_INFLUXDB_INIT_ORG=TFG_Teleco
DOCKER_INFLUXDB_INIT_BUCKET=loramesh_data
DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=tu_token_admin_muy_seguro

# ===== MQTT Configuration =====
MQTT_HOST=192.168.1.XXX          # IP de tu Raspberry Pi
MQTT_PORT=1883
MQTT_TOPIC=loramesh/+/data       # Topic MQTT (el + es wildcard)

# ===== InfluxDB Connection (para mqtt_to_influx) =====
INFLUXDB_URL=http://influxdb:8086
INFLUXDB_TOKEN=tu_token_admin_muy_seguro  # Mismo que DOCKER_INFLUXDB_INIT_ADMIN_TOKEN
INFLUXDB_ORG=TFG_Teleco
INFLUXDB_BUCKET=loramesh_data
```

> ⚠️ **Importante**: El archivo `.env` está en `.gitignore` por seguridad. No lo subas a Git.

### 3️⃣ Construcción e Inicio del Sistema

```bash
# Primera vez o cuando cambies código Python/Dockerfile
docker compose up --build -d

# Arranques normales (día a día)
docker compose up -d
```

### 4️⃣ Verificación

```bash
# Ver estado de los contenedores
docker ps

# Ver logs del servicio MQTT → InfluxDB
docker logs -f mqtt_to_influx

# Ver logs de InfluxDB
docker logs -f influxdb

# Ver logs de Grafana
docker logs -f grafana
```

---

## 🌐 Acceso a las Interfaces Web

Una vez iniciado el sistema, accede a:

- **InfluxDB UI**: [http://localhost:8086](http://localhost:8086)
  - Usuario: El definido en `DOCKER_INFLUXDB_INIT_USERNAME`
  - Password: El definido en `DOCKER_INFLUXDB_INIT_PASSWORD`

- **Grafana**: [http://localhost:3000](http://localhost:3000)
  - Usuario por defecto: `admin`
  - Password por defecto: `admin` (se pedirá cambiar en el primer acceso)

---

## 📊 Formato de Datos

### Mensaje MQTT Esperado

El sistema espera mensajes JSON en el topic configurado con el siguiente formato:

```json
{
  "src": 1,              // ID del nodo emisor
  "seq": 42,             // Número de secuencia
  "ttl": 5,              // Time To Live
  "lat": 40.4168,        // Latitud GPS
  "lon": -3.7038,        // Longitud GPS
  "state": 1,            // Estado del sensor (opcional)
  "rssi": -85            // Señal RSSI recibida (opcional)
}
```

### Estructura en InfluxDB

Los datos se almacenan en dos **measurements**:

#### 1. Measurement: `gps`
- **Tags**: `node_id`, `topic`
- **Fields**: `lat`, `lon`, `seq`, `ttl`, `rssi`
- **Timestamp**: Automático (tiempo de recepción)

#### 2. Measurement: `eventos`
- **Tags**: `node_id`
- **Fields**: `state`
- **Timestamp**: Automático (tiempo de recepción)

---

## 🛠️ Uso y Comandos

### Comandos Principales

```bash
# Iniciar todos los servicios
docker compose up -d

# Detener todos los servicios (sin borrar datos)
docker compose down

# Detener y borrar volúmenes (⚠️ borra datos históricos)
docker compose down -v

# Reconstruir solo el servicio Python (cuando cambias código)
docker compose up --build -d mqtt_to_influx

# Ver logs en tiempo real
docker logs -f mqtt_to_influx
```

### Usando el Makefile

```bash
# Iniciar servicios
make up

# Detener servicios
make down
```

---

## 📁 Estructura del Proyecto

```
MQTT-Raspberry/
├── app/                          # Aplicación Python
│   ├── Dockerfile               # Imagen Docker para mqtt_to_influx
│   ├── mqtt_to_influx.py        # Script principal de procesamiento
│   └── requirements.txt         # Dependencias Python
├── docker-compose.yml           # Orquestación de servicios
├── .env                         # Variables de entorno (no en Git)
├── .gitignore                   # Archivos ignorados
├── makefile                     # Comandos útiles
├── Notes.md                     # Notas de desarrollo
├── README.md                    # Este archivo
├── influxdb/                    # Datos persistentes de InfluxDB
│   ├── data/                   # Base de datos
│   └── config/                 # Configuración
└── grafana/                     # Datos persistentes de Grafana
    └── data/                   # Dashboards, usuarios, etc.
```

---

## 🔧 Configuración Avanzada

### Personalizar el Topic MQTT

En el archivo `.env`, puedes usar wildcards de MQTT:

```bash
# Recibir de todos los topics que empiecen con "loramesh/"
MQTT_TOPIC=loramesh/+/data

# Recibir de un topic específico
MQTT_TOPIC=loramesh/node1/data

# Recibir de múltiples niveles
MQTT_TOPIC=loramesh/+/+/data
```

### Configurar Retención de Datos en InfluxDB

1. Accede a InfluxDB UI: http://localhost:8086
2. Ve a **Data** → **Buckets**
3. Selecciona tu bucket (`loramesh_data`)
4. Configura la **Retention Policy** según tus necesidades

### Configurar Grafana

1. Accede a Grafana: http://localhost:3000
2. Configura InfluxDB como fuente de datos:
   - **URL**: `http://influxdb:8086`
   - **Organization**: La definida en `.env`
   - **Token**: El token de InfluxDB
   - **Bucket**: `loramesh_data`
3. Crea dashboards personalizados para visualizar tus datos

---

## 🐛 Troubleshooting

### El servicio mqtt_to_influx no recibe datos

```bash
# 1. Verificar logs
docker logs -f mqtt_to_influx

# 2. Verificar conexión MQTT
docker run --rm -it eclipse-mosquitto:2 \
  mosquitto_sub -h <IP_RASPBERRY> -p 1883 -t '<TU_TOPIC>' -v

# 3. Verificar variables de entorno
docker exec mqtt_to_influx env | grep MQTT
```

### InfluxDB no inicia correctamente

```bash
# Verificar logs
docker logs -f influxdb

# Verificar permisos de directorios
ls -la influxdb/data

# Si hay problemas, reiniciar con volúmenes limpios
docker compose down -v
docker compose up -d
```

### Grafana no muestra datos

1. Verifica que InfluxDB esté funcionando: http://localhost:8086
2. Verifica la configuración de la fuente de datos en Grafana
3. Comprueba que hay datos en InfluxDB:
   - Ve a InfluxDB UI → **Data Explorer**
   - Ejecuta una query: `from(bucket: "loramesh_data") |> range(start: -1h)`

### Error: "Falta INFLUXDB_TOKEN"

Asegúrate de que el archivo `.env` existe y contiene todas las variables necesarias:

```bash
# Verificar que el archivo existe
ls -la .env

# Verificar contenido (sin mostrar valores sensibles)
grep -E "^[A-Z_]+=" .env | cut -d'=' -f1
```

---

## 📚 Recursos y Referencias

### Documentación Oficial

- [InfluxDB Documentation](https://docs.influxdata.com/influxdb/v2.7/)
- [Grafana Documentation](https://grafana.com/docs/grafana/latest/)
- [MQTT Protocol](https://mqtt.org/)
- [Docker Compose](https://docs.docker.com/compose/)

### Librerías Python Utilizadas

- `paho-mqtt`: Cliente MQTT para Python
- `influxdb-client`: Cliente oficial de InfluxDB para Python

---

## 🔐 Seguridad

### Buenas Prácticas

1. **Nunca subas el archivo `.env` a Git** (ya está en `.gitignore`)
2. **Usa tokens seguros** para InfluxDB (genera tokens largos y aleatorios)
3. **Cambia las contraseñas por defecto** de Grafana
4. **Considera usar autenticación MQTT** si tu broker lo soporta
5. **Restringe el acceso a los puertos** 8086 y 3000 si no necesitas acceso externo

### Generar Token Seguro

```bash
# Generar un token aleatorio seguro
openssl rand -hex 32
```

---

## 📝 Notas de Desarrollo

- El servicio `mqtt_to_influx` espera hasta 60 segundos a que InfluxDB esté listo
- Los datos se escriben de forma síncrona en InfluxDB para garantizar persistencia
- Los mensajes JSON inválidos se registran pero no detienen el servicio
- El sistema se reinicia automáticamente si un contenedor falla (`restart: unless-stopped`)

---

## 🤝 Contribuciones

Este proyecto forma parte de un Trabajo de Fin de Grado (TFG) en Telecomunicaciones.

---

## 📄 Licencia

Este proyecto es parte de un trabajo académico. Consulta con el autor para más detalles.

---

## 👤 Autor

**Oscar Jiménez Bou**  
Trabajo de Fin de Grado - Telecomunicaciones

---

## 🎓 Agradecimientos

Proyecto desarrollado como parte del TFG en Telecomunicaciones, integrando tecnologías IoT, redes mesh LoRa, MQTT y visualización de datos en tiempo real.

---

**¿Preguntas o problemas?** Revisa la sección de [Troubleshooting](#-troubleshooting) o consulta los logs de los servicios.

