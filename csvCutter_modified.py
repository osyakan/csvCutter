import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, simpledialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import glob, sys, os

class WaveformApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Waveform Data App")
        self.geometry("1200x600")
        self.file_path = None
        self.data = None
        self.canvas = None
        self.selected_region = None
        self.secondcanvas = None
        self.window_width = 10
        self.colors = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF', '#800000', '#008000', '#000080', '#808000', '#800080', '#008080', '#C0C0C0', '#808080', '#FFA500', '#FFC0CB', '#FFD700', '#FF6347', '#7FFFD4', '#7FFF00', '#BA55D3', '#FFA07A', '#FF4500', '#DB7093', '#ADFF2F', '#FFDAB9', '#9370DB', '#FF69B4', '#00CED1', '#FFB6C1']
        self.selected_graph = None  # This will hold the name of the graph to display


        self.load_button = tk.Button(self, text="Load CSV", command=self.load_csv)
        self.load_button.pack(pady=10)

        # self.change_button = tk.Button(self, text="Change CSV", command=self.load_csv)
        self.save_button = tk.Button(self, text="Save Data", command=self.save_data, state=tk.DISABLED)
        self.window_width_text_entry = tk.Entry()
        self.window_width_text_entry.insert(0,self.window_width)

        # set dropdown
        self.graph_selector = ttk.Combobox(self, values=[""])
        self.graph_selector.pack(pady=10)
        self.graph_selector.bind('<<ComboboxSelected>>', self.update_selected_graph)

    def load_csv(self):
        self.selected_region = None
        self.secondcanvas = None
        self.selected_graph = None
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            self.file_path = file_path
            self.data = pd.read_csv(self.file_path, index_col=0, header=None)
            self.plot_data()
            # self.change_button.pack(pady=10)
            self.window_width_text_entry.pack(pady=10)
            self.graph_selector["values"] = self.data.index.tolist()

            # self.save_button.pack(pady=10)

    def plot_data(self):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        fig, ax = plt.subplots(figsize=(8, 4))

        # for label, waveform in self.data.iloc[:, 1:].items():
        #     ax.plot(waveform, label=label)

        for l, waveform,c in zip(self.data.index.tolist(),self.data.itertuples(),self.colors[:len(self.data.index.tolist())]):
            ax.plot(waveform[1:], label=l, color=c)
        # 凡例をグラフ外に表示
        ax.legend(bbox_to_anchor=(1.03, 1), loc='upper left', borderaxespad=0, fontsize=8)
        # グラフ外に出た凡例を含めてキャンバスをリサイズ
        fig.tight_layout()
        # 元々は以下のとおり
        # ax.legend()

        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        fig.canvas.mpl_connect("button_press_event", self.on_click)

    def update_selected_graph(self, event):
        '''Update the selected graph when a new one is chosen from the dropdown.'''
        self.selected_graph = self.graph_selector.get()
        print(self.selected_graph)
        if self.selected_graph=='': return
        self.show_single_data()

    def on_click(self, event):
        if event.inaxes is None:
            return

        x_coord = int(event.xdata)
        # window_width = 10  # ウィンドウサイズ
        tmp = self.window_width_text_entry.get()
        if tmp.isdecimal():
            self.window_width = int(tmp)
        else:
            self.window_width_text_entry.insert(0,tk.END)
            self.window_width_text_entry.insert(0,self.window_width)

        self.selected_region = (x_coord, x_coord + self.window_width)
        self.show_selected_data()

    # 選択した一つのグラフを表示
    def show_single_data(self):
        top = tk.Toplevel()
        top.title("Selected Data")
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(self.data.loc[self.selected_graph],label=self.selected_graph)
        ax.set_title(self.selected_graph)
        #  グラフの描写
        canvas = FigureCanvasTkAgg(fig, master=top)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def show_selected_data(self):
        if self.selected_region:
            start, end = self.selected_region
            selected_data = self.data.iloc[:, start:end]
            top = tk.Toplevel()
            top.title("Selected Data")
            
            fig, ax = plt.subplots(figsize=(6, 4))
            # for label, waveform in selected_data.items():
            #     ax.plot(waveform, label=label)
            # ax.legend()
            for l, waveform,c in zip(selected_data.index.tolist(),selected_data.itertuples(),self.colors[:len(selected_data.index.tolist())]):
                ax.plot(waveform[1:], label=l, color=c)
            # 凡例をグラフ外に表示
            ax.legend(bbox_to_anchor=(1.03, 1), loc='upper left', borderaxespad=0, fontsize=8)
            # グラフ外に出た凡例を含めてキャンバスをリサイズ
            fig.tight_layout()

            #  グラフの描写
            canvas = FigureCanvasTkAgg(fig, master=top)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
            
            # 保存ボタンの作成
            button = tk.Button(top, text="Save Data", command=self.save_data)
            button.pack(pady=10)

            self.secondcanvas = top

    # TODO ファイル名をジェスチャ名、ユーザ名がわかる形式で保存する部分を実装
    def save_data(self):
        print(self.file_path)
        file_name = simpledialog.askstring("Save Data", "Enter the file name:", initialvalue="0-0-0.csv")
        if file_name:
            file_name = file_name.strip()
            if not file_name.endswith(".csv"):
                file_name += ".csv"

            start, end = self.selected_region
            selected_data = self.data.iloc[:, start:end]
            selected_data.to_csv(file_name, index=True, header=False)

        self.selected_region = None
        self.secondcanvas.destroy()

if __name__ == "__main__":
    app = WaveformApp()
    app.mainloop()
