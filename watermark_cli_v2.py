#!/usr/bin/env python3
"""
Image Watermarker CLI v2.0
Enhanced command-line version with advanced features
"""

import os
import sys
import json
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import exifread
from datetime import datetime

class WatermarkProcessor:
    def __init__(self):
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
        self.default_settings = {
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
        
        self.watermark_settings = self.default_settings.copy()
    
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
    
    def find_images(self, path):
        """查找图片文件"""
        images = []
        path = Path(path)
        
        if path.is_file():
            if path.suffix.lower() in self.supported_formats:
                images.append(str(path))
        elif path.is_dir():
            for ext in self.supported_formats:
                images.extend(path.glob(f"**/*{ext}"))
                images.extend(path.glob(f"**/*{ext.upper()}"))
            images = [str(img) for img in images]
        
        return sorted(images)
    
    def calculate_watermark_position(self, img_width, img_height, text_width, text_height):
        """计算水印位置"""
        margin_x = self.watermark_settings['x_offset']
        margin_y = self.watermark_settings['y_offset']
        position = self.watermark_settings['position']
        
        position_map = {
            'top_left': (margin_x, margin_y),
            'top_center': ((img_width - text_width) // 2, margin_y),
            'top_right': (img_width - text_width - margin_x, margin_y),
            'middle_left': (margin_x, (img_height - text_height) // 2),
            'center': ((img_width - text_width) // 2, (img_height - text_height) // 2),
            'middle_right': (img_width - text_width - margin_x, (img_height - text_height) // 2),
            'bottom_left': (margin_x, img_height - text_height - margin_y),
            'bottom_center': ((img_width - text_width) // 2, img_height - text_height - margin_y),
            'bottom_right': (img_width - text_width - margin_x, img_height - text_height - margin_y)
        }
        
        return position_map.get(position, position_map['bottom_right'])
    
    def add_watermark_to_image(self, image, text=None):
        """为图片添加水印"""
        if text is None:
            text = self.watermark_settings['text']
        
        if not text:
            return image
        
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
        font = self.get_font()
        
        # 获取文本尺寸
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
        if self.watermark_settings['outline']:
            # 绘制描边
            outline_color = (0, 0, 0, alpha) if self.watermark_settings['opacity'] < 100 else 'black'
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), text, fill=outline_color, font=font)
        
        if self.watermark_settings['shadow']:
            # 绘制阴影
            shadow_color = (0, 0, 0, alpha // 2) if self.watermark_settings['opacity'] < 100 else 'gray'
            draw.text((x + 2, y + 2), text, fill=shadow_color, font=font)
        
        # 绘制主文本
        draw.text((x, y), text, fill=color, font=font)
        
        # 如果使用了透明度，合并图层
        if self.watermark_settings['opacity'] < 100:
            img_with_watermark = Image.alpha_composite(img_with_watermark, overlay)
            if image.mode != 'RGBA':
                img_with_watermark = img_with_watermark.convert(image.mode)
        
        return img_with_watermark
    
    def get_font(self):
        """获取字体"""
        font_size = self.watermark_settings['font_size']
        
        # 尝试加载系统字体
        font_paths = [
            "/System/Library/Fonts/Arial.ttf",  # macOS
            "/System/Library/Fonts/Helvetica.ttc",  # macOS
            "C:/Windows/Fonts/arial.ttf",  # Windows
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
        ]
        
        for font_path in font_paths:
            try:
                font = ImageFont.truetype(font_path, font_size)
                return font
            except:
                continue
        
        # 如果都失败了，使用默认字体
        try:
            return ImageFont.load_default()
        except:
            return ImageFont.load_default()
    
    def generate_output_path(self, input_path, output_dir=None):
        """生成输出文件路径"""
        input_path = Path(input_path)
        
        if output_dir:
            output_dir = Path(output_dir)
        else:
            output_dir = input_path.parent / "watermarked"
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 根据命名选项生成新文件名
        name = input_path.stem
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
        
        return output_dir / (new_name + new_ext)
    
    def process_image(self, input_path, output_path=None, auto_date=False):
        """处理单张图片"""
        try:
            # 加载图片
            with Image.open(input_path) as img:
                # 如果启用自动日期，获取EXIF日期
                if auto_date:
                    date = self.get_exif_date(input_path)
                    watermarked_img = self.add_watermark_to_image(img, date)
                else:
                    watermarked_img = self.add_watermark_to_image(img)
                
                # 生成输出路径
                if not output_path:
                    output_path = self.generate_output_path(input_path, self.export_settings.get('output_dir'))
                
                # 确保输出目录存在
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # 保存图片
                if self.export_settings['output_format'] == 'JPEG':
                    if watermarked_img.mode == 'RGBA':
                        watermarked_img = watermarked_img.convert('RGB')
                    watermarked_img.save(output_path, 'JPEG', quality=self.export_settings['jpeg_quality'])
                else:
                    watermarked_img.save(output_path, 'PNG')
                
                return str(output_path)
        
        except Exception as e:
            raise Exception(f"处理图片 {input_path} 失败: {e}")
    
    def process_batch(self, input_paths, output_dir=None, auto_date=False, progress_callback=None):
        """批量处理图片"""
        results = []
        total = len(input_paths)
        
        for i, input_path in enumerate(input_paths):
            try:
                output_path = self.process_image(input_path, None, auto_date)
                results.append({'input': input_path, 'output': output_path, 'success': True})
                
                if progress_callback:
                    progress_callback(i + 1, total, input_path)
                    
            except Exception as e:
                results.append({'input': input_path, 'error': str(e), 'success': False})
                print(f"错误: {e}")
        
        return results
    
    def save_template(self, template_name, template_dir=None):
        """保存水印模板"""
        if not template_dir:
            template_dir = Path.home() / ".watermark_templates"
        
        template_dir = Path(template_dir)
        template_dir.mkdir(parents=True, exist_ok=True)
        
        template_file = template_dir / f"{template_name}.json"
        
        template_data = {
            'watermark': self.watermark_settings,
            'export': self.export_settings,
            'created_at': datetime.now().isoformat()
        }
        
        with open(template_file, 'w', encoding='utf-8') as f:
            json.dump(template_data, f, indent=2, ensure_ascii=False)
        
        return str(template_file)
    
    def load_template(self, template_file):
        """加载水印模板"""
        with open(template_file, 'r', encoding='utf-8') as f:
            template_data = json.load(f)
        
        if 'watermark' in template_data:
            self.watermark_settings.update(template_data['watermark'])
        
        if 'export' in template_data:
            self.export_settings.update(template_data['export'])
    
    def list_templates(self, template_dir=None):
        """列出可用模板"""
        if not template_dir:
            template_dir = Path.home() / ".watermark_templates"
        
        template_dir = Path(template_dir)
        if not template_dir.exists():
            return []
        
        templates = []
        for template_file in template_dir.glob("*.json"):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)
                
                templates.append({
                    'name': template_file.stem,
                    'file': str(template_file),
                    'created_at': template_data.get('created_at', 'Unknown')
                })
            except:
                continue
        
        return templates

def create_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(description='Image Watermarker v2.0 - 高级图片水印工具')
    
    # 基本参数
    parser.add_argument('input', help='输入图片文件或目录')
    parser.add_argument('-o', '--output', help='输出目录')
    parser.add_argument('-t', '--text', default='', help='水印文本')
    parser.add_argument('--auto-date', action='store_true', help='自动使用EXIF日期作为水印')
    
    # 水印样式参数
    parser.add_argument('--font-size', type=int, default=36, help='字体大小 (默认: 36)')
    parser.add_argument('--color', default='#FFFFFF', help='文字颜色 (默认: #FFFFFF)')
    parser.add_argument('--opacity', type=int, default=100, help='透明度 0-100 (默认: 100)')
    parser.add_argument('--position', default='bottom_right', 
                       choices=['top_left', 'top_center', 'top_right', 
                               'middle_left', 'center', 'middle_right',
                               'bottom_left', 'bottom_center', 'bottom_right'],
                       help='水印位置 (默认: bottom_right)')
    parser.add_argument('--x-offset', type=int, default=10, help='水平偏移 (默认: 10)')
    parser.add_argument('--y-offset', type=int, default=10, help='垂直偏移 (默认: 10)')
    parser.add_argument('--shadow', action='store_true', help='添加阴影效果')
    parser.add_argument('--outline', action='store_true', help='添加描边效果')
    
    # 输出参数
    parser.add_argument('--format', choices=['JPEG', 'PNG'], default='JPEG', help='输出格式 (默认: JPEG)')
    parser.add_argument('--quality', type=int, default=95, help='JPEG质量 1-100 (默认: 95)')
    parser.add_argument('--naming', choices=['original', 'prefix', 'suffix'], default='suffix',
                       help='文件命名方式 (默认: suffix)')
    parser.add_argument('--prefix', default='wm_', help='文件名前缀 (默认: wm_)')
    parser.add_argument('--suffix', default='_watermarked', help='文件名后缀 (默认: _watermarked)')
    
    # 模板参数
    parser.add_argument('--save-template', help='保存当前设置为模板')
    parser.add_argument('--load-template', help='加载模板文件')
    parser.add_argument('--list-templates', action='store_true', help='列出可用模板')
    
    # 其他参数
    parser.add_argument('--preview', action='store_true', help='仅预览设置，不处理图片')
    parser.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    
    return parser

def progress_callback(current, total, filename):
    """进度回调函数"""
    percentage = (current / total) * 100
    print(f"进度: {current}/{total} ({percentage:.1f}%) - {Path(filename).name}")

def main():
    parser = create_parser()
    args = parser.parse_args()
    
    # 创建处理器
    processor = WatermarkProcessor()
    
    # 列出模板
    if args.list_templates:
        templates = processor.list_templates()
        if templates:
            print("可用模板:")
            for template in templates:
                print(f"  - {template['name']} (创建于: {template['created_at']})")
        else:
            print("没有找到模板")
        return
    
    # 加载模板
    if args.load_template:
        try:
            processor.load_template(args.load_template)
            print(f"已加载模板: {args.load_template}")
        except Exception as e:
            print(f"加载模板失败: {e}")
            return
    
    # 更新设置
    processor.watermark_settings.update({
        'text': args.text,
        'font_size': args.font_size,
        'color': args.color,
        'opacity': args.opacity,
        'position': args.position,
        'x_offset': args.x_offset,
        'y_offset': args.y_offset,
        'shadow': args.shadow,
        'outline': args.outline
    })
    
    processor.export_settings.update({
        'output_dir': args.output or '',
        'naming_option': args.naming,
        'custom_prefix': args.prefix,
        'custom_suffix': args.suffix,
        'output_format': args.format,
        'jpeg_quality': args.quality
    })
    
    # 预览设置
    if args.preview:
        print("当前水印设置:")
        print(f"  文本: {processor.watermark_settings['text']}")
        print(f"  字体大小: {processor.watermark_settings['font_size']}")
        print(f"  颜色: {processor.watermark_settings['color']}")
        print(f"  透明度: {processor.watermark_settings['opacity']}%")
        print(f"  位置: {processor.watermark_settings['position']}")
        print(f"  偏移: ({processor.watermark_settings['x_offset']}, {processor.watermark_settings['y_offset']})")
        print(f"  阴影: {processor.watermark_settings['shadow']}")
        print(f"  描边: {processor.watermark_settings['outline']}")
        print("\n输出设置:")
        print(f"  格式: {processor.export_settings['output_format']}")
        print(f"  质量: {processor.export_settings['jpeg_quality']}")
        print(f"  命名: {processor.export_settings['naming_option']}")
        return
    
    # 保存模板
    if args.save_template:
        try:
            template_file = processor.save_template(args.save_template)
            print(f"模板已保存: {template_file}")
        except Exception as e:
            print(f"保存模板失败: {e}")
    
    # 查找图片文件
    if not os.path.exists(args.input):
        print(f"错误: 输入路径不存在: {args.input}")
        return
    
    images = processor.find_images(args.input)
    if not images:
        print("没有找到支持的图片文件")
        return
    
    print(f"找到 {len(images)} 张图片")
    
    # 处理图片
    if not args.text and not args.auto_date:
        print("警告: 没有指定水印文本，将使用自动日期")
        args.auto_date = True
    
    try:
        if len(images) == 1:
            # 单张图片
            output_path = processor.process_image(images[0], None, args.auto_date)
            print(f"处理完成: {output_path}")
        else:
            # 批量处理
            print("开始批量处理...")
            results = processor.process_batch(images, args.output, args.auto_date, 
                                            progress_callback if args.verbose else None)
            
            success_count = sum(1 for r in results if r['success'])
            print(f"\n批量处理完成: {success_count}/{len(results)} 张图片处理成功")
            
            if args.verbose:
                for result in results:
                    if result['success']:
                        print(f"  ✓ {result['input']} -> {result['output']}")
                    else:
                        print(f"  ✗ {result['input']}: {result['error']}")
    
    except Exception as e:
        print(f"处理失败: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())