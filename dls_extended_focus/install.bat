CALL virtualenv --python=\Python27\python.exe ExtFocusImgSrvVenv
IF errorlevel 1 (
    SET output=Python2.7 not found at expected location: \Python27\python.exe
) ELSE (
    CALL ExtFocusImgSrvVenv\Scripts\activate
    IF errorlevel 1 (
        SET output=Could not start Virtual Environment.
    ) ELSE (
        CALL pip install -r requirements.txt
        IF errorlevel 1 (
            SET output=Could not install requirements.
        ) ELSE (
            SET output=Installation Complete!
        )
    )
)
ECHO %output%
PAUSE
