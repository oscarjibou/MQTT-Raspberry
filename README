## 1️⃣ (Solo la primera vez) Preparar carpetas de volúmenes

```bash
mkdir -p influxdb/data influxdb/config grafana/data
chmod -R 777 influxdb grafana
```

---

## 2️⃣ 🧪 Test rápido: ¿el Mac recibe MQTT de la Raspberry?

👉 **Esto es ANTES de Docker Compose**, solo para comprobar red/MQTT:

```bash
docker run --rm -it eclipse-mosquitto:2 \
  mosquitto_sub -h <IP_RASPBERRY> -p 1883 -t 'test/ejemplo/json' -v
```

📌 Si aquí no ves mensajes → **NO sigas**, hay que arreglar MQTT/red.

---

## 3️⃣ 🏗️ Primera vez (o si cambias código Python / Dockerfile)

```bash
docker compose up --build -d
```

Esto:

- construye el contenedor `mqtt_to_influx`
- levanta **InfluxDB + Grafana + mqtt_to_influx**
- crea la red `tfg-net`

---

## 4️⃣ ▶️ Arranques normales (día a día)

Cuando ya está todo construido:

```bash
docker compose up -d
```

---

## 5️⃣ 👀 Ver logs (muy importante para depurar)

### Servicio MQTT → Influx:

```bash
docker logs -f mqtt_to_influx
```

### InfluxDB:

```bash
docker logs -f influxdb
```

### Grafana:

```bash
docker logs -f grafana
```

---

## 6️⃣ 🌐 Acceso web

- **InfluxDB** → [http://localhost:8086](http://localhost:8086)
- **Grafana** → [http://localhost:3000](http://localhost:3000)

---

## 7️⃣ ⏹️ Parar todo

```bash
docker compose down
```

(⚠️ No borra datos, están en los volúmenes)

---

## 8️⃣ 🧹 Parar + borrar todo (reset total)

⚠️ **Esto borra datos históricos**

```bash
docker compose down -v
```

---

## 9️⃣ 🔁 Cuando cambias SOLO código Python

```bash
docker compose up --build -d
docker logs -f mqtt_to_influx
```

---

## 10️⃣ 🔍 Comprobar estado general

```bash
docker ps
docker network ls
docker network inspect tfg-mesh
```

---

# 🧠 Mapa mental final (importantísimo)

```
ESP32
  ↓ LoRa
Raspberry Pi
  ↓ MQTT (Mosquitto)
MacBook (Docker)
  ├── mqtt_to_influx  → escribe datos
  ├── influxdb        → almacena datos
  └── grafana         → visualiza datos
```
