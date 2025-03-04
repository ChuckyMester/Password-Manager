import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog
import customtkinter as ctk
import secrets
import string
from cryptography.fernet import Fernet
import base64
import os
import sys
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Global Variable for Icon path
# https://www.flaticon.com/free-icons/lock" Lock icons created by Pixel perfect - Flaticon
ICON_PATH = 'assets/icon.ico'
FILE_PATH = 'db.data'


# Login window at startup
class LoginDialog(simpledialog.Dialog):
    def body(self, master):
        self.geometry('350x150')
        self.title('Login')
        self.iconbitmap(ICON_PATH)
        login_frame = ttk.Frame(master)
        login_frame.pack(pady=25)
        tk.Label(login_frame, text="Password:", font=('Helvetica', 18)).grid(row=0)
        self.password_entry = tk.Entry(login_frame, show='*', width=20, font=18)
        self.password_entry.grid(row=0, column=1)
        return self.password_entry

    def apply(self):
        self.result = self.password_entry.get()


# Edit panel
class EditDialog(ctk.CTkToplevel):
    def __init__(self, parent, site, username, password, update_callback):
        super().__init__(parent)
        self.iconbitmap(ICON_PATH)
        self.title("Edit Account")
        self.geometry("400x170")

        self.parent = parent
        self.update_callback = update_callback

        # Item values: (site, username, password)
        self.site = site
        self.username = username
        self.password =  password
        self.original_site = self.site
        self.original_username = self.username

        #padding
        pad = {'padx': 5, 'pady': 5}

        # Site entry
        self.site_label = ctk.CTkLabel(self, text='Site:')
        self.site_label.grid(row=0, column=0, sticky='e', **pad)

        self.site_entry = ctk.CTkEntry(self, placeholder_text="Page name:")
        self.site_entry.insert(0, self.site)
        self.site_entry.grid(row=0, column=1, sticky='ew', **pad)

        # Username entry
        self.username_label = ctk.CTkLabel(self, text='Username:')
        self.username_label.grid(row=1, column=0, sticky='e', **pad)

        self.username_entry = ctk.CTkEntry(self, placeholder_text="Username or email:")
        self.username_entry.insert(0, self.username)
        self.username_entry.grid(row=1, column=1, sticky='ew', **pad)

        # Password entry
        self.password_label = ctk.CTkLabel(self, text='Password:')
        self.password_label.grid(row=2, column=0, sticky='e', **pad)

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password:")
        self.password_entry.insert(0, self.password)
        self.password_entry.grid(row=2, column=1, sticky='ew', **pad)

        # Update button
        self.update_button = ctk.CTkButton(self, text="Update", command=self.update_account)
        self.update_button.grid(row=3, column=0, columnspan=2, **pad)

        # Grid settings
        self.grid_columnconfigure(1, weight=1)

    def update_account(self):
        # Getting the new data, and sending it to the update method in the main class
        updated_site = self.site_entry.get()
        updated_username = self.username_entry.get()
        updated_password = self.password_entry.get()
        self.update_callback(self.original_site, self.original_username, updated_site, updated_username, updated_password)
        self.destroy()


# ToolTip Panel
class CTkToolTip(object):
    def __init__(self, widget, text='widget info'):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        "Display text in tooltip window"
        self.x, self.y, cx, cy = self.widget.bbox("insert")
        self.x += self.widget.winfo_rootx() + 25
        self.y += self.widget.winfo_rooty() + 20
        # Creates a toplevel window
        self.tipwindow = tk.Toplevel(self.widget)
        self.tipwindow.wm_overrideredirect(True)
        self.tipwindow.wm_geometry("+%d+%d" % (self.x, self.y))
        label = tk.Label(self.tipwindow, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        if self.tipwindow:
            self.tipwindow.destroy()
        self.tipwindow = None


# Slide Panel
class SlidePanel(ctk.CTkFrame):
    def __init__(self, parent, start_pos, end_pos, background_color):
        super().__init__(parent, fg_color=background_color)

        # General attributes
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.width = abs(start_pos - end_pos)

        # Animation logic
        self.pos = self.start_pos
        self.in_start_pos = True

        # Layout
        self.place(relx=self.start_pos, rely=0.9, relwidth=self.width, relheight=0.1)
    
    def animate(self):
        if self.in_start_pos:
            self.animate_forward()
        else:
            self.animate_backwards()

    def animate_forward(self):
        if self.pos > self.end_pos:
            self.pos -= 0.01 
            self.place(relx=self.pos, rely=0.9, relwidth=self.width, relheight=0.1)
            self.after(10, self.animate_forward)
        else:
            self.in_start_pos = False
            self.after(1000, self.animate_backwards)

    def animate_backwards(self):
        if self.pos < self.start_pos:
            self.pos += 0.01 
            self.place(relx=self.pos, rely=0.9, relwidth=self.width, relheight=0.1)
            self.after(10, self.animate_backwards) 
        else:
            self.in_start_pos = True


# Password add window
class AddPasswordDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.iconbitmap(ICON_PATH)
        self.title("Add new account")
        self.geometry("400x230")

        # Make this window modal
        self.transient(parent)
        self.grab_set()
        self.focus_force()

        # Entry fields container
        entry_container = ctk.CTkFrame(self)
        entry_container.pack(pady=10, padx=10, fill='both', expand=True)

        # Site entry
        self.site_entry = ctk.CTkEntry(entry_container, placeholder_text="Page name:")
        self.site_entry.pack(pady=4, fill='x')

        # Username and email entry
        self.user_entry = ctk.CTkEntry(entry_container, placeholder_text="Username or email:")
        self.user_entry.pack(pady=4, fill='x')

        # Password entry and buttons container
        self.password_container = ctk.CTkFrame(entry_container)
        self.password_container.pack(pady=4, fill='x')

        # Password entry
        self.password_entry = ctk.CTkEntry(self.password_container, placeholder_text="Password", show="*")
        self.password_entry.pack(side='left', expand=True, fill='x')

        # Show password button
        show_pass_icon = tk.PhotoImage(file='assets/resized_show.png')
        self.show_password_button = ctk.CTkButton(self.password_container, text='', image=show_pass_icon, width=40, command=self.toggle_password_visibility)
        self.show_password_button.image = show_pass_icon
        self.show_password_button.pack(side='left', padx=2)
        self.is_password_shown = False #By default the password is hidden

        # Random generate password button
        generate_password_icon = tk.PhotoImage(file='assets/resized_magic-wand.png')
        self.generate_password_button = ctk.CTkButton(self.password_container, text='', image=generate_password_icon, width=40, command=self.generate_password)
        self.generate_password_button.image = generate_password_icon
        self.generate_password_button.pack(side='left', padx=2)
        # Tooltip for the button
        CTkToolTip(self.generate_password_button, "Generate 24 character long password")

        # Submit button
        self.submit_button = ctk.CTkButton(self, text="Add account", height=50, command=self.submit)
        self.submit_button.pack(pady=4)

        self.result = None

        # Binding the enter key for the "ADD" button
        self.bind("<Return>", self.submit)


    # Show password method
    def toggle_password_visibility(self):
        if self.is_password_shown:
            self.password_entry.configure(show="*")
            self.show_password_button.configure(text='', image=tk.PhotoImage(file='assets/resized_show.png'))
            self.is_password_shown = False
        else:
            self.password_entry.configure(show="")
            self.show_password_button.configure(text='', image=tk.PhotoImage(file='assets/resized_hide.png'))
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

        # Login window
        login_dialog = LoginDialog(self)

        # Encryption
        self.encryptor = Encrypt()
        self.encryption_password = login_dialog.result

        self.title("Password Manager")
        self.geometry('700x450')

        self.iconbitmap(ICON_PATH)
        
        self.file_name = FILE_PATH
        self.accounts = self.load_accounts(self.file_name)  # For storing data

        # Custom tkinter settings
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # Main frame for the treeview and the buttons
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Left frame for the treeview
        self.tree_frame = ctk.CTkFrame(self.main_frame)
        self.tree_frame.pack(side='left', fill='both', expand=True)

        # Creating the treeview in the left frame
        self.tree = ttk.Treeview(self.tree_frame, columns=('Site', 'Username', 'Password'), show="headings")
        self.tree.pack(side='left', fill='both', expand=True)

        # Setting the treeview style
        self.treeview_style = ttk.Style()
        self.treeview_style.configure("Treeview", rowheight=30)  # Setting the height for the rows
        self.treeview_style.configure("Treeview.Heading", font=('Helvetica', 14))  # Header settings
        self.treeview_style.configure("Treeview", font=('Helvetica', 13))  # Settings for treeview elements
        
        # Setting treeview column names, and width
        self.tree.heading('Site', text='Site')
        self.tree.heading('Username', text='Username')
        self.tree.heading('Password', text='Password')

        # Treeview copy event bind for double click
        self.tree.bind('<Double-1>', self.copy_to_clipboard)

        # Right frame for the buttons
        self.button_frame = ctk.CTkFrame(self.main_frame)
        self.button_frame.pack(side='left', fill='y', padx=10)
        
        # Creating the buttons in the right frame
        # Add button
        self.add_button = ctk.CTkButton(self.button_frame, text="Add new account",fg_color='#00B026', hover_color='#008C1E', command=self.open_add_password_dialog)
        self.add_button.pack(fill='x', pady=2)
        
        # Show password button
        self.show_button = ctk.CTkButton(self.button_frame, text="Show password", command=self.show_password)
        self.show_button.pack(fill='x', pady=2)

        # Edit button
        self.edit_button = ctk.CTkButton(self.button_frame, text="Edit account", command=self.open_edit_dialog)
        self.edit_button.pack(fill='x', pady=2)

        # Delete button
        self.edit_button = ctk.CTkButton(self.button_frame, text="Delete account",fg_color='#D93033', hover_color='#910D0F', command=self.delete_account)
        self.edit_button.pack(fill='x', pady=2)

        # Slide panel for the copy message
        copy_panel_bg_color = '#00A621'
        self.slide_panel = SlidePanel(self, 1.0, 0.7, copy_panel_bg_color)
        self.copy_message = ctk.CTkLabel(self.slide_panel, text='Entry copied successfully', fg_color=copy_panel_bg_color, text_color='black').pack(expand=True, fill='both', padx=2, pady=10)

        # Slide panel for the delete message
        delete_panel_bg_color = '#B80003'
        self.delete_panel = SlidePanel(self, 1.0, 0.7, delete_panel_bg_color)
        self.delete_message = ctk.CTkLabel(self.delete_panel, text='Entry deleted succesfully', fg_color=delete_panel_bg_color, text_color='black').pack(expand=True, fill='both', padx=2, pady=10)

        # Load the data from the txt
        self.populate_treeview()

        # Calling mainloop
        self.mainloop()
        

    def open_add_password_dialog(self):
        dialog = AddPasswordDialog(self)
        self.wait_window(dialog)  # Wait for the password add window to close

        if dialog.result:
            site, password, username = dialog.result
            self.accounts.append({'site': site, 'username': username, 'password': password, 'show_password': False})
            self.save_accounts(self.file_name)
            messagebox.showinfo("Info", "Account added")
            self.update_treeview()
    

    def open_edit_dialog(self):
        selected_item = self.tree.selection()
        if selected_item:
            item_values = self.tree.item(selected_item, "values")
            site, username, password = item_values
            for account in self.accounts:
                if account['site'] == site and account['username'] == username:
                    password = account['password']
            EditDialog(self, site, username, password, self.update_account_data)
        else:
            messagebox.showwarning("Warning", "Please select an item to edit.")

    
    def update_account_data(self, original_site, original_username, site, username, password):
        for account in self.accounts:
            if account['site'] == original_site and account['username'] == original_username:
                account['site'] = site
                account['username'] = username
                account['password'] = password
                break

        # Saving the accounts data in the file
        self.save_accounts(FILE_PATH)
        
        # Refreshing the treeview
        self.update_treeview()
        

    def update_treeview(self):
        # Emptying treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Loading accounts
        for account in self.accounts:
            # Checking, if we should show the password
            if account['show_password']:
                password_display = account['password']
            else:
                # Placeholders for password
                password_display = '*' * len(account['password'])
            
            self.tree.insert('', tk.END, values=(account['site'], account['username'], password_display))



    def copy_to_clipboard(self, event):
        # Detect which row and column
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            row_id = self.tree.identify_row(event.y)
            column_id = self.tree.identify_column(event.x)
            selected_item = self.tree.item(row_id)
            values = selected_item['values']
            
            # Choosen column index
            column_index = int(column_id.replace('#', '')) - 1  # Format: '#1', '#2', etc

            if column_index == 2:  # Password is the third column
                # Finding the password by index
                account_index = self.tree.index(row_id)  # Account list index
                data_to_copy = self.accounts[account_index]['password']
            else:
                # Copy the selected column value, if it isn't the password
                data_to_copy = values[column_index]
            
            # Copy the selected item to clipboard
            self.clipboard_clear()
            self.clipboard_append(data_to_copy)
            self.slide_panel.animate()
                

    def show_password(self):
        try:
            selection_index = self.tree.selection()[0]  # Selected row index
            account_index = self.tree.index(selection_index)  # Selected index in account list
            
            # Changing the show_password in the dict
            self.accounts[account_index]['show_password'] = not self.accounts[account_index]['show_password']
            
            # Refresh the treeview for changes to take place
            self.update_treeview()
        except IndexError:
            messagebox.showerror("Error", "Please select an entry from the list")


    def delete_account(self):
        selected_items = self.tree.selection()

        response = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected account?")

        if selected_items:
                
                if response:
                    selected_item = selected_items[0] 
                    site, username, _ = self.tree.item(selected_item, 'values')
                    
                    for i, account in enumerate(self.accounts):
                        if account['site'] == site and account['username'] == username:
                            del self.accounts[i]
                            break

                    self.update_treeview()  
                    self.save_accounts(FILE_PATH)

                    self.delete_panel.animate()
        else:
            messagebox.showerror("Error", "Please select an account")



    def save_accounts(self, filename):
        with open(filename, "w") as f:
            for account in self.accounts:
                f.write(f"{account['site']},{account['username']},{account['password']}\n")
        # Encrypt the file
        self.encryptor.encrypt_file(filename, self.encryption_password)



    def load_accounts(self, filename):
        accounts = []
        try:
            self.encryptor.decrypt_file(filename, self.encryption_password)
        except:
            pass
        try:
            with open(filename, "r") as file:
                for line in file:
                    site, username, password = line.strip().split(',')
                    accounts.append({'site': site, 'username': username, 'password': password, 'show_password': False})
            self.encryptor.encrypt_file(filename, self.encryption_password)
        # If file not exists, we create it
        except FileNotFoundError:
            file_path = FILE_PATH
            with open(file_path, 'x') as file:
                pass
        # If the password is wrong
        except Exception:
            messagebox.showerror("Error", "Wrong password, access denied!")
            sys.exit()
        return accounts
    

    def populate_treeview(self):
        # Adding the data to the treeview after init
        for account in self.accounts:
            self.tree.insert('', 'end', values=(account['site'], account['username'], '*' * len(account['password'])))


    def is_file_empty(self, file_path):
        with open(file_path, 'r') as file:
            first_char = file.read(1)
            # Empty if we don't have any character to read
            if not first_char:
                return True
            else:
                return False


# Encrypting
class Encrypt():

    def derive_key(self, password: bytes, salt: bytes):
        """Key derivation from password and salt"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(password))


    def encrypt_file(self, filename: str, password: str):
        """Encrypting file with the password"""
        salt = os.urandom(16)
        key = self.derive_key(password.encode(), salt)
        fernet = Fernet(key)
        
        with open(filename, 'rb') as file:
            original_data = file.read()
        
        encrypted_data = fernet.encrypt(original_data)
        
        with open(filename, 'wb') as file:
            file.write(salt + encrypted_data)


    def decrypt_file(self,filename: str, password: str):
        """Decrypting file with the"""
        with open(filename, 'rb') as file:
            salt = file.read(16)
            encrypted_data = file.read()
        
        key = self.derive_key(password.encode(), salt)
        fernet = Fernet(key)
        decrypted_data = fernet.decrypt(encrypted_data)
        
        with open(filename, 'wb') as file:
            file.write(decrypted_data)


# Functions
def generate_random_password(length=24):

    # Possible characters: Letters, Numbers, Special characters (Except ',' because of the csv)
    characters = string.ascii_letters + string.digits + string.punctuation.replace(',', '@')

    # Choosing random characters from characters variable
    password = ''.join(secrets.choice(characters) for i in range(length))
    return password



# Run Gui
app = PasswordManagerApp()
