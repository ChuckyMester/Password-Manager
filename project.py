import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import customtkinter as ctk
import secrets
import string

# Global Variable for Icon path
# https://www.flaticon.com/free-icons/lock" Lock icons created by Pixel perfect - Flaticon
ICON_PATH = 'icon.ico'


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
        self.in_start_pos = True  # Indicates, if the panel is in the starting position

        # Layout
        self.place(relx=self.start_pos, rely=0.9, relwidth=self.width, relheight=0.1)
    
    def animate(self):
        if self.in_start_pos:
            self.animate_forward()
        else:
            self.animate_backwards()

    def animate_forward(self):
        if self.pos > self.end_pos:
            self.pos -= 0.01  # Setting the animation speed
            self.place(relx=self.pos, rely=0.9, relwidth=self.width, relheight=0.1)
            self.after(10, self.animate_forward)  # Delay for the animation
        else:
            self.in_start_pos = False
            self.after(1000, self.animate_backwards)  # Waiting to start the backward animation

    def animate_backwards(self):
        if self.pos < self.start_pos:
            self.pos += 0.01  # Setting the animation speed
            self.place(relx=self.pos, rely=0.9, relwidth=self.width, relheight=0.1)
            self.after(10, self.animate_backwards)  # Delay for the animation
        else:
            self.in_start_pos = True


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

        # Main frame for the treeview and the buttons
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Left frame for the treeview
        self.tree_frame = ctk.CTkFrame(self.main_frame)
        self.tree_frame.pack(side='left', fill='both', expand=True)

        # Creating the treeview in the left frame
        self.tree = ttk.Treeview(self.tree_frame, columns=('Site', 'Username', 'Password'), show="headings")
        self.tree.pack(side='left', fill='both', expand=True)
        
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
        self.add_button = ctk.CTkButton(self.button_frame, text="Add a new password", command=self.open_add_password_dialog)
        self.add_button.pack(fill='x', pady=2)
        
        self.show_button = ctk.CTkButton(self.button_frame, text="Show password", command=self.show_password)
        self.show_button.pack(fill='x', pady=2)

        # Slide panel for the copy message
        panel_bg_color = '#56fc82'
        self.slide_panel = SlidePanel(self, 1.0, 0.7, panel_bg_color)
        self.copy_message = ctk.CTkLabel(self.slide_panel, text='Entry copied successfully', fg_color=panel_bg_color).pack(expand=True, fill='both', padx=2, pady=10)

        # Calling mainloop
        self.mainloop()
        

    def open_add_password_dialog(self):
        dialog = AddPasswordDialog(self)
        self.wait_window(dialog)  # Wait for the password add window to close

        if dialog.result:
            site, password, username = dialog.result
            self.accounts.append({'site': site, 'username': username, 'password': password, 'show_password': False})
            messagebox.showinfo("Info", "Account added")
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



# Functions
def generate_random_password(length=20):

    # Possible characters: Letters, Numbers, Special characters
    characters = string.ascii_letters + string.digits + string.punctuation

    # Choosing random characters from characters variable
    password = ''.join(secrets.choice(characters) for i in range(length))
    return password



# Run Gui
app = PasswordManagerApp()
