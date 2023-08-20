import difflib
from collections import UserDict
import pickle
from rich.console import Console
from rich.table import Table
from abc import ABC, abstractmethod


class Tag:

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

    def __repr__(self):
        return f"{self.value}"

    def __getstate__(self):
        return self.value

    def __setstate__(self, state):
        self.value = state


class Tags:

    def __init__(self):
        self.tags = []

    def __str__(self):
        return ", ".join(str(tag) for tag in self.tags)

    def __repr__(self):
        return f"{self.tags}"

    def __getstate__(self):
        return self.tags

    def __setstate__(self, state):
        self.tags = state

    def __iter__(self):
        return iter(self.tags)


class Note:

    def __init__(self, note_text):
        self.note_text = note_text

    def __str__(self):
        return self.note_text

    def __repr__(self):
        return f"{self.note_text}"

    def __getstate__(self):
        return self.note_text

    def __setstate__(self, state):
        self.note_text = state




class Command(ABC):
    @abstractmethod
    def execute(self):
        pass

class NoteBook:
    def __init__(self):
        self.data = {}  # Словник для зберігання нотаток та їх тегів
        self.load()  # Завантаження даних з файлу під час створення об'єкта

    def execute_command(self, command):
        result = command.execute()
        if result:
            print(result)

    def add_note(self, note, tags):
        self.data[note] = tags

    def save(self, filename='notebook_data.pkl'):
        with open(filename, 'wb') as f:
            pickle.dump(self.data, f)

    def load(self, filename='notebook_data.pkl'):
        try:
            with open(filename, 'rb') as f:
                data = pickle.load(f)
                if not isinstance(data, dict):
                    raise TypeError('Invalid data type')
                self.data = data
        except (FileNotFoundError, TypeError):
            self.data = {}

    def show_notes(self):
        n = 1
        console = Console()
        table = Table(show_header=True, header_style="bold magenta", width=60, show_lines=True)
        table.add_column("#", max_width=None)
        table.add_column("Note", width=20, no_wrap=False)
        table.add_column("Tags")

        for key, tags in self.data.items():
            table.add_row(str(n), str(key), ", ".join(str(t) for t in self.data[key]))
            n += 1

        console.print(table)

    def edit_note(self):
        print("\n***Edit func***")
        self.show_notes()

        x = input("\nChoose the note you want to edit by number ('0' - to exit delete func):\n>>> ")

        try:
            x = int(x)
            keys = list(self.data.keys())
            if 1 <= x <= len(keys):
                note_to_edit = keys[x - 1]
                new_note = input(f"\nEnter the new content for note '{note_to_edit}': ")
                new_tags = input(
                    f"\nEnter the new tags for note '{note_to_edit}' (comma-separated): ").split(",")

                self.data[new_note] = [tag.strip() for tag in new_tags]
                if note_to_edit != new_note:
                    del self.data[note_to_edit]
                print(f"\nNote '{note_to_edit}' has been updated.")
            elif x == 0:
                return 'Exit "Edit func" success'
            else:
                print("\n***Ooops***\nInvalid input. Please choose a valid number.")
                self.edit_note()
        except ValueError:
            print("\n***Ooops***\nInvalid input. Please enter a number.")
            self.edit_note()

    def search_note(self, text):
        found_fields = []
        for key, value in self.data.items():
            if str(key).find(text) != -1:
                found_fields.append((key, value))

        console = Console()
        table = Table(show_header=True, header_style="bold magenta", width=60, show_lines=True)
        table.add_column("Note", width=20, no_wrap=False)
        table.add_column("Tags")

        for obj in found_fields:
            str_tags = ", ".join(str(tag) for tag in obj[1])  # Перетворення об'єктів Tag на рядки
            table.add_row(str(obj[0]), str_tags)

        if found_fields:
            return console.print(table)
        else:
            return console.print("\n***Ooops***\nNo matching found.")

    def search_tag(self, text):
        found_tags = []

        for key, value in self.data.items():
            tag_lst = ', '.join(str(v) for v in value)
            if text in tag_lst:
                found_tags.append((str(key), tag_lst))

        console = Console()
        table = Table(show_header=True, header_style="bold magenta", width=60, show_lines=True)
        table.add_column("Key", width=20, no_wrap=False)
        table.add_column("Tags")

        for obj in found_tags:
            table.add_row(str(obj[0]), str(obj[1]))

        if found_tags:
            return console.print(table)
        else:
            return console.print("\n***Ooops***\nNo matching found.")


class AddNoteCommand(Command):
    def __init__(self, note_book):
        self.note_book = note_book

    def execute(self):
        user_input_note = input('\n***Add func***\nInput your note ("0" - to exit add func):\n>>>')
        
        if user_input_note == "0":
            return 'Exit "Add func" success'
        elif not user_input_note:
            print("\nEmpty note not allowed")
            return 'Add func failed'
        else:
            user_input_tags = input('\nInput tags for the note (comma-separated):\n>>>')
            user_input_tags = user_input_tags.strip().split(',')
            tags = Tags()
            for user_tag in user_input_tags:
                tag = Tag(user_tag.strip())
                tags.tags.append(tag)
            note = Note(user_input_note)
            self.note_book.add_note(note, tags)
            return "Note has been added"


class DeleteNoteCommand(Command):
    def __init__(self, note_book):
        self.note_book = note_book

    def execute(self):
        self.note_book.show_notes()  # Виводимо список нотаток перед видаленням
        x = input("\n***Delete func***\nChoose the note you want to delete by number ('0' - to exit delete func):\n>>> ")

        try:
            x = int(x)
            keys = list(self.note_book.data.keys())
            if 1 <= x <= len(keys):
                note_to_delete = keys[x - 1]
                del self.note_book.data[note_to_delete]
                print(f"\nNote '{note_to_delete}' has been deleted.")
            elif x == 0:
                return 'Exit "Delete func" success'
            else:
                print("\n***Ooops***\nInvalid input. Please enter a valid number.")
                self.execute()  # Викликати метод execute знову
        except ValueError:
            print("\n***Ooops***\nInvalid input. Please enter a number.")
            self.execute()  # Викликати метод execute знову


class ShowNotesCommand(Command):
    def __init__(self, note_book):
        self.note_book = note_book
    
    def execute(self):
        return self.note_book.show_notes()
    

class ChangeNoteCommand(Command):
    def __init__(self, note_book):
        self.note_book = note_book
    
    def execute(self):
        return self.note_book.edit_note()
    

class SearchCommand(Command):
    def __init__(self, note_book):
        self.note_book = note_book
    
    def execute(self):
        user_choice = input("\n***Search***\nEnter '1' to search in note\nEnter '2' to search in tags\n>>>")
        if user_choice == "1" or user_choice == "2":
            search_key = input("Enter a search keyword\n>>>")
            if user_choice == '1':
                return self.note_book.search_note(search_key)
            elif user_choice == '2':
                return self.note_book.search_tag(search_key)
            else:
                return "Wrong input"
        else:
            print("\n***Ooops***\nWrong input")
            SearchCommand()


class HelpMenuCommand(Command):
    def __init__(self, note_book, note_commands):  # Додайте note_commands як аргумент
        self.note_book = note_book
        self.note_commands = note_commands  # Збережіть словник команд

    def execute(self):
        console = Console()
        table = Table(show_header=True, header_style="bold magenta", width=60, show_lines=False)
        table.add_column("Command", max_width=None, no_wrap=False)
        table.add_column("Description", width=20, no_wrap=False)

        for func_name, func in self.note_commands.items():  # Використовуйте self.note_commands
            table.add_row(str(func_name), str(func[1]))

        console.print(table)

def exit_notes():
    pass

note_commands = {
    "add": [AddNoteCommand, 'to add note'],
    "delete": [DeleteNoteCommand, 'to delete note'],
    "edit": [ChangeNoteCommand, 'to edit note'],
    "search": [SearchCommand, 'to search note'],
    "show all": [ShowNotesCommand, 'to output all notes'],
    'help': [HelpMenuCommand, 'to see list of commands'],
    "0 or exit": [exit_notes, 'to exit']
}



def pars(txt_comm: str, command_dict):
    command = None
    for key in command_dict.keys():
        if txt_comm.startswith(key):
            command = key
    return command


def command_handler(user_input, commands):
    if user_input in commands:
        return commands[user_input][0]()
    possible_command = difflib.get_close_matches(user_input, commands, cutoff=0.5)
    if possible_command:
        return f'Wrong command. Maybe you mean: {", ".join(possible_command)}'
    else:
        return f'Wrong command.'


def instruction(command_dict):
    console = Console()
    table = Table(show_header=True, header_style="bold magenta", width=60, show_lines=False)
    table.add_column("Command", max_width=None, no_wrap=False)
    table.add_column("Description", width=20, no_wrap=False)

    for func_name, func in command_dict.items():
        table.add_row(str(func_name), str(func[1]))

    console.print(table)


def notes_main():
    print("\n\n***Hello I`m a notebook.***\n")
    nb = NoteBook()
    nb.execute_command(note_commands["help"][0](nb, note_commands))
    nb.load()

    for command_name, command_info in note_commands.items():
        if command_name == 'help':
            command_info[0].note_commands = note_commands  # Передайте словник команд у HelpMenuCommand
        else:
            command_info[0].note_book = nb

    while True:
        user_input_command = str(input("\nInput a command:\n>>>"))
        command = pars(user_input_command.lower(), note_commands)
        
        if user_input_command in ("exit", "0"):
            nb.save()
            print('Notebook closed')
            break
        elif user_input_command == 'help':
            nb.execute_command(note_commands["help"][0](nb, note_commands))
        else:
            if command and command in note_commands:
                nb.execute_command(note_commands[command][0](nb))
            else:
                print("Invalid command.")

if __name__ == "__main__":
    print("hello")
    notes_main()