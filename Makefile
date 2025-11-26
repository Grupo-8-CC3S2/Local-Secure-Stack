.PHONY: help build dev test clean logs status stop restart pull-images check

.DEFAULT_GOAL := help

help:
	@echo "  LOCAL SECURE STACK - Comandos Disponibles"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## construye las imágenes Docker
	@echo "Construyendo imágenes Docker..."
	docker compose -f compose/docker-compose.yml build --no-cache

dev: ## levanta el stack en modo desarrollo
	@echo "Levantando stack completo..."
	@bash scripts/up.sh

test: ## ejecuta las pruebas del stack
	@echo "Ejecutando pruebas automatizadas..."
	@bash scripts/test-stack.sh

clean: ## apaga servicios y elimina volúmenes
	@echo "Limpiando stack y volúmenes..."
	@bash scripts/down.sh

stop: ## detiene servicios sin eliminar volúmenes
	@echo "Deteniendo servicios..."
	docker compose -f compose/docker-compose.yml stop

restart: stop dev ## Reinicia el stack

logs: ## muestra logs en tiempo real
	@echo "Mostrando logs (Ctrl+C para salir)..."
	docker compose -f compose/docker-compose.yml logs -f

status: ## muestra estado de los contenedores
	@echo "Estado de los servicios:"
	@docker compose -f compose/docker-compose.yml ps

pull-images: ## pre-descarga imágenes base
	@echo "Descargando imágenes base..."
	docker pull postgres:16-alpine
	docker pull python:3.11-slim

check: ## valida prerequisitos (Docker, puertos, etc)
	@echo "Validando entorno..."
	@command -v docker >/dev/null 2>&1 || { echo "Docker no instalado"; exit 1; }
	@docker compose version >/dev/null 2>&1 || { echo "Docker Compose no disponible"; exit 1; }
	@[ -f compose/.env ] || { echo "Archivo compose/.env no encontrado. Copia desde .env.example"; exit 1; }
	@echo "Entorno OK"