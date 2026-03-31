# -*- coding: utf-8 -*-
"""
安全员C证题库 - 安卓版 v1.0
使用 Kivy 框架开发的移动端应用
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.togglebutton import ToggleButton
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle
from kivy.properties import StringProperty, ListProperty, NumericProperty

import json
import random
import re
import os

# 数据文件路径
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
QUESTIONS_FILE = os.path.join(DATA_DIR, "questions.json")
PROGRESS_FILE = os.path.join(DATA_DIR, "progress.json")


def get_answer(q):
    """从题目中提取正确答案"""
    opts = q.get('options', [])
    ans_field = q.get('answer') or ''
    
    for opt in opts:
        m = re.search(r'正确答案[：:]?([A-Z]+)', str(opt))
        if m:
            return list(m.group(1))
    
    letters = re.findall(r'[A-Z]', ans_field)
    return [c for c in letters if c.isalpha()]


def classify_questions(qs):
    single, multi, judge = [], [], []
    for i, q in enumerate(qs):
        answer_letters = get_answer(q)
        opts = q.get("options", [])
        
        is_judge = any(x in str(opts) for x in ['正确', '错误', '对', '错'])
        if is_judge or not answer_letters:
            judge.append((i, q, answer_letters))
        elif len(answer_letters) >= 2:
            multi.append((i, q, answer_letters))
        else:
            single.append((i, q, answer_letters))
    return single, multi, judge


class QuizScreen(BoxLayout):
    """主答题界面"""
    
    current_answer = ListProperty([])
    question_text = StringProperty("")
    result_text = StringProperty("")
    result_color = ListProperty([0, 0, 0, 1])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(10)
        self.spacing = dp(8)
        
        # 数据加载
        self.all_questions = self.load_questions()
        self.single_qs, self.multi_qs, self.judge_qs = classify_questions(self.all_questions)
        self.progress = self.load_progress()
        
        # 当前状态
        self.current_qs = []
        self.current_idx = 0
        self.current_q = None
        self.current_idx_in_all = 0
        self.current_type = "all"
        self.opt_buttons = []
        
        # 构建UI
        self.build_ui()
        self.show_type("all")
    
    def load_questions(self):
        try:
            with open(QUESTIONS_FILE, encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载题库失败: {e}")
            return []
    
    def load_progress(self):
        try:
            with open(PROGRESS_FILE, encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"total": 0, "correct": 0, "wrong": [], "wrong_details": {}}
    
    def save_progress(self):
        try:
            with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.progress, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def build_ui(self):
        """构建用户界面"""
        # 顶部统计栏
        self.stats_bar = BoxLayout(size_hint_y=None, height=dp(40))
        with self.stats_bar.canvas.before:
            Color(0.08, 0.40, 0.75, 1)  # 蓝色背景
            self.stats_rect = RoundedRectangle(pos=self.stats_bar.pos, size=self.stats_bar.size)
        self.stats_bar.bind(pos=self.update_stats_rect, size=self.update_stats_rect)
        
        self.stats_label = Label(
            text="已答: 0 | 正确: 0 | 错题: 0",
            color=(1, 1, 1, 1),
            font_size=dp(14),
            bold=True
        )
        self.stats_bar.add_widget(self.stats_label)
        self.add_widget(self.stats_bar)
        
        # 题型切换按钮
        type_bar = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(5))
        types = [
            ("全部", "all", (0.36, 0.42, 0.75)),
            ("单选", "single", (0.18, 0.49, 0.20)),
            ("多选", "multi", (0.90, 0.32, 0.00)),
            ("判断", "judge", (0.42, 0.11, 0.60)),
            ("错题", "wrong", (0.72, 0.09, 0.11)),
        ]
        self.type_buttons = {}
        for text, val, color in types:
            btn = Button(
                text=text,
                font_size=dp(14),
                bold=True,
                background_normal='',
                background_color=(*color, 1),
                color=(1, 1, 1, 1)
            )
            btn.bind(on_press=lambda x, v=val: self.show_type(v))
            type_bar.add_widget(btn)
            self.type_buttons[val] = btn
        self.add_widget(type_bar)
        
        # 题目区域
        self.question_label = Label(
            text="",
            markup=True,
            size_hint_y=None,
            valign='top',
            halign='left',
            text_size=(Window.width - dp(20), None),
            font_size=dp(16),
            padding=(dp(10), dp(10))
        )
        self.question_label.bind(texture_size=self.question_label.setter('size'))
        
        scroll = ScrollView(size_hint=(1, 0.35))
        scroll.add_widget(self.question_label)
        self.add_widget(scroll)
        
        # 选项区域
        self.options_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(8)
        )
        self.options_layout.bind(minimum_height=self.options_layout.setter('height'))
        
        for i in range(6):
            btn = ToggleButton(
                text="",
                font_size=dp(15),
                size_hint_y=None,
                height=dp(55),
                markup=True,
                halign='left',
                valign='middle',
                text_size=(None, dp(55)),
                padding=(dp(15), 0)
            )
            btn.bind(on_press=lambda x, idx=i: self.click_opt(idx))
            self.options_layout.add_widget(btn)
            self.opt_buttons.append(btn)
        
        options_scroll = ScrollView(size_hint=(1, 0.40))
        options_scroll.add_widget(self.options_layout)
        self.add_widget(options_scroll)
        
        # 答案输入区
        ans_layout = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))
        
        self.ans_input = TextInput(
            hint_text="输入答案（如：A或ABC）",
            font_size=dp(22),
            multiline=False,
            size_hint_x=0.5,
            halign='center',
            padding=(dp(10), dp(15), dp(10), dp(10))
        )
        ans_layout.add_widget(self.ans_input)
        
        submit_btn = Button(
            text="提交",
            font_size=dp(18),
            bold=True,
            size_hint_x=0.25,
            background_normal='',
            background_color=(0.30, 0.69, 0.31, 1),
            color=(1, 1, 1, 1)
        )
        submit_btn.bind(on_press=self.submit)
        ans_layout.add_widget(submit_btn)
        
        show_btn = Button(
            text="答案",
            font_size=dp(18),
            size_hint_x=0.25,
            background_normal='',
            background_color=(0.61, 0.15, 0.69, 1),
            color=(1, 1, 1, 1)
        )
        show_btn.bind(on_press=self.show_ans)
        ans_layout.add_widget(show_btn)
        
        self.add_widget(ans_layout)
        
        # 结果显示
        self.result_label = Label(
            text="",
            markup=True,
            size_hint_y=None,
            height=dp(50),
            font_size=dp(16),
            bold=True
        )
        self.add_widget(self.result_label)
        
        # 导航按钮
        nav_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(5))
        
        prev_btn = Button(
            text="◀ 上题",
            font_size=dp(16),
            background_normal='',
            background_color=(0.47, 0.56, 0.61, 1),
            color=(1, 1, 1, 1)
        )
        prev_btn.bind(on_press=self.prev)
        nav_layout.add_widget(prev_btn)
        
        self.pos_label = Label(
            text="第 0 / 0 题",
            font_size=dp(16),
            bold=True,
            size_hint_x=0.4
        )
        nav_layout.add_widget(self.pos_label)
        
        next_btn = Button(
            text="下题 ▶",
            font_size=dp(16),
            background_normal='',
            background_color=(0.47, 0.56, 0.61, 1),
            color=(1, 1, 1, 1)
        )
        next_btn.bind(on_press=self.next)
        nav_layout.add_widget(next_btn)
        
        self.add_widget(nav_layout)
    
    def update_stats_rect(self, instance, value):
        self.stats_rect.pos = instance.pos
        self.stats_rect.size = instance.size
    
    def update_stats(self):
        t = self.progress.get("total", 0)
        c = self.progress.get("correct", 0)
        w = len(self.progress.get("wrong", []))
        rate = c / t * 100 if t > 0 else 0
        self.stats_label.text = f"已答: {t} | 正确: {c} | 错题: {w} | 正确率: {rate:.1f}%"
    
    def update_pos(self):
        if self.current_qs:
            self.pos_label.text = f"第 {self.current_idx+1} / {len(self.current_qs)} 题"
        else:
            self.pos_label.text = "第 0 / 0 题"
    
    def show_type(self, t):
        """切换题型"""
        self.current_type = t
        
        # 更新按钮样式
        colors = {
            "all": (0.36, 0.42, 0.75),
            "single": (0.18, 0.49, 0.20),
            "multi": (0.90, 0.32, 0.00),
            "judge": (0.42, 0.11, 0.60),
            "wrong": (0.72, 0.09, 0.11),
        }
        for key, btn in self.type_buttons.items():
            if key == t:
                btn.background_color = (1, 0.84, 0, 1)  # 金色高亮
            else:
                btn.background_color = (*colors[key], 1)
        
        # 设置题目列表
        if t == "all":
            self.current_qs = list(range(len(self.all_questions)))
        elif t == "single":
            self.current_qs = [q[0] for q in self.single_qs]
        elif t == "multi":
            self.current_qs = [q[0] for q in self.multi_qs]
        elif t == "judge":
            self.current_qs = [q[0] for q in self.judge_qs]
        elif t == "wrong":
            wrong_ids = self.progress.get("wrong", [])
            if not wrong_ids:
                self.show_popup("提示", "暂无错题记录！\n先去做题吧～")
                self.show_type("all")
                return
            self.current_qs = wrong_ids.copy()
        
        random.shuffle(self.current_qs)
        self.current_idx = 0
        self.show_current()
    
    def show_current(self):
        """显示当前题目"""
        if not self.current_qs:
            return
        
        idx = self.current_qs[self.current_idx]
        q = self.all_questions[idx]
        
        ans_letters = get_answer(q)
        self.current_q = q
        self.current_answer = ans_letters
        self.current_idx_in_all = idx
        
        # 判断题型
        n = len(ans_letters)
        if n >= 2:
            qtype, note = "[b]【多选题】[/b]", "（多选，如 ABC）"
        elif n == 1:
            qtype, note = "[b]【单选题】[/b]", "（单选一个字母）"
        else:
            qtype, note = "[b]【判断题】[/b]", "（选 A 或 B）"
        
        self.question_label.text = f"{qtype}  {note}\n\n{q.get('question', '')}"
        
        # 清理选项
        clean_opts = [re.sub(r'\s*正确答案[：:]?[A-Z]+\s*$', '', o).strip()
                      for o in q.get("options", [])]
        
        colors = [
            (0.89, 0.95, 0.99),  # 浅蓝
            (0.91, 0.96, 0.91),  # 浅绿
            (1.0, 0.95, 0.88),   # 浅橙
            (0.95, 0.90, 0.96),  # 浅紫
            (0.88, 0.97, 0.98),  # 浅青
            (0.98, 0.91, 0.91),  # 浅红
        ]
        
        for i, btn in enumerate(self.opt_buttons):
            if i < len(clean_opts) and clean_opts[i]:
                btn.text = clean_opts[i]
                btn.background_normal = ''
                btn.background_color = (*colors[i], 1)
                btn.color = (0.13, 0.13, 0.13, 1)
                btn.state = 'normal'
                btn.disabled = False
            else:
                btn.text = ""
                btn.disabled = True
        
        self.ans_input.text = ""
        self.result_label.text = ""
        self.update_pos()
    
    def click_opt(self, idx):
        """点击选项"""
        opts = self.current_q.get("options", [])
        clean_opts = [re.sub(r'\s*正确答案[：:]?[A-Z]+\s*$', '', o).strip() for o in opts]
        
        if idx < len(clean_opts) and clean_opts[idx]:
            letter = clean_opts[idx][0]
            current = self.ans_input.text.upper()
            
            if letter in current:
                self.ans_input.text = current.replace(letter, "")
            else:
                self.ans_input.text = current + letter
            
            # 更新按钮高亮
            selected = set(self.ans_input.text.upper())
            colors = [
                (0.89, 0.95, 0.99),
                (0.91, 0.96, 0.91),
                (1.0, 0.95, 0.88),
                (0.95, 0.90, 0.96),
                (0.88, 0.97, 0.98),
                (0.98, 0.91, 0.91),
            ]
            
            for i, btn in enumerate(self.opt_buttons):
                if i < len(clean_opts) and clean_opts[i]:
                    l = clean_opts[i][0]
                    if l in selected:
                        btn.background_color = (1, 0.60, 0, 1)  # 橙色高亮
                        btn.color = (1, 1, 1, 1)
                    else:
                        btn.background_color = (*colors[i], 1)
                        btn.color = (0.13, 0.13, 0.13, 1)
                        btn.state = 'normal'
    
    def submit(self, instance):
        """提交答案"""
        if not self.current_q:
            return
        
        user = self.ans_input.text.strip().upper()
        if not user:
            self.show_popup("提示", "请输入答案！")
            return
        
        correct = sorted(self.current_answer)
        user_list = sorted(c for c in user if c.isalpha())
        is_correct = user_list == correct
        
        self.progress["total"] = self.progress.get("total", 0) + 1
        
        if is_correct:
            self.progress["correct"] = self.progress.get("correct", 0) + 1
            self.result_label.text = f"[color=2E7D32]✓ 正确！答案：{''.join(correct)}[/color]"
            self.highlight_opts(correct, [])
            
            wrong = self.progress.get("wrong", [])
            if self.current_idx_in_all in wrong:
                wrong.remove(self.current_idx_in_all)
                self.progress["wrong"] = wrong
                wd = self.progress.get("wrong_details", {})
                wd.pop(str(self.current_idx_in_all), None)
                self.progress["wrong_details"] = wd
        else:
            wrong = self.progress.get("wrong", [])
            if self.current_idx_in_all not in wrong:
                wrong.append(self.current_idx_in_all)
                self.progress["wrong"] = wrong
            
            wd = self.progress.get("wrong_details", {})
            wd[str(self.current_idx_in_all)] = {
                "user_ans": ''.join(user_list),
                "correct": ''.join(correct),
                "question": self.current_q.get("question", "")[:80]
            }
            self.progress["wrong_details"] = wd
            
            self.result_label.text = f"[color=B71C1C]✗ 错误！正确：{''.join(correct)} 你选：{''.join(user_list)}[/color]"
            self.highlight_opts(correct, user_list)
        
        self.save_progress()
        self.update_stats()
    
    def highlight_opts(self, correct, user):
        """高亮选项"""
        opts = self.current_q.get("options", [])
        clean_opts = [re.sub(r'\s*正确答案[：:]?[A-Z]+\s*$', '', o).strip() for o in opts]
        
        for i, btn in enumerate(self.opt_buttons):
            if i >= len(clean_opts) or not clean_opts[i]:
                continue
            
            letter = clean_opts[i][0]
            if letter in correct:
                btn.background_color = (0.30, 0.69, 0.31, 1)  # 绿色
                btn.color = (1, 1, 1, 1)
            elif letter in user:
                btn.background_color = (0.96, 0.26, 0.21, 1)  # 红色
                btn.color = (1, 1, 1, 1)
    
    def show_ans(self, instance):
        """显示答案"""
        if self.current_answer:
            self.result_label.text = f"[color=1565C0]正确答案：{''.join(self.current_answer)}[/color]"
            self.highlight_opts(self.current_answer, [])
    
    def prev(self, instance):
        """上一题"""
        if self.current_idx > 0:
            self.current_idx -= 1
            self.show_current()
    
    def next(self, instance):
        """下一题"""
        if self.current_idx < len(self.current_qs) - 1:
            self.current_idx += 1
            self.show_current()
        else:
            self.show_popup("提示", "已经是最后一题！")
    
    def show_popup(self, title, message):
        """显示弹窗"""
        popup = Popup(
            title=title,
            content=Label(text=message, font_size=dp(16)),
            size_hint=(0.8, 0.3)
        )
        popup.open()


class SafetyQuizApp(App):
    """主应用"""
    
    def build(self):
        self.title = "安全员C证题库"
        Window.clearcolor = (0.96, 0.97, 0.98, 1)  # 浅灰背景
        return QuizScreen()


if __name__ == '__main__':
    SafetyQuizApp().run()
