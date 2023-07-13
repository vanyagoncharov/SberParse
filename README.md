# SberParse

# Для запуска в фоне требуется:

Открыть cmd от имени администатора. Перейти в папку с файлом: nssm.exe и прописать построчно:

Создание службы Windows
nssm.exe install ServiceParse "C:\PythonProject\SberParsing\startParse.bat"

Включение логов
nssm.exe set ServiceParse AppStdout "C:\PythonProject\SberParsing\logs\stdout.log"
nssm.exe set ServiceParse AppStderr "C:\PythonProject\SberParsing\logs\stderr.log"

Старт службы
nssm.exe start ServiceParse
