import tkinter as tk
import customtkinter as ctk
from tkinter import ttk
from tkinter import messagebox
import secrets
import string

# Global Variable for Icon path
# https://www.flaticon.com/free-icons/lock" Lock icons created by Pixel perfect - Flaticon
ICON_PATH = 'icon.ico'


# Password add window
class AddPasswordDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.iconbitmap(ICON_PATH)
        self.title("Add a new password")
        self.geometry("300x230")

        # Make this window modal
        self.transient(parent)  # Set to be the transient window of the parent
        self.grab_set()  # Grab all events
        self.focus_force()  # Force focus on this window

        # Widgets
        # Site entry
        self.site_entry = ctk.CTkEntry(self, placeholder_text="Page name:")
        self.site_entry.pack(pady=4)

        # Username and email entry
        self.user_entry = ctk.CTkEntry(self, placeholder_text="Username or email:")
        self.user_entry.pack(pady=4)

        # Password entry
        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*")
        self.password_entry.pack(pady=4)

        # Submit button
        submit_button = ctk.CTkButton(self, text="Add", command=self.submit)
        submit_button.pack(pady=4)

        # Show password button
        self.show_password_button = ctk.CTkButton(self, text="Show Password", command=self.toggle_password_visibility)
        self.show_password_button.pack(pady=4)

        # Random password button
        generate_password_button = ctk.CTkButton(self, text="Generate Random Password", command=self.generate_password)
        generate_password_button.pack(pady=4)
        self.is_password_shown = False # By default the password is hidden

        self.result = None

        # Binding the enter key for the "ADD" button
        self.bind("<Return>", self.submit)


    # Show password method
    def toggle_password_visibility(self):
        if self.is_password_shown:
            self.password_entry.configure(show="*")
            self.show_password_button.configure(text="Show Password")
            self.is_password_shown = False
        else:
            self.password_entry.configure(show="")
            self.show_password_button.configure(text="Hide Password")
            self.is_password_shown = True

    # Random password method
    def generate_password(self):
        random_password = generate_random_password()
        self.password_entry.delete(0, tk.END) #Empty password entry
        self.password_entry.insert(0, random_password) # Inserting new password to the entry


    # Submit method
    def submit(self, event=None): # We need the event=None parameter for the "Enter" button to work
        site = self.site_entry.get()
        username = self.user_entry.get()
        password = self.password_entry.get()
        if site and password:
            self.result = (site, password, username)
            self.destroy()
        else:
            messagebox.showerror("Error", "Fill out every line!")


# Main window
class PasswordManagerApp(ctk.CTk):
    def __init__(self):

        super().__init__()
        self.title("Password Manager")
        self.geometry('600x400')

        self.iconbitmap(ICON_PATH)
        
        self.accounts = []  # For storing data

        # Custom tkinter settings
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        # List for the passwords
        self.listbox = tk.Listbox(self)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        add_button = ctk.CTkButton(self, text="Add a new password", command=self.open_add_password_dialog)
        add_button.pack(fill=tk.X, pady=2)
        
        show_button = ctk.CTkButton(self, text="Show password", command=self.show_password)
        show_button.pack(fill=tk.X)

        # Calling mainloop
        self.mainloop()
        
    def open_add_password_dialog(self):
        dialog = AddPasswordDialog(self)
        self.wait_window(dialog)  # Wait for the password add window to close

        if dialog.result:
            site, password, username = dialog.result
            self.accounts.append({'site': site, 'username': username, 'password': password})
            messagebox.showinfo("Info", "Account added")
            self.update_listbox()
        
    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for account in self.accounts:
            self.listbox.insert(tk.END, account['site'])
            
    def show_password(self):
        try:
            selection_index = self.listbox.curselection()[0] # Currently selected index
            account = self.accounts[selection_index]  # Selected account dict
            messagebox.showinfo(account['site'], f"Username/Email: {account['username']}\nPassword: {account['password']}")
        except IndexError:
            messagebox.showerror("Error", "Please select an entry from the list")



# Functions
def generate_random_password(length=20):

    # Possible characters: Letters, Numbers, Special characters
    characters = string.ascii_letters + string.digits + string.punctuation

    # Choosing random characters from characters variable
    password = ''.join(secrets.choice(characters) for i in range(length))
    return password



# Run Gui
app = PasswordManagerApp()
