import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk  # install pillow with pip: pip install pillow
import subprocess

class FirstPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        load = Image.open("1.png")
        photo = ImageTk.PhotoImage(load)
        label = tk.Label(self, image=photo)
        label.image = photo
        label.place(x=0, y=0)

        border = tk.LabelFrame(
            self, text='Login', bg='ivory', bd=10, font=("Arial", 20))
        border.pack(fill="both", expand="yes", padx=150, pady=150)

        Label1 = tk.Label(border, text="Username",
                          font=("Arial Bold", 15), bg='ivory')
        Label1.place(x=50, y=20)
        Txt1 = tk.Entry(border, width=30, bd=5)
        Txt1.place(x=180, y=20)

        Label2 = tk.Label(border, text="Password",
                          font=("Arial Bold", 15), bg='ivory')
        Label2.place(x=50, y=80)
        TXT2 = tk.Entry(border, width=30, show='*', bd=5)
        TXT2.place(x=180, y=80)

        def verify():
            try:
                with open("credential.txt", "r") as f:
                    info = f.readlines()
                    i = 0
                    for e in info:
                        u, p = e.split(",")
                        if u.strip() == Txt1.get() and p.strip() == TXT2.get():
                            controller.show_frame(SecondPage)
                            i = 1
                            break
                    if i == 0:
                        messagebox.showinfo(
                            "Error", "Please provide correct username and password!!")
            except:
                messagebox.showinfo(
                    "Error", "Please provide correct username and password!!")

        BTN1 = tk.Button(border, text="Submit",
                 font=("Arial", 15), command=verify)
        BTN1.place(relx=1.0, rely=1.0, anchor=tk.SE, x=-20, y=-3)


        def register():
            window = tk.Tk()
            window.resizable(0, 0)
            window.configure(bg="deep sky blue")
            window.title("Register")
            Label1 = tk.Label(window, text="Username:", font=(
                "Arial", 15), bg="deep sky blue")
            Label1.place(x=10, y=10)
            txt1 = tk.Entry(window, width=30, bd=5)
            txt1.place(x=200, y=10)

            lbl2 = tk.Label(window, text="Password:", font=(
                "Arial", 15), bg="deep sky blue")
            lbl2.place(x=10, y=60)
            txt2 = tk.Entry(window, width=30, show="*", bd=5)
            txt2.place(x=200, y=60)

            lbl3 = tk.Label(window, text="Confirm Password:",
                            font=("Arial", 15), bg="deep sky blue")
            lbl3.place(x=10, y=110)
            txt3 = tk.Entry(window, width=30, show="*", bd=5)
            txt3.place(x=200, y=110)

            def check():
                if txt1.get() != "" or txt2.get() != "" or txt3.get() != "":
                    if txt2.get() == txt3.get():
                        with open("credential.txt", "a") as f:
                            f.write(txt1.get()+","+txt2.get()+"\n")
                            messagebox.showinfo(
                                "Welcome", "You are registered successfully!!")
                    else:
                        messagebox.showinfo(
                            "Error", "Your password didn't get match!!")
                else:
                    messagebox.showinfo(
                        "Error", "Please fill the complete field!!")

            btn1 = tk.Button(window, text="Sign in", font=(
                "Arial", 15), bg="#ffc22a", command=check)
            btn1.place(x=170, y=150)

            window.geometry("470x220")
            window.mainloop()

        BTN2 = tk.Button(self, text="Register", bg="dark orange",
                         font=("Arial", 15), command=register)
        BTN2.place(x=650, y=20)


class SecondPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        load = Image.open("2.png")
        photo = ImageTk.PhotoImage(load)
        label = tk.Label(self, image=photo)
        label.image = photo
        label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        Button = tk.Button(self, text="Next", font=(
            "Arial", 15), command=lambda: controller.show_frame(ThirdPage))
        Button.place(relx=0.9, rely=0.9, anchor=tk.SE)

        Button = tk.Button(self, text="Back", font=(
            "Arial", 15), command=lambda: controller.show_frame(FirstPage))
        Button.place(relx=0.1, rely=0.9, anchor=tk.SW)


class ThirdPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Load background image
        bg_image = Image.open("3.png")  # Replace "2.png" with the path to your background image
        bg_photo = ImageTk.PhotoImage(bg_image)

        # Create label widget to display background image
        bg_label = tk.Label(self, image=bg_photo)
        bg_label.image = bg_photo
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        Button = tk.Button(self, text="Home", font=(
            "Arial", 15), command=lambda: controller.show_frame(FirstPage))
        Button.place(x=650, y=450)

        Button = tk.Button(self, text="Back", font=(
            "Arial", 15), command=lambda: controller.show_frame(SecondPage))
        Button.place(x=100, y=450)

        button_frame = tk.Frame(self, bg="yellow")
        button_frame.place(relx=0.5, rely=0.95, anchor=tk.CENTER)

        button = tk.Button(button_frame, fg="black", bg="yellow", width=25, text="Start Program", command=self.run_program)
        button.pack()

    def run_program(self):
        try:
            # Replace 'path/to/your/program.py' with the actual path to your Python script
            subprocess.run(['python', "system.py"])
        except FileNotFoundError:
            print("Error: The specified program script was not found.")
        except Exception as e:
            print(f"Error: {e}")


class Application(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        # creating a window
        window = tk.Frame(self)
        window.pack()

        window.grid_rowconfigure(0, minsize=500)
        window.grid_columnconfigure(0, minsize=800)

        self.frames = {}
        for F in (FirstPage, SecondPage, ThirdPage):
            frame = F(window, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(FirstPage)

    def show_frame(self, page):
        frame = self.frames[page]
        frame.tkraise()
        self.title("Application")


app = Application()
app.maxsize(800, 500)
app.mainloop()
