IF EXIST "MediaQueue.exe" (
    DEL "MediaQueue.exe"
)
PyInstaller --windowed --onefile -n "MediaQueue" -i "mediaqueue.ico" --add-data "mediaqueue.ico;." MediaQueue.py
MOVE /y .\dist\MediaQueue.exe .\MediaQueue.exe
RMDIR .\dist /s /q
RMDIR .\build /s /q