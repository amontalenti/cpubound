python: # run python REPL (under uv)
	uv run python

ipython: # run ipython console (under uv)
	uv run ipython

run: # run python program (under uv)
	uv run main.py

help: # show help for each of the Makefile recipes
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

# `make help` idea: see https://dwmkerr.com/makefile-help-command/
