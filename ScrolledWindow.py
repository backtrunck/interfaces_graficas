#https://blog.tecladocode.com/tkinter-scrollable-frames/
import tkinter as tk
import tkinter.ttk as ttk

from collections import namedtuple
HeaderField = namedtuple("HeaderField", ['label', 'width'])

class ScrolledWindow(tk.Frame):
    """
    1. Master widget gets scrollbars and a canvas. Scrollbars are connected 
    to canvas scrollregion.

    2. self.scrollwindow is created and inserted into canvas

    Usage Guideline:
    Assign any widgets as children of <ScrolledWindow instance>.scrollwindow
    to get them inserted into canvas

    __init__(self, parent, canv_w = 400, canv_h = 400, *args, **kwargs)
    docstring:
    Parent = master of scrolled window
    canv_w - width of canvas
    canv_h - height of canvas

    """


    def __init__(self, parent, canv_w = 40, canv_h = 40, scroll_h = True, scroll_v = True , header = False, *args, **kwargs):
        """
        Parent = master of scrolled window
        canv_w - width of canvas
        canv_h - height of canvas
        scroll_h - if horizontal scroll will be created
        scroll_v - if vertical scroll will be created

       """
        super().__init__(parent, *args, **kwargs)

        self.parent = parent
        
        self.canv_header = None

        self.xscrlbr = ttk.Scrollbar(self, orient='horizontal')
        if scroll_h:
            self.xscrlbr.grid(column=0, row=2, sticky='EW', columnspan=2)
        
        self.yscrlbr = ttk.Scrollbar(self)
        if scroll_v:
            self.yscrlbr.grid(column=1, row=1, sticky='NS')
        
        # creating a canvas
        self.canv = tk.Canvas(self)
        self.canv.config(relief='flat', width=canv_w, heigh=canv_h, bd=2)
        if header:
            self._set_header()
        
        # placing a canvas into frame
        self.canv.grid(column = 0, row = 1, sticky = 'EW')

        # accociating scrollbar comands to canvas scroling
        self.xscrlbr.config(command=self.canv.xview)
        self.yscrlbr.config(command=self.canv.yview)

        # creating a frame to inserto to canvas
        self.scrollwindow = ttk.Frame(self.canv, width = 10, heigh=10)


        self.canv.create_window(0, 0, window = self.scrollwindow, anchor = 'nw')
        self.canv.config(xscrollcommand=self.xscrlbr.set,
                        yscrollcommand=self.yscrlbr.set)

        self.scrollwindow.bind('<Configure>', self._configure_window)  
        self.scrollwindow.bind('<Enter>', self._bound_to_mousewheel)
        self.scrollwindow.bind('<Leave>', self._unbound_to_mousewheel)
        
        return

    def _bound_to_mousewheel(self, event):
        #self.canv.bind_all("<MouseWheel>", self._on_mousewheel)   
        self.canv.bind_all("<Button-4>", self._on_mousewheel)
        self.canv.bind_all("<Button-5>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.canv.unbind_all("<MouseWheel>") 

    def _on_mousewheel(self, event):
#        self.canv.yview_scroll(int(-1*(event.delta/120)), "units") 
        if event.num == 4:
            self.canv.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canv.yview_scroll(1, "units")

    def _configure_window(self, event):
        # update the scrollbars to match the size of the inner frame
        size = (self.scrollwindow.winfo_reqwidth(), self.scrollwindow.winfo_reqheight())
        self.canv.config(scrollregion='0 0 %s %s' % size)
        if self.scrollwindow.winfo_reqwidth() != self.canv.winfo_width():
           # update the canvas's width to fit the inner frame
           self.canv.config(width = self.scrollwindow.winfo_reqwidth())
#        if self.scrollwindow.winfo_reqheight() != self.canv.winfo_height():
#            #update the canvas's width to fit the inner frame
#           self.scrollwindow.config(height = self.canv.winfo_reqheight())
        
    def _configure_window_header(self, event):
        size = (self.scroll_header.winfo_reqwidth(), self.scroll_header.winfo_reqheight())
        self.canv_header.config(scrollregion='0 0 %s %s' % size)
        if self.scroll_header.winfo_reqwidth() != self.canv_header.winfo_width():
           #update the canvas's width to fit the inner frame
           self.canv_header.config(width = self.scroll_header.winfo_reqwidth())
        if self.scroll_header.winfo_reqheight() != self.canv_header.winfo_height():
            #update the canvas's width to fit the inner frame
           self.canv_header.config(height = self.scroll_header.winfo_reqheight())
           
    def set_header(self, data_header):
        if self.canv_header == None:
            self._set_header()
        for c, header in enumerate(data_header):
            e= tk.Entry(self.scroll_header, relief=tk.FLAT, background=self.canv_header['background'], width=header.width)
            #e = tk.Label(self.scroll_header, relief=tk.FLAT, text=header.label, width=header.width)
            e.insert(tk.END, header.label)
            e.grid(row=0, column = c)


    def _set_header(self):
        self.canv_header= tk.Canvas(self)
        self.canv_header.config(relief='flat', bd=2)
        self.canv_header.grid(column = 0, row = 0, sticky = 'EW')
        self.canv_header.columnconfigure(0, weight=1)
        self.scroll_header = ttk.Frame(self.canv_header)
        self.canv_header.create_window(0, 0, window = self.scroll_header, anchor = 'nw')
        #self.scroll_header.columnconfigure(0, weight=1)
        self.scrollheader = ttk.Scrollbar(self)
        self.scrollheader.config(command=self.canv_header.yview)
        self.scroll_header.bind('<Configure>', self._configure_window_header)
        
        
if __name__ == '__main__':
    root = tk.Tk()
    root.title('Teste Scrolled Window')
    quantidade = 6
    scrl = ScrolledWindow(root, header=False)

    frmGrid = tk.Frame(scrl.scrollwindow)  # Frame que ficará dentro do ScrolledWindows
    headers = []
    for i in range(6):
        headers.append(HeaderField(label = 'cabeçalho ' + str(i) , width=20))
    scrl.set_header(headers)
    frmHeader = tk.Frame(scrl.scroll_header)
    frmHeader.grid(row=0, column=0)
    frmGrid.grid(row=0, column=0)

    for i in range(quantidade):
        frmGrid.rowconfigure(i,weight = 1)
        for j in range(quantidade):
            frmGrid.columnconfigure(j, weight=1)
            e = tk.Entry(frmGrid )
            e.insert(0, 'Texto {}-{}'.format(i,j))
            e.grid(row = i , column = j)
           

    scrl.pack()
    root.mainloop()
