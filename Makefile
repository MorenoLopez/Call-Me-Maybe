# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Makefile                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: horarivo <horarivo@student.42antananari    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/10/20 09:58:02 by horarivo          #+#    #+#              #
#    Updated: 2026/10/23 06:59:11 by horarivo         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #


install:
	uv sync

test:
	uv run python src/explore.py --functions_definition data/input/functions_definition.json --input data/input/function_calling_tests.json --output data/output/function_calls.json

run:
	uv run python -m src --functions_definition data/input/functions_definition.json --input data/input/function_calling_tests.json --output data/output/function_calls.json

debug:
	uv run python -m pdb src --functions_definition data/input/functions_definition.json --input data/input/function_calling_tests.json --output data/output/function_calls.json

clean:
	rm -rf __pycache__ .mypy_cache .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete


lint:
	flake8 src/
	mypy src/ --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 src/
	mypy src/ --strict

.PHONY: install run debug clean lint lint-strict
