#!/bin/sh

# Azure Oryx ya configura el entorno virtual, no activar manualmente
# 3 workers: el cache de employees esta firmado por tenant y validado con un
# marker de DB + TTL 300s, y los schedulers usan un file-lock (1 solo worker).
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 3
