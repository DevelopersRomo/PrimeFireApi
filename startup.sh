#!/bin/sh

# Azure Oryx ya configura el entorno virtual, no activar manualmente
python -m uvicorn main:app --host 0.0.0.0 --port 8000
