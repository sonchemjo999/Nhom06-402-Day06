PROJECT_DIR := vinmec-healthcare

.PHONY: help install setup dev start build lint prisma-generate prisma-migrate

help:
	@echo "Available targets:"
	@echo "  make setup   - Install deps and prepare .env"
	@echo "  make install - Install dependencies"
	@echo "  make dev     - Start development server"
	@echo "  make start   - Alias for dev"
	@echo "  make build   - Build production app"
	@echo "  make lint    - Run linter"
	@echo "  make prisma-generate - Generate Prisma client"
	@echo "  make prisma-migrate  - Run Prisma migrations"

install:
	cd $(PROJECT_DIR) && bun install

setup: install
	cd $(PROJECT_DIR) && [ -f .env ] || cp .env.example .env

dev:
	cd $(PROJECT_DIR) && bun run dev

start: dev

build:
	cd $(PROJECT_DIR) && bun run build

lint:
	cd $(PROJECT_DIR) && bun run lint

migration:
	cd $(PROJECT_DIR) && bun run prisma:generate && bun run prisma:migrate
