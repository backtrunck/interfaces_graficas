from tkinter import *
from tkinter.messagebox import *
from PIL import Image, ImageTk
import logging, datetime
from util import is_valid_date, formatar_data
#from ..util import is_valid_date


class Quitter(Frame):
    
    def __init__(self,parent=None,text='Sair', side=RIGHT):
        Frame.__init__(self,parent)
        widget = Button(self,text=text,command=self.quit)
        widget.pack()
        self.pack(side=RIGHT)
        
    def quit(self):
        ans = askokcancel('Verificar Saída','Confirma Saída?')
        if ans:
            Frame.quit(self)
 
class EntryDate(Entry):
    def __init__(self, master, **kwargs):
        # valid percent substitutions (from the Tk entry man page)
        # note: you only have to register the ones you need; this
        # example registers them all for illustrative purposes
        #
        # %d = Type of action (1=insert, 0=delete, -1 for others)
        # %i = index of char string to be inserted/deleted, or -1
        # %P = value of the entry if the edit is allowed
        # %s = value of entry prior to editing
        # %S = the text string being inserted or deleted, if any
        # %v = the type of validation that is currently set
        # %V = the type of validation that triggered the callback
        #      (key, focusin, focusout, forced)
        # %W = the tk name of the widget
        super().__init__(master, **kwargs)
        self.bind('<KeyRelease>', self.datemask)
        vcmd = (self.register(self.onValidate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        #self.entry = tk.Entry(self, validate="key", validatecommand=vcmd)
        self.configure(validate="key", validatecommand=vcmd)
        
    def datemask(self, event):
        #print('event', event.keysym,'>',  event.char, len(self.get()))
        if event.keysym != 'BackSpace' and event.char in '0123456789':
            if len(self.get()) == 2:
                super().insert(END,"/")
            elif len(self.get()) == 5:
                super().insert(END,"/")
    
                
    def onValidate(self, d, i, P, s, S, v, V, W):
        print("d='%s'" % d)
        print("i='%s'" % i)
        print("P='%s'" % P)
        print("s='%s'" % s)
        print("S='%s'" % S)
        
        size = len(P)
        if size > 10:
            return False
            
        for i, ch in enumerate(S):
            if ch not in ('1234567890/'):
                return False
            if len(S)>1:
                if ch == '/' and not(i==2 or i==5):
                    return False
        
        if S == '/' and d=='1':
            if not(len(s) == 2 or len(s) == 5):
               return False
  
        return True


    def set(self, data):
        if type(data) == str:
            if is_valid_date(data):
                self.delete(0, END)
                self.__insert(data)
        elif type(data) == datetime.datetime:
            self.__insert(formatar_data(data,  format='%d/%m/%Y'))
        else:
            self.insert("")
        
    def insert(self, *args):
        pass
    def __insert(self, data):
        super().insert(0, data)

class ScrolledText(Frame):
    
    
    def __init__(self, parent=None, text='', **args):
        Frame.__init__(self, parent)
        #self.pack(expand=YES, fill=BOTH) # make me expandable
        self.makewidgets(**args)
        self.settext(text)
        
        
    def makewidgets(self, **args):
        sbar = Scrollbar(self)
        text = Text(self, relief=SUNKEN, **args)
        sbar.config(command=text.yview) # xlink sbar and text
        text.config(yscrollcommand=sbar.set) # move one moves other
        sbar.pack(side=RIGHT, fill=Y) # pack first=clip last
        text.pack(side=LEFT, expand=YES, fill=BOTH) # text clipped first
        self.text = text
        
        
    def settext(self,text='', posicao = INSERT, go_end=False):        
        self.text.insert(posicao, text) 
        if go_end:
            self.go_end()            
        self.update_idletasks()
        
    def erase(self, posicao_inicial = '1.0',  posicao_final = END):        
        self.text.delete(posicao_inicial, posicao_final) 
        self.update_idletasks()
        
    def index(self, index):
        return self.text.index(index)
        
    def gettext(self):
        return self.text.get('1.0', END+'-1c') # first through last
    
    def getindex(self, index):
#        return tuple(map(int, string.split(self.index(index), ".")))
        return tuple(map(int, self.index(index).split(".")))
        
    def go_end(self):
        self.text.see(END)

class ChkButton(Checkbutton):
    
    def __init__(self, master, value=0, **kwarg):
        super().__init__(master, **kwarg)
        self.__value = IntVar()
        self.config(variable=self.__value)


    def get(self):
        return self.__value.get()


    def set(self):
        self.__value.set(1)


    def unset(self):
        self.__value.set(0)


class ScrolledTextHandler(logging.StreamHandler):    
    
    def __init__(self, scrolled_text):
        logging.StreamHandler.__init__(self)
        self.scroll = scrolled_text        
    def emit(self, record):
        msg = self.format(record)
        self.scroll.settext(msg + '\n', go_end=True)

def get_image(path, tamanho=(200, 200)):
    '''
        Cria um objeto Image a partir de um arquivo, para ser usado num widget
        parametros:
        (path: string): caminho do arquivo de imagem
        (tamanho:tuple): tamanho final do objeto Image
        
        return: retorna um objeto PhotoImage, para ser usado na propriedade 'image' de um tkinter widget
    '''
    
    image = Image.open(path)
    
    image2 = image.resize((200, 200), Image.ANTIALIAS)
    
    return ImageTk.PhotoImage(image2)        


def show_modal_win(win):
    #torna a janela modal
    win.focus_set()
    win.grab_set()
    win.wait_window()

def test_chkbutton(win):
    win.title('Teste CheckButton')
    chk = ChkButton(win, width=15, anchor='w', text='teste')
    chk.pack()
    bt = Button(win, text='Setar', command=chk.set)
    bt.pack(side=LEFT)
    bt = Button(win, text='Limpar', command=chk.unset)
    bt.pack(side=RIGHT)

def test_entrydate(win):
    win.title('Teste EntryDate')
    entry = EntryDate(win)
    entry.pack()
    entry.set('12/12/2020')
    Entry(win).pack()

if __name__ == '__main__':
    win = Tk()
    win.title('Teste')
    #test_chkbutton(win)
    test_entrydate(win)
    win.mainloop()

