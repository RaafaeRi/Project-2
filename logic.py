from PyQt6.QtWidgets import QMainWindow
from IDReg import Ui_MainWindow as IDRegUI
from addview import Ui_MainWindow as AddViewUI
from addCon import Ui_MainWindow as AddConUI
from contacts import Ui_MainWindow as ContactsUI

# ID File checks for who can enter the program
# Contacts file is where all contact info is stored
idFile = "contact_id.txt"
contactFile = "contacts.txt"


def makeFiles() -> None:
    '''
    Makes needed files, if not already created.  
    Starts immediately when the app starts.
    '''
    try:
        open(idFile, "a").close()
        open(contactFile, "a").close()
    except:
        pass


def getId() -> str:
    '''
    Gets the saved ID from file
    Only used during login for input match
    '''
    try:
        file = open(idFile, "r")
        oldId = file.read().strip()
        file.close()
        return oldId
    except:
        return ""


def getContacts():
    '''
    Gets contacts from file and returns as list
    Used for contactswindow to display the contacts, and 
    addcontactwindow for updating/editing contacts
    '''
    contacts = []

    try:
        file = open(contactFile, "r")
        lines = file.readlines()
        file.close()

        for line in lines:
            person = line.strip().split(",")

            if len(person) == 3:
                contacts.append(person)

    except:
        pass

    return contacts


def writeContacts(contacts) -> None:
    '''
    Writes contacts to file

    Rewrites full file everytime contact is added or edited
    '''
    try:
        file = open(contactFile, "w")

        for person in contacts:
            file.write(person[0] + "," + person[1] + "," + person[2] + "\n")

        file.close()
    except:
        pass


class Logic(QMainWindow):
    def __init__(self) -> None:
        '''
        Sets up ID Screen

        Creates the files, loads the GUI, and connects the enter button to checkId
        '''
        super().__init__()

        makeFiles()

        self.ui = IDRegUI()
        self.ui.setupUi(self)

        self.nextWindow = None

        self.ui.EnterButton.clicked.connect(self.checkId)

    def checkId(self) -> None:
        '''
        Checks the ID against file

        If file is empty, first valid 8-digit ID becomes saved
        If ID is already saved, same ID needs to be re-entered
        Screen goes to Add/View Window after ID is valid
        '''
        userId = self.ui.IDLine.text()

        if len(userId) != 8:
            self.ui.label_error.setText("Enter valid ID")
            return

        if not userId.isdigit():
            self.ui.label_error.setText("Enter valid ID")
            return

        oldId = getId()

        if oldId == "":
            try:
                file = open(idFile, "w")
                file.write(userId)
                file.close()
            except:
                self.ui.label_error.setText("File error")
                return

        elif userId != oldId:
            self.ui.label_error.setText("Wrong ID")
            return

        self.nextWindow = AddViewWindow()
        self.nextWindow.show()
        self.close()


class AddViewWindow(QMainWindow):
    def __init__(self) -> None:
        '''
        Sets up add/view screen, sends user to add or view screen depending on input
        '''
        super().__init__()

        self.ui = AddViewUI()
        self.ui.setupUi(self)

        self.nextWindow = None

        self.ui.addButton.clicked.connect(self.addPage)
        self.ui.remButton.clicked.connect(self.contactsPage)

    def addPage(self) -> None:
        '''
        Opens the add screen, where boxes are not filled, waiting on user input
        '''
        self.nextWindow = AddContactWindow()
        self.nextWindow.show()
        self.close()

    def contactsPage(self) -> None:
        '''
        Goes to contact list page, which reads all contacts and displays them to list
        '''
        self.nextWindow = ContactsWindow()
        self.nextWindow.show()
        self.close()


class AddContactWindow(QMainWindow):
    def __init__(self, oldContact=None) -> None:
        '''
        Opens the add/edit screen, where if there is an old contact, it fills in old information for editing
        If there is no old contact, the boxes are blank to add new contact
        '''
        super().__init__()

        self.ui = AddConUI()
        self.ui.setupUi(self)

        self.oldContact = oldContact
        self.nextWindow = None

        if oldContact != None:
            self.ui.editFirst.setText(oldContact[0])
            self.ui.editLast.setText(oldContact[1])
            self.ui.editPhone.setText(oldContact[2])

        self.ui.Enter.clicked.connect(self.addContact)

    def addContact(self) -> None:
        '''
        Adds or edits a contact by check text box values and reads the current contact file.  If it's new,
        it is appended, if it's an edit, it replaces the old contact.  Sends back to addview window
        '''
        first = self.ui.editFirst.text()
        last = self.ui.editLast.text()
        phone = self.ui.editPhone.text()

        self.ui.errorFirst.setText("")
        self.ui.errorLast.setText("")
        self.ui.errorPhone.setText("")

        bad = False

        if first == "":
            self.ui.errorFirst.setText("Required")
            bad = True

        if first != "" and not first.isalpha():
            self.ui.errorFirst.setText("Letters only")
            bad = True

        if last != "" and not last.isalpha():
            self.ui.errorLast.setText("Letters only")
            bad = True

        if not phone.isdigit():
            self.ui.errorPhone.setText("Digits only")
            bad = True

        if phone.isdigit() and len(phone) != 10:
            self.ui.errorPhone.setText("10 digits")
            bad = True

        if bad:
            return

        newContact = [first, last, phone]
        contacts = getContacts()

        if self.oldContact == None:
            contacts.append(newContact)
        else:
            for i in range(len(contacts)):
                if contacts[i] == self.oldContact:
                    contacts[i] = newContact

        writeContacts(contacts)

        self.nextWindow = AddViewWindow()
        self.nextWindow.show()
        self.close()


class ContactsWindow(QMainWindow):
    def __init__(self) -> None:
        '''
        Opens saved contacts screen, which reads contactFile and shows them in the list.
        Also lets users view specific contacts
        '''
        super().__init__()

        self.ui = ContactsUI()
        self.ui.setupUi(self)

        self.nextWindow = None
        self.selectedContact = None

        self.showList()

        self.ui.ContactList.itemClicked.connect(self.showInfo)
        self.ui.Menu.clicked.connect(self.goMenu)
        self.ui.Edit.clicked.connect(self.editIt)

    def showList(self) -> None:
        '''
        Loads contacts into list, displaying FirstName LastName
        '''
        contacts = getContacts()

        for person in contacts:
            name = person[0] + " " + person[1]
            self.ui.ContactList.addItem(name)

    def showInfo(self) -> None:
        '''
        Shows selected contact by reading full contact list again, finds the name,
        saves it in selectedContact, then displays all available contact information
        '''
        item = self.ui.ContactList.currentItem()

        if item == None:
            return

        picked = item.text()
        contacts = getContacts()

        for person in contacts:
            name = person[0] + " " + person[1]

            if name == picked:
                self.selectedContact = person

                self.ui.ConInfo.setText(
                    "First Name: " + person[0] + "\n" +
                    "Last Name: " + person[1] + "\n" +
                    "Phone Number: " + person[2]
                )

    def goMenu(self) -> None:
        '''
        Goes back to ID screen
        '''
        self.nextWindow = Logic()
        self.nextWindow.show()
        self.close()

    def editIt(self) -> None:
        '''
        From contact list, takes contact to edit, which goes back to the add contact screen,
        however it will include current contact info in the boxes to be edited and saved by user, 
        which replaces the contact in the contacts file
        '''
        if self.selectedContact == None:
            return

        self.nextWindow = AddContactWindow(self.selectedContact)
        self.nextWindow.show()
        self.close()