
import flet as ft
import sqlite3

class TodoApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.conn = self.create_db()  # Inicialização da conexão com o banco de dados
        self.results = self.db_execute('SELECT * FROM task')
        self.page.bgcolor = ft.colors.WHITE
        self.page.window_width = 350
        self.page.window_height = 450
        self.page.window_resizable = False
        self.page.window_always_on_top = True
        self.view = 'all'
        self.page.title = 'Tarefex'
        self.build_ui()

    def task_container(self):
        return ft.Container(
            height=self.page.height * 0.8,
            content=ft.Column(
                controls=[
                    ft.Checkbox(
                        label=res[1],
                        on_change=self.checked,
                        value=True if res[2] == 'complete' else False
                    ) for res in self.results.fetchall() if res
                ],
            )
        )

    def create_db(self):
        try:
            conn = sqlite3.connect('todo.db')
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS task (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    status TEXT NOT NULL
                )
            ''')
            conn.commit()
            print("Tabela `task` criada (se não existia).")
            return conn
        except sqlite3.Error as e:
            print(f"Erro ao criar tabela: {e}")
            return None

    def db_execute(self, query, params=[]):
        try:
            if self.conn:
                cur = self.conn.cursor()
                cur.execute(query, params)
                self.conn.commit()
                return cur
            else:
                print("Conexão com o banco de dados não está disponível.")
                return None
        except sqlite3.Error as e:
            print(f"Erro ao executar query: {e}")
            return None

    def add(self, e, input_task):
        name = input_task.value
        if not name:
            self.page.snack_bar = ft.SnackBar(ft.Text("Nome da tarefa não pode estar vazio"), open=True)
            self.page.update()
            return
        status = "incomplete"
        result = self.db_execute('INSERT INTO task (name, status) VALUES (?, ?)', [name, status])
        if result:
            input_task.value = ""
            self.results = self.db_execute('SELECT * FROM task')
            self.update_task_list()
        else:
            print("Erro ao adicionar tarefa.")

    def checked(self, e):
        is_checked = e.control.value
        label = e.control.label
        new_status = "complete" if is_checked else "incomplete"
        self.db_execute('UPDATE task SET status = ? WHERE name = ?', [new_status, label])

        if self.view == 'all':
            self.results = self.db_execute('SELECT * FROM task')
        elif self.view == 'incomplete':
            self.results = self.db_execute('SELECT * FROM task WHERE status = "incomplete"')
        elif self.view == 'complete':
            self.results = self.db_execute('SELECT * FROM task WHERE status = "complete"')

        self.update_task_list()

    def update_task_list(self):
        if self.view == 'all':
            tasks = self.db_execute('SELECT * FROM task')
        elif self.view == 'incomplete':
            tasks = self.db_execute('SELECT * FROM task WHERE status = "incomplete"')
        elif self.view == 'complete':
            tasks = self.db_execute('SELECT * FROM task WHERE status = "complete"')

        if tasks:
            self.task_list.controls.clear()
            for task in tasks.fetchall():
                self.task_list.controls.append(
                    ft.Row(
                        controls=[
                            ft.Checkbox(
                                label=task[1],
                                on_change=self.checked,
                                value=True if task[2] == 'complete' else False
                            ),
                            ft.IconButton(ft.icons.DELETE, on_click=lambda e, task_id=task[0]: self.delete_task(task_id))
                        ]
                    )
                )
            self.page.update()
        else:
            print("Erro ao atualizar a lista de tarefas.")
    
    def tabs_changed(self, e):
        if e.control.selected_index == 0:
            self.view = 'all'
        elif e.control.selected_index == 1:
            self.view = 'incomplete'
        elif e.control.selected_index == 2:
            self.view = 'complete'

        self.update_task_list()

    def delete_task(self, task_id):
        self.db_execute('DELETE FROM task WHERE id = ?', [task_id])
        self.update_task_list()

    def set_value(self, e):
        self.task = e.control.value
        print(self.task)
        # Implementação do método para manipular a mudança de valor do campo de texto
        pass

    def build_ui(self):
        self.main_page()

    def main_page(self):
        input_task = ft.TextField(hint_text='Digite uma tarefa', expand=True, on_change=self.set_value)

        input_bar = ft.Row(
            controls=[
                input_task,
                ft.FloatingActionButton(icon=ft.icons.ADD, on_click=lambda e: self.add(e, input_task))
            ]
        )

        tabs = ft.Tabs(
            on_change=self.tabs_changed,
            selected_index=0,
            tabs=[
                ft.Tab(text='Todos'),
                ft.Tab(text='Em andamento'),
                ft.Tab(text='Finalizados')
            ]
        )

        self.task_list = ft.Column()

        self.page.add(
            ft.Column(
                controls=[
                    input_bar,
                    tabs,  # Adicionando tabs ao layout principal
                    self.task_list
                ]
            )
        )

        self.update_task_list()

def main(page: ft.Page):
    TodoApp(page)

ft.app(target=main)
