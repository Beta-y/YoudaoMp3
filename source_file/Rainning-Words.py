﻿# pyinstaller -F -w -i logo.ico Rainning-Words.py
'''
程序思想：
有两个本地语音库，美音库Speech_US，英音库Speech_US
调用有道api，获取语音MP3，存入对应的语音库中
'''

import os
import urllib.request
import time
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

import re
from threading import Timer

class Youdao:
    def __init__(self):
        '''
        调用youdao API
        type = 2：美音
        type = 1：英音

        判断当前目录下是否存在两个语音库的目录
        如果不存在，创建
        '''
        self._num = 0
        self._type = 1  # 发音方式
        self._word = "word"  # 单词
        self._dirRoot = r"./"
        self._dirSpeech = r"./"

    def setSavePath(self,root_path = r"./"):
         # 文件根目录
        # if 1 == self._type:
        #         child_dir = 'Speech_EN'
        # else:
        #     child_dir = 'Speech_US'
        # self._dirSpeech = os.path.join(root_path, child_dir)  
        self._dirSpeech = root_path
        if not os.path.exists(self._dirSpeech):
            # 不存在，就创建
            os.makedirs(self._dirSpeech)

    def setAccent(self, type=1):
        '''
        type = 2：美音
        type = 1：英音
        '''
        self._type = type  # 发音方式

    def down(self, word,num):
        '''
        下载单词的MP3
        判断语音库中是否有对应的MP3
        如果没有就下载
        '''
        self._num = num
        word = word.lower()  # 小写
        tmp = self._getWordMp3FilePath(word)
        if tmp is None:
            self._getURL()  # 组合URL
            # 调用下载程序，下载到目标文件夹
            # print('不存在 %s.mp3 文件\n将URL:\n' % word, self._url, '\n下载到:\n', self._filePath)
            # 下载到目标地址
            urllib.request.urlretrieve(self._url, filename=self._filePath)
            # print('%s.mp3 下载完成' % self._word)
        else:
            pass
            # print('已经存在 %s.mp3, 不需要下载' % self._word)
        # 返回声音文件路径
        return self._filePath

    def _getURL(self):
        '''
        私有函数，生成发音的目标URL
        http://dict.youdao.com/dictvoice?&audio=单词&type=2"
        '''
        word_tmp = self._word.split()
        self._url = r'http://dict.youdao.com/dictvoice?' + r'&audio='
        # 短语
        if len(word_tmp) > 1:
            for i in range(len(word_tmp)-1):
                self._url += word_tmp[i] + '%20'
            self._url += word_tmp[i + 1]
        # 单词
        else:
            self._url += self._word
        self._url += '&type=' + str(self._type)

    def _getWordMp3FilePath(self, word):
        '''
        获取单词的MP3本地文件路径
        如果有MP3文件，返回路径(绝对路径)
        如果没有，返回None
        '''
        # 去除非法字符
        rstr = r"[\=\(\)\,\/\\\:\*\?\"\<\>\|\']"  # '= ( ) ， / \ : * ? " < > | 
        word = re.sub(rstr, "", word)  # 替换为空
        # 小写
        word = word.lower()  
        self._word = word
        self._fileName = str(self._num) + '.' +self._word + '.mp3'
        self._filePath = os.path.join(self._dirSpeech, self._fileName)

        # 判断是否存在这个MP3文件
        if os.path.exists(self._filePath):
            # 存在这个mp3
            return self._filePath
        else:
            # 不存在这个MP3，返回none
            return None
    
class Mainform(Youdao):
    def __init__(self,window):
        self.window = window
        self.frame = tk.Frame(self.window)
        self.read_path = ""
        self.save_path = os.getcwd() 
        self.filename = ""
        self.buttons ={
            "Read_Path":tk.Button(self.frame,text= "选择",width = 10,command = lambda: self.select_file()),
            "Save_Path":tk.Button(self.frame,text= "另存到",width = 10,command = lambda: self.save_file()),
            "Download":tk.Button(self.frame,text= "下载",width = 10,command = lambda: self.download(),state = 'disabled'),
            "Clear":tk.Button(self.frame,text= "清空",width = 10,command = lambda: self.textbox_clear(),state = 'disabled')
        }
        self.entries ={
            "Read_Path":tk.Entry(self.frame,width = 50),
            "Save_Path":tk.Entry(self.frame,width = 50)
        }   
        self.accent_state = tk.IntVar()
        self.accent_state.set(1)
        self.radios ={
            "England": tk.Radiobutton(self.frame, text="英音",variable = self.accent_state,value = 1),
            "America":tk.Radiobutton(self.frame, text="美音",variable = self.accent_state,value = 2)
        } 
        self.label = tk.Label(self.window,text = "等待输入/选择单词文件...",padx = 10)
        
        self.textbox = tk.Text(self.window,height = 5,width = 82)
        self.textbox.insert("end","可输入想查询的单词/短语, 每行一个...\n")
        self.textbox.bind("<ButtonRelease-1>",self.textbox_enter())

        self.entry_filled()
        self.entries["Read_Path"].grid(row = 0,column = 0)
        self.buttons["Read_Path"].grid(row = 0,column = 1)
        self.entries["Save_Path"].grid(row = 1,column = 0)
        self.buttons["Save_Path"].grid(row = 1,column = 1)
        self.radios["England"].grid(row = 0,column = 2)
        self.radios["America"].grid(row = 1,column = 2)
          
        self.frame.pack()
        self.buttons["Download"].grid(row = 0,column = 3)
        self.textbox.pack()  
        self.buttons["Clear"].grid(row = 1,column = 3)
        self.label.pack(side = 'left')  

    # 填充路径显示
    def entry_filled(self):
        self.entries["Read_Path"].delete(0,'end')
        self.entries["Save_Path"].delete(0,'end')
        self.entries["Read_Path"].insert(0,self.read_path)
        self.entries["Save_Path"].insert(0,self.save_path)

    # 选择文件
    def select_file(self):
        tmp_win = tk.Tk()
        tmp_win.withdraw()
        self.read_path = filedialog.askopenfilename(title= "请选择单词txt文件",initialdir = "./",filetypes = [('Text files','.txt')])
        (dirpath, filename) = os.path.split(self.read_path)
        (self.filename, extension) = os.path.splitext(filename)
        tmp_win.destroy()      
        # 使能按钮 
        self.buttons["Save_Path"].config(state = 'normal')
        self.buttons["Download"].config(state = 'normal')
        # 更新存储路径
        self.save_path  = os.path.join(os.getcwd(),self.filename)
        self.entry_filled()

    # 选择保存路径
    def save_file(self):
        tmp_win = tk.Tk()
        tmp_win.withdraw()
        self.save_path  = os.path.join(filedialog.askdirectory(title= "请选择音频保存路径",initialdir = "./"),self.filename)
        tmp_win.destroy()
        self.entry_filled()

    # 定时下载
    def timer_callback(self):
        self.timer.cancel()
        if(self.line == len(self.all_lines)):
            self.buttons["Download"].config(state = 'normal',text="下载")
            self.label.config(text = "全部下载完成!  共计 %d 个"%self.wordsum)
            return 
        line = self.all_lines[self.line]
        if(line.strip()):
            word = line.strip()
            self.label.config(text = str(self.wordsum) +". "+ word + " 下载完成")
            self.youdao.down(word,self.wordsum)
            self.wordsum += 1
        self.line += 1
        self.timer = Timer(0.001, self.timer_callback)
        self.timer.start()
    
    # 带参数的bind绑定中转站
    def textbox_enter(self):
        return lambda Event: self.textbox_enter_true()

    # 点击输入栏事件 回调函数
    def textbox_enter_true(self):
        if(not self.get_textbox_content()):
            self.textbox.delete('0.0','end')
        self.buttons["Download"].config(state = 'normal')
        self.buttons["Clear"].config(state = 'normal')
        self.label.config(text = "正在输入单词,如放弃请点击清空按钮...")

    # 清空输入栏
    def textbox_clear(self):
        self.buttons["Download"].config(state = 'normal')
        self.buttons["Clear"].config(state = 'disabled')
        self.label.config(text = "等待输入/选择单词文件...")
        self.textbox.delete('0.0','end')
        self.textbox.insert("end","可输入想查询的单词/短语, 每行一个...\n")

    def get_textbox_content(self):
        # 正则表达式判断中文
        Chinese_check = re.compile(u'[\u4e00-\u9fa5]+')
        content = self.textbox.get(0.0,'end').split('\n')
        match = Chinese_check.search(content[0])
        # 判断输入区当前是提示消息还是输入的单词
        if match:
            return None
        else:
            return content
    
    # 开始下载
    def download(self):
        try: 
            self.youdao = Youdao()
            self.youdao.setAccent(type = self.accent_state.get())#1设置为英音 2设置为美音
            self.youdao.setSavePath(root_path= self.save_path)
            textbox_content = self.get_textbox_content()
            # 如果输入框有单词则优先下载输入框，否则下载所选文件
            if(textbox_content):
                self.all_lines = textbox_content
            else:
                file_obj = open(self.read_path)
                self.all_lines = file_obj.readlines()
                file_obj.close()
            self.line = 0 # 标记文件读取的行数
            self.wordsum = 0 # 标记总的下载数量
            self.buttons["Download"].config(state = 'disabled',text ="正在下载...")
            self.timer = Timer(0.01, self.timer_callback)
            self.timer.start()
        except Exception:
            messagebox.showerror(title = "错误提示",message = str(Exception)+"\n请检查待下载文件及路径是否正确")
       
if __name__ == "__main__":
    window = tk.Tk()
    window.title("Rainning-Words")
    mainform = Mainform(window)
    window.mainloop()
    