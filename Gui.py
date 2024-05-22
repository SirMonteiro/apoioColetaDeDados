"""apoioColetaDeDados GUI module"""
from tkinter import (
    Button,
    Frame,
    Label,
    Text,
    StringVar,
    Tk,
    END,
    CENTER,
)
from time import strftime


class GUI(Tk):
    """GUI class to be used as a graphical user interface for program"""

    def __init__(self, button_callback, points=16):
        Tk.__init__(self)
        self.title("apoioColetaDeDados")
        self.geometry("480x320")
        # self.attributes("-fullscreen", True)  # Makes the window fullscreen

        # Title of the window
        title_label = Label(
            self, text="Apoio Coleta de dados - Medidor de tensão elétrica"
        )
        title_label.grid(row=0, columnspan=4)

        self.clock_text = StringVar(value="01/01/1970 0:00:00")
        clock_label = Label(self, textvariable=self.clock_text)
        clock_label.grid(row=0, column=4, columnspan=1)

        # Divisor line
        divisor = Frame(self, height=1, bg="black")
        divisor.grid(row=1, sticky="we", columnspan=5)

        # table headers
        last_measurement_label = Label(self, text="Última medição")
        last_measurement_label.grid(row=2, column=0)

        point1_label = Label(self, text="Ponto")
        point1_label.grid(row=2, column=1)
        voltage1_label = Label(self, text="Tensão")
        voltage1_label.grid(row=2, column=2)

        if points > 8:
            point2_label = Label(self, text="Ponto")
            point2_label.grid(row=2, column=3)
            voltage2_label = Label(self, text="Tensão")
            voltage2_label.grid(row=2, column=4)

        self.timestamp_text = StringVar(value="Esperando aferição...")
        widget_timestamp = Label(
            self, textvariable=self.timestamp_text
        )  # Create a new timestamp widget
        widget_timestamp.grid(row=3, column=0)  # Place the new timestamp widget

        for i in range(5):
            self.grid_columnconfigure(i, weight=1)

        # question label
        question_label = Label(
            self,
            text="Deseja realizar uma aferição manual?",
            fg="red",
            font=("Helvetica", 16),
        )
        question_label.place(relx=0.5, rely=0.725, anchor=CENTER)

        # manual trigger button
        button = Button(
            self,
            text="Aferição manual",
            width=20,
            height=2,
            command=button_callback,
        )
        button.place(relx=0.5, rely=0.85, anchor=CENTER)

        # doubts label
        doubts_label = Label(
            self,
            text="Dúvidas? Entre em contato com o Gabriel",
            fg="blue",
            font=("Helvetica", 10),
        )
        doubts_label.place(relx=0.5, rely=0.97, anchor=CENTER)

        # Inicialize clock
        self.update_clock()

        for i in range(1, points + 1):
            self.change_measurement(i, "Esperando...")

    def update_clock(self):
        """Update the clock text with the current time"""
        self.clock_text.set(strftime("%F %H:%M:%S"))
        self.after(1000, self.update_clock)

    def clear_grid(self, row, column):
        """Destroy all widgets in the specified row and column
        Parameters
        ----------
        row : int, required
            row of the widgets to be destroyed
        column : int, required
            column of the widgets to be destroyed
        """

        # Get all widgets in the specified row and column
        widgets = self.grid_slaves(row=row, column=column)
        for widget in widgets:
            widget.destroy()  # Destroy each widget

    def change_timestamp(self, timestamp):
        """Change the timestamp text with the specified text
        Parameters
        ----------
        timestamp : str, required
            timestamp to be displayed
        """
        self.timestamp_text.set(str(timestamp))

    def change_measurement(self, point, voltage):
        """Change the measurement text with the specified text
        Parameters
        ----------
        point : int, required
            point to be displayed
        voltage : float, required
            voltage to be displayed
        """
        column_offset = 2 if point > 8 else 0
        row_offset = point - 8 if point > 8 else point

        self.clear_grid(2 + row_offset, 1 + column_offset)
        self.clear_grid(2 + row_offset, 2 + column_offset)

        widget_point = Label(self, text=str(point))
        widget_point.grid(row=2 + row_offset, column=1 + column_offset)
        widget = Label(self, text=str(voltage) + " V")
        widget.grid(row=2 + row_offset, column=2 + column_offset)

    class FRAME(Frame):
        """Frame class to be used as a popup"""

        def __init__(self):
            Frame.__init__(self, bg="#f5f5f5")
            self.place(relx=0.01, rely=0.01, relwidth=0.98, relheight=0.98)

            # Create a textarea inside the frame
            self.text_widget = Text(
                self,
                state="disabled",
                width=450,
                bg="#f5f5f5",
                padx=4,
            )
            self.text_widget.pack(fill="both", expand=True)

        def append_text(self, t):
            """Append text to the text widget and auto scroll when needed
            Parameters
            ----------
            t : str, required
                text to append
            """
            self.text_widget.configure(state="normal")
            self.text_widget.insert(END, str(t))
            self.text_widget.see("end")
            self.text_widget.configure(state="disabled")

        def destroy_frame(self):
            """Destroy the frame"""
            self.destroy()

# GUI(1).mainloop()
