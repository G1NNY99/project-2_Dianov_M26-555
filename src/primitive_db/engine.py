import prompt


def welcome():
    print("\nПервая попытка запустить проект!\n")
    print("***")

    help_text = (
        "<command> exit - выйти из программы\n"
        "<command> help - справочная информация"
    )
    print(help_text)

    while True:
        command = prompt.string("Введите команду: ").strip().lower()

        if command == "exit":
            return
        if command == "help":
            print(help_text)
        else:
            print("Неизвестная команда. Введите help для справки.")