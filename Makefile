.DEFAULT_GOAL := help

QUARTO ?= quarto
PYTHON ?= $(shell pyenv which python 2>/dev/null || command -v python3)
QUARTO_PYTHON ?= $(PYTHON)

export QUARTO_PYTHON

.PHONY: help check-env sync-shared site preview clean

help: ## Показать цели сборки
	@printf '%s\n' 'Доступные цели:'
	@awk 'BEGIN {FS = ":.*## "}; /^[a-zA-Z0-9_.-]+:.*## / {printf "  %-14s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

check-env: ## Проверить Quarto и Python
	@command -v "$(QUARTO)" >/dev/null 2>&1 || { echo "Не найден quarto: $(QUARTO)"; exit 1; }
	@if ! command -v "$(PYTHON)" >/dev/null 2>&1 && [ ! -x "$(PYTHON)" ]; then \
	  echo "Не найден Python: $(PYTHON)"; exit 1; \
	fi

sync-shared: check-env ## Обновить общие RevealJS-ресурсы из ../neutrinohit-map
	$(PYTHON) scripts/sync_shared_assets.py

site: check-env ## Собрать страницу курса, лекции и дополнения в _site
	rm -rf _site
	$(QUARTO) render
	find _site -type f -name '*.qmd' -delete
	$(PYTHON) scripts/package_examples.py --output _site/downloads/lighthit-course-examples.zip
	test -s _site/index.html
	test -s _site/ru/slides/01_definitions.html
	test -s _site/ru/slides/02_diffusion.html
	test -s _site/ru/slides/03_isotropic_exact.html
	test -s _site/ru/exercises/index.html
	test -s _site/ru/exercises/01_definitions_exercises.html
	test -s _site/ru/exercises/02_diffusion_exercises.html
	test -s _site/ru/exercises/03_isotropic_exact_exercises.html
	test -s _site/ru/practice/index.html
	test -s _site/ru/practice/01_medium.html
	test -s _site/ru/practice/02_diffusion.html
	test -s _site/ru/practice/03_flash.html
	test -s _site/downloads/lighthit-course-examples.zip

preview: check-env ## Локальный предпросмотр сайта курса
	$(QUARTO) preview

clean: ## Удалить воспроизводимые результаты сборки
	rm -rf _site .quarto .make-tmp
