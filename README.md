# Image Watermarker v2.0

这是一个功能强大的图片水印工具，支持命令行和图形用户界面（GUI）两种模式。它允许用户为单张图片或整个文件夹中的图片添加自定义文本水印。

## 主要功能

- **多种水印模式**：支持文本水印和图片水印（即将推出）。
- **灵活的文本选项**：
  - **自动日期**：自动从图片的EXIF信息中提取拍摄日期作为水印。
  - **自定义文本**：支持任意文本内容。
- **丰富的样式控制**：
  - **字体**：自定义字体、大小、颜色。
  - **效果**：支持透明度、旋转、阴影、描边等效果。
- **精确定位**：
  - **九宫格定位**：提供九个预设位置（如左上、右下）。
  - **精确偏移**：支持自定义水平和垂直偏移。
- **批量处理**：一次性为文件夹中的所有图片添加水印。
- **模板系统**：
  - **保存和加载**：将常用设置保存为模板，方便日后调用。
  - **模板管理**：轻松管理已保存的模板。
- **多种输出选项**：
  - **格式**：支持导出为JPEG或PNG格式。
  - **命名**：可选择保留原文件名、添加前缀或后缀。
  - **质量和尺寸**：可自定义JPEG质量和调整图片尺寸。
- **跨平台支持**：提供适用于Windows和macOS的可执行文件。

## 安装和运行

### 使用可执行文件

推荐从 GitHub 最新 Release 下载可执行文件，助教以最新 Release 为准：

- 最新版下载地址（macOS/Windows）：
  - https://github.com/ethanjin/image-watermarker/releases/latest

下载后，按照操作系统运行：

- **macOS**：
  - GUI 版本：双击 `ImageWatermarkerGUI.app` 或将应用拖入应用程序文件夹。
  - CLI 版本：在终端执行 `./ImageWatermarker`。
  - 如遇“已损坏或无法打开”，请在“系统设置 -> 隐私与安全性”允许该应用运行，或运行：
    - `xattr -dr com.apple.quarantine ImageWatermarkerGUI.app`

- **Windows**：
  - GUI 版本：双击 `ImageWatermarkerGUI.exe`（如提供）。
  - CLI 版本：双击或在命令行执行 `ImageWatermarker.exe`。
  - 若出现安全提示，请选择“仍要运行”。

### 从源码运行

如果您希望从源码运行，请确保已安装Python 3.x，然后按照以下步骤操作：

1. **克隆仓库**：
   ```bash
   git clone https://github.com/your-username/image-watermarker.git
   cd image-watermarker
   ```

2. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```

3. **运行**：
   - **命令行版本**：
     ```bash
     python watermark_cli_v2.py [参数]
     ```
   - **GUI版本**（如果您的环境支持）：
     ```bash
     python watermark_gui_simple.py
     ```

## 使用方法（命令行）

命令行版本提供了丰富的功能，以下是一些常用示例：

### 基本用法

为单张图片添加自动日期水印：
```bash
./dist/ImageWatermarker test_image.jpg --auto-date
```

为整个文件夹的图片添加自定义文本水印：
```bash
./dist/ImageWatermarker /path/to/your/images --text "My Watermark"
```

### 高级用法

添加带有样式的水印：
```bash
./dist/ImageWatermarker test_image.jpg --text "Styled Watermark" --color "#FF0000" --font-size 48 --opacity 75 --position top_left --shadow --outline
```

使用模板并批量处理：
```bash
# 保存当前设置为模板
./dist/ImageWatermarker test_image.jpg --text "Template" --save-template my_template

# 加载模板并处理文件夹
./dist/ImageWatermarker /path/to/images --load-template ~/.watermark_templates/my_template.json
```

查看所有可用参数：
```bash
./dist/ImageWatermarker --help
```

## GUI版本

GUI版本提供了更直观的操作界面，支持拖放导入、实时预览和所有命令行版本的功能。双击 `watermark_gui_simple.py` 或运行打包好的GUI应用即可启动。

## 未来计划

- **图片水印**：支持使用自定义图片作为水印。
- **更丰富的UI交互**：如在预览图上直接拖动和旋转水印。
- **多语言支持**：提供多语言界面。

## 贡献

欢迎提交问题、建议或代码贡献！