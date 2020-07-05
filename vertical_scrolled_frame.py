59

My objective is to add a vertical scroll bar to a frame which has several labels in it. The scroll bar should automatically enabled as soon as the labels inside the frame exceed the height of the frame. After searching through, I found this useful post. Based on that post I understand that in order to achieve what i want, (correct me if I am wrong, I am a beginner) I have to create a Frame first, then create a Canvas inside that frame and stick the scroll bar to that frame as well. After that, create another frame and put it inside the canvas as a window object. So, I finally come up with this:

from Tkinter import *

def data():
    for i in range(50):
       Label(frame,text=i).grid(row=i,column=0)
       Label(frame,text="my text"+str(i)).grid(row=i,column=1)
       Label(frame,text="..........").grid(row=i,column=2)

def myfunction(event):
    canvas.configure(scrollregion=canvas.bbox("all"),width=200,height=200)

root=Tk()
sizex = 800
sizey = 600
posx  = 100
posy  = 100
root.wm_geometry("%dx%d+%d+%d" % (sizex, sizey, posx, posy))

myframe=Frame(root,relief=GROOVE,width=50,height=100,bd=1)
myframe.place(x=10,y=10)

canvas=Canvas(myframe)
frame=Frame(canvas)
myscrollbar=Scrollbar(myframe,orient="vertical",command=canvas.yview)
canvas.configure(yscrollcommand=myscrollbar.set)

myscrollbar.pack(side="right",fill="y")
canvas.pack(side="left")
canvas.create_window((0,0),window=frame,anchor='nw')
frame.bind("<Configure>",myfunction)
data()
root.mainloop()

    Am I doing it right? Is there better/smarter way to achieve the output this code gave me?
    Why must I use grid method? (I tried place method, but none of the labels appear on the canvas.)
    What so special about using anchor='nw' when creating window on canvas?

Please keep your answer simple, as I am a beginner.
python tkinter scrollbar frame
share
edited Mar 2 '19 at 17:52
martineau
84.9k1717 gold badges116116 silver badges216216 bronze badges
asked Apr 24 '13 at 9:32
Chris Aung
6,2522323 gold badges6969 silver badges109109 bronze badges

    2
    You have it backwards in your question, though the code looks correct at first glance. You must create a frame, embed that in the canvas, then attach the scrollbar to the canvas. – Bryan Oakley Apr 24 '13 at 11:07
    3
    possible duplicate of Adding a scrollbar to a grid of widgets in Tkinter – Trevor Boyd Smith Aug 26 '13 at 15:56
    @TrevorBoydSmith There's a lot of stuff this is a potential duplicate of, but I voted to close this as a duplicate of a different one that seems to have the best answers: stackoverflow.com/questions/1873575/… – ArtOfWarfare May 3 '15 at 15:59 

    1
    I'm extremely late, but thank you so much for this! This was the only fully-functional (and complete) example of creating a scrollable frame using only pure Tkinter (a restriction for my project). I know that wasn't your intention, but thank you! – Niema Moshiri Apr 12 '18 at 6:33

add a comment
4 Answers
Active
Oldest
Votes
23

Am i doing it right?Is there better/smarter way to achieve the output this code gave me?

Generally speaking, yes, you're doing it right. Tkinter has no native scrollable container other than the canvas. As you can see, it's really not that difficult to set up. As your example shows, it only takes 5 or 6 lines of code to make it work -- depending on how you count lines.

Why must i use grid method?(i tried place method, but none of the labels appear on the canvas?)

You ask about why you must use grid. There is no requirement to use grid. Place, grid and pack can all be used. It's simply that some are more naturally suited to particular types of problems. In this case it looks like you're creating an actual grid -- rows and columns of labels -- so grid is the natural choice.

What so special about using anchor='nw' when creating window on canvas?

The anchor tells you what part of the window is positioned at the coordinates you give. By default, the center of the window will be placed at the coordinate. In the case of your code above, you want the upper left ("northwest") corner to be at the coordinate.
share
edited May 30 '13 at 17:05
answered May 30 '13 at 16:59
Bryan Oakley
263k2828 gold badges362362 silver badges520520 bronze badges
add a comment
38

Please note that the proposed code is only valid with Python 2

Here is an example:

from Tkinter import *   # from x import * is bad practice
from ttk import *

# http://tkinter.unpythonic.net/wiki/VerticalScrolledFrame

class VerticalScrolledFrame(Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling

    """
    def __init__(self, parent, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)            

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        canvas = Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)


if __name__ == "__main__":

    class SampleApp(Tk):
        def __init__(self, *args, **kwargs):
            root = Tk.__init__(self, *args, **kwargs)


            self.frame = VerticalScrolledFrame(root)
            self.frame.pack()
            self.label = Label(text="Shrink the window to activate the scrollbar.")
            self.label.pack()
            buttons = []
            for i in range(10):
                buttons.append(Button(self.frame.interior, text="Button " + str(i)))
                buttons[-1].pack()

    app = SampleApp()
    app.mainloop()
