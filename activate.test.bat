@echo off

:: [Warning] activate venv(python 32-bit) in cmd with administrator mode
:: You can create virtual env with the command `python -m venv venv`

:: set Environment variables
set EFRIEND_HOME=%cd%
set EFRIEND_CONF=%cd%/config.test.yml
set EFRIEND_PASSWORD=Dmazhffk1!!

:: Activate Python
%cd%\venv\Scripts\activate