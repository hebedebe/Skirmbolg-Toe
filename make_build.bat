pyinstaller main.py --hide-console minimize-early --name "Skirmbolg & Toe" --splash "assets/toe/idle/idle1.png" -y
rmdir "gamedata/savedata" /s /q
mkdir "gamedata/savedata"
mkdir "dist/Skirmbolg & Toe/gamedata"
mkdir "dist/Skirmbolg & Toe/engine/textures"
mkdir "dist/Skirmbolg & Toe/assets"
mkdir "dist/Skirmbolg & Toe/_internal/samplerate"
xcopy "gamedata" "dist/Skirmbolg & Toe/gamedata" /s /e /h /y
xcopy "engine/textures" "dist/Skirmbolg & Toe/engine/textures" /s /e /h /y
xcopy "assets" "dist/Skirmbolg & Toe/assets" /s /e /h /y
xcopy ".venv/Lib/site-packages/samplerate" "dist/Skirmbolg & Toe/_internal/samplerate" /s /e /h /y
copy "./ui_theme.json" "./dist/Skirmbolg & Toe/_internal/" /Y
