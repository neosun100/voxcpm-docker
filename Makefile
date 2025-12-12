.PHONY: help start stop restart logs build test clean

help:
	@echo "VoxCPM Docker Management"
	@echo "========================"
	@echo "make start   - Start service (auto-select GPU)"
	@echo "make stop    - Stop service"
	@echo "make restart - Restart service"
	@echo "make logs    - View logs"
	@echo "make build   - Rebuild image"
	@echo "make test    - Run tests"
	@echo "make clean   - Clean outputs"

start:
	@./start.sh

stop:
	@docker-compose down

restart:
	@docker-compose restart

logs:
	@docker-compose logs -f

build:
	@docker-compose build

test:
	@./test_deployment.sh

clean:
	@rm -rf outputs/*.wav
	@echo "✅ Cleaned output files"
