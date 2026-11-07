# HUB для Android — проект APK-обёртки

Полноэкранный WebView вокруг офлайн-платформы (assets/index.html).
Вход с выбором роли (админ/сотрудник/пользователь) уже внутри HUB.

## Сборка (любой компьютер с Android Studio)
1. Установи Android Studio (developer.android.com/studio).
2. File → Open → выбери папку `android/`.
3. Дождись синхронизации Gradle.
4. Build → Build Bundle(s)/APK(s) → **Build APK(s)**.
5. Готовый файл: `app/build/outputs/apk/debug/app-debug.apk` —
   скинь на телефон и установи (разреши «неизвестные источники»).

## Командой (без студии)
Нужен JDK 17 и Android SDK; затем:
```
cd android
gradle assembleDebug      # или ./gradlew после gradle wrapper
```
