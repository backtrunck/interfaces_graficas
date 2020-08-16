import tkinter as tk
import tkinter.ttk as ttk
from tkinter.messagebox import askokcancel
from collections import OrderedDict, namedtuple
from sqlalchemy.sql import select, sqltypes
#from interfaces_graficas.ScrolledWindow import ScrolledWindow
from ..ScrolledWindow import ScrolledWindow
from .. import ChkButton, EntryDate
from util import string_to_date, formatar_data, is_valid_date
from fields import Field
#from nfce_models import products_gtin_t, classe_produto_t
#DBField = namedtuple("DBField", ['field_name', 'comparison_operator', 'label', 'width', 'type_widget'])
SearchField = namedtuple("Filter", ['field_name', 'comparison_operator', 'label', 'width'])
FormControl = namedtuple('FormControl', ['field_name', 'comparison_operator', 'label', 'width', 'type_widget', 'widget'])

class DBField():
    def __init__(self, 
                 field_name = None,
                 comparison_operator='=',
                 label='',
                 width=5, 
                 visible=True, 
                 type_widget=tk.Entry):
        
        if not field_name:
            raise Exception('Campo field_name obrigatório')
        
        self.field_name = field_name
        self.comparison_operator = comparison_operator
        if label:
            self.label = label
        else:
            self.label = field_name
        self.width = width
        self.type_widget = type_widget
        self.visible = visible


class ComboBoxDB(ttk.Combobox):
    
    def __init__(self, master = None, **options):
        super().__init__(master, **options)
        self.list_content = []
        self.bind('<Key>', self.__key)

    
    def __key(self, event):    
        #print("pressed", repr(event.char))
        if event.char == '\x7f': #se pressionou 'del'
            self.set('')


    def fill_list(self, list_content, erase=False):
        '''
            Preenche o list box, list_content deve ser um lista na qual a descrição é a coluna 1,
            e a chave a coluna 0
        '''
        
        if erase:
            self['values'] = [item[1] for item in list_content]
            self.list_content = list_content
        else:
            if self.list_content:
                self['values'].extend([item[1] for item in list_content])
                self.list_content.extend(list_content)
            else:
                self['values'] = [item[1] for item in list_content]
                self.list_content = list_content


    def get_key(self):        
        if self.current() != -1:            
            return self.list_content[self.current()][0]            
        return self.current()    

    
    def set_key(self, key):        
        try:            
            #index = self.list_content.index(key)
            index = [int(i[0]) for i in self.list_content].index(int(key))
            #self.set(self.list_content[index][0])            
            self.current(index)
        except ValueError:            
            self.set('')


class FrameForm(tk.Frame):
    
    
    def __init__(self, master, connection,data_table=None, grid_table=None, **args):
        '''
            Parametros:
                (master:tkinter.widget): Widget pai
                (connection:object): Conecção com o banco de dados
                (data_table:object): Tabela 
        '''
        self.data_table = data_table
  
        super().__init__(master, **args)
        self.controls = OrderedDict()
        self.conn = connection
        self.columns = []
        self.last_clicked_row = -1
        self.last_inserted_row = -1
        
        
        self.bg_sel_line_grig = 'gray71'
        self.bg_nor_line_grig = 'white'
        
        self._form = tk.Frame(self)
        self._form.pack(fill=tk.X)
        
        if grid_table != None:
            self.grid_table = grid_table
            self.grid_select_stm = select(self.grid_table.c).distinct()
            f = tk.Frame(self)
            f.pack(fill=tk.X)
            self.scroll = ScrolledWindow(f, canv_w=450, canv_h = 200, scroll_h = True)
            self.scroll.pack(pady=2)
            self.scrolled_frame = tk.Frame(self.scroll.scrollwindow)       #Frame que ficará dentro do ScrolledWindows
            self.scrolled_frame.grid(row = 0, column = 0)
        
        self.tool_bar = tk.Frame(self)
        self.tool_bar.pack(fill=tk.X)
        tk.Button(self.tool_bar, text='Fechar', width = 10, command=self.close).pack(side=tk.RIGHT, padx=2, pady=5)

    
    @property
    def form(self):
        return self._form

    def add_widget(self, name_widget, widget):
        '''
            Adiciona controles ao form
            Parâmetros:
                (name_widget:string) Nome único do campo, vai ser a chave(key) de self.controls
                (widget:tk.Widget) classe (class) do widget a ser inserido no form.
        '''
        if type(name_widget) == DBField:
            self.controls[name_widget.label]  =  FormControl(field_name = name_widget.field_name, 
                                                             comparison_operator=name_widget.comparison_operator, 
                                                             label = name_widget.label, 
                                                             width = name_widget.width, 
                                                             type_widget = name_widget.type_widget, 
                                                             widget = widget)
        else:
            self.controls[name_widget] = widget


    def add_widget_tool_bar(self, **kwargs):
        '''
            Adiconar widgets ao toobar(self.tool_bar, que fica na parte inferior da tela)
        '''
        tk.Button(self.tool_bar, **kwargs).pack(side=tk.RIGHT, padx=2, pady=5)


    def clear_form(self):
        '''
            Limpa todos os campos do form
        '''
        for key in self.controls.keys():
            form_widget = self.controls[key].widget
            self.set_widget_data(form_widget, '')


    def clear_grid(self): 
        ''' Limpa o grid'''
        
        for widget in self.scrolled_frame.grid_slaves():
            
            if int(widget.grid_info()['row']) > 0:
                
                widget.grid_forget()
                widget.destroy()
        self.scroll.canv.xview_moveto(0)
        self.scroll.canv.yview_moveto(0)
        self.scroll.scrollwindow.config(width = 10, heigh=10)
#        self.scrolled_frame.grid(row = 0, column = 0)
#        self.scroll.pack(pady=2, expand=1)


    def clear_grid_line(self, row):
        '''
            Limpa o grid
        '''
        qt_cols = len(self.controls.keys())
        for i, key in enumerate(reversed(self.controls.keys())):
            index = (self.last_inserted_row - (row))*len(self.controls.keys())-len(self.controls.keys())
            widget = self.scrolled_frame.grid_slaves()[index + (qt_cols + i)]
            self.set_widget_data(widget, '')


    def close(self):
        '''Fecha a janela'''
        self.master.destroy()
    

    
    def create_row_header(self, header=[], **kargs):
        '''
            Cria o cabeçalho do grid
                Pode ser criados de duas maneiras: ou passa-se uma lista de strings com os cabeçalhos(parâmetro
                header. Ou preenche-se a lista columns de FrameForm, com uma lista de objetos SearchField. E os
                labes destes objetos SearchField serão os cabeçalhos.
            Parâmetros:
                (header:list) lista com os labels a serem mostrados na ordem no cabeçalho
                
        '''
        if self.columns:                    #se columns contiver objetos DBField
            for col, field in enumerate(self.columns):
                width = 1 if not field.visible else field.width #se o campo não for visivel, largura de 1
                                                                #para não influenciar na largura do grid
                e = tk.Label(self.frame_header,text=field.label, width=width)
                e.grid(row = 0,column=col, sticky=tk.W)            
        else:
            for col, key in enumerate(self.controls.keys()):
                try:
                    value = header[col]
                except IndexError:
                    value = key        
                e = tk.Label(self.frame_header,text=value, width=self.controls[key].widget['width'])
                e.grid(row = 0,column=col, sticky=tk.W)


    def create_row_widget(self, widget_class=None, 
                                widget_name='',
                                widget_field_name='',
                                value='', 
                                row=0, 
                                column=0, 
                                width=11,
                                visible=True,  
                                **kargs):
        '''
            Cria os widgets do grid, com os respectivos dados
        '''
        
        if value is None:
            value = ''
        width_aux = 1 if not visible else width #se o campo não for visivel, largura de 1
                                                 #para não influenciar na largura do grid
        if widget_class == tk.Entry:                           
            e = widget_class(self.scroll.scrollwindow,
                             width=width_aux,
                             relief=tk.FLAT,
                             disabledbackground=self.bg_nor_line_grig, 
                             disabledforeground='black',
                             **kargs)
            
            e.grid(row = row,column=column, in_=self.scrolled_frame)
            e.insert(0, value)
            e.name = widget_name
            e.field_name = widget_field_name
            e.bind("<Key>", lambda a: "break")
            e.bind('<ButtonRelease>', self.row_click)        
            e.config(state=tk.DISABLED)
            if not visible:
                e.lower()
        if widget_class == ChkButton:
            e = widget_class(self.scrolled_frame,width=width, indicatoron=True,  background=self.bg_nor_line_grig, disabledforeground='black', **kargs)
            e.name = widget_name
            if value:
                e.set()
            else:
                e.unset()
            
        
            e.grid(row = row,column=column)
            e.bind('<ButtonRelease>', self.row_click)
            e.config(state=tk.DISABLED)


    def fill_grid(self, data_rows):
        '''
            Preenche um grid a partir de um data_rows passado
        '''
        #limpa o grid
        self.clear_grid()
        row = -1
        #para cada linha retornada em data_rows
        for row, data_row in enumerate(data_rows, 1):
            self.fill_row(row, data_row)
        self.last_inserted_row = row
        self.last_clicked_row = -1


    def fill_row(self, row, data_row):
        '''
            Criar os widgets do grid a partir dos controles do form(self.controls) e já preenche os dados nele
        '''
        if not self.columns:
            for col, key in enumerate(self.controls.keys()):
                self.create_row_widget(widget_class=tk.Entry, widget_name=key, 
                                       widget_field_name=self.controls[key].field_name, value=data_row[key],
                                       row=row, column=col, width=self.controls[key].widget['width'])
        else:
            for col, field in enumerate(self.columns):
                self.create_row_widget( widget_class=field.type_widget, 
                                        #widget_name=field.field_name,
                                        widget_name=field.label, 
                                        widget_field_name=field.field_name, 
                                        value=data_row[field.field_name], 
                                        row=row,
                                        column=col,
                                        visible= field.visible, 
                                        width=field.width)

    

    def forget_grid_line(self, row):
        '''
            Apaga a linha (row) do grid
        '''
        #pega os widgets da linha (row)
        widgets = [widget for widget in self.scrolled_frame.grid_slaves() if widget.grid_info()['row'] == row]
        for widget in widgets:
            widget.grid_forget()        #apaga o widget
    
    
    def get_key_by_field_name(self, field_name):
        return [frame_field.label for key, frame_field in self.controls.items() if frame_field.field_name == field_name][0]


    def get_form_data(self, get_extra_data=False):
        '''
            Pega os dados dos widget do formulário
        '''
        datum = {}
        for key in self.controls.keys():
            form_widget = self.controls[key].widget
            datum[key] = self.get_widget_data(form_widget)
            
            if get_extra_data and type(form_widget) == ComboBoxDB: #se for um combo pega (ou não) o valor do campo descritivo (caso tenha este propriedade)
                try:
                    datum[form_widget.ds_key] = form_widget.get()
                except AttributeError:
                    pass
        return(datum)
    

    def get_form_keys(self):
        '''
            Obtém os dados dos campos do formulaŕio que são chaves primárias da tabela
        '''
       
        data = self.get_form_data()
        datum = {}
        for field_name in self.data_table.c.keys():
            column = self.data_table.c[field_name]
            if column.primary_key:                
                datum[field_name]  = data[self.get_key_by_field_name(field_name)]  #pega o chave pelo nome do campo
        return datum


    def get_grid_data(self, row):
        '''
            Pega os dados da linha (row) passada como parâmetro e coloca num dicionário
            parametros
                (row:int) Linha do grid que se vai obter os dados
            retorno
                (widgets:dictionary) Dados obtidos da linha na forma 'campo:valor'            
        '''
        widgets_data = {}
        if row > 0:
            widgets_data = {widget.name:self.get_widget_data(widget) for widget in self.scrolled_frame.grid_slaves() if widget.grid_info()['row'] == row}
        return widgets_data
        
    def get_grid_data_by_fieldname(self, row):
        '''
            Pega os dados da linha (row) passada como parâmetro e coloca num dicionário indexados pelo nome do campo
            parametros
                (row:int) Linha do grid que se vai obter os dados
            retorno
                (widgets:dictionary) Dados obtidos da linha na forma 'campo:valor'            
        '''
        widgets_data = {}
        if row > 0:
            widgets_data = {widget.field_name:self.get_widget_data(widget) for widget in self.scrolled_frame.grid_slaves() if widget.grid_info()['row'] == row}
        return widgets_data
        
    def get_grid_dbdata(self):
        '''
            Obtem os dados do Banco de Dados e preenche o grid
        '''
        result_proxy = self.conn.execute(self.grid_select_stm) 
        self.fill_grid(result_proxy.fetchall())


    def get_grid_keys(self, row):
        '''
            Obtém os dados do grid que são chaves primárias da tabela
        '''
        data = self.get_grid_data(row)
        datum = {}
        for field_name in self.data_table.c.keys():
            column = self.data_table.c[field_name]
            if column.primary_key:                
                datum[field_name]  = data[self.get_key_by_field_name(field_name)]  #pega o chave pelo nome do campo
        return datum


    def get_widget_data(self, widget):
        '''
            Pega o dado do widget
        '''
        if type(widget) == tk.Entry:
            return widget.get().strip()
        elif type(widget) == tk.Label:
           return widget['text'].strip()
        elif type(widget) == ComboBoxDB:
            result = widget.get_key()
            if result == -1:        #caso um item do combo não tenha sido selecionado retorna string vazia
                return ""
            else:
                return result
        elif type(widget) == ChkButton or type(widget) == EntryDate:
            return widget.get()
           
   
        

    def order_by(self, list_order):
        self.grid_select_stm = self.grid_select_stm.order_by(list_order)


    def row_click(self, event):
        '''
            Disparado ao clicar no grid
            Pega os dados do grid e põe no form
        '''
        if event.num == 1: #se o botão esquerdo do mouse foi clicado
            if self.last_clicked_row > 0:
                self.set_highlight_grid_line(self.last_clicked_row, self.bg_nor_line_grig )
            self.last_clicked_row = event.widget.grid_info()['row']     #pega o numero da linha clicada
            self.set_form_data(self.get_grid_data(int(event.widget.grid_info()['row'])))
            #print(self.get_grid_data(self.last_clicked_row))
            self.set_highlight_grid_line(self.last_clicked_row, self.bg_sel_line_grig)


    def set_data_columns(self):
        '''
            Ajusta as colunas do select
        '''
        sel = []
        for field in self.columns:
            sel.append(self.grid_table.c.get(field.field_name))
        self.grid_select_stm = select(sel).distinct() 

        
    def set_form_data(self, datum):
        '''
            Atualiza o contêudo dos widgets do form com os dados passados no parâmetros datum
            Parâmetros
                (datum:dicionario) Dicionario com os dados que vão ser colocado nos widget, as chaves(key) de datum
                    devem ser idênticas as chaves(key) de self.controls
        '''
        for key in self.controls.keys():
            data = datum[key]
            form_widget = self.controls[key].widget
            self.set_widget_data(form_widget, data)


#    def set_form_widget(self, widget):
#        form_widget = self.controls[widget.name]
#        if type(form_widget) == tk.Entry:
#            if form_widget['state'] == 'readonly':
#                readonly = True
#                form_widget.config(state=tk.NORMAL)
#            else:
#                readonly = False
#            form_widget.delete(0, tk.END)
#            form_widget.insert(0, widget.get())
#            if readonly:
#                form_widget.config(state='readonly')
    

    def set_grid_line(self):
        '''
            Pega os dados do formulaŕio e atualiza a linha atual do grid
        '''
        data = self.get_form_data(get_extra_data=True)          #pega os dados do formuario
        self.set_grid_line_data(data, self.last_clicked_row)    #atualiza a linha atual


    def set_grid_line_data(self, data, row):
        '''
            Pega os dados de um dicionario passado e atualiza a linha do grid (row) passada como parâmetro
        '''
        for widget in self.scrolled_frame.grid_slaves():        #loop em todos os widget do grid
            if int(widget.grid_info()['row']) == row:           #se o widget pertence a linha (row)
                if data.get(widget.name):
                    self.set_widget_data(widget, data[widget.name]) #atualiza o widget


    def set_highlight_grid_line(self, row, background):
        for widget in self.scrolled_frame.grid_slaves():
        
            if widget.grid_info()['row'] == row:
                if type(widget) == tk.Entry:
                    widget['disabledbackground']= background
                if type(widget) == ChkButton:
                    widget['background']= background 


    def set_widget_data(self, widget, data):
        '''
            Atualiza o dado do widget
            Parâmetros
                (widget:tk.Widget) widget que vai ter seu conteúdo alterado
                (data:string) conteúdo a ser colocado no widget
        '''
        if data == None:
            data = ''
        if type(widget) == tk.Entry:
            last_state = widget['state']
            widget.config(state=tk.NORMAL)
            widget.delete(0, tk.END)
            widget.insert(0, data)
            widget.config(state=last_state)
            return 0
        elif type(widget) == tk.Label:
            widget.config(text=data)
            return 0
        elif type(widget) == ComboBoxDB:
            widget.set_key(data)
            return 0
        elif type(widget) == ChkButton:
            if data:
                widget.set()
            else:
                widget.unset()
            return 0
        elif type(widget) == EntryDate:
            last_state = widget['state']
            widget.config(state=tk.NORMAL)
            widget.delete(0, tk.END)
            widget.set(data)
            widget.config(state=last_state)
            return 0
        else:
            return -1


    def str_to_date(self, str_date):
        dt = string_to_date(str_date)        
        return formatar_data(dt) 


class FrameFormDB(FrameForm):
    
    
    def __init__(self,  master, connection, data_table=None,grid_table=None, **args):
        super().__init__( master, connection, data_table=data_table,grid_table=grid_table, **args)
    
    def get_form_dbdata(self, form_data):
        return self.get_dbdata(form_data, self.data_table)


    def check_form_for_update(self, insert=False):
        '''
            Verifica se os dados do formulário estão aptos a serem salvos, 
            conforme a estrutura do banco de dados
        '''
        
        for key in self.controls.keys():
            col = self.data_table.c.get(self.controls[key].field_name)
            data = self.get_widget_data(self.controls[key].widget)
            
            if (not col.nullable and not data and not insert) or (insert and not col.nullable and not data and not col.autoincrement):
                return (key, 'null')
            elif col.type._type_affinity in [sqltypes.Date, sqltypes.DateTime]:
                if data:                    
                    if not is_valid_date(data):
                        return(key, 'invalid_data')
            elif col.type._type_affinity in [sqltypes.Integer]:
                if data:                    
                    try: 
                        int(data)
                    except ValueError:
                        return(key, 'invalid_data')
            elif col.type._type_affinity in [sqltypes.Float, sqltypes.Numeric]:
                if data:
                    pass
                print(key, 'numérico(float)')
            elif col.type._type_affinity in [sqltypes.String]:
                if not data:
                    pass
            else:
                raise(Exception(f'Tipo do campo tratado: {col.type._type_affinity}'))
        return('', '')

    def convert_data_to_bd(self, data):
        '''
            Pega cada item do dicionario passado (data) e convert para o tipo específico de cada coluna no banco 
            de dados. É necessário que as chaves do dicionário passado sejam iguais aos nomes dos campos no banco
            de dados
            Parâmetros:
                (data:dictionarie) Dicionario com os valores a serem convertidos para o tipos de cada campo corres-
                pondente do banco.
        '''
        datum={}
        for key in data.keys():
            col = self.data_table.c.get(self.controls[key].field_name)
            if col.type._type_affinity in [sqltypes.Date, sqltypes.DateTime]:
                if is_valid_date(data[key]):
                    datum[col.name] = string_to_date(data[key])
                else:
                    datum[col.name] = None
            elif col.type._type_affinity in [sqltypes.Integer]:
                try: 
                    datum[col.name] = int(data[key])
                except ValueError:
                    datum[col.name] = None
            elif col.type._type_affinity in [sqltypes.Float, sqltypes.Numeric]:
                try:
                    datum[col.name] = float(data[key])
                except ValueError:
                    datum[col.name] = None
            elif col.type._type_affinity in [sqltypes.String]:
                datum[col.name] = data[key]
            else:
                raise(Exception(f'Tipo do campo tratado: {col.type._type_affinity}'))
        return datum


    def get_auto_increment_values(self, data):
        '''
            Obtem os dados dos campos autoincrement do formulário
        '''
        datum = {}
        for key in data.keys():
            if self.data_table.c.get(key).autoincrement == True:
                result = self.conn.execute(f'select auto_increment from information_schema.tables where table_name = "{self.data_table.name}" LOCK IN SHARE MODE ')
                datum[key] = result.fetchone()[0]
            else:
                datum[key] = data[key]
        return datum


    def get_dbdata(self, form_data, table):
        '''
            Obtem dados do banco de dados a partir de um dicionario de dados passado. Pega-se deste dicionario
            somente os dados correspondentes às chaves primárias da tabela(table). Busca os dados no banco e 
            retorna-os
            
            Parâmetros
                (form_data:dictionary) Dados de onde se vai retirar as chaves que vão filtrar os dados do banco de dados
                (table:slqAlchemyTable) Tabela do banco de dados onde se vai obter os dados
            return
                (row_proxy) com os dados obtidos do banco de dados
        '''
    
        sel = select(table.c)
        included_key = False
        for key in form_data.keys():
            column = self.data_table.c[key]  #tem que usar self.data_table para que se possa usar as chaves primárias          
            if column.primary_key:
                sel = sel.where(table.c.get(key) == form_data[key])
                included_key = True
        #se não achar nenhuma chave, filtra pelos próprios dados passados em form_data
        if not included_key:
            for key in form_data.keys():
                sel = sel.where(table.c.get(key) == form_data[key])
            
        result = self.conn.execute(sel)
        return result.fetchone()


    def set_form_dbdata(self, datum):
        '''
            Atualiza o conteúdo dos widget do form com os dados vindo do Banco de dados. os dados do banco estão
            "indexados" pelo nome da coluna e os controles no form estão "indexados" pelo labels. Esta procedimento
            faz a correspondência
            parâmetros(datum:data_row): Dados vindos do banco de dados
        '''
        data = {}
        for key in self.controls.keys():
            field_name = self.controls[key].field_name
            #key = self.get_key_by_field_name(field_name)
            data[key] = datum[field_name]
        self.set_form_data(data)
    


class FrameFormData(FrameFormDB):
    STATE_UPDATE = 0
    STATE_INSERT = 1    
    
    def __init__(self, 
                 master, connection, 
                 data_table=None,
                 grid_table=None,  
                 state=STATE_UPDATE,
                 data_keys=[],
                 grid_keys=[],
                 enabled_update=True, 
                 enabled_delete=True,
                 enabled_new=True, 
                 **args):
        
        if grid_table != None and grid_keys == []: #caso tenha passado o grid e não tenha passada as chaves gera erro
            raise Exception('grid_table sem grid_keys')
        self.data_table = data_table
                
        super().__init__(master, connection,data_table=data_table, grid_table=grid_table, **args)
        self.state=state
        
        if self.state == self.STATE_UPDATE:
            self.data_keys=data_keys
            if self.check_keys():
                return  None
        else:
            self.data_keys = None

        if enabled_update:
            self.add_widget_tool_bar(text='Salvar', width = 10, command=self.update)
        if enabled_delete:
            self.add_widget_tool_bar(text='Apagar', width = 10, command=self.delete)
        if enabled_new:
            self.add_widget_tool_bar(text='Novo', width = 10, command=self.new)
        
        
            
        

    def check_keys(self):
        '''
            Verifica se todas as chaves primárias da tabela estão em self.keys
        '''
        try:
                 
            for field_name in self.data_table.c.keys(): #loop em todos os campos da tabela
                column = self.data_table.c[field_name]
                if column.primary_key:
                    self.data_keys[field_name]   #se o campo não existir em self.data_keys, dá erro (não tem todas as chaves)
        except KeyError:
            raise Exception(f'Chaves Primárias incompletas para a tabela {self.data_table.name}')
            return 1
        return 0

    def get_db_data(self):
        result_proxy = self.conn.execute(select(self.data_table.c).where(self.data_keys)) 
        return result_proxy.fetchone()


    def delete(self):
        '''
            Apaga a linha atual do grid e a correspondente do banco de dados 
        '''
        if self.state == self.STATE_UPDATE:                 
            if not askokcancel('Delete', 'Confirme a Operação'):
                return
            dlt = self.data_table.delete()
            for key in self.data_keys:
                dlt = dlt.where(self.data_table.c[key] == self.data_keys[key])
            self.conn.execute(dlt)
            self.new()

    def get_form_dbdata(self, data):
        return super().get_dbdata(data, self.data_table)

    def insert(self):
        '''
            Insere os dados do formulário no banco de dados
        '''
        try:
            transaction = self.conn.begin()
            form_data = self.convert_data_to_bd(self.get_form_data())
            form_data = self.get_auto_increment_values(form_data)
            ins = self.data_table.insert().values(**form_data)
            self.conn.execute(ins)
            transaction.commit()            
        except Exception as e:
            transaction.rollback()
            print(f'Error: {e}')
            return -1
        self.data_keys = self.get_form_keys()
        self.state = self.STATE_UPDATE
        data = self.get_form_dbdata(self.data_keys) 
        self.set_form_dbdata(data)

        return 0

    def new(self):
        '''
            Limpa o form e ajusta o status
        '''
        
        self.clear_form()
        self.data_keys = None
        self.state = self.STATE_INSERT
    
    def row_click(self, event):
        '''
            Disparado ao clicar no grid
            Pega os dados do grid e põe no form
            metodo sobrescreve FrameForm.row_click para que ele não chame set_form_data
            já que em FrameFormData self.controls que tem dados diferentes do grid.
        '''
        if event.num == 1: #se o botão esquerdo do mouse foi clicado
            if self.last_clicked_row > 0:
                self.set_highlight_grid_line(self.last_clicked_row, self.bg_nor_line_grig )
            self.last_clicked_row = event.widget.grid_info()['row']     #pega o numero da linha clicada
            #self.set_form_data(self.get_grid_data(int(event.widget.grid_info()['row'])))
            
            self.set_highlight_grid_line(self.last_clicked_row, self.bg_sel_line_grig)

    def set_filter(self,stm, form_data):
        for key, value in self.data_keys:
            stm.where(self.data_table[key] == value)
    
    def set_filter_grid(self, list_key):
        for key, value in list_key.items():
            self.grid_select_stm = self.grid_select_stm.where(self.grid_table.c[key] == value) 

    def update(self):
        '''
            Atualiza o banco de dados com os dados do form
        '''   
        try:
            if self.state == self.STATE_INSERT:
                result = self.check_form_for_update(insert=True)
            else:
                result = self.check_form_for_update(insert=False)            
            if not result[0]:
                if self.state == self.STATE_INSERT:
                    return self.insert()
                form_data = self.convert_data_to_bd(self.get_form_data())
                form_keys = self.get_form_keys()
                updt = self.data_table.update()
                for key in self.data_keys:
                    updt = updt.where(self.data_table.c[key] == self.data_keys[key])
                updt = updt.values(**form_data)
                self.conn.execute(updt)
                for key in form_keys:
                    self.data_keys[key] = form_keys[key]
                return 0
            return -1
        except Exception as e:
            print(e)
            return -1


class FrameGridManipulation(FrameFormDB):
    
    
    def __init__(self, master, connection, data_table=None,grid_table=None, **args):
        
#        self.data_table = data_table
        if grid_table != None:
            super().__init__(master, connection, data_table = data_table, grid_table=grid_table, **args)
        else:
            super().__init__(master, connection,data_table = data_table, grid_table=data_table, **args)            
        
        
        self.add_widget_tool_bar(text='Salvar', width = 10, command=self.update)
        self.add_widget_tool_bar(text='Apagar', width = 10, command=self.delete)
        self.add_widget_tool_bar(text='Novo', width = 10, command=self.new)

#    def add_widget(self, name_widget, widget):
#        self.controls[name_widget] = widget

    
    def delete(self):
        '''
            Apaga a linha atual do grid e a correspondente do banco de dados 
        '''
        if self.last_clicked_row != -1:                     #se tiver um linha atual
            if not askokcancel('Delete', 'Confirme a Operação'):
                return
            grid_keys = self.get_grid_keys(self.last_clicked_row)
            dlt = self.data_table.delete()
            for key in grid_keys:
                dlt = dlt.where(self.data_table.c[key] == grid_keys[key])
            self.conn.execute(dlt)
            self.forget_grid_line(self.last_clicked_row)            #apaga a linha do grid
            self.last_clicked_row = self.get_grid_next_line(self.last_clicked_row) #pega a próxima linha
            self.last_inserted_row -= 1                                #diminui quantidade de linhas
            datum = self.get_grid_data(self.last_clicked_row)     #pega os dados da linha atual do grid
            self.set_form_data(datum)                               #põe os dados atuais no formulário
            self.set_highlight_grid_line(self.last_clicked_row, self.bg_sel_line_grig)


    def insert(self):
        '''
            Insere os dados do formulário no banco de dados
        '''
        try:
            transaction = self.conn.begin()
            form_data = self.convert_data_to_bd(self.get_form_data())
            form_data = self.get_auto_increment_values(form_data)
            ins = self.data_table.insert().values(**form_data)
            self.conn.execute(ins)
            transaction.commit()            
        except Exception as e:
            transaction.rollback()
            print(f'Error: {e}')
            return -1
        self.last_inserted_row +=1           
        result = self.__get_dbdata(form_data)
        self.fill_row(self.last_inserted_row, result)
        self.last_clicked_row = self.last_inserted_row
        self.set_form_data(self.get_grid_data(self.last_clicked_row))
            
            
        return 0
   


#    def get_form_dbdata(self, form_data):
#        '''
#            Obtem dados do banco de dados a partir dos dados das chaves primárias do formulário
#            Parâmetros
#                (form_data:dictionary) Dados de onde se vai retirar as chaves que vão filtrar os dados do banco de dados
#            return
#                (row_proxy) com os dados obtidos do banco de dados
#        '''
#        #sel = select(self.data_table.c)   
#        sel = select(self.grid_table.c)
#        for key in form_data.keys():
#            column = self.self.grid_table.c[key]            
#            if column.primary_key:
#                sel = sel.where(self.grid_table.c.get(key) == form_data[key])
#        result = self.conn.execute(sel)
#        return result.fetchone()
    def __get_dbdata(self, form_data):
        return self.get_dbdata(form_data, self.grid_table)


    def get_grid_next_line(self, row):
        '''
            Pega a proxima linha do grid após row, se não tiver, pega uma das primeiras linahs, caso não tenha 
            retorna uma lista vazia
        '''
        widgets = reversed(self.scrolled_frame.grid_slaves()) 
        if widgets:
            rows = [widget.grid_info()['row'] for widget in widgets if widget.grid_info()['row'] > row]
            if rows:
                return rows[0]
            rows = [widget.grid_info()['row'] for widget in self.scrolled_frame.grid_slaves() if widget.grid_info()['row'] < row]
            if rows:
                return rows[0]
        return -1


    def new(self):
        '''
            Limpa o form e ajusta a última linha clicada para -1
        '''
        self.set_highlight_grid_line(self.last_clicked_row, self.bg_nor_line_grig )
        self.last_clicked_row = -1
        
        self.clear_form()


    def update(self):
        '''
            Atualiza o banco de dados com os dados do form
        '''   
        try:
            if self.last_clicked_row == -1:
                result = self.check_form_for_update(insert=True)
            else:
                result = self.check_form_for_update(insert=False)            
            if not result[0]:
                if self.last_clicked_row == -1:
                    return self.insert()
                form_data = self.convert_data_to_bd(self.get_form_data())                
                grid_keys = self.get_grid_keys(self.last_clicked_row)
                updt = self.data_table.update()
                for key in grid_keys:
                    updt = updt.where(self.data_table.c[key] == grid_keys[key])
                updt = updt.values(**form_data)
                self.conn.execute(updt)
                self.set_grid_line()                
                return 0
            return -1
        except Exception as e:
            print(e)
            return -1

class FrameGridSearch(FrameForm):
    def __init__(self, master, connection, grid_table=None, **kwargs):
        
        #self.filters = {}
        if grid_table == None:
            return None            
        super().__init__(master, connection, data_table=None, grid_table=grid_table, **kwargs)
        self._form_search = tk.Frame(self._form)
        self._form_search.pack(fill=tk.X)
        
        f = tk.Frame(self._form)
        f.pack(fill=tk.X)
        tk.Button(f, text='Pesquisar', width = 10, command=self.search).pack(side=tk.RIGHT, padx=2, pady=5)
    
    
    def add_widget(self, filter, widget):
        '''
            Adiciona um widget aos controles do formularios (self.controls)
            parâmetros:
                (widget:tk.widget) Objeto que vai ser colocado no form de pesquisa
                (filter:named_tuple(filter)) Uma tupla com o seguinte conteudo (nome_do_verdadeiro_do_campo,operador_de_comparacao e 
                        label(nome opcional do campo, usado quando se vai usar o mesmo campo mais de uma vez na pesquisa)
                        Ex (field_name='cnpj', comparison_operator='=',label='cnpj_1'). Vai compor os filtros da pesquisa
        '''
        super().add_widget(filter, widget)
        #self.filters[filter.label] = filter  

    @property
    def form(self):
        return self._form_search
    
    def get_filters(self, form_data):
        filters = []
        for key in form_data:
            if form_data[key]:
                filters.append(f'{self.filters[key].field_name} {self.filters[key].comparison_operator} :{key}')
        return ' and '.join(filters)

    def row_click(self, event):
        '''
            Disparado ao clicar no grid
            Pega os dados do grid e põe no form
        '''
        if event.num == 1: #se o botão esquerdo do mouse foi clicado
            if self.last_clicked_row > 0:
                self.set_highlight_grid_line(self.last_clicked_row, self.bg_nor_line_grig )
            self.last_clicked_row = event.widget.grid_info()['row']     #pega o numero da linha clicada
            #self.set_form_data(self.get_grid_data(int(event.widget.grid_info()['row'])))
            self.set_highlight_grid_line(self.last_clicked_row, self.bg_sel_line_grig)


    
    def search(self):
        self.set_data_columns()             #ajusta o select da pesquisa (cria um novo self.grid_select_stm)
        form_data = self.get_form_data()    #pega os dados do formulario
        self.set_filter(form_data)          #com os dados do formulario aplica os filtros(em self.grid_select_stm)
        self.get_grid_dbdata()              #Obtem os dados do banco de dados

    def set_filter(self, form_data):
        '''
            Ajusta o where do select, a ser executado, para preencher o grid, quando se clica no botão pesquisar
            O citado where se baseia nos dados preenchidos no formulario que devem ser passados via parametro
            form_data.
            Parametros:
                (form_data:dictionary): Dicionario com os campos que vão formar o where(filtro)
            Return:
                (None:sem retorno) Ajusta o where da propriedade self.grid_select_smt que vai ser utilizada 
                    para pegar os dados do banco de dados e preencher o grid.
        '''
        for key in form_data:
            #if form_data[key]:
             if form_data[key] != '' and form_data[key] != None:
                field_name = self.controls[key].field_name
                if self.controls[key].comparison_operator == Field.OP_LIKE:
                    self.grid_select_stm = self.grid_select_stm.where(self.grid_table.c[field_name].like(form_data[key])) 
                elif self.controls[key].comparison_operator == Field.OP_GREATER:
                    self.grid_select_stm = self.grid_select_stm.where(self.grid_table.c[field_name] > form_data[key]) 
                elif self.controls[key].comparison_operator == Field.OP_LESS:
                    self.grid_select_stm = self.grid_select_stm.where(self.grid_table.c[field_name] < form_data[key]) 
                elif self.controls[key].comparison_operator == Field.OP_GREATER_EQUAL:
                    self.grid_select_stm = self.grid_select_stm.where(self.grid_table.c[field_name] >= form_data[key]) 
                elif self.controls[key].comparison_operator == Field.OP_LESS_EQUAL:
                    self.grid_select_stm = self.grid_select_stm.where(self.grid_table.c[field_name] <= form_data[key]) 
                elif self.controls[key].comparison_operator == Field.OP_EQUAL:
                    self.grid_select_stm = self.grid_select_stm.where(self.grid_table.c[field_name] == form_data[key]) 
