import logging
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
import psutil
from db import Database


class Title(tk.Frame):
    def __init__(self, parent, text):
        tk.Frame.__init__(self, parent)
        self.label = tk.Label(self, text=text)
        self.label.pack(pady=10, padx=10)


class PlotWidget(tk.Frame):
    """Виджет для отображения графика, включает в себя настройки"""

    def __init__(self, parent: tk.Frame, db: Database, npts: int = 10):
        """Инициализация виджета

        Args:
            parent (tk.Frame): Родительский виджет
            npts (int, optional): Количество точек на графике. Defaults to 10.
        """
        self.db = db
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.options_dict = {
            "1 секунда": 1000,
            "10 секунд": 10000,
            "1 минута": 60000
        }

        dateTimeObj = datetime.now() + timedelta(seconds=-npts)
        self.x_data = [dateTimeObj + timedelta(seconds=i) for i in range(npts)]
        self.y_data = [0 for i in range(npts)]

        self._set_interval(list(self.options_dict.keys())[0])
        self._setup_title()
        self._setup_figure()
        self._setup_settings()

    def _setup_title(self):
        """Настройка заголовка"""
        tk.Label(self, text="Загрузка процессора").pack(pady=10, padx=10)

    def _setup_figure(self):
        """Настройка области для графика"""
        self.figure = Figure(figsize=(7, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH,
                                         expand=True, padx=10, pady=10)

        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Загрузка процессора")
        self.ax.set_xlabel("Время")
        self.ax.set_ylabel("Загрузка, %")
        self.ax.set_ylim(0, 100)
        self.ax.set_xlim(self.x_data[0], self.x_data[-1])
        self.ax.grid()
        self.plot, = self.ax.plot(self.x_data, self.y_data)

    def _setup_settings(self):
        """Настройка области для настроек"""
        self.interval_variable = tk.StringVar(master=self, value=list(
            self.options_dict.keys())[0], name="interval")
        tk.Label(self, text="Интервал обновления").pack()
        tk.OptionMenu(
            self,
            self.interval_variable,
            *self.options_dict.keys(),
            command=self._set_interval
        ).pack()

    def _set_interval(self, choice: str):
        """Обновление интервала обновления графика"""
        self.interval = self.options_dict[choice]

    def draw_loop(self):
        """Основной цикл отрисовки графика"""

        # Обновление данных
        self.x_data.append(datetime.now())
        self.y_data.append(psutil.cpu_percent(0.5))
        self.x_data = self.x_data[1:]
        self.y_data = self.y_data[1:]

        # Обновление графика
        self.ax.set_xlim(self.x_data[0], self.x_data[-1])
        self.ax.set_ylim(0, 100)
        self.plot.set_data(self.x_data, self.y_data)
        self.canvas.draw_idle()

        # Сохранение данных в БД
        self.db.write_data(self.y_data[-1])

        # Планирование следующего обновления
        self.after(self.interval, self.draw_loop)


if __name__ == "__main__":
    # Настройка логирования
    logger = logging.getLogger("gui cpu")
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '[%(asctime)s - %(name)s - %(levelname)s] - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Инициализация БД
    db = Database("cpu_gui.db", logger)
    db.create_table("cpu_load_archive")

    # Инициализация графического интерфейса
    options_dict = {
        "1 секунда": 1000,
        "10 секунд": 10000,
        "1 минута": 60000
    }
    root = tk.Tk()
    root.title("cpu-load")
    root.geometry("1100x600")

    plot_widget = PlotWidget(root, db)
    plot_widget.pack(fill='both', expand=True)
    plot_widget.draw_loop()

    root.mainloop()
