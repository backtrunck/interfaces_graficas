import tkinter as tk
import tkinter.ttk as ttk
from tkinter.messagebox import askokcancel
from collections import OrderedDict, namedtuple
from sqlalchemy.sql import select, sqltypes
#from interfaces_graficas.ScrolledWindow import ScrolledWindow
from ..ScrolledWindow import ScrolledWindow
from util import string_to_date, formatar_data, is_valid_date
from fields import Field
DBField = namedtuple("DBField", ['field_name', 'comparison_operator', 'label', 'width', 'type_widget'])

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
            index = [i[0] for i in self.list_content].index(int(key))
            #self.set(self.list_content[index][0])            
            self.current(index)
        except ValueError:            
            self.set('')


class FrameForm(tk.Frame):
    
    
    def __init__(self, master, connection,grid_table=None, **args):
        '''
            Parametros:
                (master:tkinter.widget): Widget pai
                (connection:object): Conecção com o banco de dados
                (data_table:object): Tabela 
        '''
        
        super().__init__(master, **args)
        self.controls = OrderedDict()
        self.conn = connection
        self.columns = []
        self.last_data_rows = None
        self.last_clicked_row = -1
        self.last_inserted_row = -1
        
        
        self.bg_sel_line_grig = 'gray71'
        self.bg_nor_line_grig = 'white'
        
        self._form = tk.Frame(self)
        self._form.pack(fill=tk.X)
        
        #self.frame_header = tk.Frame(self)
        #self.frame_header.pack(fill=tk.X)
        
        if grid_table != None:
            self.grid_table = grid_table
            self.grid_select_stm = select(self.grid_table.c).distinct()
            f = tk.Frame(self)
            f.pack(fill=tk.X)
            self.scroll = ScrolledWindow(f, canv_w=450, canv_h = 200, scroll_h = False)
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
            form_widget = self.controls[key]
            self.set_widget_data(form_widget, '')


    def clear_grid(self): 
        ''' Limpa o grid'''
        
        for widget in self.scrolled_frame.grid_slaves():
            
            if int(widget.grid_info()['row']) > 0:
                
                widget.grid_forget()
                widget.destroy()


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
            col = self.data_table.c.get(key)
            if col.type._type_affinity in [sqltypes.Date, sqltypes.DateTime]:
                if is_valid_date(data[key]):
                    datum[key] = string_to_date(data[key])
                else:
                    datum[key] = None
            elif col.type._type_affinity in [sqltypes.Integer]:
                try: 
                    datum[key] = int(data[key])
                except ValueError:
                    datum[key] = None
            elif col.type._type_affinity in [sqltypes.Float, sqltypes.Numeric]:
                try:
                    datum[key] = float(data[key])
                except ValueError:
                    datum[key] = None
            elif col.type._type_affinity in [sqltypes.String]:
                datum[key] = data[key]
            else:
                raise(Exception(f'Tipo do campo tratado: {col.type._type_affinity}'))
        return datum

    
    def create_row_header(self, header=[], **kargs):
        '''
            Cria o cabeçalho do grid
                Pode ser criados de duas maneiras: ou passa-se uma lista de strings com os cabeçalhos(parâmetro
                header. Ou preenche-se a lista columns de FrameForm, com uma lista de objetos SearchField. E os
                labes destes objetos SearchField serão os cabeçalhos.
            Parâmetros:
                (header:list) lista com os labels a serem mostrados na ordem no cabeçalho
                
        '''
        if self.columns:                    #se columns contiver objetos SearchField
            for col, field in enumerate(self.columns):
                e = tk.Label(self.frame_header,text=field.label, width=field.width)
                e.grid(row = 0,column=col, sticky=tk.W)            
        else:
            for col, key in enumerate(self.controls.keys()):
                try:
                    value = header[col]
                except IndexError:
                    value = key        
                e = tk.Label(self.frame_header,text=value, width=self.controls[key]['width'])
                e.grid(row = 0,column=col, sticky=tk.W)


    def create_row_widget(self, widget_class=None, widget_name='',value='', row=0, column=0, width=11, **kargs):
        '''
            Cria os widgets do grid, com os respectivos dados
        '''
        e = widget_class(self.scrolled_frame,width=width,  disabledbackground=self.bg_nor_line_grig, disabledforeground='black', **kargs)
        
        e.grid(row = row,column=column)
        if value is None:
            value = ''
        if widget_class == tk.Entry:
            e.insert(0, value)
            e.name = widget_name
            e.bind("<Key>", lambda a: "break")
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
        self.last_data_rows = data_rows
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
                self.create_row_widget(widget_class=tk.Entry, widget_name=key, value=data_row[key], 
                                        row=row, column=col, width=self.controls[key]['width'])
        else:
            for col, field in enumerate(self.columns):
                self.create_row_widget( widget_class=field.type_widget, 
                                        widget_name=field.field_name,
                                        value=data_row[field.field_name], 
                                        row=row,
                                        column=col,
                                        width=field.width)

    

    def forget_grid_line(self, row):
        '''
            Apaga a linha (row) do grid
        '''
        #pega os widgets da linha (row)
        widgets = [widget for widget in self.scrolled_frame.grid_slaves() if widget.grid_info()['row'] == row]
        for widget in widgets:
            widget.grid_forget()        #apaga o widget


    def get_form_data(self):
        '''
            Pega os dados dos widget do formulário
        '''
        datum = {}
        for key in self.controls.keys():
            form_widget = self.controls[key]
            datum[key] = self.get_widget_data(form_widget)
        return(datum)


    def get_form_keys(self):
        '''
            Obtém os dados dos campos do formulaŕio que são chaves primárias da tabela
        '''
        datum = {}
        for key in self.controls.keys():
            column = self.data_table.c[key]
            widget = self.controls[key]
            if column.primary_key:
                datum[key]  = self.get_widget_data(widget)
        return datum


    def get_grid_data(self, row):
        '''
            Pega os dados da linha (row) passada como parâmetro e coloca num dicionário
            parametros
                (row:int) Linha do grid que se vai obter os dados
            retorno
                (datum:dictionary) Dados obtidos da linha na forma 'campo:valor'            
        '''
        datum = {}
        for key in self.last_data_rows[row-1].keys():
            datum[key] = self.last_data_rows[row-1][key]
        return datum


    def get_grid_data_3(self, row):
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


    def get_grid_data_2(self, row):
        '''
            Não está sendo usado
        '''
        datum = {}
        qt_cols = len(self.controls.keys())
        for i, key in enumerate(reversed(self.controls.keys())):            
            index = (self.last_inserted_row - (row))*len(self.controls.keys())-len(self.controls.keys())
            datum[key] = self.scrolled_frame.grid_slaves()[index + (qt_cols + i)].get()
        return datum


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
        data = self.get_grid_data_3(row)
        datum = {}
        for key in self.data_table.c.keys():
            column = self.data_table.c[key]
            if column.primary_key:
                datum[key]  = data[key]
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
            return(widget.get_key())
           
   
        

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
            self.set_form_data(self.get_grid_data_3(int(event.widget.grid_info()['row'])))
            #print(self.get_grid_data(self.last_clicked_row))
            self.set_highlight_grid_line(self.last_clicked_row, self.bg_sel_line_grig)


    def set_data_columns(self):
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
            form_widget = self.controls[key]
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
        data = self.get_form_data()                             #pega os dados do formuario
        self.set_grid_line_data(data, self.last_clicked_row)    #atualiza a linha atual


    def set_grid_line_data(self, data, row):
        '''
            Pega os dados de um dicionario passado e atualiza a linha do grid (row) passada como parâmetro
        '''
        for widget in self.scrolled_frame.grid_slaves():        #loop em todos os widget do grid
            if int(widget.grid_info()['row']) == row:           #se o widget pertence a linha (row)
                if data.get(widget.name):
                    self.set_widget_data(widget, data[widget.name]) #atualiza o widget


    def set_grid_line_data_2(self, data, row):
        qt_cols = len(self.controls.keys())
        for i, key in enumerate(reversed(self.controls.keys())):
            index = (self.last_inserted_row - (row))*len(self.controls.keys())-len(self.controls.keys())
            widget = self.scrolled_frame.grid_slaves()[index + (qt_cols + i)]
            self.set_widget_data(widget, data[key])

    def set_grid_widget(self, widget, value_widget): 
        try:
            widget.config(state=tk.NORMAL)
            widget.delete(0, tk.END)
            widget.insert(0, value_widget)
            widget.config(state='readonly')
        except Exception as e:
            raise e


    def set_highlight_grid_line(self, row, background):
        for widget in self.scrolled_frame.grid_slaves():
           if widget.grid_info()['row'] == row:
                widget['disabledbackground']= background


    def set_widget_data(self, widget, data):
        '''
            Atualiza o dado do widget
            Parâmetros
                (widget:tk.Widget) widget que vai ter seu conteúdo alterado
                (data:string) conteúdo a ser colocado no widget
        '''
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
        else:
            return -1


    def str_to_date(self, str_date):
        dt = string_to_date(str_date)        
        return formatar_data(dt) 


class FrameGridManipulation(FrameForm):
    
    
    def __init__(self, master, connection, data_table=None,grid_table=None, **args):
        
        self.data_table = data_table
        if grid_table != None:
            super().__init__(master, connection, grid_table=grid_table, **args)
        else:
            super().__init__(master, connection, grid_table=data_table, **args)            
        
        
        self.add_widget_tool_bar(text='Salvar', width = 10, command=self.update)
        self.add_widget_tool_bar(text='Apagar', width = 10, command=self.delete)
        self.add_widget_tool_bar(text='Novo', width = 10, command=self.new)

    def add_widget(self, name_widget, widget):
        self.controls[name_widget] = widget

    
    def check_form_for_update(self, insert=False):
        '''
            Verifica se os dados do formulário estão aptos a serem salvos, conforme a configurção dos campos do banco de dados
        '''
        
        for key in self.controls.keys():
            col = self.data_table.c.get(key)
            data = self.get_widget_data(self.controls[key])
            
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
            datum = self.get_grid_data_3(self.last_clicked_row)     #pega os dados da linha atual do grid
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
            self.last_inserted_row +=1           
            result = self.get_form_dbdata(form_data)
            self.fill_row(self.last_inserted_row, result)
            self.last_clicked_row = self.last_inserted_row
            self.set_form_data(self.get_grid_data_3(self.last_clicked_row))
        except Exception as e:
            print(f'Error: {e}')
            return -1
            
        return 0


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


    def get_form_dbdata(self, form_data):
        '''
            Obtem dados do banco de dados a partir dos dados das chaves primárias do formulário
            Parâmetros
                (form_data:dictionary) Dados de onde se vai retirar as chaves que vão filtrar os dados do banco de dados
            return
                (row_proxy) com os dados obtidos do banco de dados
        '''
        sel = select(self.data_table.c)            
        for key in form_data.keys():
            column = self.data_table.c[key]            
            if column.primary_key:
                sel = sel.where(self.data_table.c.get(key) == form_data[key])
        result = self.conn.execute(sel)
        return result.fetchone()


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
        
        self.filters = {}
        if grid_table == None:
            return None            
        super().__init__(master, connection, grid_table=grid_table, **kwargs)
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
        super().add_widget(filter.label, widget)
        self.filters[filter.label] = filter  


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
            #self.set_form_data(self.get_grid_data_3(int(event.widget.grid_info()['row'])))
            self.set_highlight_grid_line(self.last_clicked_row, self.bg_sel_line_grig)
    def set_filter(self, form_data):
        for key in form_data:
            if form_data[key]:
                field_name = self.filters[key].field_name
                if self.filters[key].comparison_operator == Field.OP_LIKE:
                    self.grid_select_stm = self.grid_select_stm.where(self.grid_table.c[field_name].like(form_data[key])) 
                elif self.filters[key].comparison_operator == Field.OP_GREATER:
                    self.grid_select_stm = self.grid_select_stm.where(self.grid_table.c[field_name] > form_data[key]) 
                elif self.filters[key].comparison_operator == Field.OP_LESS:
                    self.grid_select_stm = self.grid_select_stm.where(self.grid_table.c[field_name] < form_data[key]) 
                elif self.filters[key].comparison_operator == Field.OP_GREATER_EQUAL:
                    self.grid_select_stm = self.grid_select_stm.where(self.grid_table.c[field_name] >= form_data[key]) 
                elif self.filters[key].comparison_operator == Field.OP_LESS_EQUAL:
                    self.grid_select_stm = self.grid_select_stm.where(self.grid_table.c[field_name] <= form_data[key]) 
                elif self.filters[key].comparison_operator == Field.OP_EQUAL:
                    self.grid_select_stm = self.grid_select_stm.where(self.grid_table.c[field_name] == form_data[key]) 

    def search(self):
        #self.grid_select_stm = select(self.grid_table.c).distinct()
        self.set_data_columns() 
        form_data = self.get_form_data()
        self.set_filter(form_data)
        self.get_grid_dbdata()
