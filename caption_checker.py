import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
from tkinter.scrolledtext import ScrolledText

from caption_processing import valid_caption, metadata_from_caption

#Define info window
class InfoWindow(tk.Toplevel):

    def __init__(self):
        tk.Toplevel.__init__(self)

        #define window sizes
        self.geometry('500x500')
        self.minsize(500, 450)
        self.maxsize(700, 450)

        #add title
        self.infotitle = tk.Label(self,
                                  text = 'Danam Caption Guidelines',
                                  font = ('Arial', 14))
        self.infotitle.pack(pady=(3,3))

        #add scrollable text to display DANAM Caption guidelines
        self.infotext = ScrolledText(self,
                                    font = ('Arial', 12),
                                    wrap = tk.WORD
                                    )
        #text is read from howto.txt
        with open('howto.txt', 'r') as file:
            message = file.read()
        self.infotext.insert(tk.INSERT, message)

        #make text box not editable
        self.infotext.configure(state=tk.DISABLED)
        #add text box to window
        self.infotext.pack(pady=(5,5), padx=(10,10))


#Define main app window
class CaptionCheck(tk.Frame):

    ############# GUI Elements Definition ############

    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master = master

        #define info-button
        self.info_button = tk.Button(self.master,
                                        text="Caption Guidelines",
                                        comman=self.show_how_to)
        self.info_button.pack(pady=(3,3))

        #define input text box
        self.textfield = ScrolledText(self.master,
                                      font = ('Arial', 12),
                                      width=400,
                                      height=15)
        self.textfield.pack(padx=(10, 10))

        #define the two buttons in the middle in their own frame
        self.buttons_frame = tk.Frame(self.master)
        self.buttons_frame.pack(fill='both')

        self.check_button = tk.Button(self.buttons_frame,
                                      text='Check Caption',
                                      command=self.caption_button_action)

        self.clear_table = tk.Button(self.buttons_frame,
                                     text='Clear Table',
                                     command=self.clear_table_action)

        self.check_button.pack(side=tk.RIGHT, pady=(3,3), padx=3)
        self.clear_table.pack(side=tk.RIGHT, pady=(3,3), padx=3)

        ######### TABLE DEFINITION ##############
        columns = ('caption',
                   'agent',
                   'role',
                   'agent2',
                   'role2',
                   'date',
                   'source'
                   )
        #define x scrollbar and y scrollbar
        self.table_xscroll = ttk.Scrollbar(self.master, orient='horizontal')
        self.table_yscroll = ttk.Scrollbar(self.master, orient='vertical')

        self.table = ttk.Treeview(self.master,
                                  show='headings',
                                  columns=columns,
                                  height=15,
                                  xscrollcommand=self.table_xscroll.set,
                                  yscrollcommand=self.table_yscroll.set)

        self.table_yscroll.config(command=self.table.yview)
        self.table_yscroll.pack(side=tk.RIGHT, fill='both', padx=(2, 2))

        for col in columns:
            self.table.heading(col, text=col)
        self.table.pack(padx=(10, 10))

        self.table_xscroll.config(command=self.table.xview)
        self.table_xscroll.pack(fill='both', padx=(10, 10))

    ################ GUI Functions: these are functions that are called on button press ##########################
    #open info window
    def show_how_to(self):
            InfoWindow()

    #clear table
    def clear_table_action(self):
        self.table.delete(*self.table.get_children())

    #check captions
    def caption_button_action(self):
        #reset table
        self.clear_table_action()
        #read input from textbox
        input = self.textfield.get("1.0", tk.END).strip()

        if input == "":
            messagebox.showwarning("Warning", "No input given!")

        else:
            invalid_captions = []
            captions = input.split('\n')

            for caption in captions:
                print(caption)

                if valid_caption(caption):
                    #metadata = {}
                    #parts = caption.split(";")
                    #data = self.get_data(metadata_from_caption(metadata, parts))
                    #self.table.insert("", "end", values=data)
                    messagebox.showwarning("Invalid Captions", "{} is a valid caption".format(caption))
                else:
                    invalid_captions.append(str(captions.index(caption)+1))

            if len(invalid_captions) != 0:
                message = "Captions {} are incorrectly formated!".format(', '.join(invalid_captions))
                messagebox.showwarning("Invalid Captions", message)

    ############### Utility Functions #########################

    #dictionary ins set umwandeln fuer  die tabelle
    def get_data(self, data):
        return (data['caption'],
                data['agent'])

####################### Main Loop ############################

root = tk.Tk()
root.title("DANAM Caption Checker")
root.geometry("500x700")
root.minsize(500,700)
root.resizable(True,False)

app = CaptionCheck(root)
root.mainloop()
