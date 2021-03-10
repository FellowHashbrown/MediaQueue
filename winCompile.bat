IF EXIST "MediaQueue.exe" (
    DEL "MediaQueue.exe"
)
pyinstaller main.spec -w -F
MOVE /y .\dist\MediaQueue.exe .\MediaQueue.exe
RMDIR .\dist /s /q
RMDIR .\build /s /q