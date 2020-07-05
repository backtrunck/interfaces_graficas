from tkinter import *
from tkinter.messagebox import *
from PIL import Image, ImageTk
import logging


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

    
if __name__ == '__main__':
    win = Tk()
    win.title('Teste ScrolledText')
    text = 'Isto é um teste \n' * 100
    scroll = ScrolledText(win, text=text)
    scroll.pack()
    scroll.go_end()    
    win.mainloop()

