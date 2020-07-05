#-------------------------------------------------------------------------------
# Name:        ScrolledList
# Purpose:
#
# Author:      luiscar
#
# Created:     01/03/2018
# Copyright:   (c) luiscar 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from tkinter import *

class ScrolledList(Frame):

    def __init__(self,parent=None,lst_content= [],expansao=YES,preenchimento=BOTH):
        Frame.__init__(self,parent)
        self.pack(expand=expansao,fill=preenchimento)
        self.criar_componentes(lst_content)

    def criar_componentes(self,lst_content):
        self.sbar = Scrollbar(self)
        self.lst_box = Listbox(self,relief=SUNKEN)
        self.sbar.config(command=self.lst_box.yview)
        self.lst_box.config(yscrollcommand=self.sbar.set)
        self.sbar.pack(side=RIGHT,fill = Y)
        self.lst_box.pack(side=LEFT, expand=YES,fill=BOTH)

        if lst_content:
            for pos,item in enumerate(lst_content):
                if type(item) == list:
                    self.lst_box.index(pos,item[0])
                else:
                    self.lst_box.insert(pos,item)

        self.lst_content = lst_content

    def insert(self,item):

        if type(item) == tuple:
            if len(item) == 1:
                self.lst_box.insert(END,item[0])
        else:
            self.lst_box.insert(END,item)
            self.lst_content.append(item)

    def delete(self,item):
        self.lst_box.delete(item)
        self.lst_content.pop(item)
    def clear(self):
        self.lst_box.delete(0,END)
        self.lst_content = []

    def get_key(self):
        """ Return the key for the item selectioned in list """

        items = self.lst_box.curselection()
        if items:
            #check if list_content is a list of string or a list of list[value,key]
            if type(self.lst_content[0]) == list:

                #return key
                return self.lst_content[items][1]

            else:

                if len(items) == 1:
                    return self.lst_content[int(items[0])]
                else:
                    keys=[]
                    for index in items:
                        keys.append(index)
                    return keys

    def get_all_keys(self):
        """ Return all the keys in the listbox """
        return self.lst_content

def main():


    root = Tk()

    height = 5
    width = 5
    for i in range(height): #Rows
        for j in range(width): #Columns
            b = Entry(root, text="")
            b.grid(row=i, column=j)

    mainloop()

if __name__ == '__main__':
    main()
