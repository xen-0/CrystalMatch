CALL virtualenv --python=\Python27\python.exe %0\..\ExtFocusImgSrvVenv
IF errorlevel 1 (
    SET output=Could not install requirements - please check Python2.7 is at the default location and virtualenv is installed: \Python27\python.exe
) ELSE (
    CALL %0\..\ExtFocusImgSrvVenv\Scripts\activate
    IF errorlevel 1 (
        SET output=Could not start Virtual Environment.
    ) ELSE (
        CALL pip install -r %0\..\requirements.txt
        IF errorlevel 1 (
            SET output=Could not install requirements.
        ) ELSE (
            SET output=Installation Complete!
        )
    )
)
ECHO %output%
PAUSE
