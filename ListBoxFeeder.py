#-------------------------------------------------------------------------------
# Name:        ListBoxFeeder
# Purpose:
#
# Author:      luiscar
#
# Created:     01/03/2018
# Copyright:   (c) luiscar 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from tkinter import *
from interfaces_graficas.ScrolledList import ScrolledList

class ListBoxFeeder(Frame):

    def __init__(self,parent=None,list_content=[],expand=YES,fill=BOTH):
        Frame.__init__(self,parent)
        self.pack(expand=expand,fill=fill)
        self.__make_components(list_content,expand,fill)

        #self.validator -> referÃªncia para uma funÃ§Ã£o (passada pelo usuÃ¡rio)
        #que vai validar a entrada na caixa de texto, antes da mesma ir para
        #o list box. A funÃ§Ã£o deve receber um parÃ¢metro string que serÃ¡ o
        #contÃ©udo da caixa de texto.
        self.validator = None

    def __make_components(self,list_content,expand,fill):
        """ Cria os componentes do widget ListBoxFeeder (botÃµes, caixa de texto,
        e listbox """


        #Text Box
        self.txt_box = Entry(self)
        self.txt_box.pack(side=LEFT,fill = X,padx=10,pady=10,anchor=NW)

        # Buttons
        frame_buttons = Frame(self)
        frame_buttons.pack(expand=expand,fill=fill)

        self.button_insert = Button(frame_buttons,text=">",height=1,width=10 )
        self.button_insert.pack(side=TOP,fill = fill,expand=expand,padx=10,pady=2)

        self.button_delete = Button(frame_buttons,text="<",height=1,width=10)
        self.button_delete.pack(side=TOP,fill = fill,expand=expand,padx=10,pady=2)

        self.button_clear = Button(frame_buttons,text="x",height=1,width=10 )
        self.button_clear.pack(side=TOP,fill = fill,expand=expand,padx=10,pady=2)

        #events for buttons
        self.button_clear.bind('<ButtonRelease-1>',self.__clear_list)
        self.button_insert.bind('<ButtonRelease-1>',self.__insert_list)
        self.button_delete.bind('<ButtonRelease-1>',self.__delete_list)

        frame_buttons.pack(side=LEFT,expand=expand,fill=fill)

        #scrolled list
        self.scr_lst_box = ScrolledList(self,list_content)
        self.scr_lst_box.pack(side=LEFT,expand=expand,fill=fill,padx=10,pady=10)

    def __clear_list(self,event):
        """ Limpa o list box """
        self.scr_lst_box.clear()

    def __insert_list(self,event):
        """ Insere um item no list box """

        txt = self.txt_box.get().strip()
        if txt:
            #verifica se existe uma funÃ§Ã£o para validar a entrada do usuÃ¡rio
            if self.validator != None:

                #verifica se o usuÃ¡rio digitou algo na caixa de texto
                if self.validator(txt):
                    self.scr_lst_box.insert(txt)
                    #apaga cx de texto
                    self.txt_box.delete(0,END)
            else:
                    self.scr_lst_box.insert(txt)
                    #apaga cx de texto
                    self.txt_box.delete(0,END)


    def __delete_list(self,event):
        """ Deleta da lista os itens selecionados """
        itens = self.scr_lst_box.lst_box.curselection()

        for i in  itens:
            self.scr_lst_box.delete(int(i))

    def get_all_keys(self):
        """ Return all the keys in the listbox """
        return self.scr_lst_box.get_all_keys()

def main():
    root = Tk()
    ListBoxFeeder(root,list_content=['Teste1','Teste2','Teste3','Teste4','Teste5',])
    root.mainloop()

if __name__ == '__main__':
    main()
