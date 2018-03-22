CALL %0\..\ExtFocusImgSrvVenv\Scripts\activate
IF errorlevel 1 (
    ECHO Could not start Virtual Environment.
    PAUSE
) ELSE (
    CALL cmd /K python %0\..\service_start.py
)