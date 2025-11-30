#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多功能Base图片解码器
支持多种base编码格式自动解码并保存图片
作者：AiPy
"""

import os
import re
import base64
import binascii
from io import BytesIO
from PIL import Image
import sys
from datetime import datetime

class BaseImageDecoder:
    """Base图片解码器类"""
    
    def __init__(self, output_dir="decoded_images"):
        self.output_dir = output_dir
        self.supported_formats = {
            'png': '.png',
            'jpeg': '.jpg', 
            'jpg': '.jpg',
            'gif': '.gif',
            'bmp': '.bmp',
            'tiff': '.tiff',
            'webp': '.webp'
        }
    
    def read_and_preprocess_file(self, file_path):
        """读取并预处理文本文件"""
        try:
            if not os.path.exists(file_path):
                print(f"❌ 错误：文件 {file_path} 不存在！", file=sys.stderr)
                return None
                
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 移除所有空白字符
            content = re.sub(r'\s+', '', content)
            print(f"📄 成功读取文件，内容长度：{len(content)} 字符")
            return content
            
        except Exception as e:
            print(f"❌ 读取文件时出错：{str(e)}", file=sys.stderr)
            return None
    
    def try_decode_base16(self, content):
        """尝试Base16（十六进制）解码"""
        try:
            # 确保内容长度为偶数
            if len(content) % 2 != 0:
                content = '0' + content
            
            # 移除可能的十六进制前缀
            content = re.sub(r'^(0x|0X|\\x)', '', content)
            
            decoded_bytes = binascii.unhexlify(content)
            return decoded_bytes, "base16"
        except Exception:
            return None, None
    
    def try_decode_base32(self, content):
        """尝试Base32解码"""
        try:
            decoded_bytes = base64.b32decode(content, casefold=True)
            return decoded_bytes, "base32"
        except Exception:
            return None, None
    
    def try_decode_base64(self, content):
        """尝试Base64解码"""
        try:
            decoded_bytes = base64.b64decode(content)
            return decoded_bytes, "base64"
        except Exception:
            return None, None
    
    def try_decode_base85(self, content):
        """尝试Base85（Ascii85）解码"""
        try:
            decoded_bytes = base64.a85decode(content)
            return decoded_bytes, "base85"
        except Exception:
            return None, None
    
    def try_decode_base91(self, content):
        """尝试Base91解码"""
        try:
            import base91
            decoded_bytes = base91.decode(content)
            return decoded_bytes, "base91"
        except ImportError:
            print("⚠️  Base91库未安装，跳过Base91解码", file=sys.stderr)
            return None, None
        except Exception:
            return None, None
    
    def is_valid_image(self, data):
        """检查数据是否为有效图片"""
        try:
            img = Image.open(BytesIO(data))
            img.verify()  # 验证图片完整性
            return True
        except Exception:
            return False
    
    def get_image_format(self, data):
        """获取图片格式"""
        try:
            img = Image.open(BytesIO(data))
            return img.format.lower()
        except Exception:
            return None
    
    def save_image(self, data, method, format_name):
        """保存图片到文件"""
        try:
            # 创建输出目录
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)
                print(f"📁 创建输出目录: {self.output_dir}")
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            extension = self.supported_formats.get(format_name.lower(), '.bin')
            filename = f"{method}_{timestamp}{extension}"
            filepath = os.path.join(self.output_dir, filename)
            
            # 保存文件
            with open(filepath, 'wb') as f:
                f.write(data)
            
            file_size = os.path.getsize(filepath)
            print(f"✅ 图片保存成功！")
            print(f"   📁 文件名: {filename}")
            print(f"   📍 路径: {filepath}")
            print(f"   📊 大小: {file_size:,} 字节")
            print(f"   🎨 格式: {format_name.upper()}")
            
            return filepath
            
        except Exception as e:
            print(f"❌ 保存图片失败: {str(e)}", file=sys.stderr)
            return None
    
    def decode_file(self, file_path):
        """主解码流程"""
        print("🚀 Base图片解码器启动！")
        print("=" * 60)
        
        # 读取文件内容
        content = self.read_and_preprocess_file(file_path)
        if not content:
            print("❌ 无法读取文件内容，解码终止！", file=sys.stderr)
            return []
        
        # 定义所有解码函数
        decoders = [
            self.try_decode_base16,
            self.try_decode_base32, 
            self.try_decode_base64,
            self.try_decode_base85,
            self.try_decode_base91
        ]
        
        successful_decodes = []
        
        print(f"\n🔍 开始尝试各种解码方式...")
        print("-" * 60)
        
        for decoder in decoders:
            decoder_name = decoder.__name__.replace('try_decode_', '').upper()
            print(f"\n🔄 尝试 {decoder_name} 解码...")
            
            try:
                decoded_data, method = decoder(content)
                
                if decoded_data and self.is_valid_image(decoded_data):
                    format_name = self.get_image_format(decoded_data)
                    
                    print(f"🎉 {decoder_name} 解码成功！")
                    print(f"   📏 数据大小: {len(decoded_data):,} 字节")
                    print(f"   🎨 图片格式: {format_name}")
                    
                    # 保存图片
                    saved_path = self.save_image(decoded_data, method, format_name)
                    if saved_path:
                        successful_decodes.append({
                            'method': method,
                            'path': saved_path,
                            'format': format_name,
                            'size': len(decoded_data)
                        })
                else:
                    print(f"❌ {decoder_name} 解码失败或不是有效图片")
                    
            except Exception as e:
                print(f"❌ {decoder_name} 解码出错: {str(e)}")
        
        print(f"\n" + "=" * 60)
        print(f"🎊 解码完成！成功解码出 {len(successful_decodes)} 张图片")
        print("=" * 60)
        
        # 显示解码结果摘要
        if successful_decodes:
            print(f"\n📋 解码结果摘要：")
            for i, result in enumerate(successful_decodes, 1):
                print(f"   {i}. {result['method'].upper()} -> {result['format'].upper()} ({result['size']:,} 字节)")
        
        return successful_decodes


def main():
    """主函数"""
    # 默认文件路径（可以修改为你的文件路径）
    default_file_path = r"F:\ctf题\CTF那些事儿\题目\第1章\1-2\packet3.png2.txt"
    
    # 创建解码器实例
    decoder = BaseImageDecoder()
    
    # 执行解码
    results = decoder.decode_file(default_file_path)
    
    if results:
        print(f"\n🎉 任务完成！共解码出 {len(results)} 张图片")
    else:
        print(f"\n😔 很遗憾，没有成功解码出任何图片")


if __name__ == "__main__":
    main()