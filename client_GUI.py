import Tkinter as tk
import tkFont as tkfont
import time

class clientGUI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title_font = tkfont.Font(family = 'Helvetica', size=18, weight='bold')

        self.container = tk.Frame(self)
        self.container.pack(side='top', fill='both', expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.frames['LoginPage'] = LoginPage(parent = self.container, controller=self)
        self.frames['ConvoPage'] = ConvoPage(parent=self.container, controller=self)
        self.frames['WaitPage'] = WaitPage(parent=self.container, controller=self)

        self.frames['LoginPage'].grid(row=0, column=0, sticky='nsew')
        self.frames['ConvoPage'].grid(row=0, column=0, sticky='nsew')
        self.frames['WaitPage'].grid(row=0, column=0, sticky='nsew')

        # for F in (LoginPage, StartPage, WaitPage, ConvoPage):
        #     page_name = F.__name__
        #     frame = F(parent=container, controller = self)
        #     self.frames[page_name] = frame
        #
        #     frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame("LoginPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    def show_start_page(self, name):
        self.frames['StartPage'] = StartPage(parent=self.container, controller=self, name=name)
        self.frames['StartPage'].grid(row=0, column=0, sticky='nsew')
        self.show_frame('StartPage')

    def show_login_page(self):
        frame = self.frames['LoginPage']
        frame.tkraise()

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text = "Hi, what's your name?", font = controller.title_font)
        label.pack(side = 'top', fill='x', pady=10)

        login_entry = tk.Entry(self)
        login_entry.focus_set()

        login_button = tk.Button(self, text = "Start!",
                            command = lambda: controller.show_start_page(login_entry.get()))

        login_entry.pack()
        login_button.pack()


class StartPage(tk.Frame):
    def __init__(self, parent, controller, name):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text = "Thousands of people are dying to talk to you, "+name+".\nAre you ready?", font = controller.title_font)
        label.pack(side = 'top', fill='x', pady=10)
        ready_button = tk.Button(self, text="Yes!",
                                 command=lambda: controller.show_frame('WaitPage'))
        logoff_button = tk.Button(self, text="Nah, bye!",
                                 command=lambda: controller.show_login_page())
        ready_button.pack()
        logoff_button.pack()


class WaitPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text = "Looking for a convo partner...", font = controller.title_font)
        label.pack(side = 'top', fill='x', pady=10)
        hangup_button = tk.Button(self, text="Found",
                                   command=lambda: controller.show_frame("ConvoPage"))
        hangup_button.pack()


class ConvoPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text = "<partner_name>", font = controller.title_font)
        label.pack(side = 'top', fill='x', pady=10)
        hangup_button = tk.Button(self, text="End convo",
                                 command=lambda: controller.show_frame("StartPage"))
        hangup_button.pack()

if __name__ == '__main__':
    app = clientGUI()
    app.mainloop()
