call ExtFocusImgSrvVenv\Scripts\activate
if errorlevel 1 (
    ECHO Could not start Virtual Environment.
    PAUSE
) ELSE (
    call cmd /K python service_start.py
)