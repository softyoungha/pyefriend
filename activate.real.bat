@echo off

:: [Warning] activate venv(python 32-bit) in cmd with administrator mode
:: You can create virtual env with the command `python -m venv venv`

:: set Environment variables
set EFRIEND_HOME=%cd%
set EFRIEND_CONF=%cd%/config.real.yml
set EFRIEND_PASSWORD=password

:: Activate Python
%cd%\venv\Scripts\activate