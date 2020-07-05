from tkinter import *

class InvalidDictControl(Exception):
    pass

''' Formulário simples'''

class SimpleForm(Frame):
    def __init__(self, master, **args):
        '''
            Cria um formulário a partir de um conjunto de controles(uma lista de dicionarios passado por parâmetro), na vertical
            Parâmetros:
                master (widget): widget que vai ser o mestre (pai) do Simple Form
                lstControls (list of dictionaries): uma lista de dicionarios, cada dicionario com os seguintes dados:
                                'control': Tipo de Controle Entry, Option, Canvas, etc
                                'label': Texto para criação de um label para ficar ao lado do controle
                                'name' : Nome do controle a ser criado
        '''                            
        super().__init__(master=master, **args)
        self.controls = {}          #armazená todos os principais controles que vão ser criados
        #self.__make_controls(lstControls)
        self.frame_conteudo = Frame(self)
        self.frame_conteudo.pack()
        frm = Frame(self)
        frm.pack(fill = X)
        
        Button(frm, text = 'Sair', command=self.quit).pack(side = RIGHT)
        
    def make_controls(self,lstControls):
        '''
            Cria os controles e dispobiliza-os na tela
        '''
        
        for dictControl in lstControls:
            
            frm = Frame(self.frame_conteudo)
            frm.pack(fill = X)
            
            self.make_control(frm, dictControl)
                
    def make_control(self,master, dictControl, show_in_grid = False):
        '''
            Cria os controles(widget) a partir do parametro passado (type_control)
            parametros:
                master (Tkinter.Widget): Controle (widget) no qual vai ser criado o controle
                dictControl (dictionary): dicionario, com os seguintes dados:
                                'control': Tipo de Controle Entry, Option, Canvas, etc
                                'label': Texto para criação de um label para ficar ao lado do controle
                                'name' : Nome do controle a ser criado.
                show_in_grid(boolean): Vai ser mostrado num grid, não cria label nem usa o pack geometry manager.
        '''
        

                
        if dictControl['type_control'].upper() == 'ENTRY':
            
            if show_in_grid:
                return Entry(master)
            else:
                
                if dictControl['label']:
                    Label(master, text = dictControl['label']).pack(side = LEFT)   
                    
                ctrl = Entry(master)   
                ctrl.pack(side = LEFT,  fill = X, expand=YES)
                self.controls[dictControl['name']] = ctrl
                return ctrl
                
        elif  dictControl['type_control'].upper() == 'BUTTON':
            
            if show_in_grid:
                return Button(master)
            else:
                
                ctrl = Button(master, text = dictControl['label'])
                ctrl.pack(side = LEFT,  fill = X, expand=YES)
                self.controls[dictControl['name']] = ctrl
                return ctrl
        else:
            raise InvalidDictControl('dictControl must contains in key \'control\' a type of control to make')
            
        return ctrl
        
                    
class SimpleFormWithGrid(SimpleForm):
    
    
    def __init__(self, master, **args):
        super().__init__(master, **args)
        
    
    def make_controls(self, lstControls):
       
        for row, lstControl in enumerate(lstControls):
            
            for col, dictControl in enumerate(lstControl):
                
                if row == 0 and dictControl['label']:
                    lbl = Label(self.frame_conteudo, text = dictControl['label'])   
                    lbl.grid(row = row, column = col, ipadx = 0, ipady = 0,   padx = 0,  pady = 0)
                    
                ctrl = super().make_control(self.frame_conteudo,dictControl, show_in_grid = True)
                ctrl.config(width = dictControl['width'])
                
                ctrl.grid(row = row + 1, column = col , padx = 0, pady = 0, sticky = N + S + W + E)                

   
    
    
def testSimpleForm():
    controles = (   \
                    {'type_control':'entry', 'label':'Controle 1', 'name':'crt_1'},  \
                    {'type_control':'entry', 'label':'Controle 2', 'name':'crt_2'},  \
                    {'type_control':'entry', 'label':'Controle 3', 'name':'crt_3'},  \
                    {'type_control':'entry', 'label':'Controle 4', 'name':'crt_4'})
    
    root = Tk()
    root.title('Test Simple Form')
    #root.geometry('350x120')
    frm = SimpleForm(root)
    frm.make_controls(controles)
    frm.pack(fill = X)
    root.mainloop()

def testSimpleFormWithGrid():
    controles = (   \
                    ({'type_control':'entry', 'label':'Controle 1.1', 'name':'crt_1','width':2},  \
                    {'type_control':'entry', 'label':'Controle 1.2', 'name':'crt_2', 'width':2},  \
                    {'type_control':'entry', 'label':'Controle 1.3', 'name':'crt_3', 'width':2},  \
                    {'type_control':'button', 'label':'Detalhar', 'name':'crt_4','width':2}), \
                    ({'type_control':'entry', 'label':'Controle 2.1', 'name':'crt_1', 'width':2},  \
                    {'type_control':'entry', 'label':'Controle 2.2', 'name':'crt_2', 'width':2},  \
                    {'type_control':'entry', 'label':'Controle 2.3', 'name':'crt_3', 'width':2},  \
                    {'type_control':'button', 'label':'Controle 2.4', 'name':'crt_4', 'width':2}),  \
                    ({'type_control':'entry', 'label':'Controle 3.1', 'name':'crt_1', 'width':2},  \
                    {'type_control':'entry', 'label':'Controle 3.2', 'name':'crt_2', 'width':2},  \
                    {'type_control':'entry', 'label':'Controle 3.3', 'name':'crt_3', 'width':2},  \
                    {'type_control':'button', 'label':'Controle 3.4', 'name':'crt_4', 'width':2}))
    
    root = Tk()
    root.title('Test Simple Form with Grid')
    #root.geometry('350x120')
    frm = SimpleFormWithGrid(root)
    frm.make_controls(controles)
    frm.pack(fill = X)
    root.mainloop()
    
    
def main():
    testSimpleForm()
    #testSimpleFormWithGrid()

if __name__ == '__main__':
    main()
