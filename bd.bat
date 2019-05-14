@echo off
@SET DTAG=%DATE:~-10%
@SET DTAG=%DTAG:/=_%
@SET DTAG=%DTAG: =%

@SET P=%0
@SET CURDIR=%~dp0
@SET py=%~dp0..\pyenv\Scripts\python
@SET pyin=%~dp0..\pyenv\Scripts\pyinstaller
@SET pyenvstart=%~dp0..\pyenv\Scripts\activate
@SET pyenvstop=%~dp0..\pyenv\Scripts\deactivate

@SET distdir=%CURDIR%\etl_dist

REM %py% setup.py py2exe

rmdir /S /Q %distdir%

call %pyenvstart%
%pyin% --distpath %distdir% %CURDIR%\cli.spec 
call %pyenvstop%

if "%1"=="dist" call :dist

goto :eof
:dist
c:\tools\7-Zip\7z.exe a -r  -sfx7z.sfx   etl_dist.exe %distdir%
goto :eof



