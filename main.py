from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.config import Config
from telas import *
from botoes import *
import sqlite3
import time

GUI = Builder.load_file('main.kv')
Config.set('kivy', 'exit_on_escape', 'False')


def data():
    ano, mes, dia, hora, minuto, f, g, h, i = time.localtime()
    dataa = f'{dia:02}/{mes:02}/{ano} {hora}:{minuto:02}'
    return dataa


class MainApp(App):
    def __init__(self):
        super(MainApp, self).__init__()
        self.banco = sqlite3.connect("banco_cadastro.db")
        self.cursor = self.banco.cursor()

    def build(self):
        Window.size = (360, 640)
        Window.bind(on_keyboard=self.voltar)
        return GUI

    def mudar_tela(self, id_tela, titulo):
        gerenciador = self.root.ids["screen_manager"]
        gerenciador.current = id_tela
        labelT = self.root.ids['titulo']
        labelT.text = titulo
        telaP = self.root.ids.screen_manager.get_screen("pesquisar")
        if telaP.ids.btn_slv_edt.text == 'Salvar':
            cond = True
            telaP.ids.btn_slv_edt.text = 'Editar'
            telaP.ids.nometxt.readonly = cond
            telaP.ids.telltxt.readonly = cond
            telaP.ids.carrotxt.readonly = cond
            telaP.ids.infotxt.readonly = cond

    def habilitar_edicao(self):
        telaP = self.root.ids.screen_manager.get_screen("pesquisar")
        if telaP.ids.btn_slv_edt.text == 'Salvar':
            cond = True
            telaP.ids.btn_slv_edt.text = 'Editar'
            self.salvar('pesquisar')
        else:
            cond = False
            telaP.ids.btn_slv_edt.text = 'Salvar'
        telaP.ids.nometxt.readonly = cond
        telaP.ids.telltxt.readonly = cond
        telaP.ids.carrotxt.readonly = cond
        telaP.ids.infotxt.readonly = cond

    def limpar(self):
        telaC = self.root.ids.screen_manager.get_screen("cadastro")
        telaC.ids.nometxt.text = ''
        telaC.ids.telltxt.text = ''
        telaC.ids.placatxt.text = ''
        telaC.ids.carrotxt.text = ''
        telaC.ids.infotxt.text = ''

    def salvar(self, scren):
        tela = self.root.ids.screen_manager.get_screen(scren)
        nome = tela.ids.nometxt.text
        tell = tela.ids.telltxt.text
        placa = tela.ids.placatxt.text
        carro = tela.ids.carrotxt.text
        info = tela.ids.infotxt.text
        if scren == 'cadastro':
            try:
                self.cursor.execute('''CREATE TABLE IF NOT EXISTS dados(nome text,tell text,placa primary key,carro text,
                    data text, info text)''')
                if nome.strip() == '' or tell.strip() == '' or placa.strip() == '' or carro.strip() == '':
                    popup = Popup(title='Alerta', content=Label(text='Usuario nao cadastrado,\ncomplete todos os campos.'), size_hint=(None, None), size=(300, 100))
                    popup.open()
                else:
                    self.cursor.execute(
                        f'''INSERT INTO dados VALUES ('{nome}','{tell}','{placa}','{carro}','{data()}', '{info}')''')
                    self.banco.commit()
                    popup = Popup(title='Alerta', content=Label(text='Dados inseridos com sucesso!'), size_hint=(None, None), size=(300, 100))
                    popup.open()
                    self.limpar()
            except sqlite3.Error as erro:
                if str(erro) == 'UNIQUE constraint failed: dados.placa':
                    popup = Popup(title='Alerta', content=Label(text='Placa ja existente'), size_hint=(None, None), size=(300, 100))
                    popup.open()
        else:
            try:
                if nome.strip() == '' or tell.strip() == '' or placa.strip() == '' or carro.strip() == '' or info.strip() == '':
                    popup = Popup(title='Alerta', content=Label(text='Usuario nao alterado, complete todos os campos.'), size_hint=(None, None), size=(300, 100))
                    popup.open()
                else:
                    popup = Popup(title='Confirmação', size_hint=(None, None), size=(300, 200), auto_dismiss=False)
                    layout = BoxLayout(orientation='vertical')
                    layout.add_widget(Label(text='Deseja realmente alterar os dados?'))
                    buttons_layout = BoxLayout()
                    buttons_layout.add_widget(
                        Button(text='Sim', on_release=lambda *args: self.confirmarAlteracao(popup)))
                    buttons_layout.add_widget(Button(text='Não', on_release=lambda *args: popup.dismiss()))
                    layout.add_widget(buttons_layout)
                    popup.content = layout
                    popup.open()
            except sqlite3.Error as erro:
                print("Erro ao alterar os dados: ", erro)

    def confirmarAlteracao(self, popup):
        tela = self.root.ids.screen_manager.get_screen('pesquisar')
        nome = tela.ids.nometxt.text
        tell = tela.ids.telltxt.text
        placa = tela.ids.placatxt.text
        carro = tela.ids.carrotxt.text
        info = tela.ids.infotxt.text
        self.cursor.execute(
            f'''UPDATE dados SET nome = '{nome}', tell = '{tell}', carro = '{carro}', data = '{data()}', info = '{info}' WHERE placa = '{placa}' ''')
        self.banco.commit()
        popup.dismiss()
        popup = Popup(title='Alerta', content=Label(text='Usuario alterado com sucesso!!'), size_hint=(None, None), size=(300, 100))
        popup.open()

    def pesquisar_dados(self):
        placa = self.root.ids.screen_manager.get_screen("cadastro").ids.placatxt.text
        result = self.cursor.execute(
            f'''SELECT * from dados WHERE placa = '{placa}' ''').fetchall()
        if len(result) == 0:
            popup = Popup(title='Alerta', content=Label(text='Nao encontrada\nInsira uma placa existente'), size_hint=(None, None), size=(300, 100))
            popup.open()
        else:
            self.mudar_tela("pesquisar", 'Informacoes do Cliente')
            self.listar_dados_P(placa)
        self.limpar()

    def listar_dados_P(self, placa):
        nome, tell, placa, carro, data, info = self.cursor.execute(f'''SELECT * from dados WHERE placa = '{placa}' ''').fetchall()[0]
        telaP = self.root.ids.screen_manager.get_screen("pesquisar")
        telaP.ids.nometxt.text = nome
        telaP.ids.telltxt.text = tell
        telaP.ids.placatxt.text = placa
        telaP.ids.carrotxt.text = carro
        telaP.ids.datatxt.text = data
        telaP.ids.infotxt.text = info

    def excluirDados(self):
        placa = self.root.ids.screen_manager.get_screen("pesquisar").ids.placatxt.text
        popup = Popup(title='Confirmação', size_hint=(None, None), size=(300, 200), auto_dismiss=False)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='Deseja realmente excluir o cadastro?'))
        buttons_layout = BoxLayout()
        buttons_layout.add_widget(Button(text='Sim', on_release=lambda *args: self.confirmarExcluir(popup, placa)))
        buttons_layout.add_widget(Button(text='Não', on_release=lambda *args: popup.dismiss()))
        layout.add_widget(buttons_layout)
        popup.content = layout
        popup.open()

    def confirmarExcluir(self, popup, placa):
        popup.dismiss()
        try:
            self.cursor.execute(f'''DELETE FROM dados WHERE placa = '{placa}' ''')
            self.banco.commit()
            popup = Popup(title='Alerta', content=Label(text='Usuario excluido com sucesso!!'), size_hint=(None, None), size=(300, 100))
            popup.open()
            self.mudar_tela('cadastro', 'Cadastro de Clientes')
        except sqlite3.Error as erro:
            popup = Popup(title='Alerta', content=Label(text=f'Erro ao excluir {erro}!!'), size_hint=(None, None),size=(300, 100))
            popup.open()

    def voltar(self, window, key, *args):
        # Detecta quando o usuário pressiona o botão de voltar
        if key == 27:
            self.mudar_tela("cadastro", 'Cadastro de Clientes')
            # Execute a ação desejada aqui


MainApp().run()
