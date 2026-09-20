# -*- coding: utf-8 -*-
"""CathayIndex · 本地文件库索引工具（图形界面）

把一个或多个文件夹（含子文件夹、孙文件夹……）里的文件目录做成
SQLite 库「本地文件库」，建好的库可以直接被 CathayFinder 当渠道检索。
界面：拖入/选择文件夹 → 开始建库 → 进度与日志 → 顺手搜一下验证。
"""
import os
import queue
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except Exception:
    HAS_DND = False

import indexer as IDX

APP_TITLE = "%s  %s" % (IDX.APP_TITLE, IDX.APP_VERSION)
BG = "#f7f6f2"
ACCENT = "#2f4858"
GOLD = "#c8a15a"


def tk_splitlist(root, data):
    """解析 tkdnd 拖放串（支持的写法：{带 空格 路径} / 普通路径）"""
    if not data:
        return []
    if isinstance(data, (list, tuple)):
        return [str(x) for x in data]
    out, cur, inbrace = [], '', False
    for ch in str(data):
        if ch == '{':
            inbrace = True
            cur = ''
        elif ch == '}':
            inbrace = False
            if cur:
                out.append(cur)
            cur = ''
        elif ch == ' ' and not inbrace:
            if cur:
                out.append(cur)
            cur = ''
        else:
            cur += ch
    if cur:
        out.append(cur)
    return out


def bind_drop(widget, handler):
    if not HAS_DND:
        return
    try:
        widget.drop_target_register(DND_FILES)
        widget.dnd_bind('<<Drop>>', handler)
    except Exception:
        pass


class App(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=10)
        self.pack(fill='both', expand=True)
        self.roots = []
        self.q = queue.Queue()
        self.working = False
        self._build_ui()
        self.after(120, self._pump)

    # ── 界面 ──────────────────────────────────────────────
    def _build_ui(self):
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass
        style.configure('Big.TButton', font=('Microsoft YaHei UI', 10, 'bold'))
        style.configure('TLabel', background=BG)
        self.master.configure(bg=BG)
        self.configure(style='TFrame')

        tip = ttk.Label(
            self,
            text=('把文件夹拖进下面的框（或点「添加文件夹」）。子文件夹、孙文件夹里的文件\n'
                  '都会收进库「%s」；只要在上面指一下 CathayFinder 在哪，库文件就会自动\n'
                  '写进它的库目录，建完就能在 CathayFinder 里当渠道搜索。' % IDX.LIB_LABEL),
            justify='left', foreground=ACCENT)
        tip.pack(anchor='w', pady=(0, 8))

        # 根文件夹
        box = ttk.LabelFrame(self, text='要建库的文件夹', padding=6)
        box.pack(fill='both', expand=True)
        self.lb = tk.Listbox(box, height=6, activestyle='none',
                             selectmode='extended', font=('Consolas', 10))
        self.lb.pack(side='left', fill='both', expand=True)
        sb = ttk.Scrollbar(box, orient='vertical', command=self.lb.yview)
        sb.pack(side='left', fill='y')
        self.lb.config(yscrollcommand=sb.set)
        btns = ttk.Frame(box)
        btns.pack(side='left', fill='y', padx=(6, 0))
        ttk.Button(btns, text='添加文件夹', command=self.add_folder).pack(fill='x', pady=2)
        ttk.Button(btns, text='移除选中', command=self.remove_sel).pack(fill='x', pady=2)
        ttk.Button(btns, text='清空', command=self.clear_all).pack(fill='x', pady=2)
        bind_drop(self.lb, self._on_drop)

        # 参数
        opt = ttk.LabelFrame(self, text='参数', padding=6)
        opt.pack(fill='x', pady=6)
        r1 = ttk.Frame(opt)
        r1.pack(fill='x')
        ttk.Label(r1, text='CathayFinder 在哪：').pack(side='left')
        self.v_cf = tk.StringVar(value=IDX.find_cathayfinder_dir() or '')
        self.v_cf.trace_add('write', lambda *a: self._refresh_db_label())
        ttk.Entry(r1, textvariable=self.v_cf).pack(side='left', fill='x', expand=True)
        ttk.Button(r1, text='浏览…', width=8,
                   command=self.pick_cf_dir).pack(side='left', padx=4)
        ttk.Button(r1, text='自动', width=6,
                   command=self.auto_cf_dir).pack(side='left')
        r1b = ttk.Frame(opt)
        r1b.pack(fill='x', pady=(2, 0))
        ttk.Label(r1b, text='（指到 CathayFinder 的文件夹就行，不用管 data\\db）',
                  foreground='#6b7280').pack(side='left')
        self.lbl_db = ttk.Label(r1b, text='', foreground=ACCENT)
        self.lbl_db.pack(side='left', padx=(8, 0))
        self._refresh_db_label()

        r2 = ttk.Frame(opt)
        r2.pack(fill='x', pady=(6, 0))
        self.v_mode = tk.StringVar(value='full')
        ttk.Label(r2, text='方式：').pack(side='left')
        ttk.Radiobutton(r2, text='全量重建', value='full',
                        variable=self.v_mode).pack(side='left')
        ttk.Radiobutton(r2, text='增量更新（只加新增/变化的）', value='inc',
                        variable=self.v_mode).pack(side='left', padx=(6, 12))
        ttk.Label(r2, text='只收这些扩展名：').pack(side='left')
        self.v_ext = tk.StringVar(value='')
        ttk.Entry(r2, textvariable=self.v_ext, width=34).pack(side='left')
        ttk.Label(r2, text='（留空=全部文件，例：pdf,epub,azw3,djvu,txt）').pack(side='left')

        r3 = ttk.Frame(opt)
        r3.pack(fill='x', pady=(6, 0))
        self.v_hidden = tk.BooleanVar(value=True)
        self.v_clean = tk.BooleanVar(value=True)
        ttk.Checkbutton(r3, text='跳过隐藏文件夹与系统目录（$RECYCLE.BIN、System Volume Information 等）',
                        variable=self.v_hidden).pack(side='left')
        ttk.Checkbutton(r3, text='增量时清理已不存在的记录',
                        variable=self.v_clean).pack(side='left', padx=(12, 0))

        # 动作
        act = ttk.Frame(self)
        act.pack(fill='x')
        self.btn = ttk.Button(act, text='开始建库', style='Big.TButton',
                              command=self.start)
        self.btn.pack(side='left', pady=6)
        self.pb = ttk.Progressbar(act, mode='determinate', length=420)
        self.pb.pack(side='left', padx=10)
        self.lbl_stat = ttk.Label(act, text='就绪', foreground=ACCENT)
        self.lbl_stat.pack(side='left')

        # 日志
        logf = ttk.LabelFrame(self, text='日志', padding=4)
        logf.pack(fill='both', expand=True)
        self.txt = tk.Text(logf, height=7, wrap='none', font=('Consolas', 9),
                           bg='#ffffff')
        self.txt.pack(side='left', fill='both', expand=True)
        tsb = ttk.Scrollbar(logf, orient='vertical', command=self.txt.yview)
        tsb.pack(side='left', fill='y')
        self.txt.config(yscrollcommand=tsb.set)

        # 迷你检索
        sf = ttk.LabelFrame(self, text='建好之后，在这儿试搜一下（和 CathayFinder 同一套匹配）',
                            padding=4)
        sf.pack(fill='both', expand=True, pady=(6, 0))
        r = ttk.Frame(sf)
        r.pack(fill='x')
        self.v_kw = tk.StringVar()
        e = ttk.Entry(r, textvariable=self.v_kw)
        e.pack(side='left', fill='x', expand=True)
        e.bind('<Return>', lambda _e: self.do_search())
        ttk.Button(r, text='搜索', command=self.do_search).pack(side='left', padx=4)
        ttk.Button(r, text='打开所在文件夹', command=self.open_sel).pack(side='left')
        cols = ('name', 'info', 'path')
        self.tv = ttk.Treeview(sf, columns=cols, show='headings', height=6)
        self.tv.heading('name', text='文件名')
        self.tv.heading('info', text='大小 / 修改时间')
        self.tv.heading('path', text='路径')
        self.tv.column('name', width=300)
        self.tv.column('info', width=150)
        self.tv.column('path', width=520)
        self.tv.pack(fill='both', expand=True)
        self.tv.bind('<Double-1>', lambda _e: self.open_sel())

    # ── 文件夹管理 ─────────────────────────────────────────
    def add_folder(self):
        d = filedialog.askdirectory(title='选择要建库的文件夹')
        if d:
            self._add([d])

    def _add(self, paths):
        n = 0
        for p in paths:
            p = os.path.abspath(p)
            if os.path.isdir(p) and p not in self.roots:
                self.roots.append(p)
                self.lb.insert('end', p)
                n += 1
        if n:
            self.log('已添加 %d 个文件夹' % n)

    def _on_drop(self, event):
        self._add(tk_splitlist(self, event.data))

    def remove_sel(self):
        for i in sorted(self.lb.curselection(), reverse=True):
            self.lb.delete(i)
            del self.roots[i]

    def clear_all(self):
        self.lb.delete(0, 'end')
        self.roots = []

    def cf_dir(self):
        d = (self.v_cf.get() or '').strip().strip('"')
        return os.path.abspath(d) if d else ''

    def db_path(self):
        d = self.cf_dir()
        return IDX.cathayfinder_db_path(d) if d else IDX.default_db_path()

    def _refresh_db_label(self):
        try:
            self.lbl_db.config(text='→ 库文件：%s' % self.db_path())
        except Exception:
            pass

    def pick_cf_dir(self):
        d = filedialog.askdirectory(
            title='选择 CathayFinder 所在的文件夹（里面有 CathayFinder.exe / data\\db）')
        if d:
            self.v_cf.set(os.path.abspath(d))
            IDX.save_tool_settings({'cathayfinder_dir': os.path.abspath(d)})

    def auto_cf_dir(self):
        IDX.save_tool_settings({'cathayfinder_dir': ''})
        d = IDX.find_cathayfinder_dir()
        if d:
            self.v_cf.set(d)
            self.log('自动找到 CathayFinder：%s' % d)
        else:
            messagebox.showinfo('自动查找', '没找到 CathayFinder，请点「浏览…」手动指一下它的文件夹。')

    # ── 日志 / 事件泵 ──────────────────────────────────────
    def log(self, s):
        self.txt.insert('end', s + '\n')
        self.txt.see('end')

    def _pump(self):
        try:
            while True:
                kind, val = self.q.get_nowait()
                if kind == 'log':
                    self.log(val)
                elif kind == 'progress':
                    done, total = val
                    if total:
                        self.pb.config(maximum=total, value=done)
                    self.lbl_stat.config(text='已索引 %d / %d' % (done, total))
                elif kind == 'done':
                    self._finish(val)
                elif kind == 'fail':
                    self.working = False
                    self.btn.config(state='normal')
                    self.lbl_stat.config(text='出错')
                    self.log('出错：%s' % val)
                    messagebox.showerror('建库失败', str(val))
        except queue.Empty:
            pass
        self.after(120, self._pump)

    # ── 建库 ──────────────────────────────────────────────
    def read_opts(self):
        """在主线程里先读好界面控件（工作线程不碰 Tk）"""
        cf = self.cf_dir()
        return dict(
            roots=list(self.roots),
            out_db=self.db_path(),
            cathayfinder_dir=cf,
            mode=self.v_mode.get(),
            exts=[e.strip() for e in self.v_ext.get().replace('，', ',').split(',')
                  if e.strip()],
            skip_hidden=bool(self.v_hidden.get()),
            clean_deleted=bool(self.v_clean.get()),
        )

    def start(self):
        if self.working:
            return
        o = self.read_opts()
        if not o['roots']:
            messagebox.showinfo('建库', '先添加至少一个文件夹')
            return
        if not o['cathayfinder_dir'] or not os.path.isdir(o['cathayfinder_dir']):
            messagebox.showinfo('建库', '先指一下 CathayFinder 在哪（它的文件夹）。')
            return
        if not IDX.looks_like_cathayfinder(o['cathayfinder_dir']):
            if not messagebox.askyesno(
                    '确认位置',
                    '这个文件夹里没看到 CathayFinder.exe / data\\db：\n%s\n\n'
                    '确认就用它吗？（会在里面新建 data\\db\\）' % o['cathayfinder_dir']):
                return
        IDX.save_tool_settings({'cathayfinder_dir': o['cathayfinder_dir']})
        self.working = True
        self.btn.config(state='disabled')
        self.pb.config(value=0, maximum=1)
        self.lbl_stat.config(text='准备中…')
        self.log('—' * 60)
        threading.Thread(target=self._work, args=(o,), daemon=True).start()

    def _work(self, o):
        try:
            st = IDX.build(
                o['roots'], o['out_db'], exts=o['exts'] or None,
                skip_hidden=o['skip_hidden'], mode=o['mode'],
                clean_deleted=o['clean_deleted'],
                progress=lambda d, t, n: self.q.put(('progress', (d, t))),
                log=lambda s: self.q.put(('log', s)))
            self.q.put(('done', st))
        except Exception as e:
            self.q.put(('fail', e))

    def _finish(self, st):
        self.working = False
        self.btn.config(state='normal')
        self.pb.config(value=self.pb['maximum'])
        self.lbl_stat.config(text='完成：新增 %d / 共 %d' % (st['added'], st['total']))
        self.log('库文件：%s（%s）' % (st['db'], IDX.human(st['db_size'])))
        self.log('一共收录 %d 个文件（新增 %d，更新 %d，清理 %d）'
                 % (st['total'], st['added'], st['updated'], st['deleted']))
        if os.path.basename(os.path.dirname(os.path.abspath(st['db']))) == 'db':
            self.log('★ 库已放进 CathayFinder 的库目录，重启 CathayFinder 后即可在'
                     '「%s」渠道里搜索。' % IDX.LIB_LABEL)
        messagebox.showinfo('建库完成', '收录 %d 个文件\n库文件：%s' % (st['total'], st['db']))

    # ── 迷你检索 ──────────────────────────────────────────
    def do_search(self):
        kw = self.v_kw.get().strip()
        db = self.db_path()
        if not kw:
            return
        for i in self.tv.get_children():
            self.tv.delete(i)
        rows = IDX.search_db(db, kw, limit=200)
        for name, path, extra in rows:
            self.tv.insert('', 'end', values=(name, extra or '', path))
        self.log('搜索「%s」→ %d 条' % (kw, len(rows)))

    def open_sel(self):
        sel = self.tv.selection()
        if not sel:
            return
        path = self.tv.item(sel[0], 'values')[2]
        try:
            if os.path.isfile(path):
                os.system('explorer /select,"%s"' % path.replace('/', '\\'))
            elif os.path.isdir(path):
                os.startfile(path)
        except Exception as e:
            messagebox.showwarning('打开', str(e))


def _selftest_dir():
    """自检报告写到哪：打包后的 exe 放在 exe 旁边（否则写到临时目录里看不见）"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return HERE


def selftest():
    """引擎自检 + 界面构建自检，结果写 _selftest.txt"""
    lines = [IDX.selftest(), '', '--- gui ---', 'dnd=%s' % HAS_DND,
             'frozen=%s' % getattr(sys, 'frozen', False)]
    try:
        root = TkinterDnD.Tk() if HAS_DND else tk.Tk()
        root.withdraw()
        app = App(root)
        root.update()
        lines.append('CathayFinder 位置=%s' % (app.v_cf.get() or '（空）'))
        lines.append('库文件=%s' % app.db_path())
        lines.append('模式默认=%s；扩展名过滤=%r' % (app.v_mode.get(), app.v_ext.get()))
        lines.append('控件齐备=%s' % all([app.btn, app.pb, app.tv, app.lb, app.txt]))
        lines.append('列数=%d' % len(app.tv['columns']))
        lines.append('gui=OK')
        root.destroy()
    except Exception as e:
        import traceback
        lines.append('gui=FAIL %r' % (e,))
        lines.append(traceback.format_exc())
    txt = '\n'.join(lines)
    try:
        with open(os.path.join(_selftest_dir(), '_selftest.txt'), 'w', encoding='utf-8') as f:
            f.write(txt)
    except Exception:
        pass
    return txt


def main():
    if '--selftest' in sys.argv:
        print(selftest())
        return 0
    root = TkinterDnD.Tk() if HAS_DND else tk.Tk()
    root.title(APP_TITLE)
    try:
        root.iconbitmap(os.path.join(HERE, 'app.ico'))
    except Exception:
        pass
    try:
        root.call('tk', 'scaling', 1.15)
    except Exception:
        pass
    root.geometry('1180x860')
    root.configure(bg=BG)
    App(root)
    if not HAS_DND:
        root.after(200, lambda: None)
    root.mainloop()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
