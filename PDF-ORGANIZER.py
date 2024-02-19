#-*- coding: {utf-8} -*-
import tkinter
from tkinter import *
from tkinter import ttk as ttk
from fpdf import FPDF

import sv_ttk

from pathlib import Path
import pypdf as pdf
import shutil as s
import os
import time
from tktooltip import ToolTip
from PIL import ImageTk, Image
from tkinter import messagebox as msg

from tkinter import filedialog

import json

# import sys
# import numering_pages_test
# import convimg
# import zlacz_takie_same_nazwy

class Node():
    def __init__(self, state):
        self.state = state


class StackFrontier():
    def __init__(self):
        self.frontier = []

    def add(self, node):
        self.frontier.append(node)

    def contains_state(self, state):
        return any(node.state == state for node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node


class QueueFrontier(StackFrontier):

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node

class NumberPDF(FPDF):
    def __init__(self, nop, typ):
        super(NumberPDF, self).__init__()
        self.numberOfPages = nop
        self.type = typ

    # Overload Header
    def header(self):
        pass

    # Overload Footer
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        if self.type == 0:
            self.cell(0, 10, f"{self.page_no()}", 0, 0, 'R')
        else:
            self.cell(0, 10, f"{self.page_no()} z {self.numberOfPages}", 0, 0, 'R')


class PdfGui:
    def __init__(self):

        version = "BETA 2.3"

        self.size_x = 500  # 1200
        self.size_y = 500
        self.path = None
        self.path_s = None
        self.root = Tk()
        self.root.title(f"PDF-ORGANIZER ({version})")
        self.root.geometry(f"{self.size_x}x{self.size_y}")
        self.root.minsize(self.size_x, self.size_y)

        if os.path.exists("icon.ico"):
            self.root.iconbitmap("icon.ico")

        # default values
        #########################
        pad = 2.5
        icon_size = (round(self.size_y/15), round(self.size_y/15))
        #########################
        # self.root.configure(bg="White")

        self.root.grid_columnconfigure(0, weight=3)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=1)

        self.path_frame = Frame(self.root)
        self.path_frame.grid(row=0, column=0, sticky="NEWS", padx=pad, pady=pad)
        self.path_frame.rowconfigure(0, weight=1)
        self.path_frame.rowconfigure(1, weight=1)
        self.path_frame.columnconfigure(0, weight=1)

        self.path_in = tkinter.StringVar()
        self.path_out = tkinter.StringVar()

        self.config = "pdf-organizer.config"

        in_file = ttk.Entry(self.path_frame, textvariable=self.path_in)
        in_file.grid(row=0, column=0, sticky="NEWS", pady=pad, padx=pad)

        out_file = ttk.Entry(self.path_frame, textvariable=self.path_out)
        out_file.grid(row=1, column=0, sticky="NEWS", pady=pad, padx=pad)

        self.btn_frame = ttk.Frame(self.root)
        self.btn_frame.grid(row=0, column=1, sticky="NEWS", padx=pad, pady=pad)
        self.btn_frame.rowconfigure(0, weight=1)
        self.btn_frame.rowconfigure(1, weight=1)
        self.btn_frame.columnconfigure(0, weight=1)
        self.btn_frame.columnconfigure(1, weight=1)

        p0 = Image.open("resources/add_file.png")
        pr0 = p0.resize(icon_size)
        ph0 = ImageTk.PhotoImage(pr0)

        btn_open_file = ttk.Button(self.btn_frame, text="Pliki", style='Accent.TButton', image=ph0,
                                   command=lambda: self.path_in.set(self.open_file()))
        btn_open_file.grid(row=0, column=0, sticky="NEWS", padx=pad, pady=pad)
        ToolTip(btn_open_file, msg="Wybierz plik lub pliki wejściowe")

        p1 = Image.open("resources/add_dir.png")
        pr1 = p1.resize(icon_size)
        ph1 = ImageTk.PhotoImage(pr1)

        btn_open_dir = ttk.Button(self.btn_frame, text="Folder", style='Accent.TButton', image=ph1,
                                  command=lambda: self.path_in.set(self.open_dir()))
        btn_open_dir.grid(row=0, column=1, sticky="NEWS", padx=pad, pady=pad)
        ToolTip(btn_open_dir, msg="Wybierz folder z plikami wejściowymi")

        p1 = Image.open("resources/svd_file.png")
        pr1 = p1.resize(icon_size)
        ph2 = ImageTk.PhotoImage(pr1)

        btn_save_file = ttk.Button(self.btn_frame, text="Zapisz plik", style='Accent.TButton', image=ph2,
                                   command=lambda: self.path_out.set(self.save_file()))
        btn_save_file.grid(row=1, column=0, sticky="NEWS", padx=pad, pady=pad)
        ToolTip(btn_save_file, msg="Zapisz do pliku")

        p1 = Image.open("resources/svd_dir.png")
        pr1 = p1.resize(icon_size)
        ph3 = ImageTk.PhotoImage(pr1)

        btn_view_file = ttk.Button(self.btn_frame, text="Folder zapisu", style='Accent.TButton', image=ph3,
                                   command=lambda: self.path_out.set(self.open_dir()))
        btn_view_file.grid(row=1, column=1, sticky="NEWS", padx=pad, pady=pad)
        ToolTip(btn_save_file, msg="Wybierz folder zapisu")

        self.setting_frame = ttk.Frame(self.root)
        self.setting_frame.grid(row=1, column=0, columnspan=2, sticky="NEWS", padx=pad, pady=pad)
        self.setting_frame.rowconfigure((0, 1, 2), weight=1)
        self.setting_frame.columnconfigure(0, weight=1)
        self.setting_frame.columnconfigure(1, weight=1)

        # SET 1 - segregacja

        self.selected_radio_0 = tkinter.StringVar()

        lbl_seg = ttk.Label(self.setting_frame, text="Rodzaj segregacji")
        lbl_seg.grid(row=0, column=0, sticky="NW", pady=pad, padx=pad)

        cbo_seg = ttk.Combobox(self.setting_frame, values=["NON", "FILE", "AI engine", "SUPER", "SUPER AI"], state="readonly",
                               textvariable=self.selected_radio_0)
        cbo_seg.grid(row=0, column=1, pady=pad, padx=pad, sticky="news")
        self.selected_radio_0.set('NON')

        # SET 2 - wybór

        self.selected_radio_1 = tkinter.StringVar()
        self.selected_radio_1.set('DIR')

        lbl_cho = ttk.Label(self.setting_frame, text="Pliki z")
        lbl_cho.grid(row=1, column=0, sticky="NW", pady=pad, padx=pad)

        cbo_cho = ttk.Combobox(self.setting_frame, values=["DIR", "DIRS"], state="readonly",
                               textvariable=self.selected_radio_1)
        cbo_cho.grid(row=1, column=1, pady=pad, padx=pad, sticky="news")
        self.selected_radio_1.set('DIR')

        # SET 3 - motyw

        self.selected_radio_2 = tkinter.StringVar()
        self.selected_radio_2.set('Light')

        lbl_thm = ttk.Label(self.setting_frame, text="Motyw")
        lbl_thm.grid(row=2, column=0, sticky="NW", pady=pad, padx=pad)

        cbo_thm = ttk.Combobox(self.setting_frame, values=["light", "dark"], state="readonly",
                               textvariable=self.selected_radio_2)
        cbo_thm.grid(row=2, column=1, pady=pad, padx=pad, sticky="news")
        self.selected_radio_2.set('DIR')

        cbo_thm.bind("<<ComboboxSelected>>", lambda x: self.theme())

        # special button
        pfH = ImageTk.PhotoImage(Image.open("resources/fun_ph.png").resize(icon_size))

        p1 = Image.open("resources/pdf.png")
        pr1 = p1.resize(icon_size)
        ph4 = ImageTk.PhotoImage(pr1)

        btn_open_ex_file = ttk.Button(self.setting_frame, text="Folder zapisu", style='Accent.TButton', image=ph4,
                                      command=lambda: self.open_svd_file())

        btn_open_ex_file.grid(row=0, column=2, sticky="NEWS", padx=pad, pady=pad)
        ToolTip(btn_open_ex_file, msg="Otwórz zapisany plik")

        btn_fH1 = ttk.Button(self.setting_frame, text=":::", style='Accent.TButton', image=pfH)
        btn_fH1.grid(row=1, column=2, sticky="NEWS", padx=pad, pady=pad)
        ToolTip(btn_fH1, msg=":::")

        btn_fH2 = ttk.Button(self.setting_frame, text=":::", style='Accent.TButton', image=pfH)
        btn_fH2.grid(row=2, column=2, sticky="NEWS", padx=pad, pady=pad)
        ToolTip(btn_fH2, msg=":::")

        self.option_frame = ttk.Frame(self.root)
        self.option_frame.grid(row=2, column=0, columnspan=2, sticky="NEWS", padx=pad, pady=pad)
        self.option_frame.rowconfigure((0, 1, 2), weight=1)
        self.option_frame.columnconfigure(0, weight=1)
        self.option_frame.columnconfigure(1, weight=1)
        self.option_frame.columnconfigure(2, weight=1)
        self.option_frame.columnconfigure(3, weight=1)
        self.option_frame.columnconfigure(4, weight=1)

        # ROW 0
        # f1 - poprawa parzystości plików PDF

        pf1 = ImageTk.PhotoImage(Image.open("resources/fun_1.png").resize(icon_size))
        btn_f1 = ttk.Button(self.option_frame, text="Parzystość", command=lambda: self.run_pdf(1), image=pf1)
        btn_f1.grid(row=0, column=0, sticky="NEWS", padx=pad, pady=pad)
        ToolTip(btn_f1, msg="Popraw parzystość plików PDF")

        # f2 - złącz masowo pliki PDF
        # TODO dodaj do ustawień parametr pozwalający na pomijanie lub nie skanów przy łączeniu masowym (f2, f10)

        pf2 = ImageTk.PhotoImage(Image.open("resources/fun_2.png").resize(icon_size))
        btn_f2 = ttk.Button(self.option_frame, text="Złącz masowo", command=lambda: self.run_pdf(2), image=pf2)
        btn_f2.grid(row=0, column=1, sticky="NEWS", padx=pad, pady=pad)
        ToolTip(btn_f2, msg="Złącz masowo wybrane pliki PDF lub wszystkie z folderu/ów (pomija skany)")

        # f3 - podziel plik PDF na pliki duplexowe

        pf3 = ImageTk.PhotoImage(Image.open("resources/fun_3.png").resize(icon_size))
        btn_f3 = ttk.Button(self.option_frame, text="Podziel duplexy", command=lambda: self.run_pdf(6), image=pf3)
        btn_f3.grid(row=0, column=2, sticky="NEWS", padx=pad, pady=pad)
        ToolTip(btn_f3, msg="Podziel PDF na pliki duplexowe")

        # f4 - lista stron z pliku PDF
        pf4 = ImageTk.PhotoImage(Image.open("resources/fun_4.png").resize(icon_size))
        btn_f4 = ttk.Button(self.option_frame, text="Lista stron", command=lambda: self.run_pdf(7), image=pf4)
        btn_f4.grid(row=0, column=3, sticky="NEWS", padx=pad, pady=pad)
        ToolTip(btn_f4, msg="Lista stron z pliku PDF")

        pf5 = ImageTk.PhotoImage(Image.open("resources/fun_5.png").resize(icon_size))
        btn_f5 = ttk.Button(self.option_frame, text="Złącz s/p", command=lambda: self.run_pdf(5), image=pf5)
        btn_f5.grid(row=0, column=4, sticky="NEWS", padx=pad, pady=pad)
        ToolTip(btn_f5, msg="Złącz pliki z pojedyncze do pliku A i duplexowe do pliku B")

        # ROW 1
        pf6 = ImageTk.PhotoImage(Image.open("resources/fun_6.png").resize(icon_size))
        btn_f6 = ttk.Button(self.option_frame, text="2 pierwsze str", command=lambda: self.run_pdf(9), image=pf6)
        btn_f6.grid(row=1, column=0, sticky="NEWS", padx=pad, pady=pad)
        ToolTip(btn_f6, msg="Złącz masowo tylko 2 pierwsze strony z plików")

        pf7 = ImageTk.PhotoImage(Image.open("resources/fun_7.png").resize(icon_size))
        btn_f7 = ttk.Button(self.option_frame, text="2 ostatnie str", command=lambda: self.run_pdf(11), image=pf7)
        btn_f7.grid(row=1, column=1, sticky="NEWS", padx=pad, pady=pad)
        ToolTip(btn_f7, msg="Złącz masowo tylko 2 ostatnie strony z plików")

        pf8 = ImageTk.PhotoImage(Image.open("resources/fun_8.png").resize(icon_size))
        btn_f8 = ttk.Button(self.option_frame, text="Usuń wszystkie", command=lambda: self.run_pdf(12), image=pf8)
        btn_f8.grid(row=1, column=2, sticky="NEWS", padx=pad, pady=pad)
        ToolTip(btn_f8, msg="Usuń wszystko ze wskazanej lokalizacji")

        pf9 = ImageTk.PhotoImage(Image.open("resources/fun_9.png").resize(icon_size))
        btn_f9 = ttk.Button(self.option_frame, text="Złącz KW", command=lambda: self.run_pdf(8), image=pf9)
        btn_f9.grid(row=1, column=3, sticky="NEWS", padx=pad, pady=pad)
        ToolTip(btn_f9, msg="Złącz KW podzielone na działy")

        pf10 = ImageTk.PhotoImage(Image.open("resources/fun_2.png").resize(icon_size))
        btn_f10 = ttk.Button(self.option_frame, text="Złącz ALL", command=lambda: self.run_pdf(10), image=pf10)
        btn_f10.grid(row=1, column=4, sticky="NEWS", padx=pad, pady=pad)
        ToolTip(btn_f10, msg="Złącz masowo bez pomijania skanów")

        # ROW 2
        # TODO dodać możliwość wyboru miejsca numeracji, liczby początkowej, strony początkowej
        btn_f11 = ttk.Button(self.option_frame, text="Numerowanie", command=lambda: self.run_pdf(13), image=pfH)
        btn_f11.grid(row=2, column=0, sticky="NEWS", padx=pad, pady=pad)
        ToolTip(btn_f11, msg="Numerowanie pliku PDF")

        # TODO Zweryfikować poprawność działania
        pf12 = ImageTk.PhotoImage(Image.open("resources/fun_12.png").resize(icon_size))
        btn_f12 = ttk.Button(self.option_frame, text="Zdjęcie > PDF", command=lambda: self.run_pdf(14), image=pf12)
        # , command=lambda: zlacz_takie_same_nazwy.main())
        btn_f12.grid(row=2, column=1, sticky="NEWS", padx=pad, pady=pad)
        ToolTip(btn_f12, msg="Złącz zdjęcia do PDF (EXPERYMENTALNE)")

        btn_f13 = ttk.Button(self.option_frame, text=":::",command=lambda: self.run_pdf(15), image=pfH)
        # , command=lambda: zlacz_takie_same_nazwy.main())
        btn_f13.grid(row=2, column=2, sticky="NEWS", padx=pad, pady=pad)
        ToolTip(btn_f13, msg="Rozdziel po ID (EXPERYMENTALNE)")

        btn_blank_13 = ttk.Button(self.option_frame, text=":::", image=pfH)
        # , command=lambda: zlacz_takie_same_nazwy.main())
        btn_blank_13.grid(row=2, column=3, sticky="NEWS", padx=pad, pady=pad)

        btn_blank_14 = ttk.Button(self.option_frame, text=":::", image=pfH)
        # , command=lambda: zlacz_takie_same_nazwy.main())
        btn_blank_14.grid(row=2, column=4, sticky="NEWS", padx=pad, pady=pad)

        self.root.protocol("WM_DELETE_WINDOW", lambda: self.save_settings())

        self.setting = dict()

        if os.path.exists(self.config):
            with open(self.config, "r", encoding="utf-8") as file:
                line = file.readline()

                try:
                    self.setting = json.loads(line)
                    print(self.setting['path_out'])
                except:
                    self.setting['path_in'] = "C:/"
                    self.setting['path_out'] = "C:/"
                    self.setting['theme'] = "light"
                    self.setting['seg'] = "NON"
                    self.setting['deep'] = "DIR"

        else:
            self.setting['path_in'] = "C:/"
            self.setting['path_out'] = "C:/"
            self.setting['theme'] = "light"
            self.setting['seg'] = "NON"
            self.setting['deep'] = "DIR"

        self.path_in.set(self.setting['path_in'])
        self.path_out.set(self.setting['path_out'])
        self.selected_radio_0.set(self.setting['seg'])
        self.selected_radio_1.set(self.setting['deep'])
        self.selected_radio_2.set(self.setting['theme'])

        self.theme()

        self.root.mainloop()

    def save_settings(self):

        self.setting['path_in'] = self.path_in.get()
        self.setting['path_out'] = self.path_out.get()
        self.setting['seg'] = self.selected_radio_0.get()
        self.setting['deep'] = self.selected_radio_1.get()
        self.setting['theme'] = self.selected_radio_2.get()

        with open(self.config, "w", encoding="utf-8") as file:
            json.dump(self.setting, file, ensure_ascii=False)

        self.root.destroy()

    def theme(self):

        if self.selected_radio_2.get() == "light":
            sv_ttk.set_theme("light")
        else:
            sv_ttk.set_theme("dark")

    def open_file(self):

        filetypes_option = (("pliki pdf", "*.pdf"), ("Wszystkie pliki", "*.*"))
        path = filedialog.askopenfilenames(title="Wybierz plik lub pliki", filetypes=filetypes_option)
        if path is not None:
            path = str(path).replace("('", "")
            path = path.replace("',)", "\t")
            path = path.replace("')", "\t")
            path = path.replace("', '", "\t")
            path = path.strip()
            return path
        return ""

    def open_dir(self):
        path = filedialog.askdirectory(title="Wybierz folder")

        if path is not None:
            return path
        return ""

    def save_file(self):
        filetypes = (("pliki pdf", "*.pdf"), ("Wszystkie pliki", "*.*"))
        path = filedialog.asksaveasfilename(title="Zapisz plik pdf", filetypes=filetypes)
        if path is not None:
            if not path.endswith(".pdf"):
                path = path + ".pdf"

            return path
        return ""

    def open_svd_file(self):
        if os.path.isfile(str(self.path_out.get())):
            os.startfile(str(self.path_out.get()))

    def view_path(self, path):
        # os.system(self.path_s)
        os.startfile(path)

    def run_pdf(self, i):
        tic = time.perf_counter()

        if self.path_in is not None:
            self.run_pdf_toys(i, self.selected_radio_1.get(), self.path_in.get(), self.path_out.get())
            toc = time.perf_counter()
            time_pass = f"Czas: {toc - tic:0.4f} s\n"
            print(time_pass)

    def run_pdf_toys(self, program, deep, in_path, save_path: str = "C:\\"):
        sch_path = []

        if len(in_path.split("\t")) > 1:
            sch_path.append("Path(in_path)")
            src_files = list(in_path.split("\t"))
        else:
            if in_path.endswith(".pdf"):
                sch_path.append("Path(in_path)")
                # src_files = list(in_path)
                src_files = []
                src_files.append(in_path)
            else:
                sch_path.append(Path(in_path))
                suffix = ".pdf"
                if program == 14:
                    suffix = "pass"
                #if program == 10:
                    #src_files = self.super_pdf_selection(sch_path[0], deep, False, suffix)
                if self.selected_radio_0.get() == "SUPER":
                    src_files = self.super_pdf_selection(sch_path[0], deep, True, suffix)
                elif self.selected_radio_0.get() == "AI engine":
                    src_files = finder(sch_path[0], suffix, True)
                elif self.selected_radio_0.get() == "SUPER AI":
                    src_files = self.sort_by_super(finder(sch_path[0], suffix, True))
                else:
                    src_files = self.pdf_selection(sch_path[0], deep, suffix)

        # if type(in_path) is not tuple:

        #    sch_path.append(Path(in_path))
            # 0 wybór wszystkich plików pdf z folderów i pod folderów ze ścieżki
            # 1 wybór wszystkich plików pdf z folderu ze ścieżki
        #    if program == 10:
        #        src_files = self.super_pdf_selection(sch_path[0], deep, False)
        #    elif self.selected_radio_0.get() == "SUPER":
        #        src_files = self.super_pdf_selection(sch_path[0], deep, True)
        #    else:
        #        src_files = self.pdf_selection(sch_path[0], deep)
        # else:
        #     sch_path.append("Path(in_path)")
        #     src_files = list(in_path)

        if save_path is None:
            save_path = "C:\\"
        sch_path.append(Path(save_path))

        if sch_path[1] is None:
            sch_path[1] = "C:\\"

        match program:
            case 1:  # dodawanie pustej strony do pliku pdf, jeżeli nieparzysta ilość stron
                # parm = "over", "o" - nadpisz istniejący; "edit", "e" - tworzy nowy z dopiskiem "_edited"
                for file in src_files:
                    # print(file)
                    self.add_blank(file, "o")
                print(">> Zakończono: poprawianie parzystości pliku")
                msg.showinfo("PDF-Organizer", "Poprawiono parzytsość plików")
                return 1
            case 2:  # łączenie wszystkich plików pdf z src_files
                # parm = "a", "all" - łączy wszystkie; "s", "skan" - pomija skanowane
                # src_files.sort()
                self.marge_pdf(src_files, sch_path[1], "s")
                print(">> Zakończono: scalanie plików")
                msg.showinfo("PDF-Organizer", "Scalono pliki z pominięciem skanów")
                return 2
            case 3:  # dodawanie blank page przed załącznikami, jeżli przed nimi nie parzysta ilość stron
                for file in src_files:
                    self.add_blank_after_zalacznik(file)
                print(">> Zakończono: poprawę załączników")
                msg.showinfo("PDF-Organizer", "Poprawiono załączniki")
                return 3
            case 4:
                for _ in range(1):
                    for file in src_files:
                        self.add_blank_after_zawiadomienie(file)

                print(">> Zakończono: poprawę zawiadomień")
                msg.showinfo("PDF-Organizer", "Poprawiono zawiadomienia")
                return 4
            case 5:  # łączenie wszystkich plików pdf z src_files z podziałem na druk dwu i jedno stronny
                self.marge_pdf_splited(src_files, sch_path[1])
                print(">> Zakończono: scalanie plików")
                msg.showinfo("PDF-Organizer", "Złączono pliki duplexowe oraz pojedyncze")
                return 5
            case 6:
                for file in src_files:
                    in_f = file
                    out_f = in_f
                    self.split_to_duplex(in_f, out_f)
                msg.showinfo("PDF-Organizer", "Podzielono na duplexy")
                return 6
            case 7:
                # src_files.sort()
                for file in src_files:
                    self.ile_stron(file, sch_path[1])
                print(">> Zakończono: listowanie pdfów")
                msg.showinfo("PDF-Organizer", "Zapisano listę pdfów do txt")
                return 7
            case 8:
                dst_path = filedialog.askdirectory(title="Wybierz folder")
                dst_path = dst_path + "/"
                for file in src_files:
                    # print(file)
                    self.merge_kw(file, dst_path)
                print(">> Zakończono: łaczenie KW")
                msg.showinfo("PDF-Organizer", "Złączono KW rozbite na działy")
                return 8
            case 9:
                self.first_2_pages(src_files, sch_path[1])
                print(">> Zakończono: scalanie plików")
                msg.showinfo("PDF-Organizer", "Scalono 2 pierwsze strony plików")
                return 9
            case 10:
                # parm = "a", "all" - łączy wszystkie; "s", "skan" - pomija skanowane
                # src_files.sort()
                self.marge_pdf(src_files, sch_path[1], "a")
                print(">> Zakończono: scalanie plików")
                msg.showinfo("PDF-Organizer", "Scalono wszystkie pliki")
                return 10
            case 11:
                self.last_2_pages(src_files, sch_path[1])
                print(">> Zakończono: scalanie plików")
                msg.showinfo("PDF-Organizer", "Scalono 2 ostatnie strony plików")
                return 11
            case 12:
                self.delete_all_pdf(src_files)
                print(">> Zakończono: usunięto wszystkie pliki pdf")
                msg.showinfo("PDF-Organizer", "Usunięto pliki pdf ze wskazanej lokalizacji")
                return 12

            case 13:
                typ = 0
                self.add_page_number(src_files, typ)
                print(">> Zakończono: dodawanie numerów stron")
                msg.showinfo("PDF-Organizer", "Dodano numeracje strin")
                return 13
            case 14:
                self.merge_img_to_pdf(src_files, sch_path[1])
                print(">> Zakończono: konwersje zdjęć do pdf")
                msg.showinfo("PDF-Organizer", "Przekonwertowano zdjęcia do PDF")

            case 15:
                msg.showwarning("Brak działania", "Rządana funkcja nie może zostać wykonana z powodu braku kodu.")
                print(">> Brak działania do wykonania")

            case _:  # w przypadku nieporawnej wartości wyjdź
                print(">> Zakończono: poprawianie parzystości pliku")
                msg.showinfo("PDF-Organizer", "Poprawiono parzystość plików")
                return 0

    def pdf_selection(self, sch_path, deep, suffix):
        src_path = [Path(sch_path)]
        src_files = []
        src_path2 = []
        file1 = Path(src_path[0])
        if os.path.isdir(file1):  # if len(file1.suffix) == 0:
            while True:
                for p in src_path:
                    for dirs in os.listdir(p):
                        file_path = p / dirs
                        czy_folder = os.path.isdir(str(file_path))
                        if dirs.endswith("skan.png"):
                            pass
                        elif dirs.endswith(".pdf"):
                            src_files.append(file_path)
                        elif czy_folder:
                            file_path = str(file_path) + "\\"
                            src_path2.append(Path(file_path))
                        elif suffix == "pass":
                            if dirs.endswith(".jpg"):
                                src_files.append(file_path)
                            elif dirs.endswith(".jpeg"):
                                src_files.append(file_path)
                            elif dirs.endswith(".png"):
                                src_files.append(file_path)
                            elif dirs.endswith(".gif"):
                                src_files.append(file_path)
                src_path.clear()
                if deep == "DIRS":
                    src_path = src_path2.copy()
                if len(src_path) == 0:
                    break
                src_path2.clear()
        else:
            src_files.append(file1)

        src_files.sort()  # sortowanie alfabetyczne listy pdf

        return src_files

    def super_pdf_selection(self, sch_path, deep, gear, suffix):

        src_path = [Path(sch_path)]
        src_files = []
        src_path2 = []
        file1 = Path(src_path[0])
        if os.path.isdir(file1):  # if len(file1.suffix) == 0:
            while True:
                for p in src_path:
                    for dirs in os.listdir(p):
                        file_path = p / dirs
                        czy_folder = os.path.isdir(str(file_path))
                        if dirs.endswith("skan.png"):
                            pass
                        elif dirs.endswith(".pdf"):
                            src_files.append(file_path)
                        elif czy_folder:
                            file_path = str(file_path) + "\\"
                            src_path2.append(Path(file_path))
                        elif suffix == "pass":
                            if dirs.endswith(".jpg"):
                                src_files.append(file_path)
                            elif dirs.endswith(".jpeg"):
                                src_files.append(file_path)
                            elif dirs.endswith(".png"):
                                src_files.append(file_path)
                            elif dirs.endswith(".gif"):
                                src_files.append(file_path)

                src_path.clear()
                if deep == "DIRS":
                    src_path = src_path2.copy()
                if len(src_path) == 0:
                    break
                src_path2.clear()
        else:
            src_files.append(file1)

        src_files.sort()  # sortowanie alfabetyczne listy pdf

        ids = []
        for sf in src_files:
            with open(sf, "rb") as file:
                src_pdf = pdf.PdfReader(file)
                text = src_pdf.pages[0].extract_text()
                texts = text.split(" ")
                if gear:
                    ids.append(int(texts[0]))
                else:
                    ids.append(int(texts[0]))

        sorted_ids = ids.copy()
        sorted_ids.sort()
        new_list = []

        # TODO dict zawierający id oraz sciężkę, sortowanie pod ścieżce przykład w zestawienie 'godzinowe.py'
        # TODO lub lista list dwuelementowych, gdzie 1 to lista 2 to ścieżka

        for si in sorted_ids:
            for k in range(0, len(ids)):
                if ids[k] == si:
                    new_list.append(src_files[k])

        return new_list

    def sort_by_super(self, src_files):
        src_files.sort()  # sortowanie alfabetyczne listy pdf

        ids = []
        for sf in src_files:
            with open(sf, "rb") as file:
                src_pdf = pdf.PdfReader(file)
                text = src_pdf.pages[0].extract_text()
                texts = text.split(" ")
                ids.append(int(texts[0]))

        sorted_ids = ids.copy()
        sorted_ids.sort()
        new_list = []

        # TODO dict zawierający id oraz sciężkę, sortowanie pod ścieżce przykład w zestawienie 'godzinowe.py'
        # TODO lub lista list dwuelementowych, gdzie 1 to lista 2 to ścieżka

        for si in sorted_ids:
            for k in range(0, len(ids)):
                if ids[k] == si:
                    new_list.append(src_files[k])

        return new_list

    def add_blank(self, src_path, parm):
        dst_path = src_path
        edst_path = str(dst_path)
        edst_path1 = edst_path[:len(edst_path) - 4]
        edst_path2 = edst_path[len(edst_path) - 4:]

        if parm == "edit" or parm == "e":
            dst_path = edst_path1 + "_edited" + edst_path2
        else:
            dst_path = edst_path1 + "_0" + edst_path2
        dst_path = Path(dst_path)

        if type(src_path) is not Path:
            src_path = Path(src_path)
        if src_path.suffix == ".pdf":
            with open(src_path, "rb") as file:
                src_pdf = pdf.PdfReader(file)
                pages = len(src_pdf.pages)

                out_pdf = pdf.PdfWriter()
                out_pdf.append_pages_from_reader(src_pdf)
                out_pdf.add_blank_page()

                if pages % 2 != 0:
                    with open(dst_path, "wb") as file2:
                        out_pdf.write(file2)
                    if parm == "over" or parm == "o":
                        dst_path = str(dst_path)
                        src_path = str(src_path)
                        s.move(dst_path, src_path)

    def marge_pdf(self, src_files, dst_path, parm):
        out_pdf = pdf.PdfWriter()
        # parm a określa wybranie wszystkich pdf
        # parm s określa omijanie skan plików
        lst_parm = ["a", "all", "s", "skan"]
        i = 0

        print(">> Rozpoczęto scalanie plików:")

        for file in src_files:
            if type(file) is not Path:
                file = Path(file)
            if file.suffix == ".pdf":
                if parm == "s" or parm == "skan":
                    if str(file).endswith("skan.pdf"):
                        out_print = f"{file} --pominięty"
                        print(out_print)
                        continue
                out_print = f"{file}"
                print(out_print)
                src_pdf = pdf.PdfReader(file)
                out_pdf.append_pages_from_reader(src_pdf)
                i += 1

        if parm in lst_parm:
            with open(dst_path, "wb") as file:
                out_pdf.write(file)

        out_print = f"Scalono {i} plików\n"

    def add_blank_after_zalacznik(self, pdf_path):
        pdf_path = str(pdf_path)
        dst_path = ""
        if pdf_path.endswith(".pdf"):
            dst_path = pdf_path.replace(".pdf", "_temp.pdf")

        pages = []
        # text = ""
        names = ["Załącznik A", "Załącznik B", "Załącznik C", "Załącznik nr 1", "Załącznik – Wnioskodawca / uczestnik"]
        # names = ["KW-WU"]

        for n in names:
            sch_name = n
            repair = False

            with open(pdf_path, 'rb') as file0:
                pdf_reader = pdf.PdfReader(file0)
                for i in range(0, len(pdf_reader.pages)):
                    page_obj = pdf_reader.pages[i]
                    all_pages = len(pdf_reader.pages)
                    text = page_obj.extract_text()
                    if text.find(sch_name) > 0 and text.find("KW-WU ") == 0:
                        pages.append(i)

            if len(pages) % 2 != 0:
                repair = True
            out_print = f"{pdf_path} -- {sch_name} niepoprawny: {repair}\n"
            print(out_print)

            if repair:
                with open(pdf_path, 'rb') as file1:
                    src_pdf = pdf.PdfReader(file1)
                    out_pdf = pdf.PdfWriter()

                    for page2add in range(all_pages):
                        if int(pages[-1]) % 2 != 0 and page2add == int(pages[-1]):
                            out_pdf.add_blank_page(210, 297)
                        out_pdf.add_page(src_pdf.pages[page2add])

                    with open(dst_path, "wb") as file2:
                        out_pdf.write(file2)

                    s.move(dst_path, pdf_path)
            pages.clear()
        self.add_blank(Path(pdf_path), "o")

    def add_blank_after_zawiadomienie(self, pdf_path):
        pdf_path = str(pdf_path)
        dst_path = ""
        if pdf_path.endswith(".pdf"):
            dst_path = pdf_path.replace(".pdf", "_temp.pdf")

        pages = []
        # text = ""
        # names = ["ZAWIADOMIENIE", "mail", "#S19_002"]

        l_i = 1
        while True:
            sch_name = "mail"
            repair = False

            with open(pdf_path, 'rb') as file0:
                pdf_reader = pdf.PdfReader(file0)
                for i in range(3, len(pdf_reader.pages)):  # 0 na 3 spróbować od 2
                    page_obj = pdf_reader.pages[i]
                    all_pages = len(pdf_reader.pages)
                    text = page_obj.extract_text()
                    if text.find(sch_name) > 0 and i % 2 == 0:
                        pages.append(i)

            # if len(pages) % 2 != 0: repair = True
            if len(pages) != 0:
                repair = True

            out_print = f"Loop: {l_i}, {pdf_path} -- {sch_name} niepoprawny: {repair}\n"
            print(out_print)
            l_i += 1
            if repair:
                with open(pdf_path, 'rb') as file1:
                    src_pdf = pdf.PdfReader(file1)
                    out_pdf = pdf.PdfWriter()

                    for page2add in range(all_pages):
                        if page2add == int(pages[0]):  # <<<
                            out_pdf.add_blank_page(210, 297)
                        out_pdf.add_page(src_pdf.pages[page2add])

                    with open(dst_path, "wb") as file2:
                        out_pdf.write(file2)

                    s.move(dst_path, pdf_path)
            else:
                break
            pages.clear()
        self.add_blank(Path(pdf_path), "o")

    def marge_pdf_splited(self, src_files, dst_path):
        # global msg_val
        out_pdf_single = pdf.PdfWriter()
        out_pdf_plural = pdf.PdfWriter()

        files_p = 0
        files_s = 0

        i = 0
        dst_path = str(dst_path)
        split_path = dst_path.split(".")

        for file in src_files:
            if type(file) is not Path:
                file = Path(file)
            if file.suffix == ".pdf":
                print(file)
                src_pdf = pdf.PdfReader(file)
                rodzaj = "none"
                if len(src_pdf.pages) < 2:
                    out_pdf_single.append_pages_from_reader(src_pdf)
                    files_s += 1
                    rodzaj = "single"
                elif (len(src_pdf.pages) % 2) != 0:
                    out_pdf_plural.append_pages_from_reader(src_pdf)
                    out_pdf_plural.add_blank_page(210, 297)
                    files_p += 1
                    rodzaj = "plural"
                else:
                    out_pdf_plural.append_pages_from_reader(src_pdf)
                    files_p += 1
                    rodzaj = "plural"

                with open(f"{split_path[0]}raport.txt", "a", encoding="utf-8") as raportfile:
                    raportl = f"{file};\t{rodzaj};\n"
                    raportfile.write(raportl)
                i += 1

        dst_path = str(dst_path)
        split_path = dst_path.split(".")

        single = split_path[0] + "-single." + split_path[-1]
        plural = split_path[0] + "-plural." + split_path[-1]

        if files_s > 0:
            with open(single, "wb") as file:
                out_pdf_single.write(file)

        if files_p > 0:
            with open(plural, "wb") as file:
                out_pdf_plural.write(file)

            self.add_blank(Path(plural), "o")

        output_txt = f"Scalono {files_s} plików jednostronnych\nScalono {files_p} plików wielostronnych\n"
        print(output_txt)
        # msg_val = output_txt

    def split_to_duplex(self, in_f, out_f):
        # global msg_val
        reader = pdf.PdfReader(in_f)
        writer = pdf.PdfWriter()
        name = ""
        out_f = str(out_f)
        splited = out_f.split("/")
        out_f = ""
        for f in splited:
            print(f)
            if f == splited[-1]:
                name = f
                break
            out_f = out_f + f + "\\"
        j = 0
        i = 0
        x = 0
        out_f = out_f + f"{name}_duplex\\"
        if os.path.isdir(out_f) is not True:
            os.mkdir(out_f)

        for page in reader.pages:
            i += 1
            x += 1
            writer.add_page(page)

            o_file = out_f + f"{j}.pdf"

            if j < 10:
                o_file = out_f + f"00{j}.pdf"
            elif j < 100:
                o_file = out_f + f"0{j}.pdf"

            if i == 2:
                j += 1
                with open(o_file, "wb") as fp:
                    writer.write(fp)
                writer = pdf.PdfWriter()
                i = 0

        if len(writer.pages) != 0:
            o_file = out_f + f"{j}.pdf"
            if j < 10:
                o_file = out_f + f"00{j}.pdf"
            elif j < 100:
                o_file = out_f + f"0{j}.pdf"
            with open(o_file, "wb") as fp:
                writer.write(fp)

        output_txt = f"Rozdzielono {x} stronny plik na {j} plików dwustronnych zapisanych w:\n{out_f}"
        # msg_val = str(output_txt)
        print(output_txt)

    def ile_stron(self, src_path, dst_path):

        # dst_path = "Z:\\roboty\\PODZIAŁY\\Trakt Katowice\\s17\\Zawiadomienia\\EPO\\lista2.txt"
        dst_path = str(dst_path).replace(".pdf", ".txt")

        if type(src_path) is not Path:
            src_path = Path(src_path)
        if src_path.suffix == ".pdf":
            with open(src_path, "rb") as file:
                src_pdf = pdf.PdfReader(file)
                pages = len(src_pdf.pages)

                with open(dst_path, "a", encoding="utf-8") as file2:
                    file2.write(f"{src_path}\t{pages}\n")

    def merge_kw(self, src_path, dst_path):

        # TODO: TRZEBA wybrać scieżkę

        # dst_path = "Z:\\roboty\\PODZIAŁY\\Trakt Katowice\\s17\\! Dla zamawiającego\\Załącznik 2\\Ksiegi wieczyste\\"

        if dst_path == "404":
            return 404

        if type(src_path) is not Path:
            src_path = Path(src_path)
        if src_path.suffix == ".pdf":
            name = src_path.name
            pdf_name = f"{name[0:15]}.pdf"
            kw_name = name[0:15]
            wr = pdf.PdfWriter()
            new_pdf = pdf.PdfReader(src_path)

            n_dst_path = f"{dst_path}{pdf_name}"
            if os.path.exists(n_dst_path):
                src_pdf = pdf.PdfReader(n_dst_path)
                wr.append_pages_from_reader(src_pdf)
                wr.append_pages_from_reader(new_pdf)
            else:
                wr.append_pages_from_reader(new_pdf)

            with open(n_dst_path, "wb") as w_file:
                wr.write(w_file)

        return 0

    def badanie_kw(self):

        # TODO: TRZEBA wybrać scieżkę

        bad_path = ""
        kw_path = ""
        dst_path = ""

        return 0

    def first_2_pages(self, src_files, dst_path):

        out_pdf = pdf.PdfWriter()
        print("Start <<<")
        # parm a określa wybranie wszystkich pdf
        # parm s określa omijanie skan plików
        lst_parm = ["a", "all", "s", "skan"]
        i = 0

        for file in src_files:
            if type(file) is not Path:
                file = Path(file)
            if file.suffix == ".pdf":
                out_print = f"{file}\n"
                print(out_print)
                src_pdf = pdf.PdfReader(file)
                for k in range(0, 2):
                    out_pdf.add_page(src_pdf.pages[k])
                i += 1

        with open(dst_path, "wb") as file:
            out_pdf.write(file)

        out_print = f"Scalono {i} plików\n"

    def last_2_pages(self, src_files, dst_path):

        out_pdf = pdf.PdfWriter()
        print("Start <<<")
        # parm a określa wybranie wszystkich pdf
        # parm s określa omijanie skan plików
        lst_parm = ["a", "all", "s", "skan"]
        i = 0

        for file in src_files:
            if type(file) is not Path:
                file = Path(file)
            if file.suffix == ".pdf":
                out_print = f"{file}\n"
                print(out_print)
                src_pdf = pdf.PdfReader(file)

                for k in range(len(src_pdf.pages)-2, len(src_pdf.pages)):
                    out_pdf.add_page(src_pdf.pages[k])
                i += 1

        with open(dst_path, "wb") as file:
            out_pdf.write(file)

        out_print = f"Scalono {i} plików\n"

    def delete_all_pdf(self, src_files):

        for file in src_files:
            file = str(file)
            if file.endswith(".pdf"):
                try:
                    os.remove(file)
                    print(file)
                except:
                    print(file, "--passed")

    def add_page_number(self, src_files, typ):

        # TODO
        # wybór pozycji
        # inne rodzaje szablonu numeracji
        # wybór czcionki i rozmiary

        x = [add_numeration(str(file), typ) for file in src_files if str(file).endswith(".pdf")]

    def merge_img_to_pdf(self, src_files, dst_path):
        img_to_pdf(src_files, dst_path)


def main():
    gui = PdfGui()


def img_to_pdf(image_list, out_file):

    fpdf = FPDF()
    x, y = 0, 0
    w, h = 210, 297

    # imagelist is the list with all image filenames
    for image in image_list:

        img = Image.open(image)
        w, h = img.width, img.height

        orientation = "P" if (w < h) else "L"
        f1 = w if (w < h) else h
        f2 = h if (w < h) else w

        fpdf.add_page(orientation=orientation, format=(f1, f2), same=False)
        fpdf.image(image, x, y, w, h)

    fpdf.output(out_file, "F")


def add_numeration(input_file, typ):

    # Grab the file you want to add pages to
    inputfile = pdf.PdfReader(input_file)
    output_file = input_file

    # Create a temporary numbering PDF using the overloaded FPDF class, passing the number of pages
    # from your original file
    temp_num_file = NumberPDF(len(inputfile.pages), typ)

    for i in range(0, len(inputfile.pages)):
        temp_num_file.add_page()

    # Save the temporary numbering PDF
    temp_num_file.output(output_file)

    # Create a new PDFFileReader for the temporary numbering PDF
    merge_file = pdf.PdfReader(output_file)
    merge_writer = pdf.PdfWriter()

    for x, page in enumerate(merge_file.pages):
        # Grab the corresponding page from the inputFile
        input_page = inputfile.pages[x]
        # Merge the inputFile page and the temporary numbering page
        input_page.merge_page(page)
        # Add the merged page to the final output writer
        merge_writer.add_page(input_page)

    with open(output_file, 'wb') as fh:
        merge_writer.write(fh)


def finder(start, suffix: str = ".pdf", sort: bool = True):


    tic = time.perf_counter()

    start = str(start)

    start = start.replace("\\", "/")
    num_explored = 0

    start = Node(start)
    frontier = StackFrontier()
    frontier.add(start)
    explored = set()

    paths = set()

    while True:

        if frontier.empty():
            break

        node = frontier.remove()
        num_explored += 1

        # Jeżeli rozszerzenie jest poprawne do dodaj do selekcji
        if node.state.endswith(suffix):
            print(node.state)
            paths.add(node.state)

        # oznacz jako przeszukane
        explored.add(node.state)

        # Dodaj foldery z wybranego folderu do wyszukiwania
        if not os.path.isdir(node.state):
            continue
        try:
            for action in os.listdir(node.state):
                if not frontier.contains_state(action) and action not in explored:
                    action = f"{node.state}/{action}"
                    child = Node(action)
                    frontier.add(child)
        except OSError:
            print("Can't open this folder")

    toc = time.perf_counter()

    if sort:
        paths = sorted(paths)

    print(f"Przeszukane ścieżki: {num_explored} ")

    return paths


if __name__ == "__main__":
    main()
