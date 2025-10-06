#!/usr/bin/env python3
"""
Image Watermarker GUI Application
A user-friendly GUI application for adding watermarks to images.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import tkinter.font as tkFont
from tkinterdnd2 import DND_FILES, TkinterDnD
import os
import json
from PIL import Image, ImageTk, ImageDraw, ImageFont
import exifread
from datetime import datetime
import threading
from pathlib import Path

class WatermarkGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Watermarker v2.0")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # 应用状态
        self.images = []  # 导入的图片列表
        self.current_image_index = 0
        self.current_image = None
        self.preview_image = None
        
        # 水印设置
        self.watermark_settings = {
            'text': '',
            'font_size': 36,
            'font_family': 'Arial',
            'color': '#FFFFFF',
            'opacity': 100,
            'position': 'bottom_right',
            'x_offset': 10,
            'y_offset': 10,
            'rotation': 0,
            'bold': False,
            'italic': False,
            'shadow': False,
            'outline': False
        }
        
        # 导出设置
        self.export_settings = {
            'output_dir': '',
            'naming_option': 'suffix',  # 'original', 'prefix', 'suffix'
            'custom_prefix': 'wm_',
            'custom_suffix': '_watermarked',
            'output_format': 'JPEG',
            'jpeg_quality': 95,
            'resize_enabled': False,
            'resize_width': 0,
            'resize_height': 0,
            'resize_percent': 100
        }
        
        self.setup_ui()
        self.load_default_settings()
        
    def setup_ui(self):
        """设置用户界面"""
        # 创建主框架
        self.create_menu()
        self.create_main_layout()
        self.setup_drag_drop()
        
    def setup_drag_drop(self):
        """设置拖拽功能"""
        # 为整个窗口启用拖拽
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.on_drop)
        
        # 为文件列表区域也启用拖拽
        self.file_tree.drop_target_register(DND_FILES)
        self.file_tree.dnd_bind('<<Drop>>', self.on_drop)

    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="导入图片...", command=self.import_images)
        file_menu.add_command(label="导入文件夹...", command=self.import_folder)
        file_menu.add_separator()
        file_menu.add_command(label="导出当前图片...", command=self.export_current)
        file_menu.add_command(label="批量导出...", command=self.export_all)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # 模板菜单
        template_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="模板", menu=template_menu)
        template_menu.add_command(label="保存模板...", command=self.save_template)
        template_menu.add_command(label="加载模板...", command=self.load_template)
        template_menu.add_command(label="管理模板...", command=self.manage_templates)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)
        
    def create_main_layout(self):
        """创建主布局"""
        # 创建主要的PanedWindow
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 左侧面板（文件列表和水印设置）
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)
        
        # 右侧面板（预览区域）
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=2)
        
        self.create_left_panel(left_frame)
        self.create_right_panel(right_frame)
        
    def create_left_panel(self, parent):
        """创建左侧面板"""
        # 文件导入区域
        import_frame = ttk.LabelFrame(parent, text="文件导入", padding=10)
        import_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 导入按钮
        btn_frame = ttk.Frame(import_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="选择图片", command=self.import_images).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="选择文件夹", command=self.import_folder).pack(side=tk.LEFT)
        
        # 拖拽提示
        drag_label = ttk.Label(import_frame, text="或将图片/文件夹拖拽到此处", 
                              foreground="gray", font=("Arial", 9))
        drag_label.pack(pady=(10, 0))
        
        # 文件列表
        list_frame = ttk.LabelFrame(parent, text="图片列表", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建Treeview用于显示文件列表
        self.file_tree = ttk.Treeview(list_frame, columns=('size', 'format'), show='tree headings', height=8)
        self.file_tree.heading('#0', text='文件名')
        self.file_tree.heading('size', text='尺寸')
        self.file_tree.heading('format', text='格式')
        self.file_tree.column('#0', width=200)
        self.file_tree.column('size', width=80)
        self.file_tree.column('format', width=60)
        
        # 滚动条
        tree_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定选择事件
        self.file_tree.bind('<<TreeviewSelect>>', self.on_file_select)
        
        # 水印设置区域
        self.create_watermark_settings(parent)
        
    def create_watermark_settings(self, parent):
        """创建水印设置区域"""
        settings_frame = ttk.LabelFrame(parent, text="水印设置", padding=10)
        settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 文本设置
        text_frame = ttk.Frame(settings_frame)
        text_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(text_frame, text="水印文本:").pack(anchor=tk.W)
        self.text_var = tk.StringVar(value="自动日期")
        text_entry = ttk.Entry(text_frame, textvariable=self.text_var)
        text_entry.pack(fill=tk.X, pady=(2, 0))
        text_entry.bind('<KeyRelease>', self.on_settings_change)
        
        # 字体设置
        font_frame = ttk.Frame(settings_frame)
        font_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 字体大小
        size_frame = ttk.Frame(font_frame)
        size_frame.pack(fill=tk.X)
        
        ttk.Label(size_frame, text="字体大小:").pack(side=tk.LEFT)
        self.font_size_var = tk.IntVar(value=36)
        size_spin = ttk.Spinbox(size_frame, from_=8, to=200, width=8, textvariable=self.font_size_var)
        size_spin.pack(side=tk.RIGHT)
        size_spin.bind('<KeyRelease>', self.on_settings_change)
        size_spin.bind('<<Increment>>', self.on_settings_change)
        size_spin.bind('<<Decrement>>', self.on_settings_change)
        
        # 颜色设置
        color_frame = ttk.Frame(settings_frame)
        color_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(color_frame, text="颜色:").pack(side=tk.LEFT)
        self.color_var = tk.StringVar(value="#FFFFFF")
        self.color_button = tk.Button(color_frame, text="选择颜色", width=10, 
                                     bg="white", command=self.choose_color)
        self.color_button.pack(side=tk.RIGHT)
        
        # 透明度设置
        opacity_frame = ttk.Frame(settings_frame)
        opacity_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(opacity_frame, text="透明度:").pack(side=tk.LEFT)
        self.opacity_var = tk.IntVar(value=100)
        opacity_scale = ttk.Scale(opacity_frame, from_=0, to=100, orient=tk.HORIZONTAL, 
                                 variable=self.opacity_var, command=self.on_settings_change)
        opacity_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        
        # 位置设置
        position_frame = ttk.LabelFrame(settings_frame, text="位置设置", padding=5)
        position_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.position_var = tk.StringVar(value="bottom_right")
        
        # 九宫格位置选择
        grid_frame = ttk.Frame(position_frame)
        grid_frame.pack()
        
        positions = [
            ("左上", "top_left"), ("上中", "top_center"), ("右上", "top_right"),
            ("左中", "middle_left"), ("居中", "center"), ("右中", "middle_right"),
            ("左下", "bottom_left"), ("下中", "bottom_center"), ("右下", "bottom_right")
        ]
        
        for i, (text, value) in enumerate(positions):
            row, col = divmod(i, 3)
            ttk.Radiobutton(grid_frame, text=text, variable=self.position_var, 
                           value=value, command=self.on_settings_change).grid(row=row, column=col, padx=2, pady=2)
        
    def create_right_panel(self, parent):
        """创建右侧预览面板"""
        # 预览区域
        preview_frame = ttk.LabelFrame(parent, text="预览", padding=10)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 预览画布
        self.preview_canvas = tk.Canvas(preview_frame, bg="white", relief=tk.SUNKEN, bd=2)
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)
        
        # 导出设置区域
        export_frame = ttk.LabelFrame(parent, text="导出设置", padding=10)
        export_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 输出目录
        dir_frame = ttk.Frame(export_frame)
        dir_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(dir_frame, text="输出目录:").pack(side=tk.LEFT)
        self.output_dir_var = tk.StringVar()
        ttk.Entry(dir_frame, textvariable=self.output_dir_var, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        ttk.Button(dir_frame, text="选择", command=self.choose_output_dir).pack(side=tk.RIGHT)
        
        # 文件命名选项
        naming_frame = ttk.Frame(export_frame)
        naming_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(naming_frame, text="文件命名:").pack(side=tk.LEFT)
        self.naming_var = tk.StringVar(value="suffix")
        ttk.Radiobutton(naming_frame, text="保持原名", variable=self.naming_var, value="original").pack(side=tk.LEFT, padx=(10, 5))
        ttk.Radiobutton(naming_frame, text="添加前缀", variable=self.naming_var, value="prefix").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Radiobutton(naming_frame, text="添加后缀", variable=self.naming_var, value="suffix").pack(side=tk.LEFT)
        
        # 导出按钮
        button_frame = ttk.Frame(export_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="导出当前图片", command=self.export_current).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="批量导出", command=self.export_all).pack(side=tk.LEFT)
        
    # 事件处理方法
    def import_images(self):
        """导入图片文件"""
        filetypes = [
            ("图片文件", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"),
            ("JPEG文件", "*.jpg *.jpeg"),
            ("PNG文件", "*.png"),
            ("所有文件", "*.*")
        ]
        
        files = filedialog.askopenfilenames(
            title="选择图片文件",
            filetypes=filetypes
        )
        
        if files:
            self.add_images(files)
    
    def import_folder(self):
        """导入文件夹"""
        folder = filedialog.askdirectory(title="选择包含图片的文件夹")
        if folder:
            # 查找文件夹中的图片文件
            image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
            image_files = []
            
            for root, dirs, files in os.walk(folder):
                for file in files:
                    if Path(file).suffix.lower() in image_extensions:
                        image_files.append(os.path.join(root, file))
            
            if image_files:
                self.add_images(image_files)
            else:
                messagebox.showinfo("提示", "所选文件夹中没有找到支持的图片文件")
    
    def add_images(self, file_paths):
        """添加图片到列表"""
        for file_path in file_paths:
            if file_path not in [img['path'] for img in self.images]:
                try:
                    with Image.open(file_path) as img:
                        # 获取图片信息
                        width, height = img.size
                        format_name = img.format
                        
                        image_info = {
                            'path': file_path,
                            'filename': os.path.basename(file_path),
                            'size': f"{width}x{height}",
                            'format': format_name,
                            'width': width,
                            'height': height
                        }
                        
                        self.images.append(image_info)
                        
                        # 添加到树形控件
                        self.file_tree.insert('', 'end', text=image_info['filename'],
                                            values=(image_info['size'], image_info['format']))
                        
                except Exception as e:
                    print(f"无法加载图片 {file_path}: {e}")
        
        # 如果这是第一次添加图片，选择第一张
        if len(self.images) == len(file_paths):
            self.current_image_index = 0
            self.load_current_image()
    
    def on_file_select(self, event):
        """文件选择事件"""
        selection = self.file_tree.selection()
        if selection:
            item = selection[0]
            index = self.file_tree.index(item)
            self.current_image_index = index
            self.load_current_image()
    
    def load_current_image(self):
        """加载当前选中的图片"""
        if not self.images or self.current_image_index >= len(self.images):
            return
        
        image_info = self.images[self.current_image_index]
        try:
            self.current_image = Image.open(image_info['path'])
            
            # 自动设置水印文本为日期
            if self.text_var.get() == "自动日期" or not self.text_var.get():
                date = self.get_exif_date(image_info['path'])
                self.text_var.set(date)
            
            self.update_preview()
            
        except Exception as e:
            messagebox.showerror("错误", f"无法加载图片: {e}")
    
    def get_exif_date(self, image_path):
        """从EXIF数据获取日期"""
        try:
            with open(image_path, 'rb') as f:
                tags = exifread.process_file(f)
                if 'EXIF DateTimeOriginal' in tags:
                    date_str = str(tags['EXIF DateTimeOriginal'])
                    return date_str.split(' ')[0].replace(':', '-')
        except:
            pass
        
        # 如果没有EXIF日期，使用当前日期
        return datetime.now().strftime("%Y-%m-%d")
    
    def on_settings_change(self, event=None):
        """水印设置改变时更新预览"""
        self.update_watermark_settings()
        self.update_preview()
    
    def update_watermark_settings(self):
        """更新水印设置"""
        self.watermark_settings.update({
            'text': self.text_var.get(),
            'font_size': self.font_size_var.get(),
            'color': self.color_var.get(),
            'opacity': self.opacity_var.get(),
            'position': self.position_var.get()
        })
    
    def choose_color(self):
        """选择颜色"""
        color = colorchooser.askcolor(title="选择水印颜色", color=self.color_var.get())
        if color[1]:  # 如果用户选择了颜色
            self.color_var.set(color[1])
            self.color_button.config(bg=color[1])
            self.on_settings_change()
    
    def update_preview(self):
        """更新预览"""
        if not self.current_image:
            return
        
        try:
            # 创建预览图片副本
            preview_img = self.current_image.copy()
            
            # 添加水印
            if self.watermark_settings['text']:
                preview_img = self.add_watermark_to_image(preview_img)
            
            # 调整图片大小以适应预览区域
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:  # 确保画布已经初始化
                preview_img = self.resize_for_preview(preview_img, canvas_width, canvas_height)
                
                # 转换为PhotoImage并显示
                self.preview_image = ImageTk.PhotoImage(preview_img)
                
                # 清除画布并显示新图片
                self.preview_canvas.delete("all")
                
                # 居中显示图片
                x = (canvas_width - preview_img.width) // 2
                y = (canvas_height - preview_img.height) // 2
                
                self.preview_canvas.create_image(x, y, anchor=tk.NW, image=self.preview_image)
        
        except Exception as e:
            print(f"预览更新错误: {e}")
    
    def resize_for_preview(self, image, max_width, max_height):
        """调整图片大小以适应预览区域"""
        img_width, img_height = image.size
        
        # 计算缩放比例
        scale_x = (max_width - 20) / img_width  # 留出边距
        scale_y = (max_height - 20) / img_height
        scale = min(scale_x, scale_y, 1.0)  # 不放大，只缩小
        
        if scale < 1.0:
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return image
    
    def add_watermark_to_image(self, image):
        """为图片添加水印"""
        # 创建图片副本
        img_with_watermark = image.copy()
        
        # 如果需要透明度，转换为RGBA
        if self.watermark_settings['opacity'] < 100:
            if img_with_watermark.mode != 'RGBA':
                img_with_watermark = img_with_watermark.convert('RGBA')
            
            # 创建透明图层
            overlay = Image.new('RGBA', img_with_watermark.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
        else:
            draw = ImageDraw.Draw(img_with_watermark)
        
        # 设置字体
        try:
            font = ImageFont.truetype("arial.ttf", self.watermark_settings['font_size'])
        except:
            try:
                # macOS系统字体
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", self.watermark_settings['font_size'])
            except:
                font = ImageFont.load_default()
        
        # 获取文本尺寸
        text = self.watermark_settings['text']
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # 计算位置
        img_width, img_height = image.size
        x, y = self.calculate_watermark_position(img_width, img_height, text_width, text_height)
        
        # 设置颜色和透明度
        color = self.watermark_settings['color']
        if self.watermark_settings['opacity'] < 100:
            # 转换颜色为RGBA
            if color.startswith('#'):
                color = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
            alpha = int(255 * self.watermark_settings['opacity'] / 100)
            color = color + (alpha,)
        
        # 绘制文本
        draw.text((x, y), text, fill=color, font=font)
        
        # 如果使用了透明度，合并图层
        if self.watermark_settings['opacity'] < 100:
            img_with_watermark = Image.alpha_composite(img_with_watermark, overlay)
            if image.mode != 'RGBA':
                img_with_watermark = img_with_watermark.convert(image.mode)
        
        return img_with_watermark
    
    def calculate_watermark_position(self, img_width, img_height, text_width, text_height):
        """计算水印位置"""
        margin = 10
        position = self.watermark_settings['position']
        
        position_map = {
            'top_left': (margin, margin),
            'top_center': ((img_width - text_width) // 2, margin),
            'top_right': (img_width - text_width - margin, margin),
            'middle_left': (margin, (img_height - text_height) // 2),
            'center': ((img_width - text_width) // 2, (img_height - text_height) // 2),
            'middle_right': (img_width - text_width - margin, (img_height - text_height) // 2),
            'bottom_left': (margin, img_height - text_height - margin),
            'bottom_center': ((img_width - text_width) // 2, img_height - text_height - margin),
            'bottom_right': (img_width - text_width - margin, img_height - text_height - margin)
        }
        
        return position_map.get(position, position_map['bottom_right'])
    
    def choose_output_dir(self):
        """选择输出目录"""
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_dir_var.set(directory)
            self.export_settings['output_dir'] = directory
    
    def export_current(self):
        """导出当前图片"""
        if not self.current_image or not self.images:
            messagebox.showwarning("警告", "请先选择要导出的图片")
            return
        
        if not self.export_settings['output_dir']:
            self.choose_output_dir()
            if not self.export_settings['output_dir']:
                return
        
        try:
            image_info = self.images[self.current_image_index]
            output_path = self.generate_output_path(image_info)
            
            # 添加水印并保存
            img_with_watermark = self.current_image.copy()
            if self.watermark_settings['text']:
                img_with_watermark = self.add_watermark_to_image(img_with_watermark)
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 保存图片
            if self.export_settings['output_format'] == 'JPEG':
                if img_with_watermark.mode == 'RGBA':
                    img_with_watermark = img_with_watermark.convert('RGB')
                img_with_watermark.save(output_path, 'JPEG', quality=self.export_settings['jpeg_quality'])
            else:
                img_with_watermark.save(output_path, 'PNG')
            
            messagebox.showinfo("成功", f"图片已导出到: {output_path}")
            
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {e}")
    
    def export_all(self):
        """批量导出所有图片"""
        if not self.images:
            messagebox.showwarning("警告", "请先导入图片")
            return
        
        if not self.export_settings['output_dir']:
            self.choose_output_dir()
            if not self.export_settings['output_dir']:
                return
        
        # 创建进度窗口
        progress_window = tk.Toplevel(self.root)
        progress_window.title("批量导出")
        progress_window.geometry("400x150")
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        ttk.Label(progress_window, text="正在导出图片...").pack(pady=10)
        
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(progress_window, variable=progress_var, maximum=len(self.images))
        progress_bar.pack(fill=tk.X, padx=20, pady=10)
        
        status_label = ttk.Label(progress_window, text="")
        status_label.pack(pady=5)
        
        def export_thread():
            success_count = 0
            for i, image_info in enumerate(self.images):
                try:
                    status_label.config(text=f"正在处理: {image_info['filename']}")
                    progress_window.update()
                    
                    # 加载图片
                    img = Image.open(image_info['path'])
                    
                    # 获取日期并添加水印
                    if self.text_var.get() == "自动日期":
                        date = self.get_exif_date(image_info['path'])
                        original_text = self.watermark_settings['text']
                        self.watermark_settings['text'] = date
                        img_with_watermark = self.add_watermark_to_image(img)
                        self.watermark_settings['text'] = original_text
                    else:
                        img_with_watermark = self.add_watermark_to_image(img)
                    
                    # 生成输出路径并保存
                    output_path = self.generate_output_path(image_info)
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    
                    if self.export_settings['output_format'] == 'JPEG':
                        if img_with_watermark.mode == 'RGBA':
                            img_with_watermark = img_with_watermark.convert('RGB')
                        img_with_watermark.save(output_path, 'JPEG', quality=self.export_settings['jpeg_quality'])
                    else:
                        img_with_watermark.save(output_path, 'PNG')
                    
                    success_count += 1
                    
                except Exception as e:
                    print(f"导出 {image_info['filename']} 失败: {e}")
                
                progress_var.set(i + 1)
                progress_window.update()
            
            progress_window.destroy()
            messagebox.showinfo("完成", f"批量导出完成！\n成功导出 {success_count}/{len(self.images)} 张图片")
        
        # 在新线程中执行导出
        threading.Thread(target=export_thread, daemon=True).start()
    
    def generate_output_path(self, image_info):
        """生成输出文件路径"""
        filename = image_info['filename']
        name, ext = os.path.splitext(filename)
        
        # 根据命名选项生成新文件名
        if self.export_settings['naming_option'] == 'original':
            new_name = name
        elif self.export_settings['naming_option'] == 'prefix':
            new_name = self.export_settings['custom_prefix'] + name
        else:  # suffix
            new_name = name + self.export_settings['custom_suffix']
        
        # 根据输出格式设置扩展名
        if self.export_settings['output_format'] == 'JPEG':
            new_ext = '.jpg'
        else:
            new_ext = '.png'
        
        return os.path.join(self.export_settings['output_dir'], new_name + new_ext)
    
    def save_template(self):
        """保存水印模板"""
        template_name = tk.simpledialog.askstring("保存模板", "请输入模板名称:")
        if template_name:
            try:
                templates_dir = os.path.join(os.path.expanduser("~"), ".watermark_templates")
                os.makedirs(templates_dir, exist_ok=True)
                
                template_file = os.path.join(templates_dir, f"{template_name}.json")
                with open(template_file, 'w', encoding='utf-8') as f:
                    json.dump(self.watermark_settings, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("成功", f"模板 '{template_name}' 已保存")
            except Exception as e:
                messagebox.showerror("错误", f"保存模板失败: {e}")
    
    def load_template(self):
        """加载水印模板"""
        templates_dir = os.path.join(os.path.expanduser("~"), ".watermark_templates")
        if not os.path.exists(templates_dir):
            messagebox.showinfo("提示", "没有找到已保存的模板")
            return
        
        template_file = filedialog.askopenfilename(
            title="选择模板文件",
            initialdir=templates_dir,
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        
        if template_file:
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                # 更新设置
                self.watermark_settings.update(settings)
                self.update_ui_from_settings()
                self.update_preview()
                
                messagebox.showinfo("成功", "模板加载成功")
            except Exception as e:
                messagebox.showerror("错误", f"加载模板失败: {e}")
    
    def manage_templates(self):
        """管理模板"""
        # 这里可以实现一个模板管理窗口
        messagebox.showinfo("提示", "模板管理功能将在后续版本中实现")
    
    def update_ui_from_settings(self):
        """根据设置更新UI"""
        self.text_var.set(self.watermark_settings.get('text', ''))
        self.font_size_var.set(self.watermark_settings.get('font_size', 36))
        self.color_var.set(self.watermark_settings.get('color', '#FFFFFF'))
        self.opacity_var.set(self.watermark_settings.get('opacity', 100))
        self.position_var.set(self.watermark_settings.get('position', 'bottom_right'))
        
        # 更新颜色按钮
        self.color_button.config(bg=self.watermark_settings.get('color', '#FFFFFF'))
    
    def load_default_settings(self):
        """加载默认设置"""
        # 尝试加载上次的设置
        try:
            settings_file = os.path.join(os.path.expanduser("~"), ".watermark_settings.json")
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                self.watermark_settings.update(settings.get('watermark', {}))
                self.export_settings.update(settings.get('export', {}))
                self.update_ui_from_settings()
        except:
            pass
    
    def save_settings(self):
        """保存设置"""
        try:
            settings = {
                'watermark': self.watermark_settings,
                'export': self.export_settings
            }
            settings_file = os.path.join(os.path.expanduser("~"), ".watermark_settings.json")
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
        except:
            pass
    
    def show_about(self):
        """显示关于对话框"""
        about_text = """Image Watermarker v2.0

一个功能强大的图片水印添加工具

功能特点:
• 支持多种图片格式 (JPEG, PNG, BMP, TIFF)
• 实时预览水印效果
• 批量处理图片
• 自定义水印样式
• 模板保存和管理

开发者: AI Assistant
版本: 2.0.0"""
        
        messagebox.showinfo("关于 Image Watermarker", about_text)
    
    def on_drop(self, event):
        """处理拖拽文件事件"""
        files = self.root.tk.splitlist(event.data)
        
        image_files = []
        for file_path in files:
            if os.path.isfile(file_path):
                # 检查是否为支持的图片格式
                if any(file_path.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']):
                    image_files.append(file_path)
            elif os.path.isdir(file_path):
                # 如果是文件夹，递归查找图片文件
                for root, dirs, files in os.walk(file_path):
                    for file in files:
                        if any(file.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']):
                            image_files.append(os.path.join(root, file))
        
        if image_files:
            self.add_images(image_files)
        else:
            messagebox.showinfo("提示", "拖拽的文件中没有找到支持的图片格式")

def main():
    # 创建主窗口
    root = TkinterDnD.Tk()  # 支持拖拽的Tk窗口
    app = WatermarkGUI(root)
    
    # 绑定窗口关闭事件
    def on_closing():
        app.save_settings()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # 绑定画布大小改变事件
    def on_canvas_configure(event):
        app.update_preview()
    
    app.preview_canvas.bind('<Configure>', on_canvas_configure)
    
    # 启动应用
    root.mainloop()

if __name__ == "__main__":
    main()