@echo off
title Serve MkDocs

cls

cd "%~dp0"
(
	"%~dp0.venv\Scripts\activate" || (
		python -m venv .venv && "%~dp0.venv\Scripts\activate" && pip install -r "%~dp0\requirements.txt"
	)
) && mkdocs serve
