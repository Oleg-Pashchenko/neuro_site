import pyautogui
import speech_recognition as sr


# Функция для нажатия ЛКМ
def click_lkm():
    pyautogui.click()


# Функция для распознавания команды "skip"
def recognize_command(recognizer, microphone):
    with microphone as source:
        print("Скажите команду:")
        audio = recognizer.listen(source, timeout=3)
        
        try:
            command = recognizer.recognize_google(audio).lower()
            print(f"Вы сказали: {command}")
            if "skip" in command:
                click_lkm()
        except sr.UnknownValueError:
            print("Извините, не удалось распознать команду.")
        except sr.RequestError:
            print("Произошла ошибка при запросе к службе распознавания речи.")


if __name__ == "__main__":
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    while True:
        recognize_command(recognizer, microphone)
