IF EXIST "MediaQueue.exe" (
    DEL "MediaQueue.exe"
)
python3.8 setup.py py2exe
MOVE /y .\dist\MediaQueue.exe .\MediaQueue.exe
RMDIR .\dist /s /q
RMDIR .\build /s /q