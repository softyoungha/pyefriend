@echo off

:: [Warning] activate venv(python 32-bit) in cmd with administrator mode
:: You can create virtual env with the command `python -m venv venv`

:: set Environment variables
set REBAL_HOME=%cd%
set REBAL_CONF=%cd%/config.real.yml
set REBAL_PASSWORD=password

:: Activate Python
%cd%\venv\Scripts\activate